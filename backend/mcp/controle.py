from flask import session

class MCPController:
    @staticmethod
    def is_admin():
        return session.get('admin_logged_in', False)
    
    @staticmethod
    def validate_event(event_data):
        required = ['name', 'date', 'capacity', 'available']
        return all(event_data.get(field) for field in required)
