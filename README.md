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

## 📊 Complete Feature Set

### Core Pizza Ordering System
- **Dynamic Pizza Pricing**: Ingredient cost calculation with 40% margin + 9% VAT
- **Menu Management**: 12 unique pizzas with 15+ ingredients
- **Dietary Classifications**: Automatic vegetarian/vegan labeling based on ingredients
- **Web Interface**: Modern responsive design with interactive cart system
- **Real-time Cart**: Client-side JavaScript with localStorage persistence
- **Customer Management**: Complete customer profiles with address and birthday tracking

### Advanced Discount & Loyalty System
- **Multi-tier Discounts**: Birthday (free cheapest pizza), loyalty (10% after 10 pizzas), promotional codes
- **Smart Discount Stacking**: Proper calculation order preventing negative totals
- **One-time Discount Codes**: Automatic marking as used after redemption
- **Historical Purchase Tracking**: SQL-based calculation of customer pizza history

### Intelligent Delivery Management
- **Geographic Zone Assignment**: Postcode prefix mapping to delivery personnel
- **Courier Cooldown System**: 30-minute unavailability after each delivery
- **Automatic Assignment**: SQL-based selection of available couriers
- **Delivery Tracking**: Last delivery time and availability status

### Staff Dashboard & Business Intelligence
- **Real-time Reporting**: Live dashboard with auto-refresh functionality
- **Undelivered Orders Tracking**: Complete order status monitoring
- **Sales Analytics**: Top-selling pizzas with detailed statistics
- **Revenue Breakdown**: Multi-dimensional analysis by demographics
  - Customer age group analysis (18-25, 26-35, 36-50, 51+)
  - Geographic revenue by postal code zones  
  - Gender-based spending patterns
- **Monthly Business Summary**: KPIs including total orders, revenue, average order value
- **Operational Metrics**: Customer count, pizza quantities, delivery performance

### Enterprise-Grade Transaction Management
- **ACID Compliance**: Full database transaction support with automatic rollback
- **Error Recovery**: Comprehensive exception handling with detailed logging
- **Data Validation**: Multi-step order validation (customer, items, business rules)
- **Custom Exceptions**: Specific error types for different failure scenarios
- **Transaction Testing**: Built-in rollback testing functionality

### Database Integrity & Advanced Constraints  
- **SQLite Triggers**: Advanced database-level constraints for data validation
- **Business Rule Enforcement**: Automatic validation of pricing, quantities, dates
- **Data Integrity Checks**: Positive costs, valid dates, non-zero quantities
- **Constraint Testing Framework**: Automated testing of all database constraints
- **Violation Detection**: Real-time monitoring of constraint violations

### EU Regulation & Compliance Framework
- **GDPR-Ready Architecture**: Privacy-compliant customer data structure
- **VAT Integration**: Automatic 9% VAT calculation on all transactions
- **Audit Trail System**: Complete transaction logging for regulatory compliance
- **Data Validation**: Strict input validation and sanitization
- **Birthday Privacy**: Secure handling of personal information

### Advanced SQL & Performance Features
- **Complex Query Optimization**: Multi-table joins with proper indexing strategy
- **Aggregate Analytics**: Advanced statistical calculations using SQL functions
- **Date Range Analysis**: Time-based reporting for business intelligence
- **Scalable Architecture**: Efficient database design for high-volume operations
- **Performance Monitoring**: Query optimization and execution time tracking

### Testing & Quality Assurance
- **Automated Test Suite**: Comprehensive testing of orders, models, and business logic
- **Transaction Rollback Testing**: Verification of error handling and data integrity
- **Constraint Violation Testing**: Systematic testing of database validation rules
- **End-to-End Testing**: Complete order lifecycle validation
- **Error Scenario Coverage**: Testing of edge cases and failure conditions