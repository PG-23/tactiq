"""
pipeline.py
Runs the full Phase 1 pipeline:
  1. Parse FM24 HTML export
  2. Score players
  3. Load into PostgreSQL

Usage:
  python pipeline.py <path_to_fm_export.html>
"""

import sys
from fm_parser import parse_fm_html
from scoring import score_all
from database import init_db, upsert_players


def run(filepath: str):
    print(f"\n{'='*50}")
    print("FM Optimizer — Phase 1 Pipeline")
    print(f"{'='*50}\n")

    # Step 1: Parse
    print(f"[1/3] Parsing FM24 export: {filepath}")
    players = parse_fm_html(filepath)
    print(f"      → {len(players)} players parsed\n")

    # Step 2: Score
    print("[2/3] Scoring players by position...")
    scored = score_all(players)
    print(f"      → {len(scored)} players scored\n")

    # Preview top 10
    print("      Top 10 players by position score:")
    print(f"      {'Name':<22} {'Position':<8} {'Score':>6} {'Value':>12} {'Age':>4}")
    print(f"      {'-'*56}")
    for p in scored[:10]:
        val = f"£{p.value:,.0f}" if p.value else "N/A"
        print(f"      {p.name:<22} {p.primary_position:<8} {p.score:>6.2f} {val:>12} {str(p.age or '?'):>4}")

    # Merge scores back into raw player dicts for DB insertion
    score_map = {p.name: p.score for p in scored}
    for player in players:
        player["position_score"] = score_map.get(player.get("name"), None)

    # Step 3: Load into PostgreSQL
    print(f"\n[3/3] Loading into PostgreSQL...")
    init_db()
    upsert_players(players)
    print(f"\n{'='*50}")
    print("Phase 1 complete.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <path_to_fm_export.html>")
        sys.exit(1)
    run(sys.argv[1])