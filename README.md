# 🍕 Kopernik Pizza

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
