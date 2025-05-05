import requests

endpoints = ["Header", "Points", "BoxScore", "PlaybyPlay", "Comparison", "ShootingGraphic"]
season_code = "E2022"
game_code = "1"

for endpoint in endpoints:
    url = f"https://live.euroleague.net/api/{endpoint}?gamecode={game_code}&seasoncode={season_code}"
    response = requests.get(url)
    print(f"{endpoint}: {response.status_code}")
    print(response.text[:500])  # Print first 500 chars to preview the data
