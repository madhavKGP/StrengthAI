import streamlit as st
import pandas as pd
import os

st.title("Workout Logger")

# File to store PR data
PR_FILE = "pr_data.csv"

# Initialize session state
if "exercises" not in st.session_state:
    st.session_state.exercises = {}   # inits a exercises dictionary

# Function to calculate 1RM
def calculate_1rm(weight, reps, rpe):
    if(rpe == 0):
        st.warning("⚠️ RPE is 0 — this will be treated as RPE 10 (max effort).")
        rpe = 10       # initialise it 10 if no input

    rir = round(10 - rpe)  # Reps in reserve
    adjusted_reps = reps + rir
    return round(weight * (1 + adjusted_reps / 30), 2)


# Function to update PR file
def update_pr_file(log_data):
 
    if os.path.exists(PR_FILE):
        pr_df = pd.read_csv(PR_FILE)
    else:
        pr_df = pd.DataFrame(columns=["Exercise", "Best 1RM", "Max Volume", "Max RPE", "Max Weight"])

    for exercise, sets in log_data.items():
        for s in sets:
            volume = s["Weight"] * s["Reps"]
            one_rm = calculate_1rm(s["Weight"], s["Reps"], s['RPE'])
            rpe = s["RPE"]
            weight = s["Weight"]

            if exercise in pr_df["Exercise"].values:
                row = pr_df[pr_df["Exercise"] == exercise].index[0]
                
                pr_df.loc[row, "Best 1RM"] = max(pr_df.loc[row, "Best 1RM"], one_rm)
                pr_df.loc[row, "Max Volume"] = max(pr_df.loc[row, "Max Volume"], volume)
                pr_df.loc[row, "Max RPE"] = max(pr_df.loc[row, "Max RPE"], rpe)
                pr_df.loc[row, "Max Weight"] = max(pr_df.loc[row, "Max Weight"], weight)
            else:  #if no exercise
                new_row = pd.DataFrame([[exercise, one_rm, volume, rpe, weight]],
                                       columns=["Exercise", "Best 1RM", "Max Volume", "Max RPE", "Max Weight"])
                pr_df = pd.concat([pr_df, new_row], ignore_index=True)

    pr_df.to_csv(PR_FILE, index=False)
    st.success("✅ PR data updated!")

exercise_options = [
    "Bench Press",
    "Squat",
    "Deadlift",
    "Lat Pulldown",
    "Bicep Curl"
]

# Add new exercise
with st.form("add_exercise_form", clear_on_submit=True):
    exercise_name = st.selectbox("Select Exercise", exercise_options)
    submitted = st.form_submit_button("➕ Add Exercise")
    if submitted:
        if exercise_name not in st.session_state.exercises:
            st.session_state.exercises[exercise_name] = []
        else:
            st.warning("Exercise already added.")

# Display each exercise and allow adding sets
for exercise in st.session_state.exercises.keys():
    st.subheader(f"🏋️ {exercise}")
    with st.form(f"set_form_{exercise}", clear_on_submit=True):
        cols = st.columns(3)
        weight = cols[0].number_input("Weight (kg)", min_value=0, step=1, key=f"wt_{exercise}")
        reps = cols[1].number_input("Reps", min_value=1, step=1, key=f"reps_{exercise}")
        rpe = cols[2].number_input("RPE", min_value=0, max_value=10, step=1, key=f"rpe_{exercise}")
        add_set = st.form_submit_button("Add Set")
        if add_set:
            st.session_state.exercises[exercise].append({
                "Weight": weight,
                "Reps": reps,
                "RPE": rpe
            })

    # Display current sets
    if st.session_state.exercises[exercise]:
        st.write("📋 Sets:")
        set_df = pd.DataFrame(st.session_state.exercises[exercise])
        set_df["Volume"] = set_df["Weight"] * set_df["Reps"]
        set_df["Est. 1RM"] = set_df.apply(lambda row: calculate_1rm(row["Weight"], row["Reps"], row["RPE"]), axis=1)
        st.dataframe(set_df)

# Submit all data
if st.button("✅ Submit Session"):
    if st.session_state.exercises:
        update_pr_file(st.session_state.exercises)
        st.session_state.exercises = {}
    else:
        st.warning("Please add at least one exercise with sets.")
