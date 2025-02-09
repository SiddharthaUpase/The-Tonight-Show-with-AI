import os
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime, timedelta

class FirebaseService:
    def __init__(self):
        """Initialize Firebase with credentials."""
        # Get the absolute path to the credentials file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.cred_path = os.path.join(base_dir, 'firebase-credentials.json')
        
        # Check if credentials file exists
        if not os.path.exists(self.cred_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: {self.cred_path}\n"
                f"Please ensure firebase-credentials.json is in the project root directory."
            )
        
        print("Firebase credentials file found at: ", self.cred_path)
        # Check if file is readable
        try:
            with open(self.cred_path, 'r') as f:
                f.read()
        except PermissionError:
            raise PermissionError(
                f"Cannot read Firebase credentials file at: {self.cred_path}\n"
                f"Please check file permissions."
            )
        except Exception as e:
            raise Exception(
                f"Error reading Firebase credentials file: {str(e)}\n"
                f"File location: {self.cred_path}"
            )
            
        # Check if FIREBASE_STORAGE_BUCKET is set
        if not os.getenv('FIREBASE_STORAGE_BUCKET'):
            raise ValueError(
                "FIREBASE_STORAGE_BUCKET environment variable is not set.\n"
                "Please set it in your .env file."
            )
        print("FIREBASE_STORAGE_BUCKET: ", os.getenv('FIREBASE_STORAGE_BUCKET'))

        try:
            cred = credentials.Certificate(self.cred_path)
            print("Firebase bucket: ", os.getenv('FIREBASE_STORAGE_BUCKET'))
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                })
            self.bucket = storage.bucket()
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase: {str(e)}")

    def upload_video(self, file_path: str, user_id: str) -> str:
        """Upload video to Firebase Storage and return public URL."""
        try:
            # Create a unique blob path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            blob_path = f"roasts/{user_id}/{timestamp}.mp4"

            #check if firebase has been initialized
            if not firebase_admin._apps:
                raise Exception("Firebase has not been initialized")
            print("Firebase has been initialized")
            
            
            # Upload the file
            blob = self.bucket.blob(blob_path)
            blob.upload_from_filename(file_path)
            
            # Generate a signed URL that expires in 7 days
            url = blob.generate_signed_url(
                expiration=datetime.now() + timedelta(days=7),
                version="v4"
            )
            
            # Clean up local file
            os.remove(file_path)
            
            return url
        except Exception as e:
            print(f"Error uploading to Firebase: {str(e)}")
            raise 