import streamlit as st
import pandas as pd
from streamlit_local_storage import LocalStorage
from datetime import datetime
import json

st.title("Workout Logger")

localS = LocalStorage()
SESSIONS_KEY = "workout_sessions"

# Helper: Load all sessions from localStorage
sessions = localS.getItem(SESSIONS_KEY)
if not sessions or not isinstance(sessions, list):
    sessions = []

# Session state for current session
if "active_session" not in st.session_state:
    st.session_state.active_session = None

# Track which set is being edited: (exercise, idx) or None
if 'editing_set' not in st.session_state:
    st.session_state['editing_set'] = None
if 'edit_buffer' not in st.session_state:
    st.session_state['edit_buffer'] = {}

exercise_options = [
    "Bench Press",
    "Squat",
    "Deadlift",
    "Lat Pulldown",
    "Bicep Curl"
]
weight_types = ["kg", "lb"]

# Start new session
if not st.session_state.active_session:
    if st.button("Start New Workout Session"):
        st.session_state.active_session = {
            "start_time": datetime.now().isoformat(),
            "exercises": {},
            "weight_type": "kg"
        }
    st.info("Click 'Start New Workout Session' to begin logging.")
else:
    session = st.session_state.active_session
    st.markdown(f"**Session started:** {session['start_time']}")
    # Select weight type for this session
    session["weight_type"] = st.selectbox("Select weight type", weight_types, key="weight_type_select")
    # Add new exercise
    with st.form("add_exercise_form", clear_on_submit=True):
        exercise_name = st.selectbox("Select Exercise", exercise_options, key="exercise_select")
        submitted = st.form_submit_button("➕ Add Exercise")
        if submitted:
            if exercise_name not in session["exercises"]:
                session["exercises"][exercise_name] = []
            else:
                st.warning("Exercise already added.")
    # Add sets to each exercise
    for exercise in session["exercises"].keys():
        st.subheader(f"🏋️ {exercise}")
        with st.form(f"set_form_{exercise}", clear_on_submit=True):
            cols = st.columns(3)
            weight = cols[0].number_input(f"Weight ({session['weight_type']})", min_value=0.0, step=0.5, key=f"wt_{exercise}")
            reps = cols[1].number_input("Reps", min_value=1, step=1, key=f"reps_{exercise}")
            rpe = cols[2].number_input("RPE", min_value=0, max_value=10, step=1, key=f"rpe_{exercise}")
            add_set = st.form_submit_button("Add Set")
            if add_set:
                session["exercises"][exercise].append({
                    "Weight": weight,
                    "Reps": reps,
                    "RPE": rpe
                })
        # Show sets for this exercise
        if session["exercises"][exercise]:
            st.write("📋 Sets:")
            set_df = pd.DataFrame(session["exercises"][exercise])
            set_df["Volume"] = set_df["Weight"] * set_df["Reps"]
            set_df["Est. 1RM"] = set_df.apply(lambda row: round(row["Weight"] * (1 + (row["Reps"] + (10 - row["RPE"])) / 30), 2), axis=1)
            for idx, row in set_df.iterrows():
                is_editing = st.session_state['editing_set'] == (exercise, idx)
                # Use session start time as part of the key for uniqueness
                session_id = session.get('start_time', 'no_session')
                key_prefix = f"{session_id}__{exercise}__{idx}"
                cols2 = st.columns([1,1,1,1,1])
                cols2[0].write(f"Set {idx+1}")
                if is_editing:
                    buf = st.session_state['edit_buffer']
                    if not buf or buf.get('exercise') != exercise or buf.get('idx') != idx:
                        st.session_state['edit_buffer'] = {
                            'exercise': exercise,
                            'idx': idx,
                            'Weight': row['Weight'],
                            'Reps': row['Reps'],
                            'RPE': row['RPE']
                        }
                        buf = st.session_state['edit_buffer']
                    new_weight = cols2[1].number_input("Weight", value=buf['Weight'], key=f"edit_wt_{key_prefix}")
                    new_reps = cols2[2].number_input("Reps", value=buf['Reps'], key=f"edit_reps_{key_prefix}")
                    new_rpe = cols2[3].number_input("RPE", value=buf['RPE'], key=f"edit_rpe_{key_prefix}")
                    if cols2[4].button("Save", key=f"save_{key_prefix}"):
                        session["exercises"][exercise][idx] = {"Weight": new_weight, "Reps": new_reps, "RPE": new_rpe}
                        st.session_state['editing_set'] = None
                        st.session_state['edit_buffer'] = {}
                        st.rerun()
                    if cols2[4].button("Cancel", key=f"cancel_{key_prefix}"):
                        st.session_state['editing_set'] = None
                        st.session_state['edit_buffer'] = {}
                        st.rerun()
                else:
                    if cols2[1].button("Edit", key=f"edit_{key_prefix}"):
                        st.session_state['editing_set'] = (exercise, idx)
                        st.rerun()
                    if cols2[2].button("Delete", key=f"del_{key_prefix}"):
                        session["exercises"][exercise].pop(idx)
                        st.session_state['editing_set'] = None
                        st.session_state['edit_buffer'] = {}
                        st.rerun()
            st.dataframe(set_df)
    # End session
    if st.button("End Session and Save"):
        session["end_time"] = datetime.now().isoformat()
        sessions.append(session)
        localS.setItem(SESSIONS_KEY, sessions)
        st.session_state.active_session = None
        st.success("Session saved!")
    if st.button("Cancel Session"):
        st.session_state.active_session = None
        st.info("Session cancelled.")

st.markdown('---')
st.info('To backup or restore your data, please use the "💾 Backup & Restore" page.')
