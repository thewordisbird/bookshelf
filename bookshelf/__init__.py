from flask import Flask
from config import DevelopmentConfig

def create_app(config=DevelopmentConfig):
    """Create an application instance with the desired configuration.

    Also where extentions and blueprints are registered with the instance
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Extensions

    # Register Blueprints

    # Test Route
    @app.route('/hello')
    def hello():
        return f'Hello {__name__}'
    
    return app