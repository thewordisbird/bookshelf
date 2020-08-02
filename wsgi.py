import os

from bookshelf import create_app

app = create_app(os.environ["FLASK_CONFIG"])
