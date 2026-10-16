
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/FoodData_Central_branded_food_csv_2026-04-30")

nutrient_file = DATA_DIR / "nutrient.csv"

nutrients = pd.read_csv(nutrient_file)

keywords = [
    "energy",
    "protein",
    "sugar",
    "fiber",
    "fibre",
    "sodium",
    "saturated",
    "carbohydrate",
    "fat",
]

matches = nutrients[
    nutrients["name"].str.contains(
        "|".join(keywords),
        case=False,
        na=False
    )
]

print(matches[["id", "name", "unit_name"]].to_string(index=False))
