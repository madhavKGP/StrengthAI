import streamlit as st
import pandas as pd
from streamlit_local_storage import LocalStorage
from datetime import datetime
import json

st.set_page_config(page_title="🏠 StrengthAI Home", layout="wide")

# Dynamic greeting based on time
hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

st.title(f"💪 {greeting}, Welcome to StrengthAI")
st.markdown("Your AI-powered personalized training & rehab assistant.")

# Load all sessions from localStorage
localS = LocalStorage()
SESSIONS_KEY = "workout_sessions"
sessions = localS.getItem(SESSIONS_KEY)
if not sessions or not isinstance(sessions, list):
    sessions = []

# Compute personal bests records
best_records = {}
for session in sessions:
    wt_type = session.get("weight_type", "kg")
    for ex, sets in session.get("exercises", {}).items():
        for s in sets:
            one_rm = round(s["Weight"] * (1 + (s["Reps"] + (10 - s["RPE"])) / 30), 2)
            prev_best = best_records[ex]["Est. 1RM"] if ex in best_records and "Est. 1RM" in best_records[ex] else -float('inf')
            if ex not in best_records or one_rm > prev_best:
                best_records[ex] = {
                    "Exercise": ex,
                    "Best 1RM": one_rm,
                    "Est. 1RM": one_rm,
                    "Max Weight": s["Weight"],
                    "Max Reps": s["Reps"],
                    "Max RPE": s["RPE"],
                    "Weight Type": wt_type
                }

if best_records:
    pr_df = pd.DataFrame(list(best_records.values()))
    st.markdown("### 📊 Your Personal Bests (All Sessions)")
    st.dataframe(pr_df, use_container_width=True)
else:
    st.warning("No workout sessions found. Start logging to see your stats!")

# Show workout history summary
if sessions:
    st.markdown("### 🕒 Workout History (Recent Sessions)")
    hist_rows = []
    def format_dt(dt_str):
        try:
            return datetime.fromisoformat(dt_str).strftime('%b %d, %Y, %H:%M')
        except Exception:
            return dt_str or "-"
    def calc_duration(start_str, end_str):
        try:
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
            mins = int((end - start).total_seconds() // 60)
            return f"{mins} min"
        except Exception:
            return "-"
    for i, session in enumerate(reversed(sessions[-5:])):
        hist_rows.append({
            "Session #": len(sessions) - i,
            "Start": format_dt(session.get("start_time", "")),
            "Duration": calc_duration(session.get("start_time", ""), session.get("end_time", "")),
            "Exercises": ", ".join(session.get("exercises", {}).keys()),
            "Weight Type": session.get("weight_type", "kg")
        })
    hist_df = pd.DataFrame(hist_rows)
    st.dataframe(hist_df, use_container_width=True)
    st.page_link("pages/4_History.py", label="View Full History", icon="📂")

# Overview of app features
st.markdown("---")
st.markdown("### 🧭 Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📓 Workout Logger")
    st.page_link("pages/1_Workout Logger.py", label="Go to Workout Logger", icon="📝")

    st.subheader("🤕 Injury Assistant")
    st.page_link("pages/2_Ask Milo.py", label="Open Injury Assistant", icon="🧠")

with col2:
    st.subheader("🧠 AI Planner")
    st.page_link("pages/3_Planner.py", label="Launch Planner", icon="📅")

    st.subheader("📂 History")
    st.page_link("pages/4_History.py", label="View Full History", icon="📂")

# --- Unified Export/Import ---
def get_all_user_data(localS):
    data = {}
    data['workout_sessions'] = localS.getItem('workout_sessions') or []
    data['body_stats'] = localS.getItem('body_stats') or []
    return data

def merge_all_user_data(localS, imported):
    # Merge sessions
    sessions = localS.getItem('workout_sessions') or []
    imported_sessions = imported.get('workout_sessions', [])
    merged_sessions = sessions + [s for s in imported_sessions if s not in sessions]
    localS.setItem('workout_sessions', merged_sessions)
    # Merge body stats
    stats = localS.getItem('body_stats') or []
    imported_stats = imported.get('body_stats', [])
    merged_stats = stats.copy()
    for entry in imported_stats:
        match = [s for s in merged_stats if s["name"] == entry["name"] and s["date"] == entry["date"]]
        if match:
            if any(s for s in match if s == entry):
                continue
            else:
                for s in match:
                    s["name"] = f"{s['name']}-{entry['name']}"
        else:
            merged_stats.append(entry)
    localS.setItem('body_stats', merged_stats)

st.markdown('---')
st.info('To backup or restore your data, please use the "💾 Backup & Restore" page.')
