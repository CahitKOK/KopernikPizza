from app import app
from models import Pizza, Ingredient, PizzaIngredient

with app.app_context():
    print("🍕 MAMMA MIA'S PIZZA MENU 🍕\n")
    
    pizzas = Pizza.query.all()
    
    for pizza in pizzas:
        price = pizza.calculate_price()
        
        # Labels
        labels = []
        if pizza.is_vegan():
            labels.append("🌿 VEGAN")
        elif pizza.is_vegetarian():
            labels.append("🌱 VEGETARIAN")
        
        label_str = " ".join(labels)
        
        print(f"🍕 {pizza.name.upper()} - €{price:.2f} {label_str}")
        print(f"   {pizza.description}")
        
        # Show ingredients
        print("   Ingredients:", end=" ")
        ingredient_names = []
        for pi in pizza.pizza_ingredients:
            ingredient_names.append(f"{pi.ingredient.name} ({pi.quantity})")
        print(", ".join(ingredient_names))
        print()