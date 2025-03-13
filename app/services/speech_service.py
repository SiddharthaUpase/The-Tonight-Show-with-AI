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

# ElevenLabs cost calculation constants
ELEVENLABS_COST_PER_30K_CREDITS = 5.0  # $5 for 30k credits
ELEVENLABS_CREDITS_PER_MINUTE = 700  # 700 credits per minute of audio

def text_to_speech(text: str, output_path: str = "roast.mp3") -> tuple:
    """Convert text to speech using ElevenLabs API and return cost info."""
    print(f"Converting text to speech using ElevenLabs API")
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
        
        # Estimate word count and duration before making API call
        word_count = len(text.split())
        estimated_duration_seconds = word_count * 0.4  # Rough estimate: 0.4 seconds per word
        estimated_duration_minutes = estimated_duration_seconds / 60
        
        # Estimate ElevenLabs cost
        estimated_credits = estimated_duration_minutes * ELEVENLABS_CREDITS_PER_MINUTE
        estimated_cost = (estimated_credits / 30000) * ELEVENLABS_COST_PER_30K_CREDITS
        
        print(f"Estimated ElevenLabs duration: {estimated_duration_seconds:.2f} seconds")
        print(f"Estimated ElevenLabs credits: {estimated_credits:.2f}")
        print(f"Estimated ElevenLabs cost: ${estimated_cost:.6f}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get actual audio file size
            file_size = os.path.getsize(output_path)
            
            # Transcribe the audio
            transcribe_and_save_audio(output_path)
            
            # Create cost info dict to return
            cost_info = {
                'estimated_duration_seconds': estimated_duration_seconds,
                'estimated_duration_minutes': estimated_duration_minutes,
                'estimated_credits': estimated_credits,
                'estimated_cost': estimated_cost,
                'file_size_bytes': file_size
            }
            
            return output_path, cost_info
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

def generate_speech(text: str) -> tuple:
    """Main function to generate speech from text. Returns path and cost info."""
    return text_to_speech(text) 