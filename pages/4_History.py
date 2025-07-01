import streamlit as st
import pandas as pd
from streamlit_local_storage import LocalStorage
from datetime import datetime
import json

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

st.set_page_config(page_title="📂 Workout History", layout="wide")
st.title("📂 Workout History")

localS = LocalStorage()
SESSIONS_KEY = "workout_sessions"
sessions = localS.getItem(SESSIONS_KEY)
if not sessions or not isinstance(sessions, list):
    sessions = []
injury_history = localS.getItem('injury_history')
if not injury_history or not isinstance(injury_history, list):
    injury_history = []
plan_history = localS.getItem('plan_history')
if not plan_history or not isinstance(plan_history, list):
    plan_history = []

# Tabs for different histories of user
st.header('History')
tabs = st.tabs(["Workout Sessions", "Injury History", "Plan History"])

with tabs[0]:
    if not sessions:
        st.warning("No workout sessions found. Start logging to see your history!")
    else:
        for i, session in enumerate(reversed(sessions)):
            start = format_dt(session.get('start_time',''))
            end = format_dt(session.get('end_time',''))
            duration = calc_duration(session.get('start_time',''), session.get('end_time',''))
            exercises = list(session.get('exercises', {}).keys())
            n_sets = sum(len(sets) for sets in session.get('exercises', {}).values())
            header = f"🗓️  Session #{len(sessions)-i} | 🕒 {start} | ⏱️ {duration} | 🏋️ {len(exercises)} exercises, {n_sets} sets"
            with st.expander(header):
                st.markdown(f"**Weight Type:** {session.get('weight_type','kg')}")
                st.markdown(f"**Start:** {start}")
                st.markdown(f"**End:** {end}")
                for ex, sets in session.get("exercises", {}).items():
                    st.subheader(f"🏋️ {ex}")
                    if sets:
                        set_df = pd.DataFrame(sets)
                        set_df["Volume"] = set_df["Weight"] * set_df["Reps"]
                        set_df["Est. 1RM"] = set_df.apply(lambda row: round(row["Weight"] * (1 + (row["Reps"] + (10 - row["RPE"])) / 30), 2), axis=1)
                        st.dataframe(set_df, use_container_width=True)
                    else:
                        st.write("No sets logged for this exercise.")

with tabs[1]:
    if not injury_history:
        st.info("No injury history found.")
    else:
        for i, entry in enumerate(reversed(injury_history)):
            date_str = format_dt(entry.get('date', '')) if 'date' in entry else ''
            header = f"Injury #{len(injury_history)-i} | Query: {entry.get('query','')}"
            if date_str:
                header += f" | {date_str}"
            with st.expander(header):
                st.markdown(f"**Tests:** {entry.get('tests','')}")
                st.markdown(f"**Test Results:** {entry.get('test_results','')}")
                st.markdown(f"**Response:** {entry.get('response','')}")

with tabs[2]:
    if not plan_history:
        st.info("No plan history found.")
    else:
        for i, entry in enumerate(reversed(plan_history)):
            timestamp = format_dt(entry.get('timestamp',''))
            with st.expander(f"Plan #{len(plan_history)-i} | {timestamp}"):
                st.markdown(f"**Query:** {entry.get('query','')}")
                st.markdown(f"**Plan:**")
                st.markdown(entry.get('plan',''))

st.markdown('---')
st.info('To backup or restore your data, please use the "💾 Backup & Restore" page.') 