import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'fredo.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

migrations = [
    ('ALTER TABLE shopping_item ADD COLUMN category VARCHAR(50)', 'shopping_item.category'),
    ('ALTER TABLE note ADD COLUMN archived BOOLEAN DEFAULT 0', 'note.archived'),
    ('ALTER TABLE event ADD COLUMN recurrence VARCHAR(10)', 'event.recurrence'),
    ('ALTER TABLE event ADD COLUMN recurrence_end DATETIME', 'event.recurrence_end'),
    ('ALTER TABLE event ADD COLUMN parent_id INTEGER', 'event.parent_id'),
]

for sql, name in migrations:
    try:
        cur.execute(sql)
        print(f'Added: {name}')
    except Exception as e:
        print(f'Skip {name}: {e}')

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
