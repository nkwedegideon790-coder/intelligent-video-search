import supervision as sv
tracker = sv.ByteTrack()

def track_objects(detections):
    tracked_detections = tracker.update_with_detections(detections)

    if tracked_detections is not None:
        track_ids = tracked_detections.tracker_ids.tolist()
        return tracked_detections, track_ids