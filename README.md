# StrengthAI

StrengthAI is an AI-powered, Streamlit-based app for personalized strength training, injury management, and workout logging. It leverages LLMs and your own training data to help you plan, track, and optimize your workouts, while also providing injury diagnostics and rehab suggestions.

---

## Features

- 🏋️ Workout Logger: Log your workout sessions, including exercises, sets, reps, weights, and RPE. View your recent sessions and personal bests.
- 🤕 Injury Assistant (Ask Milo): Describe any pain or injury, get diagnostic tests, and receive AI-generated corrective plans. Your injury history is saved for future reference and planning.
- 🧠 AI Training Planner: Get personalized training plans based on your logged PRs and (optionally) your injury history. Plans include warm-ups, working sets, reps, weights, and RPE targets.
- 📂 History & Stats: Review your full workout history, personal records, and body stats.
- 💾 Backup & Restore: Export and import your workout and body stats data for backup or transfer.

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd StrengthAi
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the project root.
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```

4. **(Optional) Download or prepare model files:**
   - By default, the app will download required models automatically on first run.

---

## Usage

1. **Start the app:**
   ```sh
   streamlit run Home.py
   ```

2. **Navigate the app:**
   - **Home:** Overview, recent sessions, and navigation.
   - **Workout Logger:** Log new sessions and view stats.
   - **Injury Assistant:** Get diagnostic and rehab advice.
   - **Planner:** Generate personalized training plans.
   - **History:** Review all past sessions.
   - **Backup & Restore:** Export/import your data.

---

## Data Storage

- **LocalStorage:**
  All user data (workouts, injuries, plans, stats) is stored in your browser's localStorage for privacy and persistence.
- **Backup:**
  Use the Backup & Restore page to export/import your data as needed.

---

## Requirements

See `requirements.txt` for all dependencies.  
Key packages:
- streamlit
- pandas
- langchain-community
- langchain_groq
- sentence-transformers
- faiss-cpu
- streamlit-local-storage
- pypdf
- ipywidgets

---

## Notes

- The app uses LLMs via Groq for generating plans and injury advice.
- All features are accessible via the sidebar or main navigation links.
- For best results, keep your workout and injury logs up to date.

---
