import os
import json
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / ".env"
load_dotenv('sql_connector.env')
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
DB_URI = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/euroleague'
print("DB_HOST:", db_host)
print("DB_USER:", db_user)
print("DB_PASSWORD:", db_pass)

# ✅ Setup DB engine (adjust as needed)


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
def load_json_files(base_path, uri):
    rows = []
    for season_dir in Path(base_path).iterdir():
        season_code = season_dir.name
        uri_path = season_dir / uri

        if not uri_path.exists():
            continue

        for file in uri_path.glob("*.json"):
            try:
                gamecode = int(file.stem)
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if uri.lower() == "boxscore":
                    team_stats = data.get("Stats", [])
                    for team in team_stats:
                        for player in team.get("PlayersStats", []):
                            player["season_code"] = season_code
                            player["gamecode"] = gamecode
                            rows.append(player)


                elif uri.lower() == "header":
                    data["season_code"] = season_code
                    data["gamecode"] = gamecode
                    rows.append(data)

            except Exception as e:
                print(f"[ERROR] {file}: {e}")

    df=pd.DataFrame(rows)
    if 'Minutes' in df.columns:
        df['Minutes'] = df['Minutes'].apply(convert_minutes_str_to_float)
    return df

def main():
    base_path = r"C:\Users\Mantas\Desktop\AI\python projektai\Euroleague\data"
    engine = create_engine(DB_URI)
    print("Loading raw BoxScore data...")
    df_box = load_json_files(base_path, "BoxScore")
    df_box.to_sql("raw_boxscores", con=engine, if_exists="append", index=False)
    print(f"✅ Stored {len(df_box)} rows in 'raw_boxscores'")

    print("Loading raw Header data...")
    df_header = load_json_files(base_path, "Header")
    df_header.rename(columns={
        "Live": "is_live",
        "Round": "round_number",
        "Date": "game_date",
        "Hour": "game_time",
        "Stadium": "stadium_name",
        "Capacity": "stadium_capacity",
        "TeamA": "team_a_name",
        "TeamB": "team_b_name",
        "CodeTeamA": "team_a_code",
        "TVCodeA": "team_a_tvcode",
        "CodeTeamB": "team_b_code",
        "TVCodeB": "team_b_tvcode",
        "imA": "team_a_image_code",
        "imB": "team_b_image_code",
        "ScoreA": "team_a_score",
        "ScoreB": "team_b_score",
        "CoachA": "coach_a_name",
        "CoachB": "coach_b_name",
        "GameTime": "full_game_time",
        "RemainingPartialTime": "remaining_partial_time",
        "wid": "game_window_id",
        "Quarter": "current_quarter",
        "FoultsA": "team_a_fouls",
        "FoultsB": "team_b_fouls",
        "TimeoutsA": "team_a_timeouts",
        "TimeoutsB": "team_b_timeouts",
        "ScoreQuarter1A": "team_a_q1_score",
        "ScoreQuarter2A": "team_a_q2_score",
        "ScoreQuarter3A": "team_a_q3_score",
        "ScoreQuarter4A": "team_a_q4_score",
        "ScoreExtraTimeA": "team_a_extra_score",
        "ScoreQuarter1B": "team_b_q1_score",
        "ScoreQuarter2B": "team_b_q2_score",
        "ScoreQuarter3B": "team_b_q3_score",
        "ScoreQuarter4B": "team_b_q4_score",
        "ScoreExtraTimeB": "team_b_extra_score",
        "Phase": "competition_phase",
        "PhaseReducedName": "phase_short",
        "Competition": "competition_name",
        "CompetitionReducedName": "competition_code",
        "pcom": "competition_id",
        "Referee1": "referee_1_name",
        "Referee2": "referee_2_name",
        "Referee3": "referee_3_name"
        # ...add all necessary renames here
    }, inplace=True)
    df_header["game_date"] = pd.to_datetime(df_header["game_date"], format="%d/%m/%Y").dt.date
    df_header.to_sql("raw_headers", con=engine, if_exists="append", index=False)
    print(f"✅ Stored {len(df_header)} rows in 'raw_headers'")

if __name__ == "__main__":
    main()

