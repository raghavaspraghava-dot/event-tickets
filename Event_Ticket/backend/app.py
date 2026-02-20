import sys
import os
from mcp.control import EventTicketMCP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from flask import Flask, jsonify
from flask_cors import CORS

# Import routes AFTER fixing path
from routes.auth import auth_bp
from routes.events import events_bp
from routes.tickets import tickets_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(events_bp, url_prefix='/api')
    app.register_blueprint(tickets_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    @app.route('/')
    def home():
        return jsonify({"message": "Event Ticket Registration API is running!"}), 200
    @app.route('/api/mcp/tools')
def mcp_tools():
    """Expose MCP tools for AI agents"""
    from mcp.tools import get_mcp_tools
    return jsonify([{
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.inputSchema
    } for tool in get_mcp_tools()])

@app.route('/api/mcp/<tool_name>', methods=['POST'])
def mcp_tool(tool_name):
    """Execute MCP tool"""
    data = request.get_json()
    # Forward to MCP server or execute directly
    return jsonify({"status": "MCP tool executed", "tool": tool_name})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)



