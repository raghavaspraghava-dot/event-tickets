import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sb_secret_3vvd3uuPfJRQ23ijvOCIqw_Y6OnAQ2R'
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://ydsdpqnhsqiccdsivwek.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or 'sb_publishable_MPIsH6irDv5f3fTch6J3nA_gxlzCZ78'
    
    # Admin credentials (in production, use proper auth)
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin123'

