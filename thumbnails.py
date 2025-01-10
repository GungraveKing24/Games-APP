from moviepy.video.io.VideoFileClip import VideoFileClip
import os

THUMBNAIL_PATH = "static/thumbnails"

def get_thumbnail(video_path, video_name):
    
    thumbnail_file = os.path.join(THUMBNAIL_PATH, f"{video_name}.jpg")
    thumbnail_file = thumbnail_file.replace("\\", "/")   # Asegúrate de usar barras normales
    if not os.path.exists(thumbnail_file):
        try:
            clip = VideoFileClip(video_path)
            clip.save_frame(thumbnail_file, t=1)
            clip.close
        except Exception as e:
            print(f"Error generando miniatura para {video_path}: {e}")
    
    return thumbnail_file