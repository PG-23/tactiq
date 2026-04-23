"""
scoring.py
Calculates a position-weighted score for each player.

Each position has a weight profile — attributes most important to that role
get higher weights. Weights sum to 1.0 per position.

This is the most important design decision in Phase 1. These defaults are
a reasonable starting point but you should tune them based on FM24 meta.
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Weight profiles per broad position group
# Format: {attribute_name: weight}
# Weights should sum to 1.0 — enforced at runtime.
# ---------------------------------------------------------------------------

POSITION_WEIGHTS: dict[str, dict[str, float]] = {
    "GK": {
        "reflexes": 0.18,
        "handling": 0.15,
        "one_on_ones": 0.12,
        "positioning": 0.10,
        "concentration": 0.08,
        "aerial_reach": 0.08,
        "command_of_area": 0.07,
        "communication": 0.06,
        "kicking": 0.06,
        "decisions": 0.05,
        "composure": 0.05,
    },
    "DC": {
        "marking": 0.14,
        "tackling": 0.13,
        "heading": 0.12,
        "positioning": 0.11,
        "concentration": 0.10,
        "jumping_reach": 0.09,
        "strength": 0.08,
        "anticipation": 0.08,
        "composure": 0.07,
        "decisions": 0.05,
        "pace": 0.03,
    },
    "DL_DR": {  # Full backs
        "crossing": 0.13,
        "tackling": 0.12,
        "marking": 0.10,
        "pace": 0.10,
        "stamina": 0.09,
        "work_rate": 0.08,
        "acceleration": 0.08,
        "dribbling": 0.07,
        "positioning": 0.07,
        "decisions": 0.06,
        "concentration": 0.05,
        "teamwork": 0.05,
    },
    "MC": {  # Central midfield
        "passing": 0.14,
        "vision": 0.12,
        "decisions": 0.11,
        "work_rate": 0.09,
        "stamina": 0.09,
        "technique": 0.08,
        "off_the_ball": 0.08,
        "first_touch": 0.07,
        "composure": 0.07,
        "tackling": 0.06,
        "anticipation": 0.05,
        "teamwork": 0.04,
    },
    "ML_MR": {  # Wide midfield / wingers
        "dribbling": 0.15,
        "pace": 0.13,
        "acceleration": 0.11,
        "crossing": 0.10,
        "technique": 0.09,
        "flair": 0.08,
        "off_the_ball": 0.08,
        "work_rate": 0.07,
        "stamina": 0.07,
        "first_touch": 0.06,
        "decisions": 0.06,
    },
    "AMC": {  # Attacking midfielder
        "vision": 0.15,
        "passing": 0.12,
        "technique": 0.11,
        "dribbling": 0.10,
        "off_the_ball": 0.10,
        "finishing": 0.09,
        "first_touch": 0.08,
        "composure": 0.08,
        "decisions": 0.07,
        "flair": 0.06,
        "anticipation": 0.04,
    },
    "ST": {
        "finishing": 0.17,
        "composure": 0.13,
        "off_the_ball": 0.12,
        "anticipation": 0.10,
        "heading": 0.09,
        "pace": 0.08,
        "strength": 0.08,
        "first_touch": 0.07,
        "technique": 0.07,
        "decisions": 0.05,
        "acceleration": 0.04,
    },
}


# ---------------------------------------------------------------------------
# Map FM24 position strings → weight profile keys
# ---------------------------------------------------------------------------
POSITION_MAP = {
    "GK": "GK",
    "D (C)": "DC",
    "D (R)": "DL_DR",
    "D (L)": "DL_DR",
    "WB (R)": "DL_DR",
    "WB (L)": "DL_DR",
    "DM": "MC",
    "M (C)": "MC",
    "M (R)": "ML_MR",
    "M (L)": "ML_MR",
    "AM (C)": "AMC",
    "AM (R)": "ML_MR",
    "AM (L)": "ML_MR",
    "ST": "ST",
    "F (C)": "ST",
}


@dataclass
class ScoredPlayer:
    name: str
    positions: list[str]
    primary_position: str
    score: float
    value: float | None
    wage: float | None
    age: int | None


def _validate_weights():
    """Ensure all weight profiles sum to ~1.0."""
    for pos, weights in POSITION_WEIGHTS.items():
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights for {pos} sum to {total:.3f}, expected 1.0")


def score_player(player: dict, position_key: str) -> float:
    """
    Calculate a 0–20 score for a player in a given position profile.
    FM24 attributes are on a 1–20 scale, so the output is directly comparable.
    Returns 0.0 if the position has no weight profile or attributes are missing.
    """
    weights = POSITION_WEIGHTS.get(position_key)
    if not weights:
        return 0.0

    total, weight_used = 0.0, 0.0
    for attr, weight in weights.items():
        val = player.get(attr)
        if val is not None:
            try:
                total += float(val) * weight
                weight_used += weight
            except (TypeError, ValueError):
                pass

    if weight_used < 0.5:
        return 0.0
    # Re-normalise if some attributes were missing
    return round(total / weight_used * weight_used / sum(weights.values()), 2)


def get_primary_position(positions: list[str]) -> str | None:
    """Return the first recognised position from the player's position list."""
    for pos in positions:
        for fm_pos in POSITION_MAP:
            if fm_pos in pos:
                return POSITION_MAP[fm_pos]
    return None


def score_all(players: list[dict]) -> list[ScoredPlayer]:
    """
    Score every player in the list at their primary position.

    Args:
        players: Raw player dicts from parser.py

    Returns:
        List of ScoredPlayer dataclasses, sorted by score descending.
    """
    _validate_weights()
    results = []

    for p in players:
        positions = p.get("position") or []
        primary = get_primary_position(positions)
        if not primary:
            continue  # Skip unrecognised positions

        s = score_player(p, primary)
        results.append(ScoredPlayer(
            name=p.get("name", "Unknown"),
            positions=positions,
            primary_position=primary,
            score=s,
            value=p.get("value"),
            wage=p.get("wage"),
            age=p.get("age"),
        ))

    return sorted(results, key=lambda x: x.score, reverse=True)


if __name__ == "__main__":
    # Quick smoke test with dummy data
    dummy = [
        {
            "name": "Test Striker", "position": ["ST"], "age": 24,
            "finishing": 16, "composure": 15, "off_the_ball": 14,
            "anticipation": 13, "heading": 12, "pace": 15, "strength": 13,
            "first_touch": 14, "technique": 13, "decisions": 12, "acceleration": 15,
            "value": 5_000_000, "wage": 10_000,
        },
        {
            "name": "Test GK", "position": ["GK"], "age": 28,
            "reflexes": 17, "handling": 16, "one_on_ones": 15,
            "positioning": 14, "concentration": 15, "aerial_reach": 13,
            "command_of_area": 14, "communication": 12, "kicking": 11,
            "decisions": 13, "composure": 14,
            "value": 3_000_000, "wage": 8_000,
        },
    ]
    scored = score_all(dummy)
    for p in scored:
        print(f"{p.name:20s} | {p.primary_position:6s} | Score: {p.score:.2f} | Value: £{p.value:,.0f}")