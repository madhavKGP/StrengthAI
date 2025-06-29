import streamlit as st
import pandas as pd
import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

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
use_injury = st.checkbox("📌 Use Injury History (latest_injury.json)")

# Chat-based input
user_query = st.text_input("💬 Ask Milo for today's training plan", placeholder="e.g., Give me today's squat plan")

if st.button("🛠️ Generate Plan") or user_query:
    # Load PR CSV directly
    pr_file_path = "pages/data/pr_data.csv"
    if os.path.exists(pr_file_path):
        pr_df = pd.read_csv(pr_file_path)
    else:
        # Create a default empty PR table
        pr_df = pd.DataFrame({
            "Exercise": ["Squat", "Bench Press", "Deadlift"],
            "Best 1RM": [0, 0, 0],
            "Max Volume": [0, 0, 0],
            "Max RPE": [0, 0, 0],
            "Max Weight": [0, 0, 0]
        })

    pr_summary = pr_df.to_string(index=False)

    injury_summary = ""
    if use_injury and os.path.exists("pages/data/latest_injury.json"):
        with open("pages/data/latest_injury.json") as f:
            injury_data = json.load(f)
        injury_summary = f"\nUser reports injury: {injury_data['query']}\n\nTests: {injury_data['tests']}\n\nFindings: {injury_data['test_results']}\n\nRecommendations: {injury_data['response']}"

    system_prompt = PromptTemplate(
        input_variables=["context"],
        template="""
                You are a powerlifting coach named Milo. Based on the context below, respond to the user's specific query.
                Write in first person with the user.
                Include warm-ups, working sets, reps, weights  (based on their PRs), and target RPE.
                Account for any injuries mentioned. Return the plan in markdown format using code blocks (\`\`\`) for tables so that it renders properly in Streamlit.
                
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
