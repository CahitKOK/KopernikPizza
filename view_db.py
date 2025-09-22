from app import app
from models import Customer, Pizza, Order, OrderItem

with app.app_context():
    print("=== CUSTOMERS ===")
    customers = Customer.query.all()
    for customer in customers:
        print(f"{customer.id}: {customer.name} - {customer.email}")
    
    print("\n=== PIZZAS ===")
    pizzas = Pizza.query.all()
    for pizza in pizzas:
        print(f"{pizza.id}: {pizza.name} - ${pizza.price}")
    
    print("\n=== ORDERS ===")
    orders = Order.query.all()
    for order in orders:
        print(f"Order {order.id}: Customer {order.customer_id} - {order.status}")