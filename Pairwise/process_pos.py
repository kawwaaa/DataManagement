# process_pos.py
# -------------------------------------------------
# Convert raw POS → Prophet-ready per-transaction CSV
# -------------------------------------------------
import pandas as pd
from pathlib import Path
import os

# -------------------------------------------------
# 1. SETTINGS
# -------------------------------------------------
DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "transactions_prophet.csv"

# -------------------------------------------------
# 2. FIND INPUT FILE
# -------------------------------------------------
possible_inputs = [

    DATA_DIR / "bill_data.tsv",
    "data/bill_data.tsv"
]

input_path = None
for p in possible_inputs:
    if Path(p).exists():
        input_path = Path(p)
        break

if input_path is None:
    print("Error: No input file found. Expected one of:")
    for p in possible_inputs:
        print(f"  - {p}")
    exit(1)

print(f"Found: {input_path}")

# -------------------------------------------------
# 3. READ & STANDARDIZE
# -------------------------------------------------
try:
    if input_path.suffix.lower() == ".tsv":
        # Generated TSV has no header
        df = pd.read_csv(
            input_path,
            sep="\t",
            header=None,
            names=["bill_no", "product_name",
                   "no_of_units", "full_amount", "date"],
            dtype={"full_amount": float, "no_of_units": int}
        )
    else:
        # CSV has header
        df = pd.read_csv(input_path)
        df = df.rename(columns={
            "bill no": "bill_no",
            "product name": "product_name",
            "no of units": "no_of_units",
            "full amount": "full_amount",
            "date": "ds"
        })
        # Ensure date column exists
        if "ds" not in df.columns:
            df = df.rename(columns={"date": "ds"})
except Exception as e:
    print(f"Error reading {input_path}: {e}")
    exit(1)

# -------------------------------------------------
# 4. CONVERT DATE → ds (ISO format)
# -------------------------------------------------
df['ds'] = pd.to_datetime(
    df['ds' if 'ds' in df.columns else 'date']).dt.strftime('%Y-%m-%d')

# -------------------------------------------------
# 5. RENAME y
# -------------------------------------------------
df = df.rename(columns={"full_amount": "y"})

# -------------------------------------------------
# 6. KEEP ONLY NEEDED COLUMNS
# -------------------------------------------------
df = df[["ds", "y", "product_name", "no_of_units", "bill_no"]]

# -------------------------------------------------
# 7. SAVE
# -------------------------------------------------
DATA_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Success: {len(df):,} transactions saved")
print(f"File: {OUTPUT_FILE}")
print("\nFirst 5 rows:")
print(df.head())
print("\nColumns:", list(df.columns))
print("\nDate range:", df['ds'].min(), "→", df['ds'].max())
