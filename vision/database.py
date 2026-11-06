import sqlite3
from datetime import datetime

def init_db(db_name="intelligent_video_search.db"):
    """Creates a local SQLite database and tracking table if they don't exist."""
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS video_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Filename TEXT NOT NULL,
            video_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration TEXT,
            fps TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            progress INTEGER NOT NULL DEFAULT 0
        )
    ''')
    video_data_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(video_data)")
    }
    if "progress" not in video_data_columns:
        conn.execute(
            "ALTER TABLE video_data ADD COLUMN progress INTEGER NOT NULL DEFAULT 0"
        )
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
            CREATE TABLE IF NOT EXISTS track_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                video_id INTEGER,
                class_id REAL,
                object_name TEXT,
                enter_time DATETIME,
                last_seen  DATETIME,
                x1 REAL, y1 REAL, x2 REAL, y2 REAL
            )
        """)
    track_log_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(track_logs)")
    }
    if "last_seen" not in track_log_columns:
        conn.execute("ALTER TABLE track_logs ADD COLUMN last_seen DATETIME")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
            CREATE TABLE IF NOT EXISTS speed_Event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                video_id INTEGER,
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