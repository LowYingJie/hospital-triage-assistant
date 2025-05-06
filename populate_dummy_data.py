import sqlite3

# Connect to your SQLite DB
conn = sqlite3.connect("triage_log.db")
cursor = conn.cursor()

# Ensure the table exists
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

# Insert dummy records
dummy_data = [
    ("Headache and dizziness", "Low", "Self-care", "English"),
    ("Chest pain and shortness of breath", "High", "ER", "Malay"),
    ("Fever, sore throat", "Medium", "Clinic", "Tamil"),
    ("Blurred vision suddenly", "High", "ER", "Mandarin"),
    ("Mild cough", "Low", "Self-care", "English")
]

cursor.executemany("""
    INSERT INTO triage_logs (symptoms, urgency, action, language)
    VALUES (?, ?, ?, ?)
""", dummy_data)

conn.commit()
conn.close()

print("✅ Dummy triage data inserted into triage_log.db")
