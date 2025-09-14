from app import app
from extensions import db
from models import Customer

with app.app_context():
    alice = Customer.query.filter_by(name="Alice").first()
    alice.email = "alice@newmail.com"
    db.session.commit()
    print(Customer.query.all())
