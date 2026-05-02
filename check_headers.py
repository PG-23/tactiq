"""
Temporary diagnostic script — prints the raw column headers from your FM24 export.
Run from the tactiq/ root:
    python check_headers.py data/exports/brighton.html
"""

import sys
from bs4 import BeautifulSoup

filepath = sys.argv[1] if len(sys.argv) > 1 else "data/exports/brighton.html"

soup = BeautifulSoup(open(filepath, encoding="utf-8", errors="replace").read(), "lxml")
table = soup.find("table")

if not table:
    print("No table found — check the file is a valid FM24 HTML export.")
    sys.exit(1)

headers = [th.get_text(strip=True) for th in table.find("tr").find_all(["th", "td"])]

print(f"\nFound {len(headers)} columns:\n")
for i, h in enumerate(headers):
    print(f"  [{i:02d}] {h}")