import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

class ProcudtionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG=True
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

class TestingConfig(Config):
    TESTING=True
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_TEST_CREDENTIALS')
    