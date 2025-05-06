import streamlit as st
import openai
import json
from prompts import build_prompt
from utils.translator import translate_text
from utils.db_logger import init_db, log_triage

# Set the Streamlit page configuration first
st.set_page_config(page_title="AI Triage Assistant", layout="centered")

# Initialize database
init_db()

# Set the OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load hospital data (assuming the file exists)
with open("data/hospital_status.json", "r") as f:
    hospital_status = json.load(f)

# Load custom CSS for styling
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Custom style not loaded — styles.css not found.")

# Page title
st.title("🏥 AI Triage Assistant for Public Hospitals")

# Language and Literacy Level Inputs
language = st.selectbox("Choose Language", ["English", "Malay", "Mandarin", "Tamil"])
literacy = st.radio("Select Literacy Level", ["Simple", "Advanced"])

# User Inputs for Symptoms and History
symptoms = st.text_area("Describe your symptoms:")
history = st.text_input("Medical history (if any):")
allergies = st.text_input("Allergies (if any):")

# Display hospital status information
er_status = hospital_status.get("ER_Load", "Moderate")
queue_time = hospital_status.get("QueueTime_Minutes", 45)

# Button to estimate urgency
if st.button("Estimate Urgency"):
    with st.spinner("Analyzing..."):
        # Build the prompt based on the user inputs
        full_prompt = build_prompt(symptoms, history, allergies, language, literacy, er_status, queue_time)

        # Request OpenAI's GPT model for triage
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI medical triage assistant."},
                      {"role": "user", "content": full_prompt}]
        )

        result = response['choices'][0]['message']['content']

        # Parse urgency and action from the result (simplified)
        urgency = "Medium" if "Medium" in result else ("High" if "High" in result else "Low")
        action = "ER" if "ER" in result else ("Self-care" if "Self-care" in result else "Clinic")

        # Log the triage data into the database
        log_triage(symptoms, urgency, action, language)

        # Translate the result into the selected language
        translated = translate_text(result, target_lang=language)

        # Display the result
        st.markdown("### 🩺 Triage Recommendation:")
        st.success(translated)

# Optional: Allow users to use voice input (for supported browsers)
st.markdown("**Or use your microphone to describe symptoms:**")
st.markdown("""
> 🗣️ On mobile, use the mic button on your keyboard.
> On desktop Chrome, you can enable speech-to-text from browser settings.
""")

# Display the "Help" or additional instructions if needed
st.markdown("""
### How it Works:
1. **Enter your symptoms and medical history**.
2. **The AI will analyze your input and recommend an urgency level**.
3. **Follow the suggested next steps** based on the AI's triage results (e.g., ER, GP, self-care).
""")
