import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG=False
    TESTING=False

class ProcudtionConfig(Config):
    pass

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