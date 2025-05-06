import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("triage_log.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS triage_logs (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        symptoms TEXT,
        urgency TEXT,
        action TEXT,
        language TEXT
    )''')
    conn.commit()
    conn.close()

def log_triage(symptoms, urgency, action, language):
    conn = sqlite3.connect("triage_log.db")
    c = conn.cursor()
    c.execute("INSERT INTO triage_logs (timestamp, symptoms, urgency, action, language) VALUES (?, ?, ?, ?, ?)",
              (datetime.now(), symptoms, urgency, action, language))
    conn.commit()
    conn.close()
