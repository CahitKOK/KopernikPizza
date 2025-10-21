from app import app
from extensions import db
from models import *
from database_constraints import add_database_constraints

with app.app_context():
    db.drop_all()  # Start fresh
    db.create_all()
    add_database_constraints()  # Apply database constraints
    print("Database tables and constraints created successfully!")