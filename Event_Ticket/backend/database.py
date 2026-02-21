import supabase
from config import Config
import traceback
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """🔗 Connect using YOUR real credentials"""
        try:
            self.client = supabase.create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
            print("✅ Supabase connected with your credentials!")
            self._test_tables()
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            print(traceback.format_exc())
            self.client = None
    
    def _test_tables(self):
        """🔍 Verify tables exist"""
        try:
            # Test events table
            self.client.table('events').select('count').limit(1).execute()
            print("✅ Events table ready")
        except:
            print("⚠️  Create tables in Supabase SQL Editor")
    
    def get_client(self):
        return self.client
    
    def is_connected(self):
        return self.client is not None

# Global database instance
db = DatabaseManager()
