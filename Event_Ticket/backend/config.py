import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecret2026-dev-key'
    
    # Safe Supabase fallback - will use env vars in production
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://dummy.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or 'dummy-key-for-dev'
    
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
