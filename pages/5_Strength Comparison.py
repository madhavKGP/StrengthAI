import streamlit as st
import pandas as pd
import os
from streamlit_local_storage import LocalStorage
from datetime import datetime

st.set_page_config(page_title="🏋️ Strength Comparison", layout="wide")
st.title("🏋️ Strength Comparison")

# --- Helper functions ---
COMPARISON_PATH = "comparison data"
GENDERS = ["male", "female"]
UNITS = ["kg", "lb"]
COMPARE_TYPES = ["age", "bodyweight"]

# Map for display
LEVELS = ["Beg.", "Nov.", "Int.", "Adv.", "Elite"]
LEVEL_DESC = {
    "Beg.": "Beginner: Stronger than 5% of lifters.",
    "Nov.": "Novice: Stronger than 20% of lifters.",
    "Int.": "Intermediate: Stronger than 50% of lifters.",
    "Adv.": "Advanced: Stronger than 80% of lifters.",
    "Elite": "Elite: Stronger than 95% of lifters."
}

# Get available exercises
EXERCISES = []
for g in GENDERS:
    for u in UNITS:
        for c in COMPARE_TYPES:
            d = os.path.join(COMPARISON_PATH, g, u, c)
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith('.csv'):
                        ex = f.replace('.csv','').replace('-', ' ').title()
                        if ex not in EXERCISES:
                            EXERCISES.append(ex)
EXERCISES.sort()

# --- Load user bests ---
def get_user_bests():
    localS = LocalStorage()
    sessions = localS.getItem("workout_sessions")
    if not sessions or not isinstance(sessions, list):
        return {}
    bests = {}
    for session in sessions:
        for ex, sets in session.get("exercises", {}).items():
            for s in sets:
                one_rm = round(s["Weight"] * (1 + (s["Reps"] + (10 - s["RPE"])) / 30), 2)
                if ex not in bests or one_rm > bests[ex]["Est. 1RM"]:
                    bests[ex] = {
                        "Exercise": ex,
                        "Est. 1RM": one_rm,
                        "Weight": s["Weight"],
                        "Reps": s["Reps"],
                        "RPE": s["RPE"],
                        "Session": session
                    }
    return bests

# --- Lookup function ---
def lookup_level(gender, unit, compare_type, exercise, value, age=None, bw=None):
    ex_file = exercise.lower().replace(' ', '-') + ".csv"
    path = os.path.join(COMPARISON_PATH, gender, unit, compare_type, ex_file)
    if not os.path.exists(path):
        return None, None
    df = pd.read_csv(path)
    if compare_type == "age":
        if age is None:
            return None, None
        # Find closest age row
        row = df.iloc[(df["Age"]-age).abs().argsort()[:1]]
    else:
        if bw is None:
            return None, None
        row = df.iloc[(df["BW"]-bw).abs().argsort()[:1]]
    row = row.iloc[0]
    for lvl in LEVELS:
        if value < row[lvl]:
            idx = LEVELS.index(lvl)
            return LEVELS[max(0, idx-1)], row
    return LEVELS[-1], row

# --- Get default age/bodyweight from body stats ---
localS = LocalStorage()
stats = localS.getItem('body_stats')
def get_latest_stat(stats, field):
    if stats and isinstance(stats, list):
        # Use the most recent entry (by date)
        try:
            df = pd.DataFrame(stats)
            df = df.sort_values('date')
            return int(df[field].iloc[-1]) if field == 'age' else float(df[field].iloc[-1])
        except Exception:
            return 25 if field == 'age' else 70.0
    return 25 if field == 'age' else 70.0

def_age = get_latest_stat(stats, 'age')
def_bw = get_latest_stat(stats, 'weight')

# --- UI: Rate My Strength (auto) ---
st.header("Rate My Strength (Auto)")
gender = st.selectbox("Gender", GENDERS, key="auto_gender")
unit = st.selectbox("Units", UNITS, key="auto_unit")
# Default to 'bodyweight' for comparison
default_compare_type = 1  # index of 'bodyweight' in COMPARE_TYPES
compare_type = st.selectbox("Compare by", COMPARE_TYPES, index=default_compare_type, key="auto_compare_type")

bests = get_user_bests()
if not bests:
    st.info("No workout data found. Log some sessions first!")
else:
    age = st.number_input("Your Age", min_value=10, max_value=100, value=def_age) if compare_type=="age" else None
    bw = st.number_input("Your Bodyweight", min_value=20.0, max_value=200.0, value=float(def_bw)) if compare_type=="bodyweight" else None
    table = []
    for ex in bests:
        # Try to match exercise name
        ex_file = ex.lower().replace(' ', '-')
        match = [e for e in EXERCISES if e.lower().replace(' ', '-')==ex_file]
        if not match:
            continue
        level, row = lookup_level(gender, unit, compare_type, match[0], bests[ex]["Est. 1RM"], age, bw)
        table.append({
            "Exercise": match[0],
            "Your Best 1RM": bests[ex]["Est. 1RM"],
            "Level": level or "-",
            "Description": LEVEL_DESC.get(level, "-") if level else "-"
        })
    if table:
        st.dataframe(pd.DataFrame(table))
    else:
        st.info("No matching exercises found in comparison data.")

# --- UI: Manual Comparison ---
st.header("Manual Comparison")
col1, col2 = st.columns(2)
with col1:
    man_gender = st.selectbox("Gender", GENDERS, key="man_gender")
    man_unit = st.selectbox("Units", UNITS, key="man_unit")
    man_compare_type = st.selectbox("Compare by", COMPARE_TYPES, index=default_compare_type, key="man_compare_type")
    man_ex = st.selectbox("Exercise", EXERCISES, key="man_ex")
with col2:
    man_val = st.number_input("Your Value (1RM or best set)", min_value=0.0, value=0.0, key="man_val")
    man_age = st.number_input("Your Age", min_value=10, max_value=100, value=def_age, key="man_age") if man_compare_type=="age" else None
    man_bw = st.number_input("Your Bodyweight", min_value=20.0, max_value=200.0, value=float(def_bw), key="man_bw") if man_compare_type=="bodyweight" else None

if st.button("Check Level"):
    level, row = lookup_level(man_gender, man_unit, man_compare_type, man_ex, man_val, man_age, man_bw)
    if level:
        st.success(f"Level: {level} — {LEVEL_DESC.get(level, '-')}")
        if row is not None:
            st.markdown("**Reference Standards for Your Input:**")
            st.table(pd.DataFrame([row.to_dict()]))
        else:
            st.info("No reference row found.")
    else:
        st.warning("Could not determine level for the given input.") 