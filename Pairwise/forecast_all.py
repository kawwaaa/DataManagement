# forecast_product.py - ALL PRODUCTS FROM ONE CSV → ONE JSON
import pandas as pd
from prophet import Prophet
import json
import os
from pathlib import Path

# -------------------------------------------------
# 1. CONFIG
# -------------------------------------------------
DATA_DIR = Path("data")
FORECASTS_DIR = Path("forecasts")
FORECASTS_DIR.mkdir(exist_ok=True)

CSV_FILE = DATA_DIR / "historical_all.csv"
OUTPUT_FILE = FORECASTS_DIR / "all_2026.json"

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Missing: {CSV_FILE}. Run generate_2024_2025_sales.py first!")

print("Loading historical_all.csv...")
df = pd.read_csv(CSV_FILE)
df["ds"] = pd.to_datetime(df["ds"])

# Get unique products
PRODUCTS = sorted(df["product"].unique())
print(f"Found {len(PRODUCTS)} products: {PRODUCTS}")

# -------------------------------------------------
# 2. FORECAST ALL PRODUCTS
# -------------------------------------------------
all_forecasts = []

for prod in PRODUCTS:
    print(f"Forecasting: {prod}...", end=" ")

    # Filter product data
    prod_df = df[df["product"] == prod][["ds", "amount"]].copy()
    prod_df.rename(columns={"amount": "y"}, inplace=True)
    if len(prod_df) < 30:
        print("SKIPPED (too few data points)")
        continue

    # Prophet model
    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.5
    )
    m.add_country_holidays('LK')  # Poya, Vesak, New Year
    m.fit(prod_df)

    # Future: 2026
    future = m.make_future_dataframe(periods=365, freq='D')
    forecast = m.predict(future)
    forecast['yhat'] = forecast['yhat'].clip(lower=0)

    # 2026 data
    f2026 = forecast[forecast['ds'].dt.year == 2026].copy()
    if f2026.empty:
        print("NO 2026 DATA")
        continue

    f2026['month'] = f2026['ds'].dt.month_name()
    monthly_avg = f2026.groupby('month')['yhat'].sum().round(0)

    # 2025 actual sales
    sales_2025 = prod_df[prod_df['ds'].dt.year == 2025]['y'].sum()
    sales_2026 = f2026['yhat'].sum()
    growth = ((sales_2026 - sales_2025) /
              sales_2025 * 100) if sales_2025 > 0 else 0

    # Monthly 2025 actual (for comparison)
    actual_2025 = prod_df[prod_df['ds'].dt.year == 2025].copy()
    actual_2025['month'] = actual_2025['ds'].dt.month_name()
    monthly_2025 = actual_2025.groupby('month')['y'].sum().round(0).reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ], fill_value=0).to_dict()

    # Monthly 2026 forecast
    monthly_2026 = monthly_avg.reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ], fill_value=0).to_dict()
    monthly_2026 = {k: int(v) for k, v in monthly_2026.items()}

    result = {
        "product": prod,
        "sales_2025_lkr": int(round(sales_2025)),
        "sales_2026_lkr": int(round(sales_2026)),
        "growth_percent": round(growth, 1),
        "peak_month": max(monthly_2026, key=monthly_2026.get),
        "low_month": min(monthly_2026, key=monthly_2026.get),
        "monthly_2025_lkr": {k: int(v) for k, v in monthly_2025.items()},
        "monthly_2026_lkr": monthly_2026
    }

    all_forecasts.append(result)
    print(f"Done (+{growth:+.1f}%)")

# -------------------------------------------------
# 3. SAVE ALL TO ONE JSON
# -------------------------------------------------
with open(OUTPUT_FILE, "w") as f:
    json.dump(all_forecasts, f, indent=2)

print(f"\nALL FORECASTS SAVED → {OUTPUT_FILE}")
print(f"   Total products: {len(all_forecasts)}")
print("   Run mcp_server.py → Open frontend.html")
