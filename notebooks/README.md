# Ferrari Tire Degradation Analysis

This module analyzes tire degradation behavior for **Ferrari F1 drivers** using lap-by-lap stint data from real races. It is a core analytical component in the Ferrari Strategy Maker project, guiding optimal tire strategy and pit stop timing.

## 🧠 Objective

The goal is to extract actionable tire degradation patterns from processed data to support strategic decisions for:
- Choosing tire compounds for race stints
- Determining optimal stint lengths
- Benchmarking Ferrari tire performance against competitors

---

## 📁 Input

**File:** `data/processed/tire_stints_2025.csv`

Each row represents a single tire stint and includes:
- `Driver`, `Round`, `Compound`, `StintLength`
- `AvgLapTime` (seconds)
- `LapTimeSlope` (change in lap time per lap — higher means more degradation)

---

## 📊 What This Script Does

### 1. `plot_degradation_by_compound`
Visualizes Ferrari tire degradation (`LapTimeSlope`) as a boxplot grouped by compound.

### 2. `plot_optimal_stint_length`
Estimates the best stint length for each compound by plotting:
