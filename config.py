import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

ADMIN_EMAIL = "admin@eventickets.com"
ADMIN_PASSWORD = "admin123"