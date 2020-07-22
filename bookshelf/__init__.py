import os
from flask import Flask
#from config import DevelopmentConfig, TestingConfig, ProductionConfig
#import firebase_admin
#from firebase_admin import credentials
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())
from bookshelf.firebase_wrapper import Firebase

# Global Objects
firebase = Firebase()

config_name = os.environ.get("FLASK_CONFIG", "production")

def create_app(config_name=config_name):
    """Create an application instance with the desired configuration.

    Also where extentions and blueprints are registered with the instance
    """
    print('Creating Applications')
    app = Flask(__name__)
    print('config_name: ', config_name)
    print('ENVARS: ', os.environ.get('PROJECT_ID'),os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    config_module = f"config.{config_name.capitalize()}Config"
    
    app.config.from_object(config_module)

    # Initialize firebase    
    firebase.init_app(app.config.get('GOOGLE_APPLICATION_CREDENTIALS', None), \
        app.config.get('WEB_API_KEY', None))

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

