from datetime import datetime, timezone

import streamlit as st

from Frontend.api_client import APIError, process_video, stats, tracklogs, upload_video


@st.fragment(run_every="2s")
def _show_video_status(video_id: int) -> None:
    if not st.session_state.get("processing_requested", False):
        status = st.session_state.get("video_status", "pending")
        if status == "completed":
            st.success("Video processing completed.")
        elif status == "failed":
            st.error("Video processing failed.")
        else:
            st.caption("Video is waiting to be processed.")
        return

    try:
        result = stats(video_id)
    except APIError as exc:
        st.error(f"Could not retrieve status: {exc.message}")
        return

    status = result.get("status")
    progress = max(0, min(100, int(result.get("progress", 0))))
    st.session_state["video_status"] = status

    if status == "completed":
        st.success("Video processing completed.")
        st.session_state["processing_requested"] = False
    elif status == "failed":
        st.error("Video processing failed.")
        st.session_state["processing_requested"] = False
    elif status == "processing":
        st.progress(progress, text=f"Processing video: {progress}%")
        st.session_state["processing_requested"] = True
    elif status == "pending":
        st.caption("Video is waiting to be processed.")
    else:
        st.error(f"Unexpected video status: {status}")
        st.session_state["processing_requested"] = False


@st.fragment(run_every="2s")
def _show_track_logs() -> None:
    try:
        result = tracklogs()
    except APIError as exc:
        st.error(f"Could not retrieve track logs: {exc.message}")
        return

    tracks = result.get("tracks", [])
    if tracks:
        st.dataframe(
            [
                {
                    "ID": row[0],
                    "Track ID": row[1],
                    "Video ID": row[2],
                    "Object": row[3],
                    "Entered": row[4],
                    "Last seen": row[5],
                }
                for row in tracks
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No tracked objects yet.")


def render() -> None:
    st.title("INTELLIGENT VIDEO SEARCH")
    upload_col, status_col = st.columns([2, 1])
    tracks_col, details_col = st.columns([2, 1])

    with upload_col:
        with st.container(border=True):
            st.subheader("Upload video")
            st.caption("Choose a video to search.")
            video = st.file_uploader("Choose a video", type=["mp4", "avi"])
            if video is not None and st.button(
                "Upload video", icon=":material/upload:"
            ):
                try:
                    with st.spinner("Uploading video..."):
                        result = upload_video(video)
                    st.session_state["video_id"] = result["video_id"]
                    st.session_state["video_path"] = result["video_path"]
                    st.session_state["filename"] = result["filename"]
                    st.session_state["uploaded_at"] = datetime.now(
                        timezone.utc
                    ).isoformat(timespec="seconds")
                    st.session_state["processing_requested"] = False
                    st.session_state["video_status"] = "pending"
                    st.success("Video uploaded successfully.")
                except APIError as exc:
                    st.error(f"Upload failed: {exc.message}")

    video_id = st.session_state.get("video_id")
    with status_col:
        with st.container(border=True):
            st.subheader("Status")
            if video_id is None:
                st.caption("Upload a video to enable processing.")
            else:
                if st.button(
                    "Process video",
                    icon=":material/play_arrow:",
                    disabled=st.session_state.get("processing_requested", False),
                ):
                    try:
                        process_video(video_id)
                        st.session_state["processing_requested"] = True
                        st.session_state["video_status"] = "processing"
                    except APIError as exc:
                        st.error(f"Could not start processing: {exc.message}")
                _show_video_status(video_id)

    with tracks_col:
        with st.container(border=True):
            st.subheader("Recent tracked objects")
            _show_track_logs()

    with details_col:
        with st.container(border=True):
            if video_id is not None:
                st.subheader("Video details")
                st.caption(f"Video ID: {video_id}")
                st.caption(f"Filepath: {st.session_state.get('video_path', '')}")
                st.caption(f"Filename: {st.session_state.get('filename', '')}")
                st.caption(f"Uploaded at: {st.session_state.get('uploaded_at', '')}")
