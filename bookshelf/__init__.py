from flask import Flask
from config import DevelopmentConfig
import firebase_admin
def create_app(config=DevelopmentConfig):
    """Create an application instance with the desired configuration.

    Also where extentions and blueprints are registered with the instance
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Extensions
    firebase_admin.initialize_app()

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