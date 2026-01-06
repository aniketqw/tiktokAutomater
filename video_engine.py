import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def create_video(audio_path, script_text=""):
    """
    Assembles the final TikTok video by combining a background, 
    audio, and optional text overlay.
    """
    # 1. Select a random background from the assets folder
    bg_folder = "./assets/backgrounds"
    if not os.path.exists(bg_folder) or not os.listdir(bg_folder):
        raise FileNotFoundError(f"No background videos found in {bg_folder}")
    
    bg_file = random.choice([f for f in os.listdir(bg_folder) if f.endswith(('.mp4', '.mov'))])
    video_path = os.path.join(bg_folder, bg_file)
    
    # 2. Load Assets
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # 3. Process Video
    # Ensure the background is at least as long as the audio; loop if necessary
    if video.duration < audio.duration:
        video = video.loop(duration=audio.duration)
    else:
        # Start at a random point in the video if it's longer than the audio
        start_time = random.uniform(0, video.duration - audio.duration)
        video = video.subclip(start_time, start_time + audio.duration)
    
    # Resize to TikTok's vertical aspect ratio (1080x1920)
    video = video.resize(height=1920).crop(x_center=video.w/2, width=1080)
    
    # 4. Add Text Overlay (Captions)
    # Note: Requires ImageMagick to be installed on the GitHub Action runner
    final_clips = [video.set_audio(audio)]
    
    if script_text:
        txt_clip = TextClip(
            script_text,
            fontsize=70,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(video.w * 0.8, None)
        ).set_duration(audio.duration).set_position('center')
        final_clips.append(txt_clip)
    
    # 5. Composite and Render
    final_video = CompositeVideoClip(final_clips)
    output_filename = "final_tiktok_post.mp4"
    
    # Optimization for fast rendering on GitHub Actions
    final_video.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )
    
    return output_filename
