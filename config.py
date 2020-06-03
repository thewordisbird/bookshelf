import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

class ProcudtionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True

    