import fastf1
import pandas as pd
import os

# Ensure cache folder exists and enable caching
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache('cache')

# Output path for raw data
DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

def get_season_data(year: int):
    laps_df_list = []
    pitstops_df_list = []
    stints_df_list = []

    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['Session5'] == 'Race']
    schedule = schedule[schedule['EventDate'] < pd.Timestamp.now()]

    for round_number in schedule['RoundNumber']:
        try:
            session = fastf1.get_session(year, round_number, 'R')
            session.load()

            print(f"Loaded data for: {session.event['EventName']}")

            # Laps
            laps = session.laps
            laps['Round'] = round_number
            laps_df_list.append(laps)

            # Pit stops (conditionally check for column existence)
            if 'PitStops' in session.results.columns:
                pitstops = session.results[['Abbreviation', 'PitStops']]
                pitstops['Round'] = round_number
                pitstops_df_list.append(pitstops)

            # Stints
            stints = session.laps[['Driver', 'Compound', 'Stint', 'LapNumber']]
            stints = stints.groupby(['Driver', 'Stint', 'Compound']).agg(
                StartLap=('LapNumber', 'min'),
                EndLap=('LapNumber', 'max'),
                StintLength=('LapNumber', 'count')
            ).reset_index()
            stints['Round'] = round_number
            stints_df_list.append(stints)

        except Exception as e:
            print(f"Failed to load round {round_number}: {e}")

    # Save only if data was collected
    if laps_df_list:
        pd.concat(laps_df_list).to_csv(f"{DATA_DIR}/laps_{year}.csv", index=False)
    if pitstops_df_list:
        pd.concat(pitstops_df_list).to_csv(f"{DATA_DIR}/pitstops_{year}.csv", index=False)
    if stints_df_list:
        pd.concat(stints_df_list).to_csv(f"{DATA_DIR}/stints_{year}.csv", index=False)

    print("Data collection complete.")

if __name__ == "__main__":
    get_season_data(2025)
