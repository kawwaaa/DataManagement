# generate_2024_2025_sales.py - ONE CSV + CLEAR GROWTH SECTION
import pandas as pd
import random
from datetime import date, timedelta
from pathlib import Path
import numpy as np
from holidays import LK  # pip install holidays

# -------------------------------------------------
# 1. PRODUCTS & PRICES
# -------------------------------------------------
PRODUCTS = [
    # === 10 Stable (Low Fluctuation) ===
    "White Rice 1KG", "Coconut", "Plain Flour 1KG", "White Sugar 1KG", "Salt 1KG",
    "Fresh Milk 1L", "Butter 227G", "Plain Bread 450G", "Bottled Water 5L", "Toilet Paper 2PLY",
    # === 10 Holiday-Sensitive (High Fluctuation) ===
    "Ice Cream 1L", "Coconut Sweets", "Chocolate Wafers 85G", "Fresh Chicken 1KG",
    "Coca-Cola 1.5L", "Mango Jam 500G", "Milo Powder 400G", "Tomatoes 1KG",
    "Pineapple Whole", "Coconut Oil 750ML"
]

PRODUCT_PRICES = {
    "White Rice 1KG": 220, "Coconut": 130, "Plain Flour 1KG": 380, "White Sugar 1KG": 350,
    "Salt 1KG": 100, "Fresh Milk 1L": 400, "Butter 227G": 1200, "Plain Bread 450G": 180,
    "Bottled Water 5L": 250, "Toilet Paper 2PLY": 100, "Ice Cream 1L": 750,
    "Coconut Sweets": 200, "Chocolate Wafers 85G": 100, "Fresh Chicken 1KG": 1400,
    "Coca-Cola 1.5L": 300, "Mango Jam 500G": 650, "Milo Powder 400G": 1000,
    "Tomatoes 1KG": 400, "Pineapple Whole": 400, "Coconut Oil 750ML": 850
}

# -------------------------------------------------
# 2. DATES & DATA DIR
# -------------------------------------------------
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "historical_all.csv"

lk_holidays = LK(years=[2024, 2025])

# -------------------------------------------------
# 3. GROWTH RATES (5 DECLINING, 15 GROWING)
# -------------------------------------------------
# 5 DECLINING PRODUCTS (-12% per year)
DECLINING_PRODUCTS = [
    "Butter 227G",        # Replaced by margarine
    "Plain Bread 450G",   # Shift to artisanal bread
    "Milo Powder 400G",   # Energy drinks rising
    "Coca-Cola 1.5L",     # Health-conscious shift
    "Chocolate Wafers 85G"  # Sugar reduction trend
]

# Annual growth: +15% for growing, -12% for declining
ANNUAL_GROWTH = {p: 1.15 for p in PRODUCTS}  # Default +15%
for p in DECLINING_PRODUCTS:
    ANNUAL_GROWTH[p] = 0.88  # -12% per year

# -------------------------------------------------
# 4. SEASONAL & HOLIDAY MULTIPLIER
# -------------------------------------------------


def get_day_multiplier(current_date, product):
    multiplier = 1.0
    weekday = current_date.weekday()
    day = current_date.day
    month = current_date.month

    # WEEKEND BOOST
    if weekday in [5, 6]:
        multiplier *= 1.3

    # POYA DAYS: NO MEAT, +50% sweets
    if current_date in lk_holidays and "Poya" in lk_holidays.get(current_date, ""):
        if product == "Fresh Chicken 1KG":
            return 0.0  # NO SALES ON POYA
        if product in ["Coconut Sweets", "Pineapple Whole", "Ice Cream 1L"]:
            multiplier *= 1.5

    # SINHALA/TAMIL NEW YEAR (April 13-14)
    if month == 4 and day in [13, 14]:
        if product in ["Coconut Sweets", "Mango Jam 500G", "Coconut Oil 750ML"]:
            multiplier *= 2.0
        if product in ["White Rice 1KG", "Plain Flour 1KG"]:
            multiplier *= 1.6

    # CHRISTMAS (Dec 24-25)
    if month == 12 and day in [24, 25]:
        if product in ["Chocolate Wafers 85G", "Coca-Cola 1.5L", "Butter 227G"]:
            multiplier *= 1.8

    # ASALA MAHA PERAHERA (August) → Meat drop
    if month == 8:
        if product == "Fresh Chicken 1KG":
            multiplier *= 0.4  # -60%

    # SUMMER HEAT (April)
    if month == 4:
        if product == "Ice Cream 1L":
            multiplier *= 1.4

    return multiplier


# -------------------------------------------------
# 5. GENERATE DAILY SALES (ALL IN ONE LIST)
# -------------------------------------------------
print("Generating 2024–2025 sales → ONE CSV...")

all_records = []  # List of (ds, product, units, amount)

total_days = (END_DATE - START_DATE).days + 1
base_daily_units = 50

for prod in PRODUCTS:
    print(f"Generating: {prod}...", end=" ")

    for i in range(total_days):
        current_date = START_DATE + timedelta(days=i)
        ds_str = current_date.strftime('%Y-%m-%d')

        # GROWTH: Apply annual trend
        year_progress = i / 365.0
        growth_factor = ANNUAL_GROWTH[prod] ** year_progress
        units = base_daily_units * growth_factor

        # HOLIDAY & SEASONAL
        multiplier = get_day_multiplier(current_date, prod)
        units *= multiplier

        # RANDOMNESS
        units = max(0, int(units * random.uniform(0.8, 1.2)))

        if units > 0:
            price_per_unit = PRODUCT_PRICES[prod] * random.uniform(0.98, 1.02)
            amount = round(units * price_per_unit, 2)
            all_records.append([ds_str, prod, units, amount])

    print("Done")

# -------------------------------------------------
# 6. SAVE TO ONE CSV: ds, product, units, amount
# -------------------------------------------------
df = pd.DataFrame(all_records, columns=["ds", "product", "units", "amount"])
df["ds"] = pd.to_datetime(df["ds"])
df = df.sort_values(["ds", "product"])

df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSAVED: {OUTPUT_FILE} ({len(df):,} rows)")

# -------------------------------------------------
# 7. PRINT SUMMARY
# -------------------------------------------------
print("\n2024 vs 2025 Growth Summary:")
for prod in PRODUCTS:
    p2024 = df[(df["ds"].dt.year == 2024) & (
        df["product"] == prod)]["amount"].sum()
    p2025 = df[(df["ds"].dt.year == 2025) & (
        df["product"] == prod)]["amount"].sum()
    growth = ((p2025 - p2024) / p2024 * 100) if p2024 > 0 else 0
    print(f"  {prod}: 2024={p2024:,.0f} → 2025={p2025:,.0f} LKR ({growth:+.1f}%)")
