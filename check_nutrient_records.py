
from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    "data/raw/FoodData_Central_branded_food_csv_2026-04-30"
)

nutrient_file = DATA_DIR / "food_nutrient.csv"
branded_file = DATA_DIR / "branded_food.csv"

target_ids = [1008, 1003, 1004, 1005, 2000, 1235, 1079, 1093, 1258]

print("Checking duplicate product-nutrient records...")

counts = {}

for chunk in pd.read_csv(
    nutrient_file,
    usecols=["fdc_id", "nutrient_id"],
    chunksize=250_000,
):
    chunk = chunk[chunk["nutrient_id"].isin(target_ids)]

    grouped = chunk.groupby(
        ["fdc_id", "nutrient_id"]
    ).size()

    repeated = grouped[grouped > 1]

    for key, count in repeated.items():
        counts[key] = counts.get(key, 0) + int(count - 1)

print("Repeated records beyond the first:", sum(counts.values()))
print("Product-nutrient pairs with repeats:", len(counts))

print("\nChecking serving-size units...")

servings = pd.read_csv(
    branded_file,
    usecols=["serving_size", "serving_size_unit"],
)

print(servings["serving_size_unit"].value_counts(dropna=False).head(15))

print("\nCheck complete.")
