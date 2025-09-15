import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Path to processed stint-level data
FILE_PATH = "data/processed/tire_stints_2025.csv"
df = pd.read_csv(FILE_PATH)

# Ferrari driver abbreviations
ferrari_drivers = ['LEC', 'HAM']

# Filter data for Ferrari only
ferrari_stints = df[df['Driver'].isin(ferrari_drivers)].copy()

# Plot lap time degradation per compound
def plot_degradation_by_compound(stints_df):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=stints_df, x='Compound', y='LapTimeSlope')
    plt.title("Ferrari Tire Degradation Rate by Compound")
    plt.ylabel("Lap Time Increase per Lap (sec/lap)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Compute average stint length vs. total time per compound
def plot_optimal_stint_length(stints_df):
    plt.figure(figsize=(10, 6))
    compounds = stints_df['Compound'].unique()

    for compound in compounds:
        subset = stints_df[stints_df['Compound'] == compound]
        subset['TotalStintTime'] = subset['AvgLapTime'] * subset['StintLength']
        grouped = subset.groupby('StintLength')['TotalStintTime'].mean().reset_index()
        plt.plot(grouped['StintLength'], grouped['TotalStintTime'], label=compound)

    plt.title("Estimated Total Stint Time vs Stint Length (Ferrari)")
    plt.xlabel("Stint Length (laps)")
    plt.ylabel("Estimated Total Time (s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Compare Ferrari degradation with other teams
def compare_to_competitors(all_data, ferrari_data):
    competitors = all_data[~all_data['Driver'].isin(ferrari_drivers)]
    ferrari_avg = ferrari_data.groupby('Compound')['LapTimeSlope'].mean()
    competitor_avg = competitors.groupby('Compound')['LapTimeSlope'].mean()
    comparison = pd.DataFrame({
        'Ferrari': ferrari_avg,
        'Competitors': competitor_avg,
        'Difference': ferrari_avg - competitor_avg
    })
    print("Ferrari vs Competitor Tire Degradation (sec/lap):\n")
    print(comparison.round(4))

if __name__ == "__main__":
    print("Ferrari tire stint summary (2025):")
    print(ferrari_stints.groupby('Compound')['LapTimeSlope'].describe())

    plot_degradation_by_compound(ferrari_stints)
    plot_optimal_stint_length(ferrari_stints)

    # Optional: load full data and compare
    full_df = pd.read_csv(FILE_PATH)
    compare_to_competitors(full_df, ferrari_stints)
