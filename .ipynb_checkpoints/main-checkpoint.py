import update_data

# Run the data update check
update_data.check_and_update()

import os
import pandas as pd

# Load the dataset files
files = os.listdir("archive")
dfs = {file: pd.read_csv(os.path.join("archive", file)) for file in files}

# Inspect columns for all tables
for name, df in dfs.items():
    print(f"\nFile: {name}")
    print("Columns:", df.columns.tolist())