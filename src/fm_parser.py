"""
fm_parser.py
Parses FM24 squad HTML exports into a list of player dicts.

How to export from FM24:
  1. Go to your Squad screen
  2. Use the Views dropdown to add all desired attributes
  3. Press Ctrl+P → 'Web Page' → save the file
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re


# ---------------------------------------------------------------------------
# Mapping of FM24 export column headers → internal attribute names
# Derived from actual FM24 HTML export headers
# ---------------------------------------------------------------------------
COLUMN_MAP = {
    # Identity
    "name":             "name",
    "age":              "age",
    "nat":              "nationality",
    "club":             "club",
    "position":         "position",
    "best pos":         "best_pos",
    "transfer value":   "value",
    "salary":           "wage",

    # Technical
    "cor":              "corners",
    "cro":              "crossing",
    "dri":              "dribbling",
    "fin":              "finishing",
    "fir":              "first_touch",
    "fre":              "free_kick",
    "hea":              "heading",
    "lon":              "long_shots",
    "l th":             "long_throws",
    "mar":              "marking",
    "pas":              "passing",
    "pen":              "penalty_taking",
    "tck":              "tackling",
    "tec":              "technique",

    # Mental
    "agg":              "aggression",
    "ant":              "anticipation",
    "bra":              "bravery",
    "cmp":              "composure",
    "cnt":              "concentration",
    "dec":              "decisions",
    "det":              "determination",
    "fla":              "flair",
    "ldr":              "leadership",
    "otb":              "off_the_ball",
    "pos":              "positioning",
    "tea":              "teamwork",
    "vis":              "vision",
    "wor":              "work_rate",

    # Physical
    "acc":              "acceleration",
    "agi":              "agility",
    "bal":              "balance",
    "jum":              "jumping_reach",
    "pac":              "pace",
    "sta":              "stamina",
    "str":              "strength",

    # Goalkeeping
    "aer":              "aerial_reach",
    "cmd":              "command_of_area",
    "com":              "communication",
    "ecc":              "eccentricity",
    "han":              "handling",
    "kic":              "kicking",
    "1v1":              "one_on_ones",
    "ref":              "reflexes",
    "tro":              "rushing_out",
    "pun":              "tendency_to_punch",
    "thr":              "throwing",
}


def _parse_shorthand(val: str) -> float | None:
    """Convert shorthand like '27M' or '550K' to a float. Returns None if not recognised."""
    val = val.strip()
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
    try:
        return float(val)
    except ValueError:
        return None


def _clean_value(raw: str) -> str | int | float | None:
    """Coerce a raw cell string into an appropriate Python type."""
    val = raw.strip()
    if not val or val in ("-", "N/A", ""):
        return None

    # Strip currency symbols and commas
    val = re.sub(r"[£$€,]", "", val).strip()

    # Remove p/a or p/w wage suffixes
    val = re.sub(r"p/[aw]", "", val, flags=re.IGNORECASE).strip()

    # Handle value ranges e.g. "27M - 30M" → midpoint
    if " - " in val:
        parts = val.split(" - ")
        if len(parts) == 2:
            low = _parse_shorthand(parts[0].strip())
            high = _parse_shorthand(parts[1].strip())
            if low is not None and high is not None:
                return (low + high) / 2

    # Single shorthand value
    parsed = _parse_shorthand(val)
    if parsed is not None:
        return parsed

    # Try plain int
    try:
        return int(val)
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
        List of player dicts with cleaned, typed values
        using internal attribute names.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"FM export not found: {path}")

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    table = soup.find("table")
    if table is None:
        raise ValueError("No <table> found in export — check the file is a valid FM24 HTML export.")

    # Build column index from header row using COLUMN_MAP
    raw_headers = []
    header_row = table.find("tr")
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            raw_headers.append(th.get_text(strip=True).lower().strip())

    players = []
    rows = table.find_all("tr")[1:]  # skip header row

    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue

        raw_values = [c.get_text(strip=True) for c in cells]
        player: dict = {}

        for i, raw_header in enumerate(raw_headers):
            if i >= len(raw_values):
                continue
            internal_name = COLUMN_MAP.get(raw_header)
            if not internal_name:
                continue  # ignore columns we don't need

            raw = raw_values[i]
            if internal_name in ("position", "best_pos"):
                player[internal_name] = _parse_positions(raw)
            else:
                player[internal_name] = _clean_value(raw)

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