import json
import time
import requests
from pathlib import Path

# === CONFIGURATION ===
BASE_API_URL = "https://live.euroleague.net/api/"
SEASON_CODES = ["E2024"]
URIS = ["Header", "BoxScore", "Comparison", "PlayByPlay", "Points"]
SAVE_DIR = Path("data")  # Root folder for saving files
REQUEST_DELAY = 1.5  # Delay between API requests (in seconds)


# === MAIN FUNCTION ===
def fetch_and_save_json(season, uri, gamecode):
    url = f"{BASE_API_URL}{uri}?gamecode={gamecode}&seasoncode={season}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            save_path = SAVE_DIR / season / uri
            save_path.mkdir(parents=True, exist_ok=True)
            filename = f"{gamecode}.json"
            with open(save_path / filename, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[{season}] {uri} - Game {gamecode} downloaded.")
        except json.JSONDecodeError:
            print(f"[{season}] {uri} - Game {gamecode}: Invalid JSON, skipping.")
    else:
        print(f"[{season}] {uri} - Game {gamecode} NOT FOUND. Status: {response.status_code}")


def main():
    for season in SEASON_CODES:
        print(f"Processing season: {season}")
        for gamecode in range(1, 350):  # Adjust based on expected range
            for uri in URIS:
                season_path = SAVE_DIR / season / uri / f"{gamecode}.json"
                if not season_path.exists():
                    fetch_and_save_json(season, uri, gamecode)
                    time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    main()