from app import app
from extensions import db
from models import Customer, Pizza, Order
from datetime import datetime

with app.app_context():
    # tabloyu temizle ve yeniden oluştur
    db.drop_all()
    db.create_all()

    # müşteri ekle
    alice = Customer(name="Alice", email="alice@example.com", phone="1111111111", address="Main Street 1")
    bob   = Customer(name="Bob",   email="bob@example.com",   phone="2222222222", address="Second Street 5")

    # pizza ekle
    margherita = Pizza(name="Margherita", description="Tomato, mozzarella, basil", price=8.50)
    pepperoni  = Pizza(name="Pepperoni",  description="Tomato, mozzarella, salami", price=9.90)

    # sipariş ekle
    order1 = Order(customer=alice, order_date=datetime.now(), status="delivered")

    db.session.add_all([alice, bob, margherita, pepperoni, order1])
    db.session.commit()

    print("✅ Seed data inserted.")
