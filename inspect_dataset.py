
from pathlib import Path
import pandas as pd

# Dataset folder
DATA_DIR = Path("data/raw/FoodData_Central_branded_food_csv_2026-04-30")

files_to_inspect = [
    "food.csv",
    "branded_food.csv",
    "food_nutrient.csv",
    "nutrient.csv",
]

for filename in files_to_inspect:
    file_path = DATA_DIR / filename

    print(f"\n{'=' * 60}")
    print(f"File: {filename}")

    if not file_path.exists():
        print("File not found. Check the folder name.")
        continue

    try:
        # Read only the header and first five rows
        df = pd.read_csv(file_path, nrows=5, low_memory=False)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nFirst five rows:")
        print(df.head().to_string(index=False))

    except Exception as error:
        print(f"Could not inspect this file: {error}")
