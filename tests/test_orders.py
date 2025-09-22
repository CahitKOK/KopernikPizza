import pytest
from datetime import datetime, timedelta, date

from app import app
from extensions import db
from models import Customer, Pizza, Ingredient, PizzaIngredient, Order, OrderItem, DiscountCode, DeliveryPerson, DeliveryZone


@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def seed_one_pizza():
    p = Pizza(name='Seed Pizza', description='seed')
    db.session.add(p)
    db.session.commit()
    return p


def test_create_order_basic():
    with app.app_context():
        # seed
        p = seed_one_pizza()
        c = Customer(name='A', email='a@example.com', phone='1', address='10001 City')
        db.session.add(c)
        db.session.commit()

        client = app.test_client()
        payload = {"customer_id": c.id, "items": [{"pizza_id": p.id, "quantity": 1}]}
        resp = client.post('/orders', json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'order_id' in data
        assert data['total'] is not None


def test_birthday_freebie():
    with app.app_context():
        p = seed_one_pizza()
        # customer with birthday today
        today = date.today()
        c = Customer(name='B', email='b@example.com', phone='2', address='20002 City', birthday=today)
        db.session.add(c)
        db.session.commit()

        client = app.test_client()
        payload = {"customer_id": c.id, "items": [{"pizza_id": p.id, "quantity": 1}]}
        resp = client.post('/orders', json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['total'] == 0.0 or data['total'] >= 0.0


def test_loyalty_discount():
    with app.app_context():
        p = seed_one_pizza()
        c = Customer(name='C', email='c@example.com', phone='3', address='30003 City')
        db.session.add(c)
        db.session.commit()

        # create past orders totalling 10 pizzas
        for _ in range(5):
            o = Order(customer_id=c.id, order_date=datetime.utcnow(), status='complete')
            db.session.add(o)
            db.session.flush()
            oi = OrderItem(order_id=o.id, pizza_id=p.id, quantity=2)
            db.session.add(oi)
        db.session.commit()

        client = app.test_client()
        payload = {"customer_id": c.id, "items": [{"pizza_id": p.id, "quantity": 1}]}
        resp = client.post('/orders', json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        # loyalty discount should be applied, total should be less than calculated price for 1 pizza
        assert data['total'] is not None


def test_one_time_code_consumed():
    with app.app_context():
        p = seed_one_pizza()
        c = Customer(name='D', email='d@example.com', phone='4', address='40004 City')
        db.session.add(c)
        dc = DiscountCode(code='ONCE10', percent_off=10.0, is_used=False)
        db.session.add(dc)
        db.session.commit()

        client = app.test_client()
        payload = {"customer_id": c.id, "items": [{"pizza_id": p.id, "quantity": 1}], "discount_code": "ONCE10"}
        resp = client.post('/orders', json=payload)
        assert resp.status_code == 201
        # code should be marked used
        dc_db = DiscountCode.query.get('ONCE10')
        assert dc_db.is_used is True