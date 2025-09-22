from app import app
from extensions import db
from models import Customer, Order, OrderItem, Pizza, DiscountCode
from utils import calculate_order_total, assign_delivery_person
from datetime import datetime

def run():
    with app.app_context():
        # Ensure we have data from seed.py; if not, instruct user
        customer = Customer.query.first()
        pizza = Pizza.query.first()
        if not customer or not pizza:
            print("No customers or pizzas found. Run seed.py first.")
            return

        # Create a sample order
        order = Order(customer_id=customer.id, order_date=datetime.utcnow(), status='pending')
        db.session.add(order)
        db.session.commit()

        # Add an order item
        item = OrderItem(order_id=order.id, pizza_id=pizza.id, quantity=2)
        db.session.add(item)
        db.session.commit()

        # Refresh order from DB to load items and relationships
        order = Order.query.get(order.id)

        # Calculate total without discount
        total = calculate_order_total(order)
        print(f"Order {order.id} total (no discount): €{total:.2f}")

        # Optionally create a discount code and test
        disc = DiscountCode(code='TEST10', percent_off=10.0, is_used=False)
        db.session.add(disc)
        db.session.commit()

        total_with_disc = calculate_order_total(order, disc)
        print(f"Order {order.id} total (with 10%): €{total_with_disc:.2f}")

        # Assign delivery person
        dp = assign_delivery_person(order)
        if dp:
            print(f"Assigned delivery person: {dp.name}")
        else:
            print("No delivery person found for this order's postcode.")

if __name__ == '__main__':
    run()
