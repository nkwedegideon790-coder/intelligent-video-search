# uvicorn app:app --reload
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi import APIRouter, UploadFile
from database import init_db
from processing import process_and_track_video
import os
import cv2

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}


conn = init_db()
cursor = conn.cursor()

def Video_logs(video_path: str, duration: float, fps: float) -> int:
    """
    Registers the video in the database and returns the generated video_id.
    """
    cursor.execute('''
        INSERT INTO video_data (video_path, duration, fps) 
        VALUES (?, ?, ?)
    ''', (video_path, duration, fps))
    video_id = cursor.lastrowid
    conn.commit()
    return video_id,duration,fps
@app.post("/upload_video")
async def upload_file(file: UploadFile, limit: int):
    save_Dir = "uploaded_files"
    # creats the directory if it does not exist
    if not os.path.exists(save_Dir):
        os.makedirs(save_Dir)
    video_path = os.path.join(save_Dir, file.filename)
    with open(video_path, "wb") as f:
        content = await file.read()
        f.write(content)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # Fallback to 30 if metadata read fails
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps if fps > 0 else 0


    video_id = Video_logs(video_path, duration, fps)
    return video_id,duration,fps,video_path


@app.post("/videos/{video_id}/process")
async def process_video_endpoint(video_id: int, background_tasks: BackgroundTasks):
    # Connect to your database
    conn = init_db()
    cursor = conn.cursor()
    
    # Retrieve the corresponding video record from video_data
    cursor.execute(
        "SELECT video_path FROM video_data WHERE id = ?", 
        (video_id,)
    )
    video_record = cursor.fetchone()
    
    # Always close database resources when done reading
    cursor.close()
    conn.close()
    
    # If the ID doesn't exist, return a not-found response
    if not video_record:
        raise HTTPException(
            status_code=404, 
            detail=f"Video with ID {video_id} not found"
        )
        
    # Extract the file path string from the query result
    video_path = video_record[0]
    
    # If the video exists, pass its saved path and ID to your processing workflow.
    # We use FastAPI's BackgroundTasks so the client doesn't time out while YOLO runs.
    background_tasks.add_task(process_and_track_video(video_id,video_path), video_path=video_path, video_id=video_id)
    
    return {
        "message": "Video processing has started in the background",
        "video_id": video_id,
        "video_path": video_path
    }



    

