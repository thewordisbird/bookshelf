import os
from bookshelf import secrets_wrapper

class Config:
    PROJECT_ID = os.environ.get("PROJECT_ID")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG=False
    TESTING=False

class ProcudtionConfig(Config):
    WEB_API_KEY = os.environ.get('WEB_API_KEY')

class DevelopmentConfig(Config):
    DEBUG=True
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    WEB_API_KEY = os.environ.get('WEB_API_KEY')

class TestingConfig(Config):
    TESTING=True
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_TEST_CREDENTIALS')
    WEB_API_KEY = os.environ.get('WEB_API_TEST_KEY')
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = True