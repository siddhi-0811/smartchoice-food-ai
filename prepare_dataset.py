
from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    "data/raw/FoodData_Central_branded_food_csv_2026-04-30"
)
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Important nutrients and their IDs
TARGET_NUTRIENTS = {
    1008: "energy_kcal",
    1003: "protein_g",
    1004: "total_fat_g",
    1005: "carbohydrates_g",
    2000: "total_sugars_g",
    1235: "added_sugars_g",
    1079: "dietary_fiber_g",
    1093: "sodium_mg",
    1258: "saturated_fat_g",
}

print("Reading branded product information...")

products = pd.read_csv(
    DATA_DIR / "branded_food.csv",
    usecols=[
        "fdc_id",
        "brand_owner",
        "brand_name",
        "ingredients",
        "serving_size",
        "serving_size_unit",
        "branded_food_category",
    ],
    low_memory=False,
)

print(f"Products loaded: {len(products):,}")

print("Reading nutrient names...")

nutrients = pd.read_csv(DATA_DIR / "nutrient.csv")
nutrients["id"] = pd.to_numeric(
    nutrients["id"], errors="coerce"
)

nutrients = nutrients[
    nutrients["id"].isin(TARGET_NUTRIENTS)
][["id", "name", "unit_name"]]

nutrient_file = DATA_DIR / "food_nutrient.csv"

# Keep only the required nutrient records.
# Read in chunks to reduce peak memory usage.
chunks = []

print("Processing nutrient records...")

for chunk in pd.read_csv(
    nutrient_file,
    usecols=[
    "fdc_id",
    "nutrient_id",
    "amount",
    "derivation_id",
    ],
    chunksize=250_000,
):
    chunk = chunk[
        chunk["nutrient_id"].isin(TARGET_NUTRIENTS)
    ]

    if not chunk.empty:
        chunks.append(chunk)

if not chunks:
    raise ValueError("No matching nutrient records found.")

nutrient_data = pd.concat(chunks, ignore_index=True)

# Duplicate nutrient records may exist.
# Keep one record per product and nutrient for this baseline.
nutrient_data = nutrient_data.drop_duplicates(
    subset=["fdc_id", "nutrient_id"]
)

nutrient_data["nutrient_name"] = nutrient_data[
    "nutrient_id"
].map(TARGET_NUTRIENTS)

wide_nutrients = nutrient_data.pivot(
    index="fdc_id",
    columns="nutrient_name",
    values="amount",
).reset_index()

wide_nutrients.columns.name = None

print("Combining product and nutrient information...")

result = products.merge(
    wide_nutrients,
    on="fdc_id",
    how="left",
    validate="one_to_one",
)

output_file = OUTPUT_DIR / "smartchoice_products.csv"
result.to_csv(output_file, index=False)

print(f"\nSaved: {output_file}")
print(f"Products in output: {len(result):,}")
print(f"Columns: {len(result.columns)}")
print("\nPreview:")
print(result.head(5).to_string(index=False))

print("\nMissing values in selected nutrients:")
print(
    result[list(TARGET_NUTRIENTS.values())]
    .isna()
    .sum()
    .to_string()
)

print("\nDataset preparation complete!")
