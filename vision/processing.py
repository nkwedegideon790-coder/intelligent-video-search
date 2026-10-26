from detector import process_video
from track import track_objects_store
from database import init_db
# import requests
# import os
# from typing import Any, Optional


# class APIError(Exception):
#     def __init__(self, message: str, code: str | None = None, status: int | None = None):
#         super().__init__(message)
#         self.message, self.code, self.status = message, code, status


# def _secret(name: str, default: str = "") -> str:
#     value = os.getenv(name)
#     if value:
#         return value
#     try:
#         import streamlit as st
#         return str(st.secrets.get(name, default))
#     except Exception:
#         return default

# def base_url() -> str:
#     return _secret("INTELLIGENT_VIDEO_SEARCH_API_URL", "http://localhost:8000/docs").rstrip("/")


# def _request(method: str, path: str, *, timeout: float = 20, **kwargs: Any) -> Any:
#     try:
#         resp = requests.request(method, base_url() + path, timeout=timeout, **kwargs)
#     except requests.exceptions.Timeout as exc:
#         raise APIError("The request took too long. Please try again.", "timeout") from exc
#     except requests.exceptions.RequestException as exc:
#         raise APIError("We can't reach the ScamLens service right now. Check that the backend is running.",
#                        "unreachable") from exc
#     if resp.status_code >= 400:
#         try:
#             body = resp.json()
#             raise APIError(body.get("detail") or "Something went wrong.", body.get("code"), resp.status_code)
#         except ValueError:
#             raise APIError("Something went wrong. Please try again.", None, resp.status_code)
#     try:
#         return resp.json()
#     except ValueError as exc:
#         raise APIError("The service returned an unreadable response.", None, resp.status_code) from exc

# def get_video_path(video_id: int, video_path: str):
#     return _request(
#         "POST", 
#         "/upload_file", 
#         timeout=90, 
#         json={"video_id": video_id, "video_path": video_path}
#     )


def process_and_track_video(video_id,video_path):
    # unpack all values returned
    (
     model,
     class_name,
     cap,
     detections,
     frame_count


            ) = process_video(video_path)
    track_objects_store(detections,
                        class_name,
                        cap,
                        video_id,
                        frame_count)
if __name__ == "__main__":
    process_and_track_video()
    print("processing complete")