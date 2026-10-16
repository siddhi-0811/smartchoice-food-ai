
from pathlib import Path
import pandas as pd

file_path = Path("data/processed/smartchoice_products.csv")

df = pd.read_csv(file_path, nrows=100_000)

print("\n===== DATASET VALIDATION =====")
print("Rows inspected:", len(df))
print("Duplicate product IDs:", df["fdc_id"].duplicated().sum())
print("Missing ingredients:", df["ingredients"].isna().sum())
print("Missing serving sizes:", df["serving_size"].isna().sum())

nutrient_columns = [
    "energy_kcal",
    "protein_g",
    "total_fat_g",
    "carbohydrates_g",
    "total_sugars_g",
    "added_sugars_g",
    "dietary_fiber_g",
    "sodium_mg",
    "saturated_fat_g",
]

print("\nMissing nutrient values in inspected rows:")
print(df[nutrient_columns].isna().sum())

print("\nNegative nutrient values:")
for column in nutrient_columns:
    count = (df[column] < 0).sum()
    print(f"{column}: {count}")

print("\nSample product records:")
print(
    df[[
        "fdc_id",
        "brand_owner",
        "ingredients",
        "serving_size",
        "serving_size_unit",
        "energy_kcal",
        "protein_g",
        "sodium_mg",
    ]].head(10).to_string(index=False)
)

print("\nValidation inspection complete.")
