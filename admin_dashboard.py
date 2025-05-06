import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("📊 Hospital Admin Dashboard - Triage Overview")

# Check if database exists
db_path = "triage_log.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM triage_logs ORDER BY timestamp DESC", conn)
    conn.close()
else:
    st.warning("No triage database found. Showing sample data.")
    # Sample fallback DataFrame
    df = pd.DataFrame({
        "timestamp": ["2025-05-06 10:00", "2025-05-06 11:00"],
        "symptoms": ["Headache", "Fever and chills"],
        "urgency": ["Low", "High"],
        "action": ["Self-care", "ER"],
        "language": ["English", "Malay"]
    })

# Filter by urgency or language
urgency_filter = st.multiselect("Filter by Urgency", df['urgency'].unique())
language_filter = st.multiselect("Filter by Language", df['language'].unique())

filtered_df = df.copy()
if urgency_filter:
    filtered_df = filtered_df[filtered_df["urgency"].isin(urgency_filter)]
if language_filter:
    filtered_df = filtered_df[filtered_df["language"].isin(language_filter)]

# Show filtered table
st.dataframe(filtered_df, use_container_width=True)

# Summary metrics
st.markdown("### 📈 Summary")
st.metric("Total Cases", len(df))
st.metric("High Urgency", (df["urgency"] == "High").sum())
st.metric("ER Referrals", (df["action"] == "ER").sum())

# Visual
st.bar_chart(df["urgency"].value_counts())
