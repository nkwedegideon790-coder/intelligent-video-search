import cv2
from vision.database import init_db

db_conn = init_db()
def log_to_database(timestamp, video_id, track_id, object_name, kmh):
    cursor = db_conn.cursor()
    cursor.execute('''
        INSERT INTO speed_Event (timestamp, video_id, track_id, object_name, kmh) VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, video_id, track_id, object_name, kmh))
    db_conn.commit()
# Threshold lines along the Y-axis
LINE1_Y = 200  # Top Line
LINE2_Y = 400  # Bottom Line
REAL_WORLD_DISTANCE = 5  # meters

# Memory to track timestamps, directions, and lines crossed
# Structure: { track_id: {"start_time": float, "start_line": int} }
tracker_history = {}


def estimate_speed(track_id, xyxy, cap,object_name, video_id):
    """
    Estimates the speed of an object moving either upward or downward.
    
    :param track_id: Unique integer ID of the tracked object
    :param xyxy: Individual bounding box array/list [xmin, ymin, xmax, ymax]
    :param cap: cv2.VideoCapture object
    :return: Tuple (speed_mps, direction) if calculated, else (None, None)
    """
    # 1. Get current video timeline position in seconds
    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    kmh = None  # Initialize speed variable
    direction = None  # Initialize direction variable
    
    # 2. Calculate the center Y coordinate of the bounding box
    xmin, ymin, xmax, ymax = xyxy
    center_y = ymin + (ymax - ymin) / 2

    # If the object isn't registered yet, check where it enters the tracking zone
    if track_id not in tracker_history:
        # # DOWNWARD: Entered past top line but hasn't reached bottom line yet
        # if previous_y < LINE1_Y and center_y >= LINE1_Y:
        tracker_history[track_id] = {"start_time": None, "start_line": None, "previous_y": center_y}
    
    history = tracker_history[track_id]
    previous_y =history["previous_y"]
    if history["start_line"] is None:
        if previous_y > LINE2_Y and center_y <= LINE2_Y:
            history["start_time"] = timestamp
            history["start_line"] = 2
        elif previous_y < LINE1_Y and center_y >= LINE1_Y:
            history["start_time"] = timestamp
            history["start_line"] = 1
    history["previous_y"] = center_y  # Update previous Y for next frame
    # 3. Check for completion of crossing
    # Case A: Object started at Line 1 (Top) and has now crossed Line 2 (Bottom) -> DOWNWARD
    if history["start_line"] == 1 and previous_y < LINE2_Y  >= center_y:
        if history["start_time"] is not None:
            dt = timestamp - history["start_time"]
            if dt > 0:
                speed = REAL_WORLD_DISTANCE / dt
                kmh = speed * 3.6
                direction = "DOWNWARD"            
        if track_id in tracker_history:
            del tracker_history[track_id]  # Clear memory
    # Case B: Object started at Line 2 (Bottom) and has now crossed Line 1 (Top) -> UPWARD
    elif history["start_line"] == 2 and previous_y > LINE1_Y  >= center_y:
        if history["start_time"] is not None:
            dt = timestamp - history["start_time"]
            if dt > 0:
                speed = REAL_WORLD_DISTANCE / dt
                kmh = speed * 3.6
                direction = "UPWARD"
        if track_id in tracker_history:
            del tracker_history[track_id]  # Clear memory

    
    
    if kmh is not None : 
        if kmh >= 30:  # Speed threshold in km/h
            object_name = object_name
            log_to_database(timestamp, video_id, track_id, object_name, kmh)

    return kmh, direction
