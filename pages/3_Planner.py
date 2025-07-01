import streamlit as st
import pandas as pd
import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_local_storage import LocalStorage
from datetime import datetime

# Load env vars
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
groq_api_key = os.getenv("GROQ_API_KEY")

# LLM Setup
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

st.title("📅 Personalized Training Planner")
st.markdown("Milo will create today's plan using your PRs and (optionally) injury history.")

# Check for injury usage
use_injury = st.checkbox("📌 Use Injury History from Ask Milo", value=True)

localS = LocalStorage()

# Helper: Get best PRs from workout_sessions
sessions = localS.getItem('workout_sessions')
if not sessions or not isinstance(sessions, list):
    sessions = []
best_records = {}
for session in sessions:
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
                    "Max RPE": s["RPE"]
                }
pr_df = pd.DataFrame(list(best_records.values())) if best_records else pd.DataFrame({"Exercise":[],"Best 1RM":[],"Max Weight":[],"Max Reps":[],"Max RPE":[]})
pr_summary = pr_df.to_string(index=False)

# Helper: Get latest injury from localStorage
latest_injury = localS.getItem('latest_injury')
if not latest_injury or not isinstance(latest_injury, dict):
    latest_injury = None
injury_summary = ""
if use_injury and latest_injury:
    injury_summary = f"\nUser reports injury: {latest_injury.get('query','')}\n\nTests: {latest_injury.get('tests','')}\n\nFindings: {latest_injury.get('test_results','')}\n\nRecommendations: {latest_injury.get('response','')}"

# Chat-based input
user_query = st.text_input("💬 Ask Milo for today's training plan", placeholder="e.g., Give me today's squat plan")

if st.button("🛠️ Generate Plan") or user_query:
    system_prompt = PromptTemplate(
        input_variables=["context"],
        template="""
                You are a powerlifting coach named Milo. Based on the context below, respond to the user's specific query.
                Write in first person with the user.
                Include warm-ups, working sets, reps, weights  (based on their PRs), and target RPE.
                Account for any injuries mentioned. Return the plan in markdown format using code blocks (```) for tables so that it renders properly in Streamlit.
                
                Context:
                {context}
                """
    )

    query_text = user_query if user_query else "Give me today's full training plan"
    full_context = f"{pr_summary}\n\n{injury_summary}\n\nUser query: {query_text}"
    prompt = system_prompt.format(context=full_context)
    response = llm.invoke(prompt)

    st.subheader("🏋️ Milo's Plan for Today")
    st.markdown(response.content if hasattr(response, 'content') else str(response))

    # Save plan to localStorage
    plan_history = localS.getItem('plan_history')
    if not plan_history or not isinstance(plan_history, list):
        plan_history = []
    plan_entry = {
        'timestamp': str(datetime.now()),
        'query': query_text,
        'plan': response.content if hasattr(response, 'content') else str(response)
    }
    plan_history.append(plan_entry)
    localS.setItem('plan_history', plan_history, key='plan_history')
    localS.setItem('latest_plan', plan_entry, key='latest_plan')
