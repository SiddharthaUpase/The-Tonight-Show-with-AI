import os
from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    def __init__(self):
        """Initialize Supabase client."""
        # Using placeholder values for now
        supabase_url = "https://mjmxndelwgldqqgdthsm.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1qbXhuZGVsd2dsZHFxZ2R0aHNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUwNDUzOTcsImV4cCI6MjA1MDYyMTM5N30.HCIIP1Nx--m2QvsXS_9Fh-KqwaqEJBd-XEAW8aEphxk"
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise Exception(f"Failed to initialize Supabase: {str(e)}")

    def upload_video(self, file_path: str, user_id: str) -> str:
        """Upload video to Supabase Storage and return public URL."""
        try:
            # Create a unique file name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"{timestamp}.mp4"
            bucket_name = "videos"
            
            # Read the file in binary mode
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase Storage
            response = self.supabase.storage \
                .from_(bucket_name) \
                .upload(
                    path=file_name,
                    file=file_data
                )
            
            if isinstance(response, dict) and 'error' in response:
                raise Exception(f"Upload failed: {response['error']}")
            
            # Get the public URL
            public_url = self.supabase.storage \
                .from_(bucket_name) \
                .get_public_url(file_name)
            
            # Clean up local file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return public_url
            
        except Exception as e:
            print(f"Error uploading to Supabase: {str(e)}")
            raise 