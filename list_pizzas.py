from app import app
from models import Pizza
import os


def print_menu():
    with app.app_context():
        pizzas = Pizza.query.all()
        if not pizzas:
            print('No pizzas found in the database.')
            print('If you want sample data, run: python seed.py')
            return

        print('=== MENU ===')
        for p in pizzas:
            price = p.calculate_price()
            labels = []
            if p.is_vegan():
                labels.append('VEGAN')
            elif p.is_vegetarian():
                labels.append('VEGETARIAN')
            label_str = ' '.join(labels)
            print(f"{p.name} - €{price:.2f} {label_str}")
            print(f"  {p.description}")
            ing = ', '.join([f"{pi.ingredient.name} ({pi.quantity})" for pi in p.pizza_ingredients])
            print(f"  Ingredients: {ing}")
            print()


if __name__ == '__main__':
    # Auto-seed if requested via environment variable
    if os.environ.get('AUTO_SEED') == '1':
        print('AUTO_SEED=1 detected: running seed.py to populate sample data...')
        os.system('python seed.py')

    print_menu()
