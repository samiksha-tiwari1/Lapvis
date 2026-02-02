"""
LapVis — F1 Telemetry Visualization

This script:
1) Loads an F1 session using FastF1
2) Extracts telemetry (GPS, speed, throttle, brake)
3) Draws the circuit map using real GPS points
4) Colors the racing line by different telemetry signals
"""

import fastf1
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------------------------
# Enable cache (FastF1 requires an existing folder to store data)
# -------------------------------------------------------------------
fastf1.Cache.enable_cache('cache')

# -------------------------------------------------------------------
# Load a race session
# Format: (year, race name, session type)
# Q = Qualifying, R = Race, FP1/FP2/FP3 = Practice
# -------------------------------------------------------------------
session = fastf1.get_session(2023, 'Monaco', 'Q')
session.load()

# -------------------------------------------------------------------
# Pick a driver and their fastest lap from the session
# Example drivers: 'VER', 'HAM', 'LEC', 'NOR', etc.
# -------------------------------------------------------------------
driver = 'VER'  # Max Verstappen
lap = session.laps.pick_driver(driver).pick_fastest()

# -------------------------------------------------------------------
# Get telemetry data for that lap
# This contains GPS coordinates and car data over the lap
# -------------------------------------------------------------------
tel = lap.get_telemetry()

# Extract useful telemetry channels
x = tel['X'].values          # GPS X coordinate
y = tel['Y'].values          # GPS Y coordinate
speed = tel['Speed'].values  # Speed in km/h
throttle = tel['Throttle'].values  # Throttle percentage (0-100)
brake = tel['Brake'].values.astype(int)  # Brake (True/False → 1/0)

# -------------------------------------------------------------------
# Function to plot telemetry on track map
# -------------------------------------------------------------------
def plot_track_map(x, y, data, title, cmap, label):
    """
    Draws the racing line colored by telemetry data.

    Parameters:
    x, y  -> GPS coordinates
    data  -> telemetry channel to color by
    title -> plot title
    cmap  -> matplotlib color map
    label -> colorbar label
    """
    plt.figure(figsize=(10, 8))
    plt.scatter(x, y, c=data, cmap=cmap, s=5)
    plt.title(title, fontsize=14)
    plt.axis('off')
    plt.colorbar(label=label)
    plt.show()


# -------------------------------------------------------------------
# Plot 1 — Speed Map
# Shows where the car is fastest and slowest
# -------------------------------------------------------------------
plot_track_map(
    x, y,
    speed,
    f"{driver} Fastest Lap — Speed Map",
    'viridis',
    'Speed (km/h)'
)

# -------------------------------------------------------------------
# Plot 2 — Throttle Map
# Shows where driver is full throttle vs lifting
# -------------------------------------------------------------------
plot_track_map(
    x, y,
    throttle,
    f"{driver} Fastest Lap — Throttle Map",
    'plasma',
    'Throttle (%)'
)

# -------------------------------------------------------------------
# Plot 3 — Brake Map
# Highlights braking zones on the circuit
# -------------------------------------------------------------------
plot_track_map(
    x, y,
    brake,
    f"{driver} Fastest Lap — Brake Map",
    'coolwarm',
    'Brake (On/Off)'
)

# ================================================================
# DRIVER vs DRIVER — LAP DELTA VISUALIZATION
# ================================================================

# Choose two drivers
driver1 = 'VER'
driver2 = 'HAM'

lap1 = session.laps.pick_driver(driver1).pick_fastest()
lap2 = session.laps.pick_driver(driver2).pick_fastest()

# Get telemetry with distance for both laps
tel1 = lap1.get_car_data().add_distance()
tel2 = lap2.get_car_data().add_distance()

# Interpolate lap2 speed onto lap1 distance axis
# (so we can compare point-by-point around the track)
speed1 = tel1['Speed'].values
dist1 = tel1['Distance'].values

speed2_interp = np.interp(
    dist1,
    tel2['Distance'].values,
    tel2['Speed'].values
)

# Compute time delta approximation from speed difference
# (simplified but very effective for visualization)
delta_time = np.cumsum((1/speed2_interp - 1/speed1)) * 100

# Plot time delta vs distance
plt.figure(figsize=(12, 6))
plt.plot(dist1, delta_time)
plt.title(f"Lap Time Delta — {driver1} vs {driver2}")
plt.xlabel("Distance around track (m)")
plt.ylabel("Time Delta (approx)")
plt.grid(True)
plt.show()