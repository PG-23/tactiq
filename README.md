# Tactiq ⚽
> An intelligent squad optimization engine for Football Manager 24.

Tactiq analyses your FM24 squad, scores players using a position-weighted attribute model, and recommends the optimal set of transfers given your budget and league context — powered by integer programming and a clean REST API.

---

## What it does

- **Parses** your FM24 squad HTML export into structured player data
- **Scores** every player across 7 position profiles using weighted FM attributes
- **Stores** your squad in a PostgreSQL database for fast querying
- **Optimizes** transfer decisions within a defined budget (Phase 2 — in progress)
- **Recommends** tactics and formations based on your squad's strengths (Phase 2)
- **Serves** results via a FastAPI REST API (Phase 3)
- **Visualizes** squad composition and transfer suggestions in a dashboard (Phase 4)

---

## Project status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Data layer — parser, scoring model, PostgreSQL loader | ✅ Complete |
| 2 | Core engine — squad optimizer, transfer planner, tactic recommender | 🔄 In progress |
| 3 | API layer — FastAPI backend | ⏳ Planned |
| 4 | Frontend — Streamlit dashboard | ⏳ Planned |

---

## Tech stack

- **Language:** Python 3.11
- **Database:** PostgreSQL via SQLAlchemy
- **Optimization:** PuLP / OR-Tools (Phase 2)
- **API:** FastAPI (Phase 3)
- **Dashboard:** Streamlit + Plotly (Phase 4)
- **Environment:** Anaconda

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/tactiq.git
cd tactiq
```

### 2. Create the Anaconda environment

```bash
conda env create -f environment.yml
conda activate tactiq
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your PostgreSQL connection string
```

### 4. Export your squad from FM24

1. Open your squad screen in FM24
2. Add all desired attribute columns using the **Views** dropdown
3. Press `Ctrl + P` → select **Print to HTML** → save to `data/exports/`

### 5. Run the pipeline

```bash
python src/pipeline.py data/exports/your_squad.html
```

---

## How the scoring model works

Each player is scored on a 1–20 scale (matching FM's own attribute scale) using a weighted average of their attributes for their primary position. For example, a striker's score weights finishing, composure, and off-the-ball movement most heavily, while a centre-back's score prioritises marking, tackling, and positioning.

Position weight profiles are defined in `src/scoring.py` and can be tuned to reflect different tactical philosophies or league metas.

| Position group | Key weighted attributes |
|----------------|------------------------|
| GK | Reflexes, handling, one-on-ones |
| DC | Marking, tackling, heading, positioning |
| DL / DR | Crossing, tackling, pace, stamina |
| MC | Passing, vision, decisions, work rate |
| ML / MR | Dribbling, pace, crossing, technique |
| AMC | Vision, passing, technique, dribbling |
| ST | Finishing, composure, off the ball |

---

## Project structure

```
tactiq/
├── .env.example
├── .gitignore
├── environment.yml
├── README.md
│
├── data/
│   └── exports/        # FM24 HTML exports (git-ignored)
│
└── src/
    ├── parser.py       # FM24 HTML → player dicts
    ├── scoring.py      # Position-weighted scoring model
    ├── database.py     # PostgreSQL schema + loader
    └── pipeline.py     # End-to-end orchestration
```

---

## Roadmap

- [ ] Transfer optimizer using integer programming
- [ ] Tactic recommender based on squad attribute strengths
- [ ] FastAPI REST endpoints
- [ ] Streamlit dashboard with squad visualization
- [ ] Support for FM25

---

## Contributing

This is a portfolio project — contributions aren't expected, but feedback is always welcome. Feel free to open an issue if you spot something or have a suggestion.

---

## Disclaimer

This project is not affiliated with or endorsed by Sports Interactive or SEGA. Football Manager is a trademark of Sports Interactive.