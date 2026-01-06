import os
import asyncio
import edge_tts
import datetime
import glob
from google import genai
from video_engine import create_video
from tiktok_uploader.upload import upload_video

# 1. Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_voiceover(text, output_path):
    """Free high-quality speech using Microsoft Edge TTS."""
    voice = "en-US-AvaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def cleanup_old_videos(days_to_keep=7):
    """Deletes videos older than the specified days to save GitHub storage."""
    print(f"🧹 Cleaning up videos older than {days_to_keep} days...")
    now = datetime.datetime.now()
    # Look for all video_*.mp4 files
    for file in glob.glob("video_*.mp4"):
        file_time = datetime.datetime.fromtimestamp(os.path.getctime(file))
        if (now - file_time).days > days_to_keep:
            os.remove(file)
            print(f"🗑️ Deleted: {file}")

def update_index_html(video_file, timestamp, script_text):
    """Appends the new video entry to the dashboard."""
    html_file = "index.html"
    
    # Create basic HTML structure if it doesn't exist
    if not os.path.exists(html_file):
        with open(html_file, "w") as f:
            f.write("<html><head><title>TikTok Bot Archive</title><style>body{font-family:sans-serif;background:#121212;color:white;padding:20px;}.video-card{background:#1e1e1e;padding:15px;margin-bottom:20px;border-radius:10px;border:1px solid #333;}video{border-radius:5px;max-width:100%;}a{color:#00f2ea;text-decoration:none;font-weight:bold;}</style></head><body><h1>🎥 Video Archive</h1><div id='gallery'>")

    # Entry to append
    entry = f"""
    <div class="video-card">
        <h3>📅 Generated: {timestamp}</h3>
        <p>"{script_text[:100]}..."</p>
        <video width="280" height="500" controls>
          <source src="{video_file}" type="video/mp4">
        </video>
        <br><br>
        <a href="{video_file}" download>💾 Download Video</a>
    </div>
    """
    
    with open(html_file, "r") as f:
        content = f.read()
    
    # Insert new entry at the TOP of the gallery for better UX
    if "<div id='gallery'>" in content:
        new_content = content.replace("<div id='gallery'>", f"<div id='gallery'>{entry}")
        with open(html_file, "w") as f:
            f.write(new_content)

async def run_automation():
    # 0. Cleanup storage before starting
    cleanup_old_videos(days_to_keep=7)

    # Generate Timestamp for unique filenames
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = f"video_{timestamp_str}.mp4"

    print(f"🎬 Step 1: Generating Script for {timestamp_str}...")
    prompt = """
    Write a 25-30 second viral TikTok script about a 'Mind-Blowing Fact'.
    STYLE: High energy, punchy. CONTEXT: Plays over stunt footage.
    Output spoken text ONLY. No emojis or stage directions.
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    script_text = response.text

    print("🎙️ Step 2: Generating Audio...")
    audio_path = "temp_voice.mp3"
    await generate_voiceover(script_text, audio_path)

    print("🎞️ Step 3: Assembling Stunt Video...")
    # Generate the video
    temp_path = create_video(audio_path, script_text=script_text)
    # Move to timestamped filename
    os.rename(temp_path, video_filename)

    print("📄 Step 4: Updating Index Dashboard...")
    update_index_html(video_filename, timestamp_str, script_text)

    print("📱 Step 5: Posting to TikTok...")
    try:
        # Using the Selenium-based tiktok-uploader settings
        upload_video(
            video_filename,
            description=f"Wait for the end! 🤯 #stunts #facts #ai",
            cookies='cookies.txt',
            browser='chrome',
            headless=True
        )
        print(f"✅ Success! Video posted and saved as {video_filename}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_automation())
