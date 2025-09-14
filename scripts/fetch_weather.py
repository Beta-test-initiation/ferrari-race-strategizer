import fastf1
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
assert API_KEY, "Missing Visual Crossing API key in .env"

# Output file
OUTPUT_FILE = "data/raw/weather_2025.csv"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_race_locations(year):
    """
    Get list of (round, event name, date, location) from FastF1 schedule.
    """
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['Session5'] == 'Race']
    schedule = schedule[schedule['EventDate'] < pd.Timestamp.now()]

    records = []
    for _, row in schedule.iterrows():
        event = row['EventName']
        date = row['EventDate'].strftime("%Y-%m-%d")
        circuit = row['Location']
        records.append({
            'Round': row['RoundNumber'],
            'Event': event,
            'Date': date,
            'Location': circuit
        })
    return pd.DataFrame(records)

def query_weather(location, date):
    """
    Query Visual Crossing for historical weather at a given location and date.
    """
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{location}/{date}?unitGroup=metric&key={API_KEY}&include=hours"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Weather request failed: {response.status_code}, {response.text}")
    return response.json()

def extract_hourly_weather(json_data, round_number):
    """
    Extract average race-hour weather (assume 14:00 local start) ± 1 hour.
    """
    hours = json_data.get('days', [])[0].get('hours', [])
    selected = [h for h in hours if 13 <= int(h['datetime'].split(':')[0]) <= 15]
    if not selected:
        return None

    df = pd.DataFrame(selected)
    return {
        'Round': round_number,
        'TrackTemp': df['temp'].mean(),
        'Humidity': df['humidity'].mean(),
        'WindSpeed': df['windspeed'].mean(),
        'Conditions': ','.join(df['conditions'].unique())
    }

def main():
    year = 2025
    schedule = get_race_locations(year)
    weather_rows = []

    for _, row in schedule.iterrows():
        try:
            print(f"Fetching weather for {row['Event']} ({row['Location']}) on {row['Date']}...")
            json_data = query_weather(row['Location'], row['Date'])
            weather = extract_hourly_weather(json_data, row['Round'])
            if weather:
                weather_rows.append(weather)
        except Exception as e:
            print(f"Failed to get weather for Round {row['Round']} ({row['Location']}): {e}")

    weather_df = pd.DataFrame(weather_rows)
    weather_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Weather data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
