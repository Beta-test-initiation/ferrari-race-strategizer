import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import numpy as np

# Input file paths (from raw data)
LAPS_FILE = "data/raw/laps_2025.csv"
STINTS_FILE = "data/raw/stints_2025.csv"
OUTPUT_FILE = "data/processed/tire_stints_2025.csv"

# Output directory
OUTPUT_FILE = "data/processed/tire_stints_2025.csv"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def load_and_merge():
    """
    Load lap and stint data from raw CSVs and prepare for processing.
    """
    laps = pd.read_csv(LAPS_FILE)
    stints = pd.read_csv(STINTS_FILE)
    
    # Filter out laps with missing lap times
    laps = laps[laps['LapTime'].notna()]
    
    # Convert lap time string to seconds if necessary
    if laps['LapTime'].dtype == object:
        laps['LapTime'] = pd.to_timedelta(laps['LapTime']).dt.total_seconds()
    
    return laps, stints

def extract_stint_features(laps, stints):
    """
    Generate tire wear and performance features per stint.
    """
    records = []

    for _, stint in stints.iterrows():
        driver = stint['Driver']
        compound = stint['Compound']
        round_num = stint['Round']
        stint_id = stint['Stint']
        start_lap = stint['StartLap']
        end_lap = stint['EndLap']
        stint_len = stint['StintLength']

        # Skip very short stints (not useful for degradation modeling)
        if stint_len < 5:
            continue

        # Extract laps for this specific stint
        driver_laps = laps[
            (laps['Driver'] == driver) &
            (laps['Round'] == round_num) &
            (laps['Stint'] == stint_id)
        ].copy()

        # Skip if data is missing
        if driver_laps.empty:
            continue

        # Fit a linear regression: LapNumber vs. LapTime to estimate degradation
        x = driver_laps['LapNumber'].values.reshape(-1, 1)
        y = driver_laps['LapTime'].values

        model = LinearRegression()
        model.fit(x, y)

        lap_time_slope = model.coef_[0]
        avg_lap_time = np.mean(y)

        records.append({
            'Driver': driver,
            'Round': round_num,
            'Stint': stint_id,
            'Compound': compound,
            'StintLength': stint_len,
            'StartLap': start_lap,
            'EndLap': end_lap,
            'AvgLapTime': avg_lap_time,
            'LapTimeSlope': lap_time_slope
        })

    return pd.DataFrame(records)

def main():
    print("Loading raw data...")
    laps, stints = load_and_merge()

    print("Extracting stint features...")
    stint_features = extract_stint_features(laps, stints)

    print(f"Saving processed features to {OUTPUT_FILE}...")
    stint_features.to_csv(OUTPUT_FILE, index=False)

    print("Done.")

if __name__ == "__main__":
    main()
