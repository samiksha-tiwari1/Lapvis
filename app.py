# ================================================================
# LapVis — F1 Telemetry Intelligence Dashboard
# ================================================================

import os
import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import plotly.graph_objects as go

# --------------------------------------------------
# FASTF1 CACHE (ONLY ONCE)
# --------------------------------------------------
CACHE_DIR = "fastf1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# -------------------------------------------------------
# Warm up FastF1 engine (removes first load lag)
# -------------------------------------------------------
if "engine_warm" not in st.session_state:
    with st.spinner("Warming telemetry engine..."):
        warm = fastf1.get_session(2023, "Monaco", "Q")
        warm.load(laps=False, telemetry=False)
    st.session_state.engine_warm = True

# --------------------------------------------------
# STREAMLIT PAGE SETUP (ONLY ONCE)
# --------------------------------------------------
st.set_page_config(page_title="LapVis — F1 Telemetry", layout="wide")
st.title("🏎️ LapVis — F1 Telemetry Intelligence Dashboard")

st.markdown("""
<style>

/* ===== Remove Streamlit chrome ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== App background ===== */
.stApp {
    background: radial-gradient(circle at center, #0b0f14 0%, #05080c 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: #0e1117 !important;
    border-right: 1px solid rgba(0,255,255,0.2);
}

section[data-testid="stSidebar"] * {
    color: #00ffff !important;
}

/* ===== Titles ===== */
h1, h2, h3 {
    color: #00ffff !important;
    text-shadow: 0 0 10px #00ffff55;
}

/* ===== Tabs ===== */
button[data-baseweb="tab"] {
    color: #00ffff !important;
    background: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #00ffff !important;
}

/* ===== Buttons ===== */
.stButton>button {
    border: 1px solid #00ffff;
    color: #00ffff;
    background: transparent;
}
.stButton>button:hover {
    background: #00ffff22;
}

/* ===== Selectbox (NO SPLIT BOX, CLEAN RECTANGLE) ===== */
div[data-baseweb="select"] > div {
    background: #0f1620 !important;
    border: 1px solid #00ffff66 !important;
    border-radius: 6px !important;
}

/* kill inner divider */
div[data-baseweb="select"] > div > div {
    border: none !important;
}

/* arrow color */
div[data-baseweb="select"] svg {
    color: #00ffff !important;
}

/* dropdown */
ul[role="listbox"] {
    background: #0f1620 !important;
    border: 1px solid #00ffff55 !important;
}

li[role="option"]:hover {
    background: #00ffff22 !important;
}

li[aria-selected="true"] {
    background: #00ffff33 !important;
}

/* ===== Inputs ===== */
input, textarea {
    background: #0f1620 !important;
    color: #00ffff !important;
    border: 1px solid #00ffff55 !important;
}

/* ===== Labels ===== */
label {
    color: #00ffff !important;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FASTF1 ENGINE PRELOAD (HUGE SPEED BOOST)
# --------------------------------------------------
if "preload_done" not in st.session_state:
    with st.spinner("Preparing telemetry engine..."):
        preload = fastf1.get_session(2023, "Monaco", "Q")
        preload.load(laps=True, telemetry=True)
    st.session_state.preload_done = True
# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

@st.cache_data
def get_races_for_year(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule['EventName'].tolist()


@st.cache_data
def load_session(year, race, session_type):
    # This is what made LapVis super fast
    s = fastf1.get_session(year, race, session_type)
    s.load()
    return s


def get_drivers(session):
    return sorted(session.laps['Driver'].unique())


# -------------------------------------------------------
# Sidebar Controls
# -------------------------------------------------------
st.sidebar.header("Session Controls")

year = st.sidebar.selectbox("Year", [2021, 2022, 2023, 2024, 2025])
race = st.sidebar.selectbox("Race", get_races_for_year(year))
session_type = st.sidebar.selectbox("Session", ['FP1', 'FP2', 'FP3', 'Q', 'R', 'S'])

# Load session FIRST
session = load_session(year, race, session_type)

# Get drivers AFTER session load
driver_list = get_drivers(session)

driver1 = st.sidebar.selectbox("Driver 1", driver_list, index=0)
driver2 = st.sidebar.selectbox("Driver 2", driver_list, index=1)

# Get fastest laps
lap1 = session.laps.pick_drivers(driver1).pick_fastest()
lap2 = session.laps.pick_drivers(driver2).pick_fastest()

# -------------------------------------------------------
# Base telemetry for maps
# -------------------------------------------------------
tel = lap1.get_telemetry()
x = tel['X'].values
y = tel['Y'].values
speed = tel['Speed'].values
throttle = tel['Throttle'].values
brake = tel['Brake'].astype(int).values

# -------------------------------------------------------
# Styling helper
# -------------------------------------------------------
def dark(ax, title):
    ax.set_facecolor('#0b0f14')
    ax.set_title(title, color='white', fontsize=16, pad=15)
    ax.tick_params(colors='white')
    for s in ax.spines.values():
        s.set_color('white')

# -------------------------------------------------------

# -------------------------------------------------------
# Styling helper
# -------------------------------------------------------
def dark(ax, title):
    ax.set_facecolor('#0b0f14')
    ax.set_title(title, color='white', fontsize=16, pad=15)
    ax.tick_params(colors='white')
    for s in ax.spines.values():
        s.set_color('white')

# -------------------------------------------------------
# Telemetry Maps
# -------------------------------------------------------
def plot_map(data, title, cmap):
    fig, ax = plt.subplots(figsize=(9,7), facecolor='#0b0f14')
    ax.scatter(x, y, c=data, cmap=cmap, s=6)
    dark(ax, title)
    ax.axis('off')
    st.pyplot(fig, transparent=True)

# -------------------------------------------------------
# Racing Line Overlay
# -------------------------------------------------------
def plot_overlay():
    t1 = lap1.get_telemetry()
    t2 = lap2.get_telemetry()

    fig, ax = plt.subplots(figsize=(10,7), facecolor='#0b0f14')

    ax.plot(t1['X'], t1['Y'], color='#00FFFF', linewidth=2)
    ax.plot(t2['X'], t2['Y'], color='#FF69B4', linewidth=2)

    dark(ax, "Racing Line Overlay")
    ax.axis('off')

    ax.text(0.02, 0.95, driver1, transform=ax.transAxes,
            color='#00FFFF', fontsize=13, weight='bold')
    ax.text(0.02, 0.90, driver2, transform=ax.transAxes,
            color='#FF69B4', fontsize=13, weight='bold')

    st.pyplot(fig, width='stretch')

# -------------------------------------------------------
# Speed Trace Comparison
# -------------------------------------------------------
def plot_speed_trace():
    t1 = lap1.get_car_data().add_distance()
    t2 = lap2.get_car_data().add_distance()

    fig, ax = plt.subplots(figsize=(12,5), facecolor='#0b0f14')

    ax.plot(t1['Distance'], t1['Speed'], color='#00FFFF', label=driver1)
    ax.plot(t2['Distance'], t2['Speed'], color='#FF69B4', label=driver2)

    dark(ax, "Speed Trace Comparison")
    ax.set_xlabel("Distance (m)", color='white')
    ax.set_ylabel("Speed (km/h)", color='white')

    legend = ax.legend()
    for t in legend.get_texts():
        t.set_color('white')

    st.pyplot(fig, width='stretch')

# -------------------------------------------------------
# TRUE Lap Delta — Broadcast Style
# -------------------------------------------------------
def plot_true_delta():
    t1 = lap1.get_car_data().add_distance()
    t2 = lap2.get_car_data().add_distance()

    d = t1['Distance'].values
    t1s = t1['Time'].dt.total_seconds().values
    t2_interp = np.interp(d, t2['Distance'], t2['Time'].dt.total_seconds())

    delta = t2_interp - t1s

    fig, ax = plt.subplots(figsize=(14,5), facecolor='#0b0f14')

    line = ax.plot(d, delta, color='#00F5D4', linewidth=2.5)[0]
    line.set_path_effects([
        pe.Stroke(linewidth=8, foreground='#00F5D4', alpha=0.15),
        pe.Normal()
    ])

    ax.axhline(0, color='white', linewidth=1, alpha=0.6)
    ax.grid(color='white', alpha=0.08)

    dark(ax, f"Lap Delta — {driver1} vs {driver2}")
    ax.set_xlabel("Distance (m)", color='white')
    ax.set_ylabel("Time Delta (s)", color='white')

    st.pyplot(fig, width='stretch')

# -------------------------------------------------------
# Time Loss Map
# -------------------------------------------------------
def plot_time_loss_map():
    tel1 = lap1.get_telemetry().add_distance()
    tel2 = lap2.get_telemetry().add_distance()

    d1 = tel1['Distance'].values
    t1 = tel1['Time'].dt.total_seconds().values

    t2_interp = np.interp(
        d1,
        tel2['Distance'].values,
        tel2['Time'].dt.total_seconds().values
    )

    delta = t2_interp - t1
    norm = (delta - delta.min()) / (delta.max() - delta.min())

    fig, ax = plt.subplots(figsize=(10,7), facecolor='#0b0f14')
    ax.scatter(tel1['X'], tel1['Y'], c=norm, cmap='RdYlGn_r', s=8)

    dark(ax, "Time Loss Map (Green = Gain, Red = Loss)")
    ax.axis('off')

    st.pyplot(fig, width='stretch')

def plot_strategy_predictor():
    car = lap1.get_car_data().add_distance()
    speed = car['Speed'].values

    avg_speed = np.mean(speed)
    consistency = np.std(speed)

    fig, ax = plt.subplots(figsize=(12,5), facecolor='#0b0f14')
    ax.axis('off')

    # Title
    ax.text(0.02, 0.88, "AI Race Strategy Predictor",
            fontsize=20, color='white', weight='bold')

    # Metrics
    ax.text(0.02, 0.60, f"Average Speed: {avg_speed:.1f} km/h",
            fontsize=14, color='#00F5D4')

    ax.text(0.02, 0.48, f"Speed Consistency Index: {consistency:.1f}",
            fontsize=14, color='#00F5D4')

    # Strategy logic
    if avg_speed > 250 and consistency < 20:
        strategy = "Hard → Medium (Long Stint)"
        color = '#00FF88'
        reason = "Driver maintains high speed with low variance. Tyre wear is stable."
    else:
        strategy = "Medium → Soft (Aggressive)"
        color = '#FF4D6D'
        reason = "High speed variance indicates aggressive driving. Softer tyres faster."

    ax.text(0.02, 0.30, f"Recommended Strategy: {strategy}",
            fontsize=18, color=color, weight='bold')

    ax.text(0.02, 0.18, reason,
            fontsize=13, color='white')

    st.pyplot(fig, width='stretch')

def plot_anomaly_detection():
    tel = lap1.get_telemetry()

    speed = tel['Speed'].values
    throttle = tel['Throttle'].values

    anomalies = np.where(
        (speed < np.mean(speed) - 2*np.std(speed)) &
        (throttle > 85)
    )[0]

    fig, ax = plt.subplots(figsize=(10,7), facecolor='#0b0f14')

    ax.scatter(tel['X'], tel['Y'], color='#1f2a36', s=6)
    ax.scatter(tel['X'].values[anomalies],
               tel['Y'].values[anomalies],
               color='#FF3B3B', s=40)

    dark(ax, "Driver Performance Anomaly Detection")
    ax.axis('off')

    ax.text(0.02, 0.95,
            f"Detected {len(anomalies)} anomalous slow zones",
            transform=ax.transAxes,
            color='#FF3B3B', fontsize=13, weight='bold')

    st.pyplot(fig, width='stretch')

def plot_risk_predictor():
    tel = lap1.get_telemetry()

    brake = tel['Brake'].values
    speed = tel['Speed'].values

    risk = np.where((brake == 1) & (speed > 230))[0]

    fig, ax = plt.subplots(figsize=(10,7), facecolor='#0b0f14')

    ax.scatter(tel['X'], tel['Y'], color='#1f2a36', s=6)
    ax.scatter(tel['X'].values[risk],
               tel['Y'].values[risk],
               color='#FFA500', s=35)

    dark(ax, "Crash / Safety Risk Predictor")
    ax.axis('off')

    ax.text(0.02, 0.95,
            f"{len(risk)} High-Risk Braking Zones Detected",
            transform=ax.transAxes,
            color='#FFA500', fontsize=13, weight='bold')

    st.pyplot(fig, width='stretch')

def telemetry_insights(l1, l2, d1, d2):
    st.markdown("##  Lap Intelligence Insights")

    t1 = l1.get_car_data().add_distance()
    t2 = l2.get_car_data().add_distance()

    d = t1['Distance'].values
    t1s = t1['Time'].dt.total_seconds().values
    t2_interp = np.interp(d, t2['Distance'], t2['Time'].dt.total_seconds())
    delta = t2_interp - t1s

    # Where biggest gain happens
    gain_index = np.argmin(delta)
    gain_distance = d[gain_index]

    # Sector split
    total = d[-1]
    s1 = total/3
    s2 = 2*total/3

    def sector(time_array):
        return np.mean(time_array)

    s1_delta = np.mean(delta[d < s1])
    s2_delta = np.mean(delta[(d >= s1) & (d < s2)])
    s3_delta = np.mean(delta[d >= s2])

    # Speed aggression
    speed_std_1 = np.std(t1['Speed'])
    speed_std_2 = np.std(t2['Speed'])

    # Brake comparison
    brake1 = np.sum(l1.get_telemetry()['Brake'])
    brake2 = np.sum(l2.get_telemetry()['Brake'])

    # Output insights
    if s2_delta < s1_delta and s2_delta < s3_delta:
        best_sector = "Sector 2 (technical corners)"
    elif s1_delta < s3_delta:
        best_sector = "Sector 1 (high speed)"
    else:
        best_sector = "Sector 3 (corner exits)"

    st.success(f"Biggest time gain for **{d1}** occurs around **{int(gain_distance)} meters**")

    st.info(f"**{d1}** is strongest in **{best_sector}**")

    if speed_std_1 > speed_std_2:
        st.warning(f"**{d1}** is driving more aggressively than **{d2}** (higher speed variance)")
    else:
        st.warning(f"**{d2}** is driving more aggressively than **{d1}**")

    if brake1 < brake2:
        st.write(f"🟢 **{d1} brakes later** than {d2}")
    else:
        st.write(f"🟢 **{d2} brakes later** than {d1}")

def corner_by_corner_analysis(l1, l2, d1, d2):
    st.markdown("## 🏁 Corner-by-Corner Analysis")

    tel1 = l1.get_telemetry().add_distance()
    tel2 = l2.get_telemetry().add_distance()

    brake = tel1['Brake'].values
    distance = tel1['Distance'].values

    # Detect braking start points (corner entries)
    corners = []
    for i in range(1, len(brake)):
        if brake[i] == 1 and brake[i-1] == 0:
            corners.append(distance[i])

    # Remove very close detections (noise)
    filtered = []
    last = -100
    for c in corners:
        if c - last > 80:  # minimum spacing between corners
            filtered.append(c)
            last = c

    # Compute time delta
    t1 = tel1['Time'].dt.total_seconds().values
    t2_interp = np.interp(
        distance,
        tel2['Distance'].values,
        tel2['Time'].dt.total_seconds().values
    )
    delta = t2_interp - t1

    # Analyze each corner
    for idx, c in enumerate(filtered[:12], start=1):  # limit to 12 corners for readability
        window = (distance > c - 40) & (distance < c + 40)
        corner_delta = np.mean(delta[window])

        if corner_delta < 0:
            st.success(f"Turn {idx}: **{d1} gains {abs(corner_delta):.3f}s**")
        else:
            st.error(f"Turn {idx}: **{d2} gains {abs(corner_delta):.3f}s**")

def race_engineer_summary(l1, l2, d1, d2):
    st.markdown("##  Race Engineer Summary")

    tel1 = l1.get_telemetry().add_distance()
    tel2 = l2.get_telemetry().add_distance()

    brake = tel1['Brake'].values
    distance = tel1['Distance'].values

    # Detect corners
    corners = []
    for i in range(1, len(brake)):
        if brake[i] == 1 and brake[i-1] == 0:
            corners.append(distance[i])

    # Filter noise
    filtered = []
    last = -100
    for c in corners:
        if c - last > 80:
            filtered.append(c)
            last = c

    t1 = tel1['Time'].dt.total_seconds().values
    t2_interp = np.interp(
        distance,
        tel2['Distance'].values,
        tel2['Time'].dt.total_seconds().values
    )
    delta = t2_interp - t1

    gains_d1 = 0
    gains_d2 = 0

    for c in filtered[:12]:
        window = (distance > c - 40) & (distance < c + 40)
        corner_delta = np.mean(delta[window])

        if corner_delta < 0:
            gains_d1 += 1
        else:
            gains_d2 += 1

    if gains_d1 > gains_d2:
        st.success(
            f"{d1} is stronger in technical corner sections and gains time in more turns than {d2}."
        )
    else:
        st.error(
            f"{d2} is stronger in corner exits and braking zones, gaining advantage over {d1}."
        )

    st.info(
        "This summary is generated automatically from braking patterns and time delta across every corner."
    )

def corner_type_analysis(l1, l2, d1, d2):
    st.markdown("##  Corner Type Performance")

    tel1 = l1.get_telemetry().add_distance()
    tel2 = l2.get_telemetry().add_distance()

    brake = tel1['Brake'].values
    speed = tel1['Speed'].values
    distance = tel1['Distance'].values

    # Detect corner start from braking
    corners = []
    for i in range(1, len(brake)):
        if brake[i] == 1 and brake[i-1] == 0:
            corners.append((distance[i], speed[i]))

    # Filter close duplicates
    filtered = []
    last = -100
    for d, s in corners:
        if d - last > 80:
            filtered.append((d, s))
            last = d

    # Delta calculation
    t1 = tel1['Time'].dt.total_seconds().values
    t2_interp = np.interp(
        distance,
        tel2['Distance'].values,
        tel2['Time'].dt.total_seconds().values
    )
    delta = t2_interp - t1

    slow_gain = 0
    medium_gain = 0
    fast_gain = 0

    for d, s in filtered[:15]:
        window = (distance > d - 40) & (distance < d + 40)
        corner_delta = np.mean(delta[window])

        # Classify corner by speed at braking
        if s < 120:
            if corner_delta < 0:
                slow_gain += 1
        elif 120 <= s < 220:
            if corner_delta < 0:
                medium_gain += 1
        else:
            if corner_delta < 0:
                fast_gain += 1

    st.write(f"**Slow corners gained by {d1}:** {slow_gain}")
    st.write(f"**Medium speed corners gained by {d1}:** {medium_gain}")
    st.write(f"**High speed corners gained by {d1}:** {fast_gain}")

    # Smart sentence
    if slow_gain > medium_gain and slow_gain > fast_gain:
        st.success(f"{d1} is significantly stronger in slow technical hairpins.")
    elif fast_gain > slow_gain and fast_gain > medium_gain:
        st.success(f"{d1} gains major time in high-speed sweepers and flowing sections.")
    else:
        st.success(f"{d1} shows balanced performance across corner types.")



def lap_replay_animation(lap):
    tel = lap.get_telemetry()

    x = tel['X'].values
    y = tel['Y'].values
    speed = tel['Speed'].values

    norm_speed = (speed - speed.min()) / (speed.max() - speed.min())

    step = 8
    frames = []

    for i in range(0, len(x), step):
        frames.append(
            go.Frame(
                data=[
                    # glowing track trail till current point
                    go.Scatter(
                        x=x[:i],
                        y=y[:i],
                        mode="lines",
                        line=dict(color="#00F5D4", width=6),
                        opacity=0.9
                    ),
                    # moving car dot
                    go.Scatter(
                        x=[x[i]],
                        y=[y[i]],
                        mode="markers",
                        marker=dict(
                            size=16,
                            color="#FF2E88",  # bright pink car
                            line=dict(width=2, color='white')
                        )
                    )
                ]
            )
        )

    # initial faint full track (reference)
    base_track = go.Scatter(
        x=x,
        y=y,
        mode='lines',
        line=dict(color='white', width=3),
        opacity=0.15
    )

    fig = go.Figure(
        data=[base_track],
        frames=frames
    )

    fig.update_layout(
        title="Lap Replay Animation",
        plot_bgcolor="#0b0f14",
        paper_bgcolor="#0b0f14",
        xaxis=dict(range=[x.min(), x.max()], visible=False),
        yaxis=dict(range=[y.min(), y.max()], visible=False),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[None, {
                            "frame": {"duration": 20, "redraw": True},
                            "fromcurrent": True
                        }]
                    )
                ]
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(l1, l2, d1, d2, year, race, session_type):
    doc = SimpleDocTemplate("LapVis_Report.pdf")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"LapVis Race Engineer Report", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Session: {race} {year} — {session_type}", styles['Normal']))
    elements.append(Paragraph(
        f"Drivers Compared: {d1} vs {d2}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Compute delta
    tel1 = l1.get_car_data().add_distance()
    tel2 = l2.get_car_data().add_distance()

    d = tel1['Distance'].values
    t1 = tel1['Time'].dt.total_seconds().values
    t2_interp = np.interp(d, tel2['Distance'], tel2['Time'].dt.total_seconds())
    delta = t2_interp - t1

    gain_index = np.argmin(delta)
    gain_distance = int(d[gain_index])

    elements.append(Paragraph(
        f"Biggest time gain for {d1} occurs around {gain_distance} meters.",
        styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        "This report is auto-generated using telemetry intelligence from LapVis.",
        styles['Italic']))

    doc.build(elements)

if st.button("📄 Generate Race Engineer PDF Report"):
    generate_pdf_report(lap1, lap2, driver1, driver2, year, race, session_type)
    st.success("PDF Report generated as LapVis_Report.pdf")

# -------------------------------------------------------
# 🧠 Auto Race Engineer Commentary
# -------------------------------------------------------
def generate_engineer_insights(l1, l2, d1, d2):
    t1 = l1.get_car_data().add_distance()
    t2 = l2.get_car_data().add_distance()

    d = t1['Distance'].values
    s1 = t1['Speed'].values
    s2_interp = np.interp(d, t2['Distance'], t2['Speed'].values)

    # True delta
    t1s = t1['Time'].dt.total_seconds().values
    t2_interp = np.interp(d, t2['Distance'], t2['Time'].dt.total_seconds())
    delta = t2_interp - t1s

    # Where biggest gain happens
    max_gain_idx = np.argmin(delta)
    gain_point = int(d[max_gain_idx])

    # Straight line performance
    straight_mask = s1 > np.percentile(s1, 85)
    straight_adv = np.mean(s1[straight_mask] - s2_interp[straight_mask])

    # Braking zones
    brake_mask = s1 < np.percentile(s1, 30)
    brake_adv = np.mean(s1[brake_mask] - s2_interp[brake_mask])

    st.markdown("##  Lap Intelligence Insights")

    if delta[-1] < 0:
        st.success(f"{d1} is faster overall than {d2} on this lap.")
    else:
        st.error(f"{d2} is faster overall than {d1} on this lap.")

    st.info(f"Biggest time gain occurs around **{gain_point} meters** of the track.")

    if straight_adv > 0:
        st.write(f"• {d1} has superior straight-line speed compared to {d2}.")
    else:
        st.write(f"• {d2} has superior straight-line speed compared to {d1}.")

    if brake_adv < 0:
        st.write(f"• {d2} brakes later into heavy braking zones.")
    else:
        st.write(f"• {d1} brakes later into heavy braking zones.")

    st.write("• Time differences are mainly created on corner exits rather than entries.")

# -------------------------------------------------------
# Tabs
# -------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "Speed Map",
    "Throttle Map",
    "Brake Map",
    "True Lap Delta",
    "Racing Line Overlay",
    "Speed Trace",
    "Time Loss Map",
    "Race Strategy Predictor",
    "Anomaly Detection",
    "Crash Risk Predictor",
    "Lap Replay ",
])

with tab1:
    plot_map(speed, f"{driver1} Speed Map", 'viridis')

with tab2:
    plot_map(throttle, f"{driver1} Throttle Map", 'plasma')

with tab3:
    plot_map(brake, f"{driver1} Brake Map", 'coolwarm')

with tab4:
    plot_true_delta()

with tab5:
    plot_overlay()

with tab6:
    plot_speed_trace()

with tab7:
    plot_time_loss_map()
    
with tab8:
    plot_strategy_predictor()

with tab9:
    plot_anomaly_detection()

with tab10:
    plot_risk_predictor()

with tab11:
    lap_replay_animation(lap1)

telemetry_insights(lap1, lap2, driver1, driver2)
corner_by_corner_analysis(lap1, lap2, driver1, driver2)
race_engineer_summary(lap1, lap2, driver1, driver2)
corner_type_analysis(lap1, lap2, driver1, driver2)
generate_engineer_insights(lap1, lap2, driver1, driver2)

