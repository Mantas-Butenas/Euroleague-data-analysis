import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from sqlalchemy import create_engine
import numpy as np

# Define the Kaggle dataset and path
dataset = "babissamothrakis/euroleague-datasets"
download_dir = "archive"

# Set up the Kaggle API
api = KaggleApi()
api.authenticate()

# Download the latest dataset
print("Downloading the latest Euroleague dataset...")
api.dataset_download_files(dataset, path=download_dir, unzip=True)
print("Dataset updated successfully!")

# Create the SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:0338Monteur0494@localhost/euroleague")

# List of all files in the dataset folder
files = os.listdir(download_dir)

# Loop through files and load them into the database
for file in files:
    if file.endswith(".csv"):
        # Load the CSV into a Pandas DataFrame
        df = pd.read_csv(os.path.join(download_dir, file))

        # Replace -inf with NaN (will be stored as NULL in MySQL)
        df.replace([-np.inf, np.inf], np.nan, inplace=True)

        # Use the filename as the table name (without .csv)
        table_name = file.replace(".csv", "")

        # Insert or replace data in MySQL
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

print("Data has been updated in the database!")
