import streamlit as st
import time
from api_client import APIError, process_video, upload_video, stats
from vision.database import init_db
from datetime import timezone,datetime
st.set_page_config(page_title="INTELLIGENT VIDEO SEARCH", page_icon="🔎", layout="wide")
st.title("INTELLIGENT VIDEO SEARCH")

upload_col, status_col = st.columns([2, 1])
lastest_frame_col, vid_details_col = st.columns([2, 1])
table_placeholder = st.empty()
conn = init_db()
def get_recent_rows():
    try:
        read_conn = conn
        read_cursor = read_conn.cursor()
        read_cursor.execute(
            "SELECT id,track_id,object_name FROM track_logs ORDER BY id DESC LIMIT 5"
        )
        rows = read_cursor.fetchall()
        read_conn.close()
        return rows
    except conn.Error:
        return []

with upload_col:
    with st.container(border=True):
        st.subheader("Upload video")
        st.caption("Choose a video to search.")
        video = st.file_uploader("Choose a video", type=["mp4", "avi"])
        if video is not None and st.button("Upload video", icon=":material/upload:"):
            try:
                with st.spinner("Uploading video..."):
                    result = upload_video(video)
                    st.session_state["video_id"] = result["video_id"]
                    st.session_state["video_path"] = result["video_path"]
                    st.session_state["filename"] = result["filename"]
                    st.session_state["processing_requested"] = False
                    st.success("Video uploaded successfully.")
                
            except APIError as exc:
                st.error(f"Upload failed: {exc.message}")

with status_col:
    with st.container(border=True):
        st.subheader("Status")
        video_id = st.session_state.get("video_id")
        video_path = st.session_state.get("video_path")
        filename = st.session_state.get('filename')
        now = datetime.now(timezone.utc).isoformat()

        if video_id is not None:
            if st.button("Process video", icon=":material/play_arrow:"):
                try:
                    process_video()
                    st.session_state["processing_requested"] = True
                except APIError as exc:
                    st.error(f"Could not start processing: {exc.message}")
            if st.session_state.get("processing_requested", False):
                status_display = st.empty()
                progress_bar = st.progress(0, text="Starting video processing...")
                try:
                    with st.spinner("Processing video..."):
                        while True:
                            status_result = stats()
                            status = status_result.get("status")
                            progress = max(0, min(100, int(status_result.get("progress", 0))))

                            if status == "completed":
                                progress_bar.progress(100, text="Video processing complete.")
                                status_display.success("Video processing completed.")
                                st.session_state["processing_requested"] = False
                                break
                            if status == "failed":
                                status_display.error("Video processing failed.")
                                st.session_state["processing_requested"] = False
                                break
                            if status not in {"pending", "processing"}:
                                status_display.error(f"Unexpected video status: {status}")
                                st.session_state["processing_requested"] = False
                                break

                            progress_bar.progress(
                                progress,
                                text=f"Processing video: {progress}%",
                            )
                            status_display.info("Video is waiting to be processed." if status == "pending" else f"video {video_id} is been processing.")
                            time.sleep(2)
                        st.caption('processing takes 1-2 mins depending on the size')
                except APIError as exc:
                    status_display.error(f"Could not retrieve status: {exc.message}")
                    st.session_state["processing_requested"] = False
        else:
            st.caption("Upload a video to enable processing.")

with lastest_frame_col:
    with st.container (border=True):
        st.subheader('Lastest video preview')
        live_rows = get_recent_rows()
        while True:
            if live_rows:
                table_data = [
                    {
                        "id": row[1], "track_id": row[2], "object_name": row[3]
                    } for row in live_rows
                ]
                table_placeholder.table(table_data)
            time.sleep(2)

with vid_details_col:
    with st.container(border=True):
        if video is not None:
            st.subheader('video details')
            st.caption(f'video_id : {video_id}')
            st.caption(f'Filepath : {video_path}')
            st.caption(f'Filename: {filename}')
            st.caption(f'Uploaded at: {now}')

        
