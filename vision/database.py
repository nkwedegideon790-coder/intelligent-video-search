import sqlite3
from datetime import datetime

def init_db(db_name="intelligent_video_search.db"):
    """Creates a local SQLite database and tracking table if they don't exist."""
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS video_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            fps REAL
        )
    ''')
    conn.execute("""
            CREATE TABLE IF NOT EXISTS track_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                video_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES video_data(id) ON DELETE CASCADE,
                class_id INTEGER,
                object_name TEXT,
                enter_time  DATETIME,
                x1 REAL, y1 REAL, x2 REAL, y2 REAL
            )
        """)
    conn.execute("""
            CREATE TABLE IF NOT EXISTS speed_Event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                video_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES video_data(id) ON DELETE CASCADE,
                track_id INTEGER,
                object_name TEXT,
                kmh REAL
            )
""")
    conn.commit()
    return conn


# def Video_logs(conn,video_path, duration, fps):
#     timestamp = datetime.now()
#     conn.execute('''
#         INSERT INTO video_data (video_path, timestamp, duration, fps) VALUES (?, ?, ?, ?)
#     ''', (video_path, timestamp, duration, fps))
#     conn.commit()