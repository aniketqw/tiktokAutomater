import os
import asyncio
import edge_tts
import datetime
import glob
from google import genai
from video_engine import create_video
from youtube_up.uploader import YTUploaderApp 

# 1. Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_voiceover(text, output_path):
    """Free high-quality speech using Microsoft Edge TTS."""
    voice = "en-US-AvaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def cleanup_old_videos(days_to_keep=7):
    """Deletes videos older than the specified days."""
    now = datetime.datetime.now()
    for file in glob.glob("short_*.mp4"):
        file_time = datetime.datetime.fromtimestamp(os.path.getctime(file))
        if (now - file_time).days > days_to_keep:
            os.remove(file)

def update_index_html(video_file, timestamp, script_text):
    """Appends the new video entry to your dashboard gallery."""
    html_file = "index.html"
    if not os.path.exists(html_file):
        with open(html_file, "w") as f:
            f.write("<html><head><title>Archive</title><style>body{font-family:sans-serif;background:#121212;color:white;padding:20px;}.video-card{background:#1e1e1e;padding:15px;margin-bottom:20px;border-radius:10px;border:1px solid #333;}video{border-radius:5px;max-width:100%;}a{color:#ff0000;text-decoration:none;font-weight:bold;}</style></head><body><h1>🎥 YouTube Shorts Archive</h1><div id='gallery'>")

    entry = f"""
    <div class="video-card">
        <h3>📅 Generated: {timestamp}</h3>
        <p>"{script_text[:100]}..."</p>
        <video width="280" height="500" controls>
          <source src="{video_file}" type="video/mp4">
        </video>
        <br><br>
        <a href="{video_file}" download>💾 Download Short</a>
    </div>
    """
    with open(html_file, "r") as f:
        content = f.read()
    
    if "<div id='gallery'>" in content:
        new_content = content.replace("<div id='gallery'>", f"<div id='gallery'>{entry}")
        with open(html_file, "w") as f:
            f.write(new_content)

async def run_automation():
    cleanup_old_videos(days_to_keep=7)

    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = f"short_{timestamp_str}.mp4"

    print(f"🎬 Generating Script...")
    prompt = "Write a 25-30 second viral YouTube Shorts script about an Insane Fact. Output spoken text ONLY."
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    script_text = response.text

    print("🎙️ Generating Audio...")
    audio_path = "temp_voice.mp3"
    await generate_voiceover(script_text, audio_path)

    print("🎞️ Assembling Video...")
    temp_path = create_video(audio_path, script_text=script_text)
    os.rename(temp_path, video_filename)

    print("📄 Updating Archive...")
    update_index_html(video_filename, timestamp_str, script_text)

    print("🚀 Uploading to YouTube...")
    try:
        # Uses the youtube_cookies.json created by the Action
        uploader = YTUploaderApp(cookie_bundle='youtube_cookies.json')
        uploader.upload(
            video_filename,
            title=f"Did you know? 🤯 #Shorts",
            description=f"{script_text}\n\n#stunts #facts #shorts",
            public=True
        )
        print(f"✅ Success! Posted: {video_filename}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_automation())
