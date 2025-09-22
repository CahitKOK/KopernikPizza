import pytest
from datetime import datetime

from app import app
from extensions import db
from models import Customer, Pizza, Order, OrderItem


@pytest.fixture(autouse=True)
def setup_db():
    # ensure a clean database for each test
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def test_pizza_orderitem_bidirectional():
    with app.app_context():
        # create a customer
        c = Customer(name='Tester', email='t@example.com', phone='000', address='12345 City')
        db.session.add(c)
        db.session.commit()

        # create pizza
        p = Pizza(name='Test Pizza', description='Test')
        db.session.add(p)
        db.session.commit()

        # create order
        o = Order(customer_id=c.id, order_date=datetime.utcnow(), status='pending')
        db.session.add(o)
        db.session.commit()

        # create order item linking pizza and order
        oi = OrderItem(order_id=o.id, pizza_id=p.id, quantity=2)
        db.session.add(oi)
        db.session.commit()

        # reload from DB
        p_db = Pizza.query.get(p.id)
        oi_db = OrderItem.query.get(oi.id)

        # order_item -> pizza
        assert oi_db.pizza is not None
        assert oi_db.pizza.id == p_db.id

        # pizza -> order_items
        assert any(item.id == oi_db.id for item in p_db.order_items)
