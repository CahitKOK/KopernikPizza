from app import app
from extensions import db
from models import *
from datetime import datetime

with app.app_context():
    # Clear existing data
    db.session.query(OrderItem).delete()
    db.session.query(Order).delete()
    db.session.query(PizzaIngredient).delete()
    db.session.query(Pizza).delete()
    db.session.query(Ingredient).delete()
    db.session.query(Customer).delete()
    
    # Add 15 ingredients (more than required 10)
    ingredients = [
        Ingredient(name="Mozzarella", cost_per_unit=2.50, is_vegetarian=True, is_vegan=False),
        Ingredient(name="Tomato Sauce", cost_per_unit=0.80, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Pepperoni", cost_per_unit=3.20, is_vegetarian=False, is_vegan=False),
        Ingredient(name="Mushrooms", cost_per_unit=1.50, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Bell Peppers", cost_per_unit=1.20, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Olives", cost_per_unit=2.00, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Ham", cost_per_unit=3.80, is_vegetarian=False, is_vegan=False),
        Ingredient(name="Vegan Cheese", cost_per_unit=4.00, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Basil", cost_per_unit=1.00, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Chicken", cost_per_unit=4.50, is_vegetarian=False, is_vegan=False),
        Ingredient(name="Red Onions", cost_per_unit=0.90, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Bacon", cost_per_unit=4.20, is_vegetarian=False, is_vegan=False),
        Ingredient(name="Pineapple", cost_per_unit=2.10, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Spinach", cost_per_unit=1.80, is_vegetarian=True, is_vegan=True),
        Ingredient(name="Feta Cheese", cost_per_unit=3.50, is_vegetarian=True, is_vegan=False)
    ]
    
    for ingredient in ingredients:
        db.session.add(ingredient)
    
    # Add 12 pizzas (more than required 10)
    pizzas = [
        Pizza(name="Margherita", description="Classic tomato and mozzarella"),
        Pizza(name="Pepperoni", description="Pepperoni with mozzarella"),
        Pizza(name="Vegetarian", description="Bell peppers, mushrooms, olives"),
        Pizza(name="Vegan Delight", description="Vegan cheese, tomatoes, basil"),
        Pizza(name="Meat Lovers", description="Pepperoni, ham, chicken"),
        Pizza(name="Hawaiian", description="Ham and pineapple (controversial!)"),
        Pizza(name="BBQ Chicken", description="Chicken with red onions"),
        Pizza(name="Mediterranean", description="Olives, feta, spinach"),
        Pizza(name="Bacon Supreme", description="Bacon, mushrooms, peppers"),
        Pizza(name="Vegan Veggie", description="All veggies with vegan cheese"),
        Pizza(name="Spinach & Feta", description="Fresh spinach with feta cheese"),
        Pizza(name="Four Cheese", description="Mozzarella, feta, vegan cheese blend")
    ]
    
    for pizza in pizzas:
        db.session.add(pizza)
    
    db.session.commit()
    
    # Add pizza-ingredient relationships
    pizza_ingredients = [
        # Margherita (1)
        (1, 1, 1.0), (1, 2, 0.5), (1, 9, 0.2),
        # Pepperoni (2)
        (2, 1, 1.0), (2, 2, 0.5), (2, 3, 0.8),
        # Vegetarian (3)
        (3, 1, 1.0), (3, 2, 0.5), (3, 4, 0.6), (3, 5, 0.4), (3, 6, 0.3),
        # Vegan Delight (4)
        (4, 8, 1.0), (4, 2, 0.5), (4, 9, 0.3),
        # Meat Lovers (5)
        (5, 1, 1.0), (5, 2, 0.5), (5, 3, 0.8), (5, 7, 0.6), (5, 10, 0.7),
        # Hawaiian (6)
        (6, 1, 1.0), (6, 2, 0.5), (6, 7, 0.7), (6, 13, 0.5),
        # BBQ Chicken (7)
        (7, 1, 1.0), (7, 2, 0.5), (7, 10, 0.8), (7, 11, 0.4),
        # Mediterranean (8)
        (8, 1, 0.5), (8, 15, 0.8), (8, 2, 0.5), (8, 6, 0.4), (8, 14, 0.6),
        # Bacon Supreme (9)
        (9, 1, 1.0), (9, 2, 0.5), (9, 12, 0.8), (9, 4, 0.5), (9, 5, 0.4),
        # Vegan Veggie (10)
        (10, 8, 1.0), (10, 2, 0.5), (10, 4, 0.5), (10, 5, 0.4), (10, 11, 0.3), (10, 14, 0.4),
        # Spinach & Feta (11)
        (11, 1, 0.5), (11, 15, 1.0), (11, 2, 0.5), (11, 14, 0.8),
        # Four Cheese (12)
        (12, 1, 0.8), (12, 8, 0.5), (12, 15, 0.7)
    ]
    
    for pizza_id, ingredient_id, quantity in pizza_ingredients:
        db.session.add(PizzaIngredient(pizza_id=pizza_id, ingredient_id=ingredient_id, quantity=quantity))
    
    # Add customers
    customers = [
        Customer(name="Mario Rossi", email="mario@email.com", phone="1234567890", address="Via Roma 1, 00100 Rome"),
        Customer(name="Luigi Verde", email="luigi@email.com", phone="0987654321", address="Via Milano 2, 20100 Milan"),
        Customer(name="Anna Bianchi", email="anna@email.com", phone="5555555555", address="Via Napoli 3, 80100 Naples"),
        Customer(name="Sofia Russo", email="sofia@email.com", phone="1111111111", address="Via Torino 4, 10100 Turin"),
        Customer(name="Marco Ferrari", email="marco@email.com", phone="2222222222", address="Via Firenze 5, 50100 Florence"),
        Customer(name="Giulia Romano", email="giulia@email.com", phone="3333333333", address="Via Bologna 6, 40100 Bologna"),
        Customer(name="Alessandro Costa", email="ale@email.com", phone="4444444444", address="Via Genova 7, 16100 Genoa"),
        Customer(name="Francesca Ricci", email="fra@email.com", phone="6666666666", address="Via Palermo 8, 90100 Palermo"),
        Customer(name="Davide Bruno", email="davide@email.com", phone="7777777777", address="Via Venezia 9, 30100 Venice"),
        Customer(name="Chiara Greco", email="chiara@email.com", phone="8888888888", address="Via Bari 10, 70100 Bari")
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    # Add 3 delivery persons with postal codes
    delivery_persons = [
        DeliveryPerson(name="Giuseppe Bianchi", postal_codes="00100,00200,00300", is_available=True),
        DeliveryPerson(name="Maria Rossi", postal_codes="20100,20200,20300", is_available=True), 
        DeliveryPerson(name="Antonio Verde", postal_codes="80100,90100,70100", is_available=True)
    ]
    
    for person in delivery_persons:
        db.session.add(person)
    
    # Add drinks
    drinks = [
        Drink(name="Coca Cola", price=2.50, size="330ml"),
        Drink(name="Pepsi", price=2.50, size="330ml"),
        Drink(name="Orange Juice", price=3.00, size="250ml"),
        Drink(name="Water", price=1.50, size="500ml"),
        Drink(name="Beer", price=4.00, size="330ml")
    ]
    
    for drink in drinks:
        db.session.add(drink)
    
    # Add desserts  
    desserts = [
        Dessert(name="Tiramisu", price=5.50, description="Classic Italian dessert"),
        Dessert(name="Gelato", price=4.00, description="Italian ice cream"),
        Dessert(name="Cannoli", price=4.50, description="Sicilian pastry"),
        Dessert(name="Panna Cotta", price=5.00, description="Creamy dessert")
    ]
    
    for dessert in desserts:
        db.session.add(dessert)

    db.session.commit()
    print("Sample data created successfully!")
    print(f"Created {len(pizzas)} pizzas and {len(ingredients)} ingredients")
    print(f"Created {len(customers)} customers")
    print(f"Created {len(delivery_persons)} delivery persons")
    print(f"Created {len(drinks)} drinks and {len(desserts)} desserts")
    
    # Show menu with calculated prices
    print("\n=== MENU WITH DYNAMIC PRICES ===")
    pizzas = Pizza.query.all()
    for pizza in pizzas:
        price = pizza.calculate_price()
        veg_label = "🌱 VEGETARIAN" if pizza.is_vegetarian() else ""
        vegan_label = "🌿 VEGAN" if pizza.is_vegan() else ""
        labels = f"{vegan_label} {veg_label}".strip()
        print(f"{pizza.name}: €{price:.2f} {labels}")