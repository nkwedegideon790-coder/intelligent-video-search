from collections.abc import Callable

import cv2
import supervision as sv
from ultralytics import YOLO


def process_video(
    video_path: str,
    on_detections: Callable[[sv.Detections, dict[int, str], cv2.VideoCapture, int], None],
    on_progress: Callable[[int], None] | None = None,
) -> None:
    print('initialization')
    model = YOLO("yolov8n.pt")
    class_name = model.names
    
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print('processing')
    FRAME_SKIP = 3
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_progress = -1

    try:
        if not cap.isOpened():
            raise OSError(f"Could not open video: {video_path}")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if on_progress is not None and total_frames > 0:
                progress = min(99, frame_count * 100 // total_frames)
                if progress != last_progress:
                    on_progress(progress)
                    last_progress = progress
            if frame_count % FRAME_SKIP == 0:
                results = model(frame, imgsz=320, verbose=False)[0]
                detections = sv.Detections.from_ultralytics(results)
                on_detections(detections, class_name, cap, frame_count)
    finally:
        cap.release()
