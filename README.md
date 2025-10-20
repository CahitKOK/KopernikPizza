# 🍕 Kopernik Pizza
<img width="686" height="435" alt="image" src="https://github.com/user-attachments/assets/cb7fea2a-8353-4fa5-bdce-4a424a8c2249" />


A comprehensive database-driven pizza ordering system built with **Flask + SQLAlchemy ORM**.  
This project is part of the Maastricht University **KEN2110 – Databases** course.  

---

## 🚀 Core Features
- Flask web application with SQLAlchemy ORM
- Complete database models with relationships
- SQLite database (`kopernikpizza.db`)
- Dynamic pizza pricing with ingredients, VAT, and margin calculations
- Multi-tier discount system (birthday, loyalty, promotional codes)
- Delivery management with postcode zones and courier cooldown system
- Staff reporting dashboard with business analytics
- Transaction handling with rollback capabilities
- Database constraints and data integrity enforcement

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

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create and initialize database:
   ```bash
   python create_db.py
   python seed.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and visit: http://127.0.0.1:5000/

---

## 🍕 Application Features
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

## 📦 Order Management & Business Logic

### Complete Implementation
- **Order Placement**
  - Orders can be placed via `/orders` endpoint.
  - New customers are added automatically; existing customers can be reused.
  - Orders include linked `OrderItem` records for pizzas.

- **Customer Tracking**
  - Customer information (name, email, phone, address, birthday) stored in database.
  - Pizza count per customer tracked for loyalty discounts.

- **Discounts**
  - 🎂 **Birthday discount**: Customer receives the cheapest pizza for free on their birthday.
  - 🏆 **Loyalty discount**: After 10 pizzas, customer gets 10% off all future orders.
  - 💸 **Discount codes**: One-time codes supported, marked as used after redemption.

- **Delivery Assignment**
  - Delivery personnel linked to postcode prefixes (`DeliveryZone` table).
  - SQL-based assignment selects an available courier for the matching zone.
  - 🚲 **Cooldown rule**: After each delivery, courier is unavailable for 30 minutes.
  - If no courier is available → system returns: *"No delivery person available"*.

### 🎯 Technical Implementation
- Complete order lifecycle management with database persistence
- Automated discount calculation and application
- Intelligent delivery assignment with geographic zones
- Comprehensive business rule enforcement
- Full transaction support with error handling and rollback capabilities
- Staff dashboard with real-time analytics and reporting