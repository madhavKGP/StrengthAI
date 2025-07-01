import streamlit as st
import pandas as pd
import json
from streamlit_local_storage import LocalStorage
from datetime import datetime

st.set_page_config(page_title="🧑‍💼 Body Stats", layout="wide")
st.title("🧑‍💼 Body Stats Tracker")

localS = LocalStorage()
STATS_KEY = "body_stats"
stats = localS.getItem(STATS_KEY)
if not stats or not isinstance(stats, list):
    stats = []

# --- Add/Edit Body Stat ---
st.header("Add/Update Body Stat Entry")
with st.form("add_stat_form", clear_on_submit=True):
    name = st.text_input("Name", value="")
    age = st.number_input("Age", min_value=0, max_value=120, value=25)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    weight = st.number_input("Bodyweight (kg)", min_value=20.0, max_value=300.0, value=70.0)
    date = st.date_input("Date", value=datetime.today())
    submitted = st.form_submit_button("Add/Update Entry")
    if submitted and name:
        # If name+date exists, update; else add
        found = False
        for s in stats:
            if s["name"] == name and s["date"] == str(date):
                s.update({"age": age, "height": height, "weight": weight})
                found = True
        if not found:
            stats.append({"name": name, "age": age, "height": height, "weight": weight, "date": str(date)})
        localS.setItem(STATS_KEY, stats)
        st.success("Entry saved!")

# --- Select user for graph ---
if stats:
    st.header("Bodyweight History")
    names = sorted(list(set(s["name"] for s in stats)))
    selected_name = st.selectbox("Select Name", names)
    user_stats = [s for s in stats if s["name"] == selected_name]
    if user_stats:
        df = pd.DataFrame(user_stats)
        df = df.sort_values("date")
        st.line_chart(df.set_index("date")["weight"], use_container_width=True)
        st.dataframe(df, use_container_width=True)
else:
    st.info("No body stats found. Add your first entry above!")

st.markdown('---')
st.info('To backup or restore your data, please use the "💾 Backup & Restore" page.')