
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_FILE = DATA_DIR / "processed" / "smartchoice_products.csv"
RAW_DIR = DATA_DIR / "raw"

# Find the extracted USDA folder automatically.
candidates = [
    p for p in RAW_DIR.iterdir()
    if p.is_dir() and (p / "food.csv").exists()
]
if not candidates:
    raise FileNotFoundError(
        "Could not find the extracted USDA folder inside data/raw."
    )

USDA_DIR = candidates[0]
FOOD_FILE = USDA_DIR / "food.csv"
DB_FILE = DATA_DIR / "processed" / "smartchoice.db"

DATA_DIR.joinpath("processed").mkdir(exist_ok=True)

if DB_FILE.exists():
    DB_FILE.unlink()

connection = sqlite3.connect(DB_FILE)

print("Importing product descriptions...")

# Import food descriptions into a SQLite lookup table.
connection.execute("""
    CREATE TABLE food_descriptions (
        fdc_id INTEGER PRIMARY KEY,
        description TEXT
    )
""")

for chunk in pd.read_csv(
    FOOD_FILE,
    usecols=["fdc_id", "description"],
    chunksize=100_000,
):
    chunk.to_sql(
        "food_descriptions",
        connection,
        if_exists="append",
        index=False,
    )

print("Importing processed product data...")

# Import the prepared CSV in chunks.
for chunk in pd.read_csv(
    PROCESSED_FILE,
    chunksize=25_000,
    low_memory=False,
):
    chunk.to_sql(
        "products",
        connection,
        if_exists="append",
        index=False,
    )

connection.execute("""
    CREATE INDEX idx_products_fdc_id ON products (fdc_id)
""")
connection.execute("""
    CREATE INDEX idx_food_description ON food_descriptions (description)
""")

connection.commit()
connection.close()

print(f"Database created: {DB_FILE}")
print("Database build complete!")
