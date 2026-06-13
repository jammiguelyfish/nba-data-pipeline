# 🏀 NBA Data Pipeline & Analytics Dashboard

An end-to-end data engineering project that extracts NBA team and player statistics from the official NBA API, transforms them in a local DuckDB warehouse, and presents interactive analytics via a Streamlit dashboard.

Note: The data and views are quite limited as this is just for practice only

## Architecture

```
NBA API  →  Python ETL (nba_api)  →  DuckDB (local warehouse)  →  Streamlit Dashboard
```

## Features

- **ETL Pipeline** — Extracts team standings and league leaders from the NBA API for the 2025-26 season, loads into staging tables, and transforms into analytics-ready tables.
- **DuckDB Warehouse** — Local analytical database with `analytics_team_standings` and `analytics_league_leaders` tables.
- **Interactive Dashboard** — Streamlit app with:
  - Sidebar filters (team selection, minimum games played)
  - KPI metrics row
  - Win % vs Offensive Efficiency scatter plot
  - Head-to-head team comparison tool
  - League leaders across Points, Assists, Rebounds, Steals, and Blocks
  - Top scorers bar chart

## Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/nba-data-pipeline.git
cd nba-data-pipeline

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the dashboard (includes an ETL trigger button)
python -m streamlit run app.py
```

On first launch, click **"🔄 Trigger Data Pipeline ETL"** in the sidebar to fetch data and populate the database.

You can also run the pipeline standalone:

```bash
python pipeline.py
```

## Project Structure

```
nba-data-pipeline/
├── app.py            # Streamlit dashboard
├── pipeline.py       # ETL pipeline (extract, load, transform)
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- See `requirements.txt` for package dependencies

## License

MIT
