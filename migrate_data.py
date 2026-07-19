import sqlite3
import psycopg2
from datetime import datetime

# Connect to SQLite
sqlite_conn = sqlite3.connect('santinel_feedback.db')
sqlite_cursor = sqlite_conn.cursor()

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="santinel_prod",
    user="postgres",
    password="postgres123",
    port="5432"
)
pg_cursor = pg_conn.cursor()

print("=== MIGRATING DATA ===\n")

# Disable foreign key checks temporarily
print("🔓 Disabling foreign key constraints...")
pg_cursor.execute("ALTER TABLE feedback DISABLE TRIGGER ALL")
pg_cursor.execute("ALTER TABLE outcomes DISABLE TRIGGER ALL")
pg_conn.commit()

# Migrate FEEDBACK
print("📥 Migrating feedback...")
sqlite_cursor.execute("SELECT session_id, coaching_id, rating, quality_score, useful_aspects, comments, timestamp FROM feedback")
feedback_rows = sqlite_cursor.fetchall()

for row in feedback_rows:
    session_id, coaching_id, rating, quality_score, useful_aspects, comments, timestamp = row
    try:
        pg_cursor.execute("""
            INSERT INTO feedback (session_id, coaching_id, rating, quality_score, useful_aspects, comments, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session_id, coaching_id, rating, quality_score, useful_aspects, comments, timestamp))
        print(f"  ✅ Feedback row inserted: {session_id}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Migrate OUTCOMES
print("\n📥 Migrating outcomes...")
sqlite_cursor.execute("""
    SELECT session_id, contact_name, company_name, negotiation_type, success, 
           target_value, actual_value, target_achieved, actual_achieved, notes, timestamp 
    FROM outcomes
""")
outcome_rows = sqlite_cursor.fetchall()

for row in outcome_rows:
    session_id, contact_name, company_name, negotiation_type, success, target_value, actual_value, target_achieved, actual_achieved, notes, timestamp = row
    try:
        pg_cursor.execute("""
            INSERT INTO outcomes (session_id, contact_name, company_name, negotiation_type, success, 
                                 target_value, actual_value, target_achieved, actual_achieved, notes, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session_id, contact_name, company_name, negotiation_type, success, target_value, actual_value, target_achieved, actual_achieved, notes, timestamp))
        print(f"  ✅ Outcome row inserted: {session_id}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Re-enable foreign key checks
print("\n🔒 Re-enabling foreign key constraints...")
pg_cursor.execute("ALTER TABLE feedback ENABLE TRIGGER ALL")
pg_cursor.execute("ALTER TABLE outcomes ENABLE TRIGGER ALL")

# Commit changes
pg_conn.commit()

print("\n✅ Migration complete!")
print(f"Feedback rows: {len(feedback_rows)}")
print(f"Outcome rows: {len(outcome_rows)}")

sqlite_conn.close()
pg_conn.close()