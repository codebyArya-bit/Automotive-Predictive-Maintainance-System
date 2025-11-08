import sqlite3

# Check both database files
for db_name in ["automotive_data.db", "automotive_ai.db"]:
    print(f"\n=== Checking {db_name} ===")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Available tables:", [t[0] for t in tables])

        # Check if maintenance_records table exists and its structure
        if "maintenance_records" in [t[0] for t in tables]:
            cursor.execute("PRAGMA table_info(maintenance_records)")
            columns = cursor.fetchall()
            print("\nMaintenance records table structure:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")

            # Check if there are any records
            cursor.execute("SELECT COUNT(*) FROM maintenance_records")
            count = cursor.fetchone()[0]
            print(f"\nMaintenance records count: {count}")
        else:
            print("\nMaintenance records table does not exist")

        conn.close()
    except Exception as e:
        print(f"Error accessing {db_name}: {e}")
