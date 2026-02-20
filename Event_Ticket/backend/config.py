import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Admin credentials (in production, use proper auth)
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin123'
