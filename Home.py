import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

# Load PR data
pr_file_path = "pages/data/pr_data.csv"
if os.path.exists(pr_file_path):
    pr_df = pd.read_csv(pr_file_path)
    st.markdown("### 📊 Your Current Personal Records (PRs)")
    st.dataframe(pr_df, use_container_width=True)
else:
    st.warning("No PR data found. Log your first workout to start tracking your progress.")

# Overview of app features
st.markdown("---")
st.markdown("### 🧭 Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📓 Workout Logger")
    # st.markdown("Log your sets, weights, RPEs, and track PRs automatically.")
    st.page_link("pages/1_Workout Logger.py", label="Go to Workout Logger", icon="📝")

    st.subheader("🤕 Injury Assistant")
    # st.markdown("Describe your pain and get diagnostic tests + corrective exercises.")
    st.page_link("pages/2_Ask Milo.py", label="Open Injury Assistant", icon="🧠")

with col2:
    st.subheader("🧠 AI Planner")
    # st.markdown("Get your personalized training day plan using your PRs and injury status.")
    st.page_link("pages/3_Planner.py", label="Launch Planner", icon="📅")

    st.subheader("📂 History (Coming Soon)")
    st.markdown("View your logged workouts, trends, and recovery history.")
