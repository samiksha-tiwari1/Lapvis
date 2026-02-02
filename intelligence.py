# ============================================================
# LapVis v2 — Intelligence Layer
# Module 1: Driver Style Fingerprinting
# ============================================================

import numpy as np


def build_driver_style(tel):
    """
    Analyze telemetry and build a Driver Style Profile.
    Works on a single fastest lap telemetry.
    """

    speed = tel['Speed'].values
    throttle = tel['Throttle'].values
    brake = tel['Brake'].values
    distance = tel['Distance'].values

    # --------------------------------------------------------
    # 1. Braking Style (Late vs Early)
    # --------------------------------------------------------
    brake_points = np.where(brake > 0)[0]

    if len(brake_points) == 0:
        braking_style = "Unknown"
    else:
        avg_brake_dist = np.mean(distance[brake_points])
        track_mid = distance[-1] / 2

        if avg_brake_dist > track_mid:
            braking_style = "Late Braker"
        else:
            braking_style = "Early Braker"

    # --------------------------------------------------------
    # 2. Throttle Aggression
    # --------------------------------------------------------
    throttle_gradient = np.mean(np.abs(np.gradient(throttle)))

    if throttle_gradient > 8:
        throttle_style = "Aggressive Throttle Application"
    else:
        throttle_style = "Progressive Throttle Application"

    # --------------------------------------------------------
    # 3. Driving Smoothness (car control)
    # --------------------------------------------------------
    smoothness = np.std(np.gradient(speed))

    if smoothness > 12:
        smoothness_style = "Unstable / Aggressive Inputs"
    else:
        smoothness_style = "Smooth / Controlled Inputs"

    # --------------------------------------------------------
    # 4. Corner Priority (Entry vs Exit)
    # --------------------------------------------------------
    # Compare average speed before braking vs after braking
    pre_brake_speeds = []
    post_brake_speeds = []

    for i in brake_points:
        if i > 20 and i < len(speed) - 20:
            pre_brake_speeds.append(np.mean(speed[i-20:i]))
            post_brake_speeds.append(np.mean(speed[i:i+20]))

    if len(pre_brake_speeds) > 0:
        if np.mean(post_brake_speeds) > np.mean(pre_brake_speeds):
            corner_priority = "Exit-Focused Driving"
        else:
            corner_priority = "Entry-Focused Driving"
    else:
        corner_priority = "Balanced"

    # --------------------------------------------------------
    # Driver Style Profile Output
    # --------------------------------------------------------
    profile = {
        "Braking Style": braking_style,
        "Throttle Style": throttle_style,
        "Driving Smoothness": smoothness_style,
        "Corner Priority": corner_priority
    }

    return profile