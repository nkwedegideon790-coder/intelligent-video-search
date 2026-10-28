from __future__ import annotations
from dataclasses import dataclass, field
import sqlite3
import cv2
import supervision as sv
from database import init_db


@dataclass
class TrackingState:
    tracker: sv.ByteTrack = field(default_factory=sv.ByteTrack)
    seen_objects: set[int] = field(default_factory=set)
    enter_time: dict[int, str] = field(default_factory=dict)
    conn: sqlite3.Connection = field(default_factory=init_db)


def _timestamp(frame_count: int, fps: float) -> str:
    sec = max(frame_count / fps, 0)
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"

fps_cache = {}

def _get_fps(cap, video_id) -> float:
    if video_id not in fps_cache:
        fps = cap.get(cv2.CAP_PROP_FPS)
        fps_cache[video_id] = fps if fps and fps > 1 else 30.0  # fallback
    return fps_cache[video_id]


def track_objects_store(detections, class_name, cap, video_id, frame_count, state: TrackingState):
    tracked_detections = state.tracker.update_with_detections(detections)
    timestamp = _timestamp(frame_count, _get_fps(cap, video_id))

    if tracked_detections is not None:
        for bbox, class_id, track_id in zip(
            tracked_detections.xyxy,
            tracked_detections.class_id,
            tracked_detections.tracker_id,
        ):
            object_name = class_name[class_id]
            track_id = int(track_id)
            x1, y1, x2, y2 = bbox.tolist()

            if track_id not in state.seen_objects:
                state.seen_objects.add(track_id)
                state.enter_time[track_id] = timestamp
                state.conn.execute("""
                    INSERT INTO track_logs (
                        track_id, video_id, class_id, object_name, enter_time,
                        last_seen, x1, y1, x2, y2
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track_id,
                    int(video_id),
                    int(class_id),
                    object_name,
                    state.enter_time[track_id],
                    timestamp,
                    x1,
                    y1,
                    x2,
                    y2,
                ))
            else:
                state.conn.execute("""
                    UPDATE track_logs
                    SET last_seen = ?, x1 = ?, y1 = ?, x2 = ?, y2 = ?
                    WHERE video_id = ? AND track_id = ?
                """, (
                    timestamp,
                    x1,
                    y1,
                    x2,
                    y2,
                    int(video_id),
                    track_id,
                ))

    state.conn.commit()
    return tracked_detections, state.enter_time
