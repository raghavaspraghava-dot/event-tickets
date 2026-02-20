import supabase
from config import Config
import os

def get_supabase_client():
    """
    Initialize and return Supabase client
    """
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_KEY
    
    if not url or not key:
        raise Exception("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return supabase.create_client(url, key)

def init_tables():
    """
    Initialize database tables if they don't exist
    """
    client = get_supabase_client()
    
    # Users table
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Events table
    events_table = """
    CREATE TABLE IF NOT EXISTS events (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        date TIMESTAMP WITH TIME ZONE NOT NULL,
        total_tickets INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Registrations table
    registrations_table = """
    CREATE TABLE IF NOT EXISTS registrations (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_email TEXT NOT NULL,
        event_id UUID REFERENCES events(id) ON DELETE CASCADE,
        tickets INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Enable RLS (Row Level Security) - disabled for simplicity in this demo
    client.rpc('execute_sql', {'sql': users_table})
    client.rpc('execute_sql', {'sql': events_table})
    client.rpc('execute_sql', {'sql': registrations_table})
    
    print("Tables initialized successfully!")
