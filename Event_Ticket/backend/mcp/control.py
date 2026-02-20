from mcp.server import Server
from mcp.types import (
    Tool, TextContent, ImageContent, Resource,
    InitializationOptions, InitializationResponse
)
import asyncio
import logging
from typing import Any, Dict, List
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventTicketMCP")

class EventTicketMCP:
    def __init__(self):
        self.server = Server("event-ticket-mcp")
        self.setup_tools()
    
    def setup_tools(self):
        """Register MCP tools for event ticket management"""
        
        # Tool 1: Get Events
        self.server.setRequestHandler(
            "list_events",
            self.list_events
        )
        
        # Tool 2: Create Event  
        self.server.setRequestHandler(
            "create_event",
            self.create_event
        )
        
        # Tool 3: Manage Tickets
        self.server.setRequestHandler(
            "book_tickets", 
            self.book_tickets
        )
        
        # Tool 4: Admin Stats
        self.server.setRequestHandler(
            "admin_stats",
            self.admin_stats
        )
    
    async def list_events(self, params: Dict[str, Any]) -> str:
        """List all available events"""
        # Connect to your Supabase
        from supabase import create_client
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        response = client.table('events').select('*').order('date').execute()
        events = response.data
        
        event_list = []
        for event in events:
            event_list.append({
                "id": event['id'],
                "title": event['title'],
                "date": event['date'],
                "tickets_available": event['total_tickets']
            })
        
        return json.dumps({
            "events": event_list,
            "message": f"Found {len(events)} events"
        })
    
    async def create_event(self, params: Dict[str, Any]) -> str:
        """Create new event (Admin only)"""
        import uuid
        from supabase import create_client
        
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        event_data = {
            "id": str(uuid.uuid4()),
            "title": params.get("title"),
            "description": params.get("description", ""),
            "date": params.get("date"),
            "total_tickets": params.get("total_tickets", 100)
        }
        
        client.table('events').insert(event_data).execute()
        return json.dumps({"message": f"Created event: {event_data['title']}"})
    
    async def book_tickets(self, params: Dict[str, Any]) -> str:
        """Book tickets for event"""
        from supabase import create_client
        
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        
        # Check availability
        event = client.table('events').select('total_tickets').eq('id', params['event_id']).execute().data[0]
        
        if event['total_tickets'] < params.get('tickets
