from flask import Blueprint, request, jsonify, make_response
from app.services.linkedin_service import get_linkedin_data
from app.services.claude_service import generate_roast
from app.services.speech_service import generate_speech
from app.services.video_service import generate_video
from app.services.supabase_service import SupabaseService
import os
import uuid
import json
import shutil

api_bp = Blueprint('api', __name__)

# Initialize services
supabase_service = SupabaseService()

# Add a route to handle OPTIONS requests for CORS
@api_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

@api_bp.route('/generate-roast', methods=['POST'])
def generate_roast_video():
    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin_url')
        
        print(linkedin_url)
        
        if not linkedin_url:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
        
        # Track costs
        cost_info = {
            'claude': {
                'estimated_tokens': 0,
                'estimated_cost': 0.0
            },
            'elevenlabs': {
                'estimated_duration_seconds': 0,
                'estimated_credits': 0,
                'estimated_cost': 0.0
            },
            'total_cost': 0.0
        }
        
        print('Attempting to get linkedin data')
        linkedin_data = get_linkedin_data(linkedin_url)
        print('Linkedin data retrieved')

        print('Generating roast content')
        roast_content = generate_roast(linkedin_data)
        print('Roast content generated')
        
        # Estimate Claude cost
        prompt_words = len(str(linkedin_data).split()) * 0.5  # Rough estimate
        response_words = len(roast_content.split())
        token_count = int((prompt_words + response_words) * 1.3)
        claude_cost = (token_count / 1000000) * 5.0
        cost_info['claude']['estimated_tokens'] = token_count
        cost_info['claude']['estimated_cost'] = claude_cost
        
        print('Generating speech audio')
        audio_path, elevenlabs_cost_info = generate_speech(roast_content)
        cost_info['elevenlabs'] = elevenlabs_cost_info
        print('Speech audio generated')
        
        # Calculate total cost
        total_cost = cost_info['claude']['estimated_cost'] + cost_info['elevenlabs']['estimated_cost']
        cost_info['total_cost'] = total_cost
        
        print(f"\n===== COST SUMMARY =====")
        print(f"Claude: ${cost_info['claude']['estimated_cost']:.6f}")
        print(f"ElevenLabs: ${cost_info['elevenlabs']['estimated_cost']:.6f}")
        print(f"TOTAL COST: ${total_cost:.6f}")
        print(f"=======================\n")
        
        print('Generating and uploading final video')
        video_url = generate_video(linkedin_data, audio_path, roast_content)
        print('Video generated and uploaded')
        
        return jsonify({
            'status': 'success',
            'message': 'Video generated and uploaded successfully',
            'video_url': video_url,
            'cost_info': cost_info
        })
        
    except Exception as e:
        print(f"Error in generate_roast_video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/test-roast', methods=['POST'])
def test_roast_generation():
    """Test endpoint that uses cached data when available."""
    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin_url')
        use_cached_roast = data.get('use_cached_roast', True)  # New parameter to control using cached roast
        
        if not linkedin_url:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
            
        # First run: Get LinkedIn data and cache it
        test_data_dir = "test/data"
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Create temp_files directory
        temp_files_dir = "temp_files"
        os.makedirs(temp_files_dir, exist_ok=True)
        
        cached_linkedin_file = os.path.join(test_data_dir, "test_linkedin_data.json")
        cached_audio_file = os.path.join(test_data_dir, "test_audio.mp3")
        cached_transcription_file = os.path.join(test_data_dir, "test_transcription.json")
        cached_roast_file = os.path.join(test_data_dir, "test_roast.txt")
        
        # Track costs
        cost_info = {
            'claude': {
                'estimated_tokens': 0,
                'estimated_cost': 0.0
            },
            'elevenlabs': {
                'estimated_duration_seconds': 0,
                'estimated_credits': 0,
                'estimated_cost': 0.0
            },
            'total_cost': 0.0
        }
        
        # If we don't have cached LinkedIn data, get it and cache it
        if not os.path.exists(cached_linkedin_file):
            print('Fetching and caching LinkedIn data...')
            linkedin_data = get_linkedin_data(linkedin_url)
            with open(cached_linkedin_file, 'w') as f:
                json.dump(linkedin_data, f)
        else:
            print('Using cached LinkedIn data')
            with open(cached_linkedin_file, 'r') as f:
                linkedin_data = json.load(f)
        
        # Generate or use cached roast content
        if use_cached_roast and os.path.exists(cached_roast_file):
            print('Using cached roast content')
            with open(cached_roast_file, 'r') as f:
                roast_content = f.read()
            # Estimate Claude costs for cached content
            word_count = len(roast_content.split())
            token_count = int(word_count * 1.3)
            claude_cost = (token_count / 1000000) * 5.0
            cost_info['claude']['estimated_tokens'] = token_count
            cost_info['claude']['estimated_cost'] = claude_cost
        else:
            print('Generating fresh roast content with Claude')
            roast_content = generate_roast(linkedin_data, use_cache=False)
            # Cache the roast content for future use
            with open(cached_roast_file, 'w') as f:
                f.write(roast_content)
            
            # Rough estimation of Claude cost - this could be improved
            prompt_words = len(str(linkedin_data).split()) * 0.5  # Rough estimate
            response_words = len(roast_content.split())
            token_count = int((prompt_words + response_words) * 1.3)
            claude_cost = (token_count / 1000000) * 5.0
            cost_info['claude']['estimated_tokens'] = token_count
            cost_info['claude']['estimated_cost'] = claude_cost
        
        # If we don't have cached audio, generate it and cache it
        if not os.path.exists(cached_audio_file) or not os.path.exists(cached_transcription_file):
            print('Generating and caching speech audio and transcription')
            audio_path, elevenlabs_cost_info = generate_speech(roast_content)
            shutil.copy(audio_path, cached_audio_file)
            
            # Update cost info with ElevenLabs data
            cost_info['elevenlabs'] = elevenlabs_cost_info
            
            # Also copy transcription.json if it exists
            if os.path.exists("transcription.json"):
                shutil.copy("transcription.json", cached_transcription_file)
        else:
            print('Using cached audio file and transcription')
            # Copy cached audio to working location (same path where generate_speech would put it)
            working_audio_path = "roast.mp3"  # This should match the default output path in generate_speech
            shutil.copy(cached_audio_file, working_audio_path)
            audio_path = working_audio_path
            
            # Estimate ElevenLabs costs for cached audio
            word_count = len(roast_content.split())
            duration_seconds = word_count * 0.4
            duration_minutes = duration_seconds / 60
            credits = duration_minutes * 700
            elevenlabs_cost = (credits / 30000) * 5.0
            
            cost_info['elevenlabs'] = {
                'estimated_duration_seconds': duration_seconds,
                'estimated_duration_minutes': duration_minutes,
                'estimated_credits': credits,
                'estimated_cost': elevenlabs_cost,
                'file_size_bytes': os.path.getsize(cached_audio_file) if os.path.exists(cached_audio_file) else 0
            }
            
            # Copy cached transcription to working location
            shutil.copy(cached_transcription_file, "transcription.json")
            
        # Calculate total cost
        total_cost = cost_info['claude']['estimated_cost'] + cost_info['elevenlabs']['estimated_cost']
        cost_info['total_cost'] = total_cost
        
        print(f"\n===== COST SUMMARY =====")
        print(f"Claude: ${cost_info['claude']['estimated_cost']:.6f}")
        print(f"ElevenLabs: ${cost_info['elevenlabs']['estimated_cost']:.6f}")
        print(f"TOTAL COST: ${total_cost:.6f}")
        print(f"=======================\n")
            
        print('Generating and uploading final video')
        video_url = generate_video(linkedin_data, audio_path, roast_content)
        
        return jsonify({
            'status': 'success',
            'message': 'Test video generated successfully',
            'roast_content': roast_content,
            'video_url': video_url,
            'cost_info': cost_info
        })
        
    except Exception as e:
        print(f"Error in test_roast_generation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}) 

@api_bp.route('/say-hi', methods=['GET'])
def say_hi():
    response = jsonify({'message': 'Hi from the API!'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@api_bp.route('/test-supabase', methods=['GET'])
def test_supabase():
    """Test endpoint for Supabase video upload."""
    try:
        # Use existing video file
        test_file_path = "output/final_roast.mp4"
        
        # Check if file exists
        if not os.path.exists(test_file_path):
            return jsonify({'error': 'Test video file not found'}), 404
            
        # Upload to Supabase
        public_url = supabase_service.upload_video(
            file_path=test_file_path,
            user_id='test_user'
        )
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'url': public_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/test-roast-only', methods=['POST'])
def test_roast_only():
    """Simple endpoint that only returns the roast text, useful for quick testing."""
    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin_url')
        use_cached_roast = data.get('use_cached_roast', False)
        include_speech_cost = data.get('include_speech_cost', True)  # Option to include speech cost
        
        if not linkedin_url:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
            
        # Set up cache directory
        test_data_dir = "test/data"
        os.makedirs(test_data_dir, exist_ok=True)
        
        cached_linkedin_file = os.path.join(test_data_dir, "test_linkedin_data.json")
        cached_roast_file = os.path.join(test_data_dir, "test_roast.txt")
        
        # Get or load LinkedIn data
        if not os.path.exists(cached_linkedin_file):
            print('Fetching and caching LinkedIn data...')
            linkedin_data = get_linkedin_data(linkedin_url)
            with open(cached_linkedin_file, 'w') as f:
                json.dump(linkedin_data, f)
        else:
            print('Using cached LinkedIn data')
            with open(cached_linkedin_file, 'r') as f:
                linkedin_data = json.load(f)
        
        # Track costs
        cost_info = {
            'claude': {
                'estimated_tokens': 0,
                'estimated_cost': 0.0
            },
            'elevenlabs': {
                'estimated_duration_seconds': 0,
                'estimated_credits': 0,
                'estimated_cost': 0.0
            },
            'total_cost': 0.0
        }
        
        # Generate or use cached roast content
        if use_cached_roast and os.path.exists(cached_roast_file):
            print('Using cached roast content')
            with open(cached_roast_file, 'r') as f:
                roast_content = f.read()
            # Estimate token info for cached content
            word_count = len(roast_content.split())
            token_count = int(word_count * 1.3)
            claude_cost = (token_count / 1000000) * 5.0
            cost_info['claude']['estimated_tokens'] = token_count
            cost_info['claude']['estimated_cost'] = claude_cost
        else:
            print('Generating fresh roast content with Claude')
            roast_content = generate_roast(linkedin_data, use_cache=False)
            # Cache the roast content for future use
            with open(cached_roast_file, 'w') as f:
                f.write(roast_content)
            # Rough estimation of Claude cost
            prompt_words = len(str(linkedin_data).split()) * 0.5
            response_words = len(roast_content.split())
            token_count = int((prompt_words + response_words) * 1.3)
            claude_cost = (token_count / 1000000) * 5.0
            cost_info['claude']['estimated_tokens'] = token_count
            cost_info['claude']['estimated_cost'] = claude_cost
        
        # Calculate speech costs without actually generating the audio
        if include_speech_cost:
            # Estimate ElevenLabs costs
            word_count = len(roast_content.split())
            duration_seconds = word_count * 0.4
            duration_minutes = duration_seconds / 60
            credits = duration_minutes * 700
            elevenlabs_cost = (credits / 30000) * 5.0
            
            cost_info['elevenlabs'] = {
                'estimated_duration_seconds': duration_seconds,
                'estimated_duration_minutes': duration_minutes,
                'estimated_credits': credits,
                'estimated_cost': elevenlabs_cost,
                'estimated_word_count': word_count
            }
        
        # Calculate total cost
        total_cost = cost_info['claude']['estimated_cost'] + cost_info['elevenlabs']['estimated_cost']
        cost_info['total_cost'] = total_cost
        
        print(f"\n===== COST SUMMARY =====")
        print(f"Claude: ${cost_info['claude']['estimated_cost']:.6f}")
        print(f"ElevenLabs: ${cost_info['elevenlabs']['estimated_cost']:.6f}")
        print(f"TOTAL COST: ${total_cost:.6f}")
        print(f"=======================\n")
        
        # Calculate estimated speaking duration
        word_count = len(roast_content.split())
        estimated_duration_seconds = int(word_count * 0.4)  # Rough estimate: 0.4 seconds per word
        
        return jsonify({
            'status': 'success',
            'message': 'Roast content generated successfully',
            'roast_content': roast_content,
            'cost_info': cost_info,
            'estimated_duration': f"{estimated_duration_seconds // 60}:{estimated_duration_seconds % 60:02d}"
        })
        
    except Exception as e:
        print(f"Error in test_roast_only: {str(e)}")
        return jsonify({'error': str(e)}), 500
