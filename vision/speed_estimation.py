import cv2

# Threshold lines along the Y-axis
LINE1_Y = 200  # Top Line
LINE2_Y = 400  # Bottom Line
REAL_WORLD_DISTANCE = 5  # meters

# Memory to track timestamps, directions, and lines crossed
# Structure: { track_id: {"start_time": float, "start_line": int} }
tracker_history = {}


def estimate_speed(track_id, xyxy, cap):
    """
    Estimates the speed of an object moving either upward or downward.
    
    :param track_id: Unique integer ID of the tracked object
    :param xyxy: Individual bounding box array/list [xmin, ymin, xmax, ymax]
    :param cap: cv2.VideoCapture object
    :return: Tuple (speed_mps, direction) if calculated, else (None, None)
    """
    # 1. Get current video timeline position in seconds
    now = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

    # 2. Calculate the center Y coordinate of the bounding box
    xmin, ymin, xmax, ymax = xyxy
    center_y = ymin + (ymax - ymin) / 2

    # If the object isn't registered yet, check where it enters the tracking zone
    if track_id not in tracker_history:
        # DOWNWARD: Entered past top line but hasn't reached bottom line yet
        if center_y >= LINE1_Y and center_y < LINE2_Y:
            tracker_history[track_id] = {"start_time": now, "start_line": 1}
        # UPWARD: Entered going up past bottom line but hasn't reached top line yet
        elif center_y <= LINE2_Y and center_y > LINE1_Y:
            tracker_history[track_id] = {"start_time": now, "start_line": 2}
        return None, None

    history = tracker_history[track_id]

    # 3. Check for completion of crossing
    # Case A: Object started at Line 1 (Top) and has now crossed Line 2 (Bottom) -> DOWNWARD
    if history["start_line"] == 1 and center_y >= LINE2_Y:
        dt = now - history["start_time"]
        del tracker_history[track_id]  # Clear memory
        if dt > 0:
            speed = REAL_WORLD_DISTANCE / dt
            return speed, "downward"

    # Case B: Object started at Line 2 (Bottom) and has now crossed Line 1 (Top) -> UPWARD
    elif history["start_line"] == 2 and center_y <= LINE1_Y:
        dt = now - history["start_time"]
        del tracker_history[track_id]  # Clear memory
        if dt > 0:
            speed = REAL_WORLD_DISTANCE / dt
            return speed, "upward"

    return None, None
