import os
import json
import gdown
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image
from app.services.linkedin_service import download_profile_picture
from app.services.supabase_service import SupabaseService

# Compatibility fix for Pillow
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

class VideoGenerator:
    def __init__(self, base_video_url: str = "https://drive.google.com/file/d/1tbH-PBdQPM1Ya_hmiq0MKn3WKFuLZ54K/view?usp=sharing"):
        """Initialize the video generator with base video URL."""
        self.base_video_url = base_video_url
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def _download_base_video(self):
        """Download the base video from Google Drive."""
        temp_video_path = os.path.join(self.temp_dir, "base_video.mp4")
        gdown.download(url=self.base_video_url, output=temp_video_path, fuzzy=True)
        return temp_video_path

    def create_video(self, audio_path: str, profile_image_path: str, transcript_text: str, output_path: str):
        """Create the final video with audio, image and synchronized subtitles."""
        try:
            # Download base video
            base_video_path = self._download_base_video()
            
            # Load transcription data
            with open('transcription.json', 'r', encoding='utf-8') as f:
                transcription_data = json.load(f)
            
            words_data = transcription_data['results']['channels'][0]['alternatives'][0]['words']
            
            # Load audio and set duration
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            
            # Add buffer for fade out
            total_duration = audio_duration + 2
            
            # Load and trim base video
            video = VideoFileClip(base_video_path).subclip(0, total_duration)
            
            # Load and prepare image overlay
            image = (ImageClip(profile_image_path)
                    .set_duration(total_duration)
                    .resize(width=200)
                    .set_position((50, 50)))
            
            # Vibrant color palette
            COLORS = [
                '#FF1E1E', '#FF9C1E', '#FFE61E',
                '#1EFF1E', '#1E8FFF', '#961EFF'
            ]
            
            # Font settings
            FONT_SETTINGS = {
                'normal': {
                    'font': './assets/KOMIKAX_.ttf',
                    'stroke_color': 'black',
                    'stroke_width': 4,
                    'kerning': 0
                },
                'emphasis': {
                    'font': './assets/KOMIKAX_.ttf',
                    'stroke_color': 'black',
                    'stroke_width': 5,
                    'kerning': 0
                }
            }
            
            # Create text clips
            text_clips = []
            for i, word_data in enumerate(words_data):
                word = word_data['punctuated_word']
                start_time = float(word_data['start'])
                end_time = float(word_data['end'])
                
                is_emphasis = (i == len(words_data) - 1) or any(c in word for c in ['!', '?', '.'])
                font_settings = FONT_SETTINGS['emphasis'] if is_emphasis else FONT_SETTINGS['normal']
                
                color = COLORS[i % len(COLORS)]
                fontsize = max(60, 60 + (10 - len(word)) * 4)
                
                text_clip = (TextClip(word, 
                                    fontsize=fontsize,
                                    font=font_settings['font'],
                                    color=color,
                                    stroke_color=font_settings['stroke_color'],
                                    stroke_width=font_settings['stroke_width'],
                                    kerning=font_settings['kerning'])
                            .set_position('center')
                            .set_start(start_time)
                            .set_duration(end_time - start_time))
                
                text_clips.append(text_clip)
            
            # Combine everything
            final_video = CompositeVideoClip([video, image] + text_clips)
            final_video = final_video.set_audio(audio)
            
            # Apply fade effects
            final_video = final_video.fadein(1.5).fadeout(1.5)
            
            # Write final video
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Clean up video objects
            video.close()
            audio.close()
            final_video.close()
            
            return output_path
        
        except Exception as e:
            self._cleanup()
            raise e

    def _cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")

def generate_video(linkedin_data: dict, audio_path: str, roast_text: str) -> str:
    """Main function to generate video from LinkedIn data and audio."""
    temp_dir = "temp_files"
    generator = None
    try:
        # Download profile picture
        profile_pic = download_profile_picture(linkedin_data)
        if not profile_pic:
            profile_pic = "assets/default_profile.jpg"
        
        # Create temp directory for processing
        os.makedirs(temp_dir, exist_ok=True)
        
        # Initialize video generator
        generator = VideoGenerator()
        
        # Generate output video file
        output_path = os.path.join(temp_dir, "final_roast.mp4")
        
        # Create the video
        generator.create_video(
            audio_path=audio_path,
            profile_image_path=profile_pic,
            transcript_text=roast_text,
            output_path=output_path
        )
        
        # Upload to Supabase
        supabase_service = SupabaseService()
        video_url = supabase_service.upload_video(output_path, "default_user")
        
        return video_url
        
    finally:
        # Cleanup only after upload is complete
        if generator:
            generator._cleanup()
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(profile_pic) and profile_pic != "assets/default_profile.jpg":
            os.remove(profile_pic)
        if os.path.exists("transcription.json"):
            os.remove("transcription.json") 