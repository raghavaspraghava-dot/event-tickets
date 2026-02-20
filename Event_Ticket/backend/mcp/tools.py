from typing import Any, Dict, List
from mcp.types import Tool

# MCP Tools Schema
EVENT_TICKET_TOOLS = [
    Tool(
        name="list_events",
        description="List all upcoming events with available tickets",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="create_event",
        description="Create a new event (Admin only)",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "date": {"type": "string", "format": "date-time"},
                "total_tickets": {"type": "integer"}
            },
            "required": ["title", "date", "total_tickets"]
        }
    ),
    Tool(
        name="book_tickets",
        description="Book tickets for an event",
        inputSchema={
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "tickets": {"type": "integer", "minimum": 1}
            },
            "required": ["event_id", "email"]
        }
    ),
    Tool(
        name="admin_stats",
        description="Get admin statistics and analytics",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]

def get_mcp_tools() -> List[Tool]:
    """Get all available MCP tools"""
    return EVENT_TICKET_TOOLS
