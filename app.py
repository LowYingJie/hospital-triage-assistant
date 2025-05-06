import streamlit as st
import openai
import json
from prompts import build_prompt
from utils.translator import translate_text
from utils.db_logger import init_db, log_triage

# ------------------ Config ------------------ #
st.set_page_config(page_title="🏥 AI Triage Assistant", layout="centered")
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load CSS styling from styles.css
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database
init_db()

# ------------------ UI Container ------------------ #
st.markdown('<div class="main">', unsafe_allow_html=True)

st.title("🏥 AI Triage Assistant")
st.caption("Built for Public Hospitals in Malaysia — multilingual & low-literacy friendly")

# ------------------ Language & Literacy ------------------ #
st.subheader("🌐 Language & Literacy Preferences")
col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("Choose Language", ["English", "Malay", "Mandarin", "Tamil"])
with col2:
    literacy = st.radio("Select Literacy Level", ["Simple", "Advanced"], horizontal=True)

# ------------------ Patient Input ------------------ #
st.subheader("📝 Describe Your Condition")
symptoms = st.text_area("Describe your symptoms:", placeholder="e.g. Fever and cough for 3 days")
col3, col4 = st.columns(2)
with col3:
    history = st.text_input("Medical history (if any):", placeholder="e.g. Asthma, Diabetes")
with col4:
    allergies = st.text_input("Allergies (if any):", placeholder="e.g. Penicillin")

# ------------------ Hospital Load Info ------------------ #
with open("data/hospital_status.json", "r") as f:
    hospital_status = json.load(f)

er_status = hospital_status.get("ER_Load", "Moderate")
queue_time = hospital_status.get("QueueTime_Minutes", 45)

st.info(f"🚦 Current ER Load: **{er_status}** | ⏱️ Avg Wait Time: **{queue_time} mins**")

# ------------------ Estimate Urgency ------------------ #
if st.button("🔍 Estimate Urgency"):
    with st.spinner("Analyzing symptoms using AI..."):
        full_prompt = build_prompt(symptoms, history, allergies, language, literacy, er_status, queue_time)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI medical triage assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )

        result = response['choices'][0]['message']['content']
        translated = translate_text(result, target_lang=language)

        # Parse urgency and action from output
        urgency = "Medium" if "Medium" in result else ("High" if "High" in result else "Low")
        action = "ER" if "ER" in result else ("Self-care" if "Self-care" in result else "Clinic")

        log_triage(symptoms, urgency, action, language)

        st.subheader("📋 AI Recommendation")
        if urgency == "High":
            st.error(translated)
        elif urgency == "Medium":
            st.warning(translated)
        else:
            st.success(translated)

# ------------------ Voice Input ------------------ #
st.subheader("🎤 Voice Input (Optional)")
st.markdown("Use your mobile keyboard mic or browser speech-to-text to dictate symptoms.")
st.text_area("Paste transcribed speech here:", placeholder="e.g. I feel weak and dizzy")

st.markdown('</div>', unsafe_allow_html=True)
