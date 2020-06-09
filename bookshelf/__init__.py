from flask import Flask
from config import DevelopmentConfig
from .auth.firebase_auth import initialize_firebase

def create_app(config=DevelopmentConfig):
    """Create an application instance with the desired configuration.

    Also where extentions and blueprints are registered with the instance
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Extensions
    initialize_firebase()

    # Register Blueprints
    from bookshelf.main.routes import bp as books_bp
    from bookshelf.auth.routes import bp as auth_bp
    
    app.register_blueprint(books_bp)
    app.register_blueprint(auth_bp)

    # Test Route
    @app.route('/hello')
    def hello():
        return f'Hello {__name__}'
    
    return app