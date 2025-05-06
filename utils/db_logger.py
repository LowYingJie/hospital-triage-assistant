import sqlite3

def init_db():
    conn = sqlite3.connect("triage_log.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symptoms TEXT,
            urgency TEXT,
            action TEXT,
            language TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_triage(symptoms, urgency, action, language):
    conn = sqlite3.connect("triage_log.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO triage_logs (symptoms, urgency, action, language)
        VALUES (?, ?, ?, ?)
    """, (symptoms, urgency, action, language))
    conn.commit()
    conn.close()
