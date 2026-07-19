import sqlite3

db_path = "santinel_feedback.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("=== TABLES IN DATABASE ===\n")
    
    if not tables:
        print("No tables found (empty database)")
    else:
        for (table_name,) in tables:
            print(f"\n📊 TABLE: {table_name}")
            print("-" * 50)
            
            # Get schema for this table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                print(f"  {col_name} ({col_type})")
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"\n  Rows: {row_count}")
    
    conn.close()
    print("\n✅ Database check complete")
    
except Exception as e:
    print(f"❌ Error: {e}")