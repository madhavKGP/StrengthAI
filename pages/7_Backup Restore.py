import streamlit as st
import json
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="💾 Backup & Restore", layout="wide")
st.title("💾 Backup & Restore All Data")

localS = LocalStorage()

def get_all_user_data(localS):
    data = {}
    data['workout_sessions'] = localS.getItem('workout_sessions')
    if not data['workout_sessions'] or not isinstance(data['workout_sessions'], list):
        data['workout_sessions'] = []
    data['body_stats'] = localS.getItem('body_stats')
    if not data['body_stats'] or not isinstance(data['body_stats'], list):
        data['body_stats'] = []
    data['injury_history'] = localS.getItem('injury_history')
    if not data['injury_history'] or not isinstance(data['injury_history'], list):
        data['injury_history'] = []
    data['plan_history'] = localS.getItem('plan_history')
    if not data['plan_history'] or not isinstance(data['plan_history'], list):
        data['plan_history'] = []
    data['latest_injury'] = localS.getItem('latest_injury')
    if not data['latest_injury'] or not isinstance(data['latest_injury'], dict):
        data['latest_injury'] = None
    data['latest_plan'] = localS.getItem('latest_plan')
    if not data['latest_plan'] or not isinstance(data['latest_plan'], dict):
        data['latest_plan'] = None
    return data

def merge_all_user_data(localS, imported):
    # Merge sessions
    sessions = localS.getItem('workout_sessions')
    if not sessions or not isinstance(sessions, list):
        sessions = []
    imported_sessions = imported.get('workout_sessions', [])
    merged_sessions = sessions + [s for s in imported_sessions if s not in sessions]
    localS.setItem('workout_sessions', merged_sessions, key='workout_sessions')
    # Merge body stats
    stats = localS.getItem('body_stats')
    if not stats or not isinstance(stats, list):
        stats = []
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
    localS.setItem('body_stats', merged_stats, key='body_stats')
    # Merge injury history
    injury_history = localS.getItem('injury_history')
    if not injury_history or not isinstance(injury_history, list):
        injury_history = []
    imported_injury = imported.get('injury_history', [])
    merged_injury = injury_history + [i for i in imported_injury if i not in injury_history]
    localS.setItem('injury_history', merged_injury, key='injury_history')
    # Merge plan history
    plan_history = localS.getItem('plan_history')
    if not plan_history or not isinstance(plan_history, list):
        plan_history = []
    imported_plan = imported.get('plan_history', [])
    merged_plan = plan_history + [p for p in imported_plan if p not in plan_history]
    localS.setItem('plan_history', merged_plan, key='plan_history')
    # Latest injury/plan (just overwrite with imported if present)
    if imported.get('latest_injury'):
        localS.setItem('latest_injury', imported['latest_injury'], key='latest_injury')
    if imported.get('latest_plan'):
        localS.setItem('latest_plan', imported['latest_plan'], key='latest_plan')

st.markdown('---')
st.subheader('📤 Export / 📥 Import All Data')
col_exp, col_imp = st.columns(2)
with col_exp:
    if st.button('Export All Data as JSON'):
        all_data = get_all_user_data(localS)
        json_data = json.dumps(all_data, indent=2)
        st.download_button('Download JSON', data=json_data, file_name='strengthai_backup.json', mime='application/json')
with col_imp:
    uploaded = st.file_uploader('Import All Data (JSON)', type='json')
    if uploaded:
        try:
            imported = json.load(uploaded)
            if isinstance(imported, dict):
                merge_all_user_data(localS, imported)
                st.success('Imported and merged all user data!')
            else:
                st.error('Invalid file format.')
        except Exception as e:
            st.error(f'Import failed: {e}') 