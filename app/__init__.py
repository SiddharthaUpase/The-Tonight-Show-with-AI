from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config
from app.routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)
    
    # Enable CORS for all routes with all necessary headers
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         }},
         supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add a route to serve the test HTML page
    @app.route('/test')
    def test_page():
        return send_from_directory('static', 'test.html')
    
    return app