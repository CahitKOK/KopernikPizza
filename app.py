from flask import Flask
from config import Config
from extensions import db
from models import Pizza  # Import Pizza model

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

import models

@app.route("/")
def hello():
    """
    Home page with welcome message and navigation to menu.
    """
    return '''
    <h1>🍕 Kopernik Pizza is running! 🍕</h1>
    <p>Welcome to Mamma Mia's Pizza!</p>
    <a href="/menu" style="
        background-color: #ff6b6b; 
        color: white; 
        padding: 15px 25px; 
        text-decoration: none; 
        border-radius: 5px; 
        font-size: 18px;
        display: inline-block;
        margin: 20px 0;
    ">🍕 View Menu</a>
    '''

@app.route("/menu")
def menu():
    """
    Display pizza menu with dynamic pricing and dietary labels.
    Shows all pizzas with calculated prices based on ingredients.
    """
    pizzas = Pizza.query.all()
    
    menu_html = '''
    <h1>🍕 MAMMA MIA'S PIZZA MENU 🍕</h1>
    <a href="/" style="
        background-color: #4CAF50; 
        color: white; 
        padding: 10px 20px; 
        text-decoration: none; 
        border-radius: 5px;
        margin-bottom: 20px;
        display: inline-block;
    ">← Back to Home</a>
    <hr>
    '''
    
    for pizza in pizzas:
        price = pizza.calculate_price()
        
        # Labels
        labels = []
        if pizza.is_vegan():
            labels.append("🌿 VEGAN")
        elif pizza.is_vegetarian():
            labels.append("🌱 VEGETARIAN")
        
        label_str = " ".join(labels)
        
        menu_html += f"<h3>🍕 {pizza.name.upper()} - €{price:.2f} {label_str}</h3>"
        menu_html += f"<p><em>{pizza.description}</em></p>"
        
        # Show ingredients
        ingredient_names = []
        for pi in pizza.pizza_ingredients:
            ingredient_names.append(f"{pi.ingredient.name} ({pi.quantity})")
        menu_html += f"<p><strong>Ingredients:</strong> {', '.join(ingredient_names)}</p>"
        menu_html += "<hr>"
    
    return menu_html

if __name__ == "__main__":
    app.run(debug=True)
