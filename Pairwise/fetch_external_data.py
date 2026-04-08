# fetch_external_data.py - Fetch all holidays and weather online
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()


def get_sri_lanka_holidays(start_year=2024, mid_year=2025, end_year=2026):
    api_key = os.getenv('CALENDARIFIC_API_KEY')
    holidays = []
    for year in [start_year, mid_year, end_year]:
        if api_key:
            url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country=LK&year={year}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()['response']['holidays']
                holidays.extend([
                    {'holiday': h['name'], 'ds': h['date']['iso'].split('T')[
                        0]}
                    for h in data
                ])
            except Exception as e:
                print(
                    f"❌ Holiday API failed for {year}: {e}. Using fake holidays.")
                holidays.extend([
                    {'holiday': 'New Year\'s Day', 'ds': f'{year}-01-01'},
                    {'holiday': 'Duruthu Poya', 'ds': f'{year}-01-03'},
                    {'holiday': 'Tamil Thai Pongal', 'ds': f'{year}-01-15'},
                    {'holiday': 'Independence Day', 'ds': f'{year}-02-04'},
                    {'holiday': 'Navam Poya', 'ds': f'{year}-02-12'},
                    {'holiday': 'Id-Ul-Fitr', 'ds': f'{year}-03-31'},
                    {'holiday': 'Bak Poya', 'ds': f'{year}-04-10'},
                    {'holiday': 'Sinhala & Tamil New Year', 'ds': f'{year}-04-14'},
                    {'holiday': 'Good Friday', 'ds': f'{year}-04-18'},
                    {'holiday': 'Vesak Poya', 'ds': f'{year}-05-12'},
                    {'holiday': 'Poson Poya', 'ds': f'{year}-06-09'},
                    {'holiday': 'Esala Poya', 'ds': f'{year}-07-24'},
                    {'holiday': 'Nikini Poya', 'ds': f'{year}-08-21'},
                    {'holiday': 'Binara Poya', 'ds': f'{year}-09-18'},
                    {'holiday': 'Vap Poya', 'ds': f'{year}-10-17'},
                    {'holiday': 'Deepavali', 'ds': f'{year}-10-31'},
                    {'holiday': 'Il Poya', 'ds': f'{year}-11-14'},
                    {'holiday': 'Unduvap Poya', 'ds': f'{year}-12-13'},
                    {'holiday': 'Christmas Day', 'ds': f'{year}-12-25'}
                ])
        else:
            print(f"⚠️ No Calendarific key for {year}. Using fake holidays.")
            holidays.extend([
                {'holiday': 'New Year\'s Day', 'ds': f'{year}-01-01'},
                {'holiday': 'Duruthu Poya', 'ds': f'{year}-01-03'},
                {'holiday': 'Tamil Thai Pongal', 'ds': f'{year}-01-15'},
                {'holiday': 'Independence Day', 'ds': f'{year}-02-04'},
                {'holiday': 'Navam Poya', 'ds': f'{year}-02-12'},
                {'holiday': 'Id-Ul-Fitr', 'ds': f'{year}-03-31'},
                {'holiday': 'Bak Poya', 'ds': f'{year}-04-10'},
                {'holiday': 'Sinhala & Tamil New Year', 'ds': f'{year}-04-14'},
                {'holiday': 'Good Friday', 'ds': f'{year}-04-18'},
                {'holiday': 'Vesak Poya', 'ds': f'{year}-05-12'},
                {'holiday': 'Poson Poya', 'ds': f'{year}-06-09'},
                {'holiday': 'Esala Poya', 'ds': f'{year}-07-24'},
                {'holiday': 'Nikini Poya', 'ds': f'{year}-08-21'},
                {'holiday': 'Binara Poya', 'ds': f'{year}-09-18'},
                {'holiday': 'Vap Poya', 'ds': f'{year}-10-17'},
                {'holiday': 'Deepavali', 'ds': f'{year}-10-31'},
                {'holiday': 'Il Poya', 'ds': f'{year}-11-14'},
                {'holiday': 'Unduvap Poya', 'ds': f'{year}-12-13'},
                {'holiday': 'Christmas Day', 'ds': f'{year}-12-25'}
            ])
    holidays_df = pd.DataFrame(holidays)
    holidays_df['ds'] = pd.to_datetime(holidays_df['ds'])
    holidays_df['lower_window'] = 0
    holidays_df['upper_window'] = 1
    return holidays_df


def get_weather_data(start_date='2025-01-01', end_date='2025-12-31'):
    # Fetch historical data for 2025
    url_2025 = f"https://archive-api.open-meteo.com/v1/archive?latitude=6.9271&longitude=79.8612&start_date=2025-01-01&end_date=2025-12-31&daily=temperature_2m_mean,precipitation_sum&timezone=Asia/Colombo"
    try:
        response = requests.get(url_2025)
        response.raise_for_status()
        data = response.json()['daily']
        weather_2025 = pd.DataFrame({
            'ds': pd.to_datetime(data['time']),
            'temperature': data['temperature_2m_mean'],
            'precip': data['precipitation_sum']
        })
        weather_2025['precip'] = weather_2025['precip'].fillna(0)
        print(f"✅ Fetched weather for 2025: {len(weather_2025)} days")
    except Exception as e:
        print(f"❌ Weather API failed for 2025: {e}. Using fake weather.")
        dates = pd.date_range('2025-01-01', '2025-12-31')
        weather_2025 = pd.DataFrame({
            'ds': dates,
            'temperature': 28 + 4 * np.sin(2 * np.pi * np.arange(len(dates)) / 365),
            'precip': np.random.exponential(2, len(dates))
        })

    # Simulate 2026 data (repeat 2025 with slight warming)
    weather_2026 = weather_2025.copy()
    weather_2026['ds'] += pd.DateOffset(years=1)
    weather_2026['temperature'] += 0.5  # Assume slight warming
    weather = pd.concat([weather_2025, weather_2026])
    weather = weather[weather['ds'].between(start_date, end_date)]
    return weather


if __name__ == "__main__":
    holidays_df = get_sri_lanka_holidays()
    holidays_df.to_csv('holidays.csv', index=False)
    weather_df = get_weather_data()
    weather_df.to_csv('weather.csv', index=False)
    print("✅ Saved holidays.csv and weather.csv")
