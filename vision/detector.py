from ultralytics import YOLO
import supervision as sv
from database import init_db
import cv2


conn = init_db()
cursor = conn.cursor()
def process_video():
    model = YOLO("yolov8n.pt")
    video_path = 'uploaded_files/'
    class_name = model.names
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_SKIP = 3
    frame_count = 0
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            results = model(frame, imgsz=320, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)
            fps = cap.get(cv2.CAP_PROP_FPS)
            msec = cap.get(cv2.CAP_PROP_POS_MSEC)
            sec = msec/1000.0
            minutes = int(sec//60)
            seconds = int(sec % 60)
            timestamp = f'{minutes:02d}:{seconds:02d}'
        else:
            continue

    duration = total_frames/fps
  

        # current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

    cap.release()
    cursor.execute('''
            INSERT INTO video_data (video_path, timestamp, duration, fps) VALUES (?, ?, ?, ?)
        ''', (video_path, timestamp, duration, fps))
    video_id = cursor.lastrowid
    conn.commit()
    return video_path, duration, fps,model,video_id,class_name,cap


            

            


