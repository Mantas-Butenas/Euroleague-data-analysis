import os
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIGURATION ---
DATA_DIR = r"C:\Users\Mantas\Desktop\AI\python projektai\Euroleague\data"
BOX_PATH = lambda season: os.path.join(DATA_DIR, season, "BoxScore")
HEADER_PATH = lambda season: os.path.join(DATA_DIR, season, "Header")
SEASONS = ['E2021', 'E2022', 'E2023', 'E2024']
load_dotenv('sql_connector.env')
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")

DB_URI = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{3306}/euroleague'
TABLE_NAME = "euroleague_boxscores"


# --- FUNCTIONS ---
def convert_minutes_str_to_float(minutes_str):
    if isinstance(minutes_str, str):
        minutes_str = minutes_str.strip().upper()
        if minutes_str in ["DNP", ""]:
            return 0.0
        try:
            minutes, seconds = map(int, minutes_str.split(":"))
            return round(minutes + seconds / 60, 2)
        except Exception:
            return 0.0
    return 0.0


def load_boxscores(season):
    all_games = []

    for file in os.listdir(BOX_PATH(season)):
        if file.endswith('.json'):
            gamecode = int(file.replace('.json', ''))
            path = os.path.join(BOX_PATH(season), file)
            with open(path, encoding='utf-8') as f:
                game = json.load(f)

            if 'Stats' not in game:
                print(f"⚠️ No 'Stats' key in {path}")
                continue

            # Extract team scores
            team_scores = {}
            for team_data in game['Stats']:
                team_name = team_data.get("Team", "")
                totr = team_data.get("totr", {})
                points = int(totr.get("Points", 0))
                team_scores[team_name] = points

            if len(team_scores) != 2:
                print(f"⚠️ Incomplete score data in {path}")
                continue

            max_score = max(team_scores.values())

            # Add player stats + TeamWin
            for team_data in game['Stats']:
                team_name = team_data.get("Team", "")
                team_score = team_scores.get(team_name, 0)
                team_win = team_score == max_score

                players = team_data.get('PlayersStats', [])
                for player in players:
                    player['SeasonCode'] = season
                    player['GameCode'] = gamecode
                    player['Team'] = team_name  # ensure team is saved in DF
                    player['TeamWin'] = team_win
                    all_games.append(player)

    df = pd.DataFrame(all_games)

    if 'Minutes' in df.columns:
        df['Minutes'] = df['Minutes'].apply(convert_minutes_str_to_float)

    return df


def load_headers(season):
    headers = []
    for file in os.listdir(HEADER_PATH(season)):
        if file.endswith('.json'):
            gamecode = int(file.replace('.json', ''))
            with open(os.path.join(HEADER_PATH(season), file), encoding='utf-8') as f:
                data = json.load(f)
                headers.append({
                    "SeasonCode": season,
                    "GameCode": gamecode,
                    "Round": data.get("Round"),
                    "TeamA": data.get("TeamA"),
                    "TeamB": data.get("TeamB")
                })
    return pd.DataFrame(headers)


def calculate_fantasy_points(row):
    try:
        points = row.get('Points', 0)
        dreb = row.get('DefensiveRebounds', 0)
        oreb = row.get('OffensiveRebounds', 0)
        assists = row.get('Assistances', 0)
        steals = row.get('Steals', 0)
        blocks = row.get('BlocksFavour', 0)
        drawn_fouls = row.get('FoulsReceived', 0)
        team_win = row.get('TeamWin')  # Boolean or can be calculated externally
        team_loss = not team_win

        missed_shots = (row.get('FieldGoalsAttempted2', 0) - row.get('FieldGoalsMade2', 0)) + (
                row.get('FieldGoalsAttempted3', 0) - row.get('FieldGoalsMade3', 0))
        missed_free_throws = row.get('FreeThrowsAttempted', 0) - row.get('FreeThrowsMade', 0)
        turnovers = row.get('Turnovers', 0)
        block_against = row.get('BlocksAgainst', 0)
        fouled_out = row.get('FoulsCommited', 0) >= 5

        total_rebounds = dreb + oreb

        # Bonuses
        double_double = sum(x >= 10 for x in [points, total_rebounds, assists, steals, blocks]) >= 2
        triple_double = sum(x >= 10 for x in [points, total_rebounds, assists, steals, blocks]) >= 3
        quadruple_double = sum(x >= 10 for x in [points, total_rebounds, assists, steals, blocks]) >= 4

        score = 0
        score += points
        score += dreb * 1
        score += oreb * 1.5
        score += assists * 1.5
        score += steals * 1.5
        score += blocks * 1
        score += drawn_fouls * 1
        score += 1.5 if team_win else -1.5
        score -= missed_shots * 1
        score -= missed_free_throws * 1
        score -= turnovers * 1.5
        score -= block_against * 0.5
        score -= 5 if fouled_out else 0
        score += 10 if double_double else 0
        score += 30 if triple_double else 0
        score += 100 if quadruple_double else 0

        return round(score, 2)
    except Exception:
        return 0.0


def calculate_advanced_stats(df):
    df['Effectivefg'] = (df['FieldGoalsMade2'] + 1.5 * df['FieldGoalsMade3']) / (df['FieldGoalsAttempted2'] + df['FieldGoalsAttempted3']).replace(0, np.nan)

    df['TrueShooting'] = df['Points'] / (
            2 * (df['FieldGoalsAttempted2'] + df['FieldGoalsAttempted3'] + 0.44 * df['FreeThrowsAttempted'])
    ).replace(0, np.nan)

    df['UsageRate'] = 100 * (
            (df['FieldGoalsAttempted2'] + df['FieldGoalsAttempted3'] +
             0.44 * df['FreeThrowsAttempted'] + df['Turnovers']) /
            (df['Minutes'] * 5).replace(0, np.nan)
    )

    df['FantasyPoints'] = df.apply(calculate_fantasy_points, axis=1)

    return df


def add_round_and_opponent(df, headers):
    merged = df.merge(headers, on=['SeasonCode', 'GameCode'], how='left')
    merged['OpponentTeam'] = merged.apply(
        lambda row: row['TeamB'] if row['Team'] == row['TeamA'] else row['TeamA'], axis=1
    )
    return merged.drop(columns=['TeamA', 'TeamB'])

def calculate_scoring_system(df):
    df['ScoringSystemAdvantage']=df['FantasyPoints']-df['Valuation']
    return df

def upload_to_sql(df, engine):
    existing = pd.read_sql(f"SELECT SeasonCode, GameCode, Player_ID FROM {TABLE_NAME}", engine)
    before = len(df)
    df = df.merge(existing, on=['SeasonCode', 'GameCode', 'Player_ID'], how='left', indicator=True)
    df = df[df['_merge'] == 'left_only'].drop(columns=['_merge'])
    print(f"Uploading {len(df)} new rows (skipped {before - len(df)})")
    df.to_sql(TABLE_NAME, con=engine, if_exists='append', index=False)


# --- MAIN SCRIPT ---

def main():
    full_df = []
    for season in SEASONS:
        print(f"Processing {season}...")
        box = load_boxscores(season)
        print(f"\n{season} boxscore columns:", box.columns.tolist())
        header = load_headers(season)

        box = calculate_advanced_stats(box)
        box = add_round_and_opponent(box, header)
        full_df.append(box)

    df_final = pd.concat(full_df, ignore_index=True)
    # Clean boolean conversions
    df_final['IsPlaying'] = df_final['IsPlaying'].astype(bool)
    df_final['IsStarter'] = df_final['IsStarter'].astype(bool)
    df_final['TeamWin'] = df_final['TeamWin'].astype(bool)
    calculate_scoring_system(df_final)
    engine = create_engine(DB_URI)
    upload_to_sql(df_final, engine)
    print("✅ Data upload complete.")


if __name__ == "__main__":
    main()