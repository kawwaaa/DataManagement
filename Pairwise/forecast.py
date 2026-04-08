# forecast.py - Train Prophet for all products and forecast dynamically (positive numbers)
import pandas as pd
from prophet import Prophet
import joblib
import json
import numpy as np


def map_product(query, products):
    """Map user query to a Product_Name using simple keyword matching."""
    query = query.lower()
    product_mappings = {
        'ice cream': 'HIGHLAND SET YOGHURT 90G',
        'yoghurt': 'HIGHLAND SET YOGHURT 90G',
        'yogurt': 'HIGHLAND SET YOGHURT 90G',
        'coconut': 'COCONUT',
        'treacle': 'KITHUL TREACLE BOTTLE 750ML',
        'tea': 'DILMAH PREMIUM LEAF TEA 200G',
        'sugar': 'BROWN SUGAR 1KG',
        'flour': 'PRIMA PLAIN FLOUR 1KG (25)',
        'egg': 'LAKMO EGG PACK L 10',
        'pop corn': 'SIRILAK POP CORN',
        'peanuts': 'SIRILAK ROASTED PEANUTS 75G',
        'toothbrush': 'CLOGARD TOOTHBRUSH SMART PROMO (180)',
        'soya': 'RAIGAM FRIED & DEVILLED SOYA CHICKEN 110G',
        'cuttlefish': 'LAKMEE SOY CUTTLEFISH 60G'
    }
    for keyword, product in product_mappings.items():
        if keyword in query.lower() and product in products:
            return product
    print(f"⚠️ No product match for '{query}'. Using default: {products[0]}")
    return products[0]


def train_and_cache_models():
    """Train Prophet models for all products and cache them."""
    print("🚀 Training Prophet models for all products...")

    # Load POS data
    try:
        daily_sales = pd.read_csv('thistorical_sales.csv')
        daily_sales['ds'] = pd.to_datetime(daily_sales['ds'])
    except FileNotFoundError:
        print("❌ historical_sales.csv not found! Run process_pos.py first.")
        return {}, None

    # Load holidays and weather
    try:
        holidays = pd.read_csv('holidays.csv')
        holidays['ds'] = pd.to_datetime(holidays['ds'])
    except FileNotFoundError:
        print("⚠️ holidays.csv not found! Using empty holidays.")
        holidays = pd.DataFrame(
            columns=['holiday', 'ds', 'lower_window', 'upper_window'])
    try:
        weather = pd.read_csv('weather.csv')
        weather['ds'] = pd.to_datetime(weather['ds'])
    except FileNotFoundError:
        print("⚠️ weather.csv not found! Generating fake weather.")
        dates = pd.date_range('2025-01-01', '2025-12-31')
        weather = pd.DataFrame({
            'ds': dates,
            'temperature': 28 + 4 * np.sin(2 * np.pi * np.arange(len(dates)) / 365),
            'precip': np.random.exponential(2, len(dates))
        })

    # Merge weather with sales
    daily_sales = daily_sales.merge(weather, on='ds', how='left').fillna({
        'temperature': 30, 'precip': 0})

    # Train models for all products
    products = daily_sales['Product_Name'].unique()
    models = {}
    for product in products:
        product_data = daily_sales[daily_sales['Product_Name'] == product][[
            'ds', 'y', 'temperature', 'precip']]
        if len(product_data) < 2:
            print(
                f"⚠️ Skipping {product}: only {len(product_data)} days of data")
            continue
        m = Prophet(
            holidays=holidays,
            seasonality_mode='multiplicative',
            yearly_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05,
            holidays_prior_scale=10.0
        )
        m.add_regressor('temperature')
        m.add_regressor('precip')
        m.fit(product_data)
        models[product] = m
        print(f"✅ Trained model for {product}")

    # Save models
    joblib.dump(models, 'prophet_models.pkl')
    context = {
        'products': list(models.keys()),
        'training_start': str(daily_sales['ds'].min().date()),
        'training_end': str(daily_sales['ds'].max().date())
    }
    with open('model_context.json', 'w') as f:
        json.dump(context, f)
    return models, weather


def forecast_for_product(product, models, weather):
    """Generate forecast for a specific product, ensuring positive numbers."""
    if product not in models:
        print(f"❌ Error: No model for {product}")
        return None

    m = models[product]
    weather_2026 = weather[weather['ds'].dt.year == 2026]
    future = m.make_future_dataframe(periods=365)
    future = future.merge(weather_2026, on='ds', how='left').fillna(
        {'temperature': 30, 'precip': 0})
    forecast = m.predict(future)
    forecast['yhat'] = forecast['yhat'].clip(
        lower=0)  # Ensure positive forecasts
    forecast['Product_Name'] = product
    return forecast


if __name__ == "__main__":
    # Train and cache models
    models, weather = train_and_cache_models()
    if not models:
        print("❌ No models trained! Exiting.")
        exit(1)

    # Simulate user queries
    queries = [
        "What are ice cream sales in 2026?",
        "Show coconut sales for 2026",
        "Forecast treacle sales for April 2026"
    ]

    # Process each query
    products = list(models.keys())
    forecasts = []
    for query in queries:
        product = map_product(query, products)
        print(f"\n📝 Processing query: '{query}' → Product: {product}")
        forecast = forecast_for_product(product, models, weather)
        if forecast is None:
            continue

        # Save forecast for this product
        forecast.to_csv(
            f'forecast_2026_{product.replace(" ", "_")}.csv', index=False)

        # Identify peaks (top 10% sales)
        peaks = forecast[forecast['yhat'] > forecast['yhat'].quantile(0.9)][[
            'ds', 'yhat']]
        peaks['ds'] = peaks['ds'].dt.strftime('%Y-%m-%d')

        # Print results
        total_2026 = forecast[forecast['ds'].dt.year == 2026]['yhat'].sum()
        print(f"✅ Forecast for {product} in 2026: {total_2026:,.0f} LKR")
        print(f"📈 Sample Peaks (Top 10%):")
        for _, row in peaks.head().iterrows():
            print(f"  - {row['ds']}: {row['yhat']:,.0f} LKR")
        print(
            f"📊 Holiday Effects: {forecast[forecast['ds'].dt.year == 2026].get('holidays', pd.Series(0)).sum():,.0f} LKR")
        print(
            f"💾 Forecast saved to forecast_2026_{product.replace(' ', '_')}.csv")
        forecasts.append(forecast)

    # Combine all forecasts
    if forecasts:
        combined_forecast = pd.concat(forecasts)
        combined_forecast.to_csv('forecast_2026_all.csv', index=False)
        print("✅ Combined forecast saved to forecast_2026_all.csv")
