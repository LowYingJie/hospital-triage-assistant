import streamlit as st
import openai
import json
from prompts import build_prompt
from utils.translator import translate_text
from utils.db_logger import init_db, log_triage

# Initialize DB
init_db()

# Load API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set up Streamlit page
st.set_page_config(page_title="AI Triage Assistant", layout="centered")
st.title("🏥 AI Triage Assistant for Public Hospitals")

# Load hospital ER data
with open("data/hospital_status.json", "r") as f:
    hospital_status = json.load(f)

# Collect user input
language = st.selectbox("Choose Language", ["English", "Malay", "Mandarin", "Tamil"])
literacy = st.radio("Select Literacy Level", ["Simple", "Advanced"])

st.markdown("**Or use your microphone to describe symptoms:**")
symptoms = st.text_area("Describe your symptoms (or paste from mic):", placeholder="e.g. Chest pain for 2 hours")
st.markdown("""
> 🗣️ On mobile, use the mic button on your keyboard.  
> On desktop Chrome, enable speech-to-text in browser settings.
""")

history = st.text_input("Medical history (if any):")
allergies = st.text_input("Allergies (if any):")

# Read simulated ER status
er_status = hospital_status.get("ER_Load", "Moderate")
queue_time = hospital_status.get("QueueTime_Minutes", 45)

# Response section
if st.button("Estimate Urgency"):
    with st.spinner("Analyzing..."):
        full_prompt = build_prompt(
            symptoms, history, allergies,
            language, literacy, er_status, queue_time
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI medical triage assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )

        result = response['choices'][0]['message']['content']
        translated = translate_text(result, target_lang=language)

        # Extract urgency level and recommended action (very basic parsing)
        urgency = "Medium" if "Medium" in result else ("High" if "High" in result else "Low")
        action = "ER" if "ER" in result else ("Self-care" if "Self-care" in result else "Clinic")

        # Log the triage session
        log_triage(symptoms, urgency, action, language)

        # Display result
        st.markdown("### 🩺 Recommendation:")
        st.success(translated)
