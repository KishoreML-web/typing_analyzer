import sqlite3

DATABASE = 'typing_analyzer.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                raw_text TEXT NOT NULL,
                mood TEXT,
                avg_speed REAL,
                total_pauses INTEGER,
                total_backspaces INTEGER,
                burst_percentage REAL,
                total_words INTEGER,
                duration_seconds REAL
            )
        ''')
        conn.commit()
    print(f"Database '{DATABASE}' initialized successfully.")


def save_session(raw_text, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words, duration_seconds):
    """Insert a new typing session into DB"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions 
            (raw_text, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (raw_text, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words, duration_seconds))
        conn.commit()


def fetch_sessions(limit=10):
    """Fetch last N typing sessions"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words 
            FROM sessions ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return rows


if __name__ == '__main__':
    init_db()
