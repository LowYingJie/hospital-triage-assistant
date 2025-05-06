import streamlit as st
import openai
import json
from prompts import build_prompt
from utils.translator import translate_text

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Triage Assistant", layout="centered")

# Load hospital data
with open("data/hospital_status.json", "r") as f:
    hospital_status = json.load(f)

st.title("🏥 AI Triage Assistant for Public Hospitals")

language = st.selectbox("Choose Language", ["English", "Malay", "Mandarin", "Tamil"])
literacy = st.radio("Select Literacy Level", ["Simple", "Advanced"])

symptoms = st.text_area("Describe your symptoms:")
history = st.text_input("Medical history (if any):")
allergies = st.text_input("Allergies (if any):")

er_status = hospital_status.get("ER_Load", "Moderate")
queue_time = hospital_status.get("QueueTime_Minutes", 45)

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

        st.markdown("### 🩺 Recommendation:")
        st.success(translated)
