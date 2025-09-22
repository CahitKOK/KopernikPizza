# 🍕 Kopernik Pizza
<img width="686" height="435" alt="image" src="https://github.com/user-attachments/assets/cb7fea2a-8353-4fa5-bdce-4a424a8c2249" />


A database-driven pizza ordering system built with **Flask + SQLAlchemy ORM**.  
This project is part of the Maastricht University **KEN2110 – Databases** course.  

---

## 🚀 Features (Week 1–2)
- Flask app with SQLAlchemy ORM
- Database models: `Customer`, `Pizza`, `Order`
- SQLite database (`kopernikpizza.db`)
- Initial setup with migrations, static, and templates folders

Planned (next steps):
- Order items (many-to-many between Orders and Pizzas)
- Dynamic pizza pricing (ingredients, VAT, margin)
- Discounts & delivery rules
- Reports for staff

---

## 📂 Project Structure
KopernikPizza/
│── app.py # Flask entry point
│── config.py # Database configuration
│── models.py # ORM models
│── requirements.txt # Dependencies
│── migrations/ # (later) Alembic migrations
│── static/ # CSS/JS
│── templates/ # HTML templates
│── venv/ # Virtual environment (not in git)


---

## ⚙️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/CahitKOK/KopernikPizza.git
   cd KopernikPizza
2. Create virtual environment
   python -m venv venv
.\venv\Scripts\activate    # Windows PowerShell
# or
source venv/bin/activate   # Mac/Linux

3. Install dependencies
   pip install -r requirements.txt
4. Run the app
   python app.py
Database Setup
from app import db
db.create_all()
This creates kopernikpizza.db with initial tables : customers,pizzas,orders

---

# Kopernik Pizza - Week 3

Post-EU Pizza Scandal ordering system for Mamma Mia's Pizza.

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requiremnts.txt
```

2. Create database:
```bash
python create_db_v2.py
```

3. Seed with sample data:
```bash
python seed_week3.py
```

4. Run the app:
```bash
python app.py
```

5. Visit: http://127.0.0.1:5000/

## Features (Week 3)
- ✅ 12 pizzas with dynamic pricing
- ✅ 15 ingredients with costs
- ✅ Vegetarian/Vegan labeling
- ✅ Web interface with menu display
- ✅ 10 customers, 3 delivery persons
- ✅ Drinks and desserts

## Database Models
- `Customer` - Customer information
- `Pizza` - Pizzas with dynamic pricing
- `Ingredient` - Pizza ingredients with costs
- `PizzaIngredient` - Many-to-many relationship
- `Order`, `OrderItem` - Order management
- `DeliveryPerson` - Delivery staff

- `Drink`, `Dessert` - Additional menu items- `Drink`, `Dessert` - Additional menu items
