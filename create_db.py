from app import app
from extensions import db
from models import *

with app.app_context():
    db.drop_all()  # Start fresh
    db.create_all()
    print("Database tables created successfully!")