
# Euroleague Data Analysis 📊🏀

This portfolio project focuses on collecting, processing, and analyzing Euroleague basketball data using Python and public API access. The  goal is to build insights that could support data-driven decision-making for selecting high-performing players for fantasy leagues.

## 🔍 Project Overview

- ✅ Fetched live game data via Euroleague's public API
- ✅ Cleaned and transformed BoxScore statistics of the players
- ✅ Successfully stored raw JSON and processed DataFrame data in MySQL server
- ✅ Jupyter Notebook environment for analysis, exploration and data engineering
- ✅ Developed modular Python scripts for data ingestion and database integration
- ✅ Project structured for future automation (weekly updates)
- 🧠 Planned: AI implementation for player clustering and fantasy performance prediction
- 🧠 Planned: PowerBI implementation for insight presentation

## 📂 Structure

```
.
├── Euroleague.ipynb        # Main notebook with EDA and cleaning
├── main.py                 # Loads JSONs and stores raw data to SQL
├── download_jsons_from_api.py          # Script to fetch and save JSONs from Euroleague API
├── processed_boxscores.py # Processes data and stores final DataFrame to SQL
├── .gitignore              # Ignores CSVs, venv, and cache files

```

## 🚀 Technologies Used

- **Python** — Pandas, Requests, JSON, Glob, Pathlib, Regex
- **Jupyter Notebook** — EDA, feature engineering, visualization
- **MySQL** — Storage of raw and processed data
- **SQLAlchemy** — Python-DB bridge for SQL operations
- **PyMySQL** — MySQL driver
- **dotenv** — Secure handling of credentials
- **Git & GitHub** — Version control and collaboration
- **Euroleague Public API** *(Unofficial endpoints)*

> 🔄 *Project is in active development — contributions and suggestions welcome!*
