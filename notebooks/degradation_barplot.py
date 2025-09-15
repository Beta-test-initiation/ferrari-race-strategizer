import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import fastf1

"""
What This Will Show
X-axis: Races (tracks), sorted by total degradation

Y-axis: Average LapTimeSlope (degradation rate)

Grouped bars: Different compounds per track

Helps answer questions like:
Which compounds degrade fastest at hot tracks like Bahrain or Miami?

Do Hards always outperform Mediums?

Are there specific tracks where Ferrari suffers more?

"""


# Load processed stint + weather data
FILE_PATH = "data/processed/tire_stints_weather_2025.csv"
df = pd.read_csv(FILE_PATH)

# Focus on Ferrari 2025 drivers
ferrari_drivers = ['HAM', 'LEC']
ferrari_stints = df[df['Driver'].isin(ferrari_drivers)]

# Drop missing or extreme values
ferrari_stints = ferrari_stints.dropna(subset=['LapTimeSlope', 'Compound'])
ferrari_stints = ferrari_stints[ferrari_stints['LapTimeSlope'].between(-0.5, 0.5)]

# Map round numbers to track names
def get_track_names(year):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['Session5'] == 'Race']
    schedule = schedule[schedule['EventDate'] < pd.Timestamp.now()]
    return schedule[['RoundNumber', 'EventName']].rename(columns={
        'RoundNumber': 'Round',
        'EventName': 'Track'
    })

track_map = get_track_names(2025)
ferrari_stints = pd.merge(ferrari_stints, track_map, on='Round', how='left')

# Aggregate: mean degradation per Track + Compound
agg = ferrari_stints.groupby(['Track', 'Compound'])['LapTimeSlope'].mean().reset_index()

# Sort tracks by average degradation for clarity
track_order = agg.groupby('Track')['LapTimeSlope'].mean().sort_values(ascending=False).index

# Plot: Grouped bar chart
plt.figure(figsize=(12, 6))
sns.barplot(
    data=agg,
    x='Track',
    y='LapTimeSlope',
    hue='Compound',
    order=track_order
)
plt.title("Ferrari (HAM + LEC) Average Tire Degradation Rate by Track and Compound")
plt.ylabel("Avg Degradation Rate (sec/lap)")
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y')
plt.tight_layout()
plt.show()
