import sqlite3
conn = sqlite3.connect('fredo.db')
cur = conn.cursor()

try:
    cur.execute('ALTER TABLE shopping_item ADD COLUMN category VARCHAR(50)')
    print('Added: shopping_item.category')
except Exception as e:
    print(f'Skip: {e}')

cur.execute('''CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY,
    action VARCHAR(200) NOT NULL,
    member_id INTEGER,
    created_at DATETIME
)''')
print('OK: activity_log')

cur.execute('''CREATE TABLE IF NOT EXISTS monthly_score (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    points INTEGER DEFAULT 0
)''')
print('OK: monthly_score')

conn.commit()
conn.close()
print('Migration done.')
