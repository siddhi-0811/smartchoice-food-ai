
from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    "data/raw/FoodData_Central_branded_food_csv_2026-04-30"
)

df = pd.read_csv(
    DATA_DIR / "food_nutrient.csv",
    usecols=["fdc_id", "nutrient_id", "amount", "derivation_id"],
    nrows=100_000,
)

nutrients = pd.read_csv(DATA_DIR / "nutrient.csv")

selected_ids = [1008, 1003, 1004, 1005, 2000, 1235, 1079, 1093, 1258]

df = df[df["nutrient_id"].isin(selected_ids)]

print("Derivation ID counts:")
print(df["derivation_id"].value_counts(dropna=False).head(15))

print("\nSelected nutrient records:")
print(
    df.merge(
        nutrients[["id", "name", "unit_name"]],
        left_on="nutrient_id",
        right_on="id",
        how="left",
    )[
        ["fdc_id", "name", "amount", "unit_name", "derivation_id"]
    ].head(20).to_string(index=False)
)
