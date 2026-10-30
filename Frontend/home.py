import streamlit as st
from api_client import APIError, process_video, upload_video,stats
import time
st.title("INTELLIGENT VIDEO SEARCH")
video = st.file_uploader("Upload a video", type=["mp4", "avi"])
if video is not None:
    if st.button("Upload video"):
        try:
            with st.spinner("Uploading video..."):
                result = upload_video(video)
            st.session_state["video_id"] = result["video_id"]
            st.session_state["processing_requested"] = False
            st.success("Video uploaded successfully.")
            st.json(result)
        except APIError as exc:
            st.error(f"Upload failed: {exc.message}")

video_id = st.session_state.get("video_id")
if video_id is not None:
    if st.button("process"):
        try:
            with st.spinner("Processing...."):
                process_video()
                st.session_state['processing_requested'] = True
        except APIError as exc:
            st.error(f"Could not start processing: {exc.message}")
        if st.session_state.get('processing_requested',False):
            status_display = st.empty()
            while True:
                try:
                    status_result = stats()
                    status = status_result.get('status',"")
                    status_display.info(f'video_status:{status}')
                    if status == ['processing']:
                        status_display.info('Processing Video Pls wait....')
                        st.session_state["processing_requested"] = True
                    if status == ["completed"]:
                        status_display.success("video processing completed")
                        st.session_state["processing_requested"] = False
                        break
                    elif status == "failed":
                        status_display.error('video processing failed')
                        st.session_state['processing_requested'] = False
                        break
                    time.sleep(2)
                except APIError as exc:
                    status_display.error(f'could not retrive status:{exc.message}')
                    break
