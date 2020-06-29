from flask import Flask
from config import DevelopmentConfig, TestingConfig
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def create_app(config=DevelopmentConfig):
    """Create an application instance with the desired configuration.

    Also where extentions and blueprints are registered with the instance
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Extensions
    cred_path = app.config.get('GOOGLE_APPLICATION_CREDENTIALS', None)
    if cred_path:
        cred = credentials.Certificate(cred_path)
    else:
        cred = credentials.ApplicationDefault()
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass
    except Exception as e:
        print(e)
        raise e

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

