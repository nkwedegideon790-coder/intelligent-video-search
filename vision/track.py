import cv2
import supervision as sv
import sqlite3
import datetime as datetime
from database import init_db
tracker = sv.ByteTrack()
seen_objects = set()
enter_time = {}
# last_seen ={}
# exit_timeout = 10
conn = init_db()

def track_objects_store(detections,class_name,db_conn,cap,video_id):
    global seen_objects
    tracked_detections = tracker.update_with_detections(detections)
    # current_ids = set([track_id for _,_,_,_, track_id in tracked_detections])
    msec = cap.get(cv2.CAP_PROP_POS_MSEC)
    sec = msec/1000.0
    minutes = int(sec//60)
    seconds = int(sec % 60)
    timestamp = f'{minutes:02d}:{seconds:02d}'
    
    if tracked_detections is not None:
        labels=[]
        # current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        for bbox,class_id, track_id in zip(tracked_detections.xyxy,tracked_detections.class_id,tracked_detections.tracker_id):
            object_name = class_name[class_id]
            track_id = int(track_id)  # Ensure track_id is an integer
            x1, y1, x2, y2 = bbox.tolist()
            

            if track_id not in seen_objects:
                seen_objects.add(track_id)
                enter_time[track_id] = timestamp
                conn.execute("""
                         INSERT INTO track_logs 
                         (track_id,video_id, class_id, object_name,enter_time, x1, y1, x2, y2)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                     """, (int(track_id), int(video_id), int(class_id), object_name, enter_time[track_id], x1, y1, x2, y2))
            
           
        db_conn.commit()
        return tracked_detections,enter_time,object_name


 # for track_id in current_ids:
            #     if track_id not in seen_objects:
            #         enter_time[track_id] = timestamp
            #         seen_objects.add(track_id)
            #         last_seen[track_id]

            # for track_id in list(seen_objects):
            #     if current_frame - last_seen.get(track_id,0) > exit_timeout:
            #         duration = timestamp - enter_time.get(track_id,timestamp)
            #         cursor.execute("""
            #             INSERT INTO track_logs 
            #             (track_id, class_id, object_name,enter_time, last_seen, duration x1, y1, x2, y2)
            #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            #         """, (int(track_id), int(class_id), object_name, int(enter_time), int(last_seen),int(duration), x1, y1, x2, y2))
            
