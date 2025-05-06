import streamlit as st
import openai
import json
from prompts import build_prompt
from utils.translator import translate_text
from utils.db_logger import init_db, log_triage
import datetime

# ---------------- Setup ---------------- #
st.set_page_config(page_title="AI Triage Assistant", layout="centered")
init_db()
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------- Header ---------------- #
st.markdown("""
<style>
    .main { background-color: #f4f6f8; }
    h1, h2, h3 { color: #003366; }
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stRadio > label {
        font-weight: 600;
    }
</style>

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.markdown('<div class="main">', unsafe_allow_html=True)

# --- Your app content here ---
st.title("🏥 AI Triage Assistant")
# ... form inputs, etc.

st.markdown('</div>', unsafe_allow_html=True)


# ---------------- Language & Literacy ---------------- #
st.subheader("🌐 Language & Literacy")
col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("Choose Language", ["English", "Malay", "Mandarin", "Tamil"])
with col2:
    literacy = st.radio("Select Literacy Level", ["Simple", "Advanced"], horizontal=True)

# ---------------- Patient Form ---------------- #
st.subheader("📝 Patient Input")
symptoms = st.text_area("Describe your symptoms:", placeholder="e.g. Chest pain, fever, headache")
col3, col4 = st.columns(2)
with col3:
    history = st.text_input("Medical history (if any):", placeholder="e.g. Diabetes, Asthma")
with col4:
    allergies = st.text_input("Allergies (if any):", placeholder="e.g. Penicillin")

# ---------------- Hospital Load (Dynamic Status) ---------------- #
with open("data/hospital_status.json", "r") as f:
    hospital_status = json.load(f)
er_status = hospital_status.get("ER_Load", "Moderate")
queue_time = hospital_status.get("QueueTime_Minutes", 45)

st.info(f"🚦 Current ER Load: **{er_status}** | ⏱️ Avg Waiting Time: **{queue_time} mins**")

# ---------------- Estimate Button ---------------- #
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

        # Determine urgency level for color display
        urgency = "Medium" if "Medium" in result else ("High" if "High" in result else "Low")
        action = "ER" if "ER" in result else ("Self-care" if "Self-care" in result else "Clinic")

        # Save to DB
        log_triage(symptoms, urgency, action, language)

        # Show result
        st.subheader("📋 AI Recommendation")
        if "High" in result:
            st.error(translated)
        elif "Medium" in result:
            st.warning(translated)
        else:
            st.success(translated)

# ---------------- Voice Input Guide ---------------- #
st.markdown("### 🎤 Or describe symptoms by voice:")
st.markdown("Use voice-to-text from your device’s keyboard or browser. Most modern browsers and mobile keyboards support this.")
st.text_area("Paste voice transcription here:", placeholder="e.g. I feel dizzy and have chest tightness")
