
# Euroleague Data Analysis 📊🏀

This project focuses on collecting, processing, and analyzing Euroleague basketball data using Python and public API access. The ultimate goal is to build insights that could support smarter decision-making — such as selecting high-performing players for fantasy leagues.

## 🔍 Project Overview

- ✅ Fetched live game data via Euroleague's public API
- ✅ Cleaned and transformed player BoxScore and metadata
- ✅ Jupyter Notebook environment for analysis and exploration
- 🛠️ Data cleaning in progress (e.g. handling player minutes formatting)
- 🧠 Planned: player clustering and fantasy performance prediction

## 📂 Structure

```
.
├── Euroleague.ipynb        # Main notebook with EDA and cleaning
├── main.py                 # Deprecated - initial CSV loader
├── update_data.py          # API data fetcher (legacy)
├── archive/                # Contains old scripts, not currently used
├── .gitignore              # Ignores CSVs, venv, and cache files
```

## 🚀 Technologies Used

- Python (Pandas, Requests, NumPy)
- Jupyter Notebook
- Git & GitHub
- API Integration
- [Euroleague API](#) *(Unofficial endpoint)*

## 🧩 What's Next?

- Finish transforming player time played (`MM:SS` → minutes as float)
- Store cleaned datasets in SQL or CSV for further analysis
- Perform player segmentation and ranking
- Visualize key metrics using matplotlib/seaborn

---

> 🔄 *Project is in active development — follow to see progress or suggestions welcome!*
