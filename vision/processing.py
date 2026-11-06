from detector import process_video
from track import TrackingState, track_objects_store
from database import init_db


conn = init_db
status_state = {
    "status": "processing"
}


def _update_status(video_id, **kwargs):
    conn = init_db()
    try:
        updates = ", ".join(f"{key} = ?" for key in kwargs)
        values = list(kwargs.values()) + [video_id]
        conn.execute(f"UPDATE video_data SET {updates} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()



def process_and_track_video(video_path, video_id):
    state = None
    try:
        _update_status(video_id, status="processing", progress=0)
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

        process_video(
            video_path,
            track_frame,
            lambda progress: _update_status(video_id, progress=progress),
        )
    except Exception:
        _update_status(video_id, status="failed")
        raise
    finally:
        if state is not None:
            state.conn.close()

    _update_status(video_id, status="completed", progress=100)
