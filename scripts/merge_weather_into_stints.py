import pandas as pd
import os

# Input files
STINTS_FILE = "data/processed/tire_stints_2025.csv"
WEATHER_FILE = "data/raw/weather_2025.csv"
OUTPUT_FILE = "data/processed/tire_stints_weather_2025.csv"

# Create output directory if missing
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def main():
    print("Loading data...")
    stints = pd.read_csv(STINTS_FILE)
    weather = pd.read_csv(WEATHER_FILE)

    print("Merging weather with stint data...")
    merged = pd.merge(stints, weather, on="Round", how="left")

    missing = merged['TrackTemp'].isna().sum()
    if missing > 0:
        print(f"Warning: {missing} stints missing weather data.")

    print(f"Saving merged dataset to {OUTPUT_FILE}...")
    merged.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
