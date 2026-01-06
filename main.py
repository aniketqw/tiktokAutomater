import os
import asyncio
import edge_tts
import datetime
import glob
from google import genai
from video_engine import create_video
from youtube_up.uploader import YTUploaderApp 

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_voiceover(text, output_path):
    """Generates high-quality voiceover for free."""
    voice = "en-US-AvaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def update_index_html(video_file, timestamp, script_text):
    """Updates the dashboard to fix the 404 error."""
    html_file = "index.html"
    if not os.path.exists(html_file):
        with open(html_file, "w") as f:
            f.write("<html><head><title>Shorts Archive</title><style>body{font-family:sans-serif;background:#121212;color:white;padding:20px;}.video-card{background:#1e1e1e;padding:15px;margin-bottom:20px;border-radius:10px;border:1px solid #333;}video{border-radius:5px;max-width:100%;}a{color:#ff0000;text-decoration:none;font-weight:bold;}</style></head><body><h1>🎥 YouTube Shorts Archive</h1><div id='gallery'>")

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
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = f"short_{timestamp_str}.mp4"

    print(f"🎬 Step 1: Generating Script...")
    prompt = "Write a 25-second viral YouTube Shorts script about an Insane Fact. High energy. Output spoken text ONLY."
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    script_text = response.text

    print("🎙️ Step 2: Generating Audio...")
    audio_path = "temp_voice.mp3"
    await generate_voiceover(script_text, audio_path)

    print("🎞️ Step 3: Assembling Video...")
    # This automatically picks bg1, bg2, or bg3 based on your engine logic
    temp_path = create_video(audio_path, script_text=script_text)
    os.rename(temp_path, video_filename)

    print("📄 Step 4: Updating Gallery Dashboard...")
    update_index_html(video_filename, timestamp_str, script_text)

    print("🚀 Step 5: Uploading to YouTube...")
    try:
        # Uses the cookie file decoded by the GitHub Action
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
