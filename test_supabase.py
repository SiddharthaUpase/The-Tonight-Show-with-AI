from supabase import create_client

# Supabase credentials
supabase_url = "https://mjmxndelwgldqqgdthsm.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1qbXhuZGVsd2dsZHFxZ2R0aHNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUwNDUzOTcsImV4cCI6MjA1MDYyMTM5N30.HCIIP1Nx--m2QvsXS_9Fh-KqwaqEJBd-XEAW8aEphxk"

print("Testing Supabase connection...")

try:
    # Initialize the client
    supabase = create_client(supabase_url, supabase_key)
    print("Successfully created Supabase client")
    
    # Try to list storage buckets
    print("\nTrying to list storage buckets...")
    buckets = supabase.storage.list_buckets()
    print(f"Found buckets: {buckets}")
    
    # Try to list files in 'videos' bucket
    print("\nTrying to list files in 'videos' bucket...")
    files = supabase.storage.from_('videos').list()
    print(f"Files in videos bucket: {files}")

except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    print("\nFull error trace:")
    print(traceback.format_exc()) 