import os
from bookshelf import secrets_wrapper
PROJECT_ID = "bookshelf-89de1"
TESTING_PROJECT_ID = "bookshelf-test-20855"
class Config:
    DEBUG=False
    TESTING=False

class ProcudtionConfig(Config):
    SESSION_COOKIE_SECURE = True
    GOOGLE_APPLICATION_CREDENTIAL = secrets_wrapper.access_secret_version(PROJECT_ID, 'GOOGLE_APPLICATION_CREDENTIAL')
    SECRET_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'SECRET_KEY')    
    WEB_API_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'WEB_API_KEY')

class DevelopmentConfig(Config):
    DEBUG=True
    GOOGLE_APPLICATION_CREDENTIAL = os.environ.get('GOOGLE_APPLICATION_CREDENTIAL')
    SECRET_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'SECRET_KEY')    
    WEB_API_KEY = secrets_wrapper.access_secret_version(PROJECT_ID, 'WEB_API_KEY')

class TestingConfig(Config):
    TESTING=True
    WTF_CSRF_ENABLED = False

    #SECRET_KEY = secrets_wrapper.access_secret_version(TESTING_PROJECT_ID, 'SECRET_KEY')
    #GOOGLE_APPLICATION_CREDENTIAL = secrets_wrapper.access_secret_version(TESTING_PROJECT_ID, 'GOOGLE_APPLICATION_CREDENTIAL')
    #WEB_API_KEY = secrets_wrapper.access_secret_version(TESTING_PROJECT_ID, 'WEB_API_KEY')
    