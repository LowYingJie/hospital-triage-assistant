import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("📊 Hospital Admin Dashboard - Triage Overview")

# --- Step 1: Define the DB path ---
db_path = "triage_log.db"

# --- Step 2: Check if the database exists before connecting ---
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM triage_logs ORDER BY timestamp DESC", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error reading database: {e}")
        df = pd.DataFrame()  # empty fallback
else:
    st.warning("⚠️ No triage database found. Showing sample data instead.")
    df = pd.DataFrame({
        "timestamp": ["2025-05-06 10:00", "2025-05-06 11:00"],
        "symptoms": ["Headache", "Fever and chills"],
        "urgency": ["Low", "High"],
        "action": ["Self-care", "ER"],
        "language": ["English", "Malay"]
    })

# --- Step 3: Display Filters ---
if not df.empty:
    urgency_filter = st.multiselect("Filter by Urgency", df['urgency'].unique())
    language_filter = st.multiselect("Filter by Language", df['language'].unique())

    filtered_df = df.copy()
    if urgency_filter:
        filtered_df = filtered_df[filtered_df["urgency"].isin(urgency_filter)]
    if language_filter:
        filtered_df = filtered_df[filtered_df["language"].isin(language_filter)]

    # --- Step 4: Show Filtered Data ---
    st.dataframe(filtered_df, use_container_width=True)

    # --- Step 5: Summary Stats ---
    st.markdown("### 📈 Summary")
    st.metric("Total Cases", len(df))
    st.metric("High Urgency", (df["urgency"] == "High").sum())
    st.metric("ER Referrals", (df["action"] == "ER").sum())

    # --- Step 6: Visual Chart ---
    st.bar_chart(df["urgency"].value_counts())
else:
    st.info("No triage data available to display.")
