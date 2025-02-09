from dotenv import load_dotenv
import os

# Force reload environment variables at startup
load_dotenv(override=True)

from app import create_app

app = create_app()

if __name__ == '__main__':
    print(f"Using ElevenLabs API Key: {os.getenv('ELEVENLABS_API_KEY')}")
    print(f"Using Deepgram API Key: {os.getenv('DEEPGRAM_API_KEY')}")
    print(f"Using Voice ID: {os.getenv('VOICE_ID')}")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 