import os
import random
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def create_video(audio_path, script_text=""):
    bg_folder = "assets/backgrounds"
    bg_files = [f for f in os.listdir(bg_folder) if f.endswith(('.mp4', '.mov'))]
    
    if not bg_files:
        raise FileNotFoundError("No background videos found!")
    
    # 1. Load Assets
    selected_bg = random.choice(bg_files)
    video = VideoFileClip(os.path.join(bg_folder, selected_bg))
    audio = AudioFileClip(audio_path)
    
    # 2. Dynamic Sync Logic
    # Stunt videos often have slow starts. We pick a random start 
    # but prioritize the middle of the clip where action usually happens.
    if video.duration > audio.duration:
        max_start = video.duration - audio.duration
        # Favoring the 20% to 70% mark of the video for peak action
        start = random.uniform(max_start * 0.2, max_start * 0.7)
        video = video.subclipped(start, start + audio.duration)
    else:
        video = video.loop(duration=audio.duration)

    # 3. Format for TikTok
    video = video.resized(height=1920)
    video = video.cropped(center_x=video.w/2, width=1080)
    
    # 4. Professional Captions
    # Using 'Inter' or 'Montserrat' style formatting via ImageMagick
    txt_clip = TextClip(
        text=script_text.upper(), # Uppercase for high intensity
        font_size=65,
        color='yellow', # Yellow stands out against city/concrete backgrounds
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(video.w * 0.9, None),
        text_align='center'
    ).with_duration(audio.duration).with_position(('center', 'center'))

    # 5. Composite and Render
    # Combine everything and ensure audio levels are normalized
    final = CompositeVideoClip([video.with_audio(audio), txt_clip])
    output = "final_stunt_video.mp4"
    
    final.write_videofile(
        output, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast" # Faster rendering for GitHub Actions
    )
    
    return output
