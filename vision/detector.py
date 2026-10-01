from ultralytics import YOLO
import sqlite3
from datetime import datetime
import cv2

# database connection
with sqlite3.connect("video_data.db") as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration TEXT,
            fps TEXT,
        )
    ''')
    conn.commit()

# Active Theard 
conn = sqlite3.connect("video_data.db", check_same_thread=False)
cursor = conn.cursor()

def log_to_database(video_path, duration, fps):
    timestamp = datetime.now()
    cursor.execute('''
        INSERT INTO video_data (video_path, timestamp, duration, fps) VALUES (?, ?, ?, ?)
    ''', (video_path, timestamp, duration, fps))
    conn.commit()

def process_video():
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture("")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_SKIP = 5
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    last_detection = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            results = model(frame)[0]
            


