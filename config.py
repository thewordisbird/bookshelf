import os
from bookshelf import secrets_wrapper

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    PROJECT_ID = os.environ.get('PROJECT_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    SECRET_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'SECRET_KEY')    
    WEB_API_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'WEB_API_KEY')

class ProductionConfig(Config):
    """Production configuration"""
    SESSION_COOKIE_SECURE = True
    SECURE_FIREBASE = True

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SECURE_FIREBASE = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SECURE_FIREBASE = False
    

    