from extensions import db

# Customer file
class Customer(db.Model):
    """
    Customer model for pizza ordering system.
    Tracks customer info and relationships to orders.
    """
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)

    # relationships one customer can have many orders 
    orders = db.relationship('Order', back_populates='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.name}>"
# Ingredient table
class Ingredient(db.Model):
    """
    Ingredient model for pizza toppings.
    Tracks cost per unit and dietary restrictions (vegetarian/vegan).
    """
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)
    is_vegetarian = db.Column(db.Boolean, default=True)
    is_vegan = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Ingredient {self.name}>"

class PizzaIngredient(db.Model):
    __tablename__ = 'pizza_ingredients' 
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    
    pizza = db.relationship('Pizza', backref='pizza_ingredients')
    ingredient = db.relationship('Ingredient', backref='pizza_ingredients')

class Pizza(db.Model):
    """
    Pizza model with dynamic pricing based on ingredients.
    Price = (ingredient_costs + 40% margin + 9% VAT)
    """
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    # Remove price field - calculate dynamically
    
    order_items = db.relationship('OrderItem', back_populates='pizza', lazy=True)
    
    def calculate_price(self):
        """Calculate price: ingredients cost + 40% margin + 9% VAT"""
        total_cost = 0
        for pi in self.pizza_ingredients:
            total_cost += pi.ingredient.cost_per_unit * pi.quantity
        
        with_margin = total_cost * 1.40  # 40% margin
        with_vat = with_margin * 1.09    # 9% VAT
        return round(with_vat, 2)
    
    def is_vegetarian(self):
        return all(pi.ingredient.is_vegetarian for pi in self.pizza_ingredients)
    
    def is_vegan(self):
        return all(pi.ingredient.is_vegan for pi in self.pizza_ingredients)

    def __repr__(self):
        return f"<Pizza {self.name}>"
# Order table
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    # relationships one order belongs to one customer
    customer = db.relationship('Customer', back_populates='orders', lazy=True)
    # one order can have many order items
    order_items = db.relationship('OrderItem', back_populates='order', lazy=True)

    def __repr__(self):
        return f"<Order {self.id} - Customer {self.customer_id}>"
# OrderItem table
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # relationships one order item belongs to one order
    order = db.relationship('Order', back_populates='order_items', lazy=True)
    # one order item refers to one pizza
    pizza = db.relationship('Pizza', back_populates='order_items', lazy=True)

    def __repr__(self):
        return f"<OrderItem {self.id} - Order {self.order_id} - Pizza {self.pizza_id}>"

class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    postal_codes = db.Column(db.String(200), nullable=False)  # Comma-separated
    is_available = db.Column(db.Boolean, default=True)
    last_delivery_time = db.Column(db.DateTime, nullable=True)

class Drink(db.Model):
    __tablename__ = 'drinks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(50), nullable=True)

class Dessert(db.Model):
    __tablename__ = 'desserts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
# Note: Ensure to create the tables in the database by running create_db.py after defining models.
# Also, you can seed initial data using seed.py.
# Relationships summary:
# Customer 1---* Order
# Order 1---* OrderItem
# Pizza 1---* OrderItem
# This setup allows you to manage customers, pizzas, orders, and order items effectively.
# You can expand these models with more fields and relationships as needed.
# Remember to run the necessary scripts to create and seed the database.
# You can now use these models in your CRUD operations and other application logic.
# Example usage:
# from models import Customer, Pizza, Order, OrderItem
# new_customer = Customer(name="John Doe", email=" ...", phone="...", address="...")
# db.session.add(new_customer)  
# db.session.commit()
# db.session.rollback() if needed
# customer = Customer.query.first() 
# print(customer)
# customer.name = "Jane Doe"
# db.session.commit()
# db.session.delete(customer)
# db.session.commit()
# Refer to test_crud.py for more examples of CRUD operations.
# Make sure to handle exceptions and edge cases in your actual application code.
# Always test your models and database interactions thoroughly.
# This is a basic setup; you can enhance it with validations, methods, and more complex queries as needed.