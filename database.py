from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connected")
except:
    supabase = None
    print("⚠️ Supabase failed")