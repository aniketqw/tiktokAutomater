import os
import asyncio
import edge_tts
from google import genai
from video_engine import create_video
from tiktok_uploader.upload import upload_video

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_voiceover(text, output_path):
    """Free high-quality speech. Using 'Ava' for a more energetic tone."""
    voice = "en-US-AvaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

async def run_automation():
    print("🎬 Step 1: Generating High-Intensity Script...")
    
    # We explicitly tell Gemini about the stunt-heavy background assets
    prompt = """
    Write a 25-30 second viral TikTok script about a 'Mind-Blowing Fact' or 'Life Hack'.
    STYLE: High energy, punchy, and fast-paced. 
    CONTEXT: This will play over high-intensity parkour and BMX stunt footage. 
    STRUCTURE: Start with a 2-second hook, followed by 3 fast facts, and end with a call to action.
    Output spoken text ONLY. No emojis, no stage directions.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    script_text = response.text

    print("🎙️ Step 2: Generating Sync-Ready Audio...")
    audio_path = "voiceover.mp3"
    await generate_voiceover(script_text, audio_path)

    print("🎞️ Step 3: Assembling Stunt Video...")
    # Passing the text ensures the engine knows where to place captions
    video_path = create_video(audio_path, script_text=script_text)

    print("📱 Step 4: Posting to TikTok...")
    try:
        upload_video(
            video_path,
            description=f"Wait for the end! 🤯 #stunts #parkour #facts #ai #automation",
            cookies='cookies.txt',
            browser='chromium'
        )
        print("✅ Success! Your stunt video is live.")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_automation())
