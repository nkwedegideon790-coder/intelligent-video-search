from detector import process_video
from track import TrackingState, track_objects_store



def process_and_track_video(video_path,video_id):
    state = TrackingState()

    def track_frame(detections, class_name, cap, frame_count):
        track_objects_store(
            detections,
            class_name,
            cap,
            video_id,
            frame_count,
            state,
        )

    try:
        process_video(video_path, track_frame)
    finally:
        state.conn.close()
    