import os
from dotenv import load_dotenv
import json
import requests
from deepgram import DeepgramClient, PrerecordedOptions

# Load environment variables
load_dotenv()

# Print to verify the key being used
print(f"Using ElevenLabs API Key: {os.getenv('ELEVENLABS_API_KEY')}")
print(f"Using Deepgram API Key: {os.getenv('DEEPGRAM_API_KEY')}")
print(f"Using Voice ID: {os.getenv('VOICE_ID')}")

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
VOICE_ID = os.getenv('VOICE_ID', '1SM7GgM6IMuvQlz2BwM3')

def text_to_speech(text: str, output_path: str = "roast.mp3") -> str:
    """Convert text to speech using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    try:
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "language_code": "en",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.7,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            transcribe_and_save_audio(output_path)
            return output_path
        else:
            raise Exception(f"ElevenLabs API error: {response.text}")
    except Exception as e:
        raise

def transcribe_and_save_audio(audio_path: str, output_json: str = "transcription.json") -> None:
    """Transcribe audio and save the transcript as JSON with timing data."""
    try:
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        
        with open(audio_path, "rb") as file:
            buffer_data = file.read()
        
        payload = {
            "buffer": buffer_data,
        }
        
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language="en",
            diarize=False,
            punctuate=True,
            utterances=False,
        )
        
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(response.to_dict(), f, indent=2)
            
    except Exception as e:
        raise

def generate_speech(text: str) -> str:
    """Main function to generate speech from text."""
    return text_to_speech(text) 