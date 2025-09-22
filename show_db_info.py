import os
from app import app

with app.app_context():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print('SQLALCHEMY_DATABASE_URI =', uri)
    if uri and uri.startswith('sqlite:///'):
        path = uri.replace('sqlite:///', '')
        print('DB file path:', path)
        print('Exists:', os.path.exists(path))
        if os.path.exists(path):
            print('Size bytes:', os.path.getsize(path))
