from flask import Blueprint, request, jsonify
from app.services.linkedin_service import get_linkedin_data
from app.services.roast_service import generate_roast
from app.services.speech_service import generate_speech
from app.services.video_service import generate_video
from app.services.firebase_service import FirebaseService
from app.services.supabase_service import SupabaseService
import os
import uuid

api_bp = Blueprint('api', __name__)

# Initialize services
supabase_service = SupabaseService()

@api_bp.route('/generate-roast', methods=['POST'])
def generate_roast_video():
    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin_url')


        print(linkedin_url)
        
        if not linkedin_url:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
        
        print('Attempting to get linkedin data')
        linkedin_data = get_linkedin_data(linkedin_url)
        print('Linkedin data retrieved')

        print('Generating roast content')
        roast_content = generate_roast(linkedin_data)
        print('Roast content generated')
        
        print('Generating speech audio')
        audio_path = generate_speech(roast_content)
        print('Speech audio generated')
        
        print('Generating and uploading final video')
        video_url = generate_video(linkedin_data, audio_path, roast_content)
        print('Video generated and uploaded')
        
        return jsonify({
            'status': 'success',
            'message': 'Video generated and uploaded successfully',
            'video_url': video_url
        })
        
    except Exception as e:
        print(f"Error in generate_roast_video: {str(e)}")
        return jsonify({'error': str(e)}), 500



@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}) 




@api_bp.route('/say-hi', methods=['GET'])
def say_hi():
    return jsonify({'message': 'Hi from the API!'})

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
