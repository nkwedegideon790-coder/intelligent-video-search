import cv2
import supervision as sv
from ultralytics import YOLO
from database import init_db

conn = init_db()
cursor = conn.cursor()

def Video_logs(video_path: str, duration: float, fps: float) -> int:
    """
    Registers the video in the database and returns the generated video_id.
    """
    cursor.execute('''
        INSERT INTO video_data (video_path, duration, fps) 
        VALUES (?, ?, ?)
    ''', (video_path, duration, fps))
    video_id = cursor.lastrowid
    conn.commit()
    return video_id

def process_video(video_path: str = 'traffic.mp4'):
    print('initialization')
    model = YOLO("yolov8n.pt")
    class_name = model.names
    
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Metadata extraction for video registration
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # Fallback to 30 if metadata read fails
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps if fps > 0 else 0
    
    # Register the video first to get the video_id
    video_id = Video_logs(video_path, duration, fps)
    
    print('processing')
    FRAME_SKIP = 3
    frame_count = 0
    detections = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            results = model(frame, imgsz=320, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)
            
            # Timestamp calculation
            msec = cap.get(cv2.CAP_PROP_POS_MSEC)
            sec = msec / 1000.0
            minutes = int(sec // 60)
            seconds = int(sec % 60)
            timestamp = f'{minutes:02d}:{seconds:02d}'
            
            # Optional: You can now use `video_id` inside this loop 
            # to insert detection logs or frame data tied to this video.

    cap.release()
    return model, class_name, cap, detections, frame_count
