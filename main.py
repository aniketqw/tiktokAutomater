import os
import base64
from google import genai
from video_engine import create_video
from tiktok_uploader.upload import upload_video

# 1. Setup Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run():
    # Generate content with Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Give me a 30-second script for a faceless 'Life Hack' TikTok.",
        config={"response_modalities": ["AUDIO"]}
    )
    
    # Save the audio and create the video
    with open("voice.mp3", "wb") as f:
        f.write(response.candidates[0].content.parts[0].inline_data.data)
    
    video_path = create_video("voice.mp3")

    # 2. Upload using Cookies
    # We will read the cookie secret from GitHub and save it to a temp file
    upload_video(
        video_path,
        description="Daily Life Hack #lifehacks #ai",
        cookies='cookies.txt',
        browser='chromium'
    )

if __name__ == "__main__":
    run()
