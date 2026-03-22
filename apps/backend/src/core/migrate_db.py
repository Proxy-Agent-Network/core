import sqlite3

def upgrade_database():
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()

    print("Checking for Marketplace table...")
    
    # Create the marketplace_bids table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marketplace_bids (
            bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id TEXT NOT NULL,
            sats_offered INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Optional: Add a sample bid so the page isn't empty
    cursor.execute("SELECT COUNT(*) FROM marketplace_bids")
    if cursor.fetchone()[0] == 0:
        print("Inserting sample bids...")
        sample_bids = [
            ('USER_ALICE', 500, 'Web Scraping', 'PENDING'),
            ('USER_BOB', 1200, 'Data Validation', 'PENDING'),
            ('USER_CHARLIE', 250, 'Ping Test', 'PENDING')
        ]
        cursor.executemany(
            'INSERT INTO marketplace_bids (requester_id, sats_offered, task_type, status) VALUES (?, ?, ?, ?)',
            sample_bids
        )

    conn.commit()
    conn.close()
    print("✅ Database upgraded successfully with Marketplace support.")

if __name__ == "__main__":
    upgrade_database()