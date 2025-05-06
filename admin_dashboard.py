import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

st.set_page_config(page_title="Hospital Admin Dashboard")

st.title("🏥 Triage Admin Dashboard")
password = st.text_input("Enter Password", type="password")
if password != "your-secure-password":
    st.warning("Incorrect password!")
    st.stop()  # This will stop execution of the dashboard
# Load DB
conn = sqlite3.connect("triage_log.db")
df = pd.read_sql_query("SELECT * FROM triage_logs ORDER BY timestamp DESC", conn)

# Metrics
st.metric("Total Triage Sessions", len(df))
st.metric("Average Queue Time", "90 mins (simulated)")
st.metric("Languages Used", df["language"].nunique())

# Pie chart of urgency
chart = alt.Chart(df).mark_arc().encode(
    theta=alt.Theta(field="count", type="quantitative"),
    color=alt.Color(field="urgency", type="nominal"),
).transform_aggregate(
    count='count()',
    groupby=["urgency"]
)

st.altair_chart(chart, use_container_width=True)

# Latest logs
st.subheader("📋 Recent Triage Logs")
st.dataframe(df[['timestamp', 'symptoms', 'urgency', 'action', 'language']])
