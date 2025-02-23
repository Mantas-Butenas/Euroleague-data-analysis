# import update_data
#
# # Run the data update check
# update_data.check_and_update()

import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# MySQL Connection Settings
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "0338Monteur0494"
DB_NAME = "euroleague"

# Load the dataset files
data_dir = "archive"
files = os.listdir(data_dir)
dfs = {}
for file in files:
    df = pd.read_csv(os.path.join(data_dir, file), low_memory=False)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)  # Fix inf values
    dfs[file] = df

# Connect to MySQL using SQLAlchemy
try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    with engine.begin() as conn:
        for file, df in dfs.items():
            table_name = file.replace(".csv", "")
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ {file} imported into MySQL as `{table_name}` table.")
except Exception as e:
    print(f"❌ Error while importing data: {e}")

# Inspect columns for all tables
for name, df in dfs.items():
    print(f"\n📂 File: {name}")
    print("🔹 Columns:", df.columns.tolist())
