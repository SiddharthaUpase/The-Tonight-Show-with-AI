from flask import Flask
from app.config import Config
from app.routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app 