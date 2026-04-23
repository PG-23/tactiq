"""
fm_parser.py
Parses FM24 squad HTML exports into a list of player dicts.

How to export from FM24:
  1. Go to your Squad screen
  2. Use the Views dropdown to add all desired attributes
  3. Press Ctrl+P → 'Print to HTML' → save the file
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re


# ---------------------------------------------------------------------------
# Attribute columns expected from a full FM24 squad export.
# Adjust these if your custom view includes different columns.
# ---------------------------------------------------------------------------
ATTRIBUTE_COLUMNS = [
    "name", "age", "nationality", "club", "position",
    "value", "wage",
    # Technical
    "corners", "crossing", "dribbling", "finishing", "first_touch",
    "free_kick", "heading", "long_shots", "long_throws", "marking",
    "passing", "penalty_taking", "tackling", "technique",
    # Mental
    "aggression", "anticipation", "bravery", "composure", "concentration",
    "decisions", "determination", "flair", "leadership", "off_the_ball",
    "positioning", "teamwork", "vision", "work_rate",
    # Physical
    "acceleration", "agility", "balance", "jumping_reach", "natural_fitness",
    "pace", "stamina", "strength",
    # Goalkeeping
    "aerial_reach", "command_of_area", "communication", "eccentricity",
    "handling", "kicking", "one_on_ones", "reflexes", "rushing_out",
    "tendency_to_punch", "throwing",
]


def _clean_value(raw: str) -> str | int | float | None:
    """Coerce a raw cell string into an appropriate Python type."""
    val = raw.strip()
    if not val or val == "-":
        return None
    # Strip currency symbols and commas from values/wages (e.g. '£1.2M', '£500p/w')
    val = re.sub(r"[£$€,]", "", val)
    val = re.sub(r"p/w", "", val, flags=re.IGNORECASE).strip()
    # Convert shorthand millions/thousands
    if val.endswith("M"):
        try:
            return float(val[:-1]) * 1_000_000
        except ValueError:
            pass
    if val.endswith("K"):
        try:
            return float(val[:-1]) * 1_000
        except ValueError:
            pass
    # Try numeric
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def _parse_positions(raw: str) -> list[str]:
    """
    FM24 encodes positions like 'GK', 'D (C)', 'M (R, L)', 'AM (C)', 'ST'.
    Returns a flat list of canonical position strings.
    """
    if not raw or raw.strip() == "-":
        return []
    positions = []
    for part in re.split(r",\s*(?=[A-Z])", raw.strip()):
        part = part.strip()
        if part:
            positions.append(part)
    return positions


def parse_fm_html(filepath: str | Path) -> list[dict]:
    """
    Parse an FM24 HTML squad export file.

    Args:
        filepath: Path to the .html export file.

    Returns:
        List of player dicts with cleaned, typed values.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"FM export not found: {path}")

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.fm_parser")
    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> found in export — check the file is a valid FM HTML export.")

    # Build column map from the header row
    headers = []
    header_row = table.find("tr")
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            raw_header = th.get_text(strip=True).lower()
            # Normalise header to snake_case
            normalised = re.sub(r"[^a-z0-9]+", "_", raw_header).strip("_")
            headers.append(normalised)

    players = []
    rows = table.find_all("tr")[1:]  # skip header row

    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue  # skip empty/separator rows

        raw_values = [c.get_text(strip=True) for c in cells]
        player: dict = {}

        for i, header in enumerate(headers):
            if i >= len(raw_values):
                player[header] = None
                continue
            raw = raw_values[i]
            if header == "position" or header == "best_pos":
                player[header] = _parse_positions(raw)
            else:
                player[header] = _clean_value(raw)

        # Skip rows that don't look like players
        if not player.get("name"):
            continue

        players.append(player)

    return players


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python fm_parser.py <path_to_fm_export.html>")
        sys.exit(1)

    players = parse_fm_html(sys.argv[1])
    print(f"Parsed {len(players)} players.")
    print(json.dumps(players[:2], indent=2, default=str))