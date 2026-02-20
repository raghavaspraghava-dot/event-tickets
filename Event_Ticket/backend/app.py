import sys
import os
# FIX: Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask


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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

