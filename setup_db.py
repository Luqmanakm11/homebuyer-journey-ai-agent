import sqlite3
import json
import os

def create_database():
    print("🏗️ Building local SQL Database (chinhin_erp.db)...")
    
    # 1. Connect to SQLite (This creates the file if it doesn't exist)
    conn = sqlite3.connect('chinhin_erp.db')
    cursor = conn.cursor()

    # 2. Create the Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id TEXT PRIMARY KEY,
        buyer_id TEXT,
        buyer_name TEXT,
        unit_id TEXT,
        current_stage TEXT,
        is_spa_signed INTEGER,
        idsaya_transaction_id TEXT,
        is_spa_stamped INTEGER,
        lhdn_certificate_no TEXT
    )
    ''')

    # 3. Create the Properties Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Properties (
        unit_id TEXT PRIMARY KEY,
        project_name TEXT,
        construction_percentage INTEGER
    )
    ''')

    # 4. Load JSON Data and Insert into SQL Tables
    try:
        if os.path.exists("mock_transactions.json"):
            with open("mock_transactions.json", "r") as f:
                transactions = json.load(f)
                for txn in transactions:
                    # Extract milestones safely
                    m = txn.get("milestones", {})
                    cursor.execute('''
                        INSERT OR REPLACE INTO Transactions 
                        (transaction_id, buyer_id, buyer_name, unit_id, current_stage, 
                        is_spa_signed, idsaya_transaction_id, is_spa_stamped, lhdn_certificate_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        txn["transaction_id"], txn["buyer_id"], txn["buyer_name"], 
                        txn["unit_id"], txn["current_stage"],
                        1 if m.get("is_spa_signed") else 0,
                        m.get("idsaya_transaction_id", ""),
                        1 if m.get("is_spa_stamped") else 0,
                        m.get("lhdn_certificate_no", "")
                    ))
            print("✅ Transactions inserted successfully!")

        if os.path.exists("mock_properties.json"):
            with open("mock_properties.json", "r") as f:
                properties = json.load(f)
                for prop in properties:
                    cursor.execute('''
                        INSERT OR REPLACE INTO Properties (unit_id, project_name, construction_percentage)
                        VALUES (?, ?, ?)
                    ''', (prop["unit_id"], prop["project_name"], prop["construction_percentage"]))
            print("✅ Properties inserted successfully!")

        # Save and close
        conn.commit()
        print("🎉 Database setup complete! You now have a real SQL DB.")

    except Exception as e:
        print(f"⚠️ Error loading data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()