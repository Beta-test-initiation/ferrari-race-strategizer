import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load merged data
FILE_PATH = "data/processed/tire_stints_weather_2025.csv"
df = pd.read_csv(FILE_PATH)

# Use correct 2025 Ferrari drivers
ferrari_drivers = ['HAM', 'LEC']
ferrari_stints = df[df['Driver'].isin(ferrari_drivers)].dropna(subset=['TrackTemp', 'LapTimeSlope'])

# Remove extreme degradation outliers
ferrari_stints = ferrari_stints[ferrari_stints['LapTimeSlope'].between(-1, 1)]

# Map round numbers to track names (optional)
import fastf1

def get_track_map(year):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['Session5'] == 'Race']
    schedule = schedule[schedule['EventDate'] < pd.Timestamp.now()]
    return schedule[['RoundNumber', 'EventName']].rename(columns={
        'RoundNumber': 'Round',
        'EventName': 'Track'
    })

track_map = get_track_map(2025)
ferrari_stints = pd.merge(ferrari_stints, track_map, on='Round', how='left')


# Replace missing track names with "Round X"
ferrari_stints['Track'] = ferrari_stints['Track'].fillna('Round ' + ferrari_stints['Round'].astype(str))

# Plot: LapTimeSlope vs TrackTemp, faceted by Track
g = sns.lmplot(
    data=ferrari_stints,
    x="TrackTemp",
    y="LapTimeSlope",
    hue="Compound",
    col="Track",
    col_wrap=3,
    ci=None,
    height=4,
    aspect=1.2,
    scatter_kws={'alpha': 0.6}
)

g.set_titles("{col_name}")
g.set_axis_labels("Track Temp (°C)", "Degradation Rate (sec/lap)")
plt.subplots_adjust(top=0.9)
g.fig.suptitle("Ferrari (HAM + LEC) Tire Degradation vs Track Temp (by Track)")

plt.show()
