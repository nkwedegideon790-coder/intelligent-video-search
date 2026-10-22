from detector import process_video
from track import track_objects_store



def process_and_track_video():
    # unpack all values returned
    (video_path,
     duration,
     fps,
     model,
     video_id,
     class_name,
     cap,
     detections


            ) = process_video()
    track_objects_store(detections,
                        class_name,
                        cap,
                        video_id)
    return{
        "duration":duration,
        "Fps":fps
    }
if __name__ == "__main__":
    process_and_track_video()
    print("processing complete")