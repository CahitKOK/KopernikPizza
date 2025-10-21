"""
Kopernik Pizza - Main Flask Application
"""

from flask import Flask, render_template, request, jsonify
from config import Config
from extensions import db
from models import Pizza, Customer, Order, OrderItem, DiscountCode, Drink, Dessert
from utils import apply_discounts, assign_delivery_person_sql
from staff_reports import (
    get_undelivered_orders, get_top_pizzas_past_month, 
    get_earnings_by_gender, get_earnings_by_age_group, 
    get_earnings_by_postal_code, get_monthly_summary
)
from transactions import create_order_transaction, test_transaction_rollback
from database_constraints import (
    add_database_constraints, test_constraint_violations, 
    get_constraint_status, validate_vegetarian_pizza_constraint
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

import models

@app.route("/")
def hello():
    """
    Home page with navigation links.
    """
    return '''
    <h1>🍕 Kopernik Pizza is running! 🍕</h1>
    <p>Welcome to Mamma Mia's Pizza!</p>
    <div style="margin: 20px 0;">
        <a href="/menu" style="
            background-color: #ff6b6b; 
            color: white; 
            padding: 15px 25px; 
            text-decoration: none; 
            border-radius: 5px; 
            font-size: 18px;
            display: inline-block;
            margin: 10px;
        ">🍕 View Menu</a>
        
        <a href="/staff" style="
            background-color: #2196f3; 
            color: white; 
            padding: 15px 25px; 
            text-decoration: none; 
            border-radius: 5px; 
            font-size: 18px;
            display: inline-block;
            margin: 10px;
        ">📊 Staff Dashboard</a>
    </div>
    '''

@app.route("/menu")
def menu():
    """
    Display complete menu with pizzas, drinks and desserts.
    """
    pizzas = Pizza.query.all()
    drinks = Drink.query.all()
    desserts = Dessert.query.all()
    return render_template('menu.html', pizzas=pizzas, drinks=drinks, desserts=desserts)


@app.route("/checkout")
def checkout():
    pizzas = Pizza.query.all()
    drinks = Drink.query.all()
    desserts = Dessert.query.all()

    pizzas_data = []
    for p in pizzas:
        pizzas_data.append({
            "id": p.id,
            "name": p.name,
            "price": round(p.calculate_price(), 2) if hasattr(p, "calculate_price") else float(p.base_price or 0),
            "type": "pizza"
        })

    drinks_data = []
    for d in drinks:
        drinks_data.append({
            "id": d.id,
            "name": d.name,
            "price": float(d.price),
            "type": "drink"
        })

    desserts_data = []
    for d in desserts:
        desserts_data.append({
            "id": d.id,
            "name": d.name,
            "price": float(d.price),
            "type": "dessert"
        })

    # Combine all items for JavaScript access
    all_items = pizzas_data + drinks_data + desserts_data
    
    return render_template("checkout.html", pizzas=pizzas_data, drinks=drinks_data, desserts=desserts_data, all_items=all_items)



@app.route('/orders', methods=['POST'])
def create_order():
    """
    Create an order with transaction handling.

    Expected JSON:
    {
      "customer_id": <id> OR {"customer": {"name":..., "email":..., "phone":..., "address":..., "birthday": "YYYY-MM-DD"}},
      "items": [{"pizza_id": <id>, "quantity": <int>}],
      "discount_code": "CODE" (optional)
    }
    """
    data = request.get_json() or {}
    
    # Use new transaction-safe order creation
    result = create_order_transaction(data)
    
    if result['success']:
        return jsonify({
            "success": True,
            "order_id": result['order_id'],
            "customer_name": result['customer_name'],
            "total": result['total'],
            "delivery_person": result['delivery_person'],
            "discount_applied": result['discount_applied'],
            "items_count": result['items_count']
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": result['error'],
            "error_type": result['error_type']
        }), 400


@app.route('/staff')
def staff_dashboard():
    """
    Staff dashboard with reports and analytics.
    """
    try:
        # Get all required reports
        undelivered = get_undelivered_orders()
        top_pizzas = get_top_pizzas_past_month(3)
        monthly_summary = get_monthly_summary()
        gender_earnings = get_earnings_by_gender()
        age_earnings = get_earnings_by_age_group()
        postal_earnings = get_earnings_by_postal_code()
        
        return render_template('staff_dashboard.html', 
                             undelivered_orders=undelivered,
                             top_pizzas=top_pizzas,
                             monthly_summary=monthly_summary,
                             gender_earnings=gender_earnings,
                             age_earnings=age_earnings,
                             postal_earnings=postal_earnings)
    except Exception as e:
        return f"<h1>Staff Dashboard Error</h1><p>{str(e)}</p><a href='/'>← Back to Home</a>"


@app.route('/staff/reports/undelivered')
def undelivered_orders_report():
    """API endpoint for undelivered orders report."""
    try:
        orders = get_undelivered_orders()
        return jsonify({"undelivered_orders": orders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/staff/reports/top-pizzas')
def top_pizzas_report():
    """API endpoint for top pizzas report."""
    try:
        pizzas = get_top_pizzas_past_month(3)
        return jsonify({"top_pizzas": pizzas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/staff/reports/earnings')
def earnings_report():
    """API endpoint for earnings breakdown reports."""
    try:
        return jsonify({
            "monthly_summary": get_monthly_summary(),
            "by_gender": get_earnings_by_gender(),
            "by_age_group": get_earnings_by_age_group(),
            "by_postal_code": get_earnings_by_postal_code()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/staff/test-transactions')
def test_transactions():
    """
    Test transaction rollback functionality.
    """
    try:
        results = test_transaction_rollback()
        
        html = "<h1>🔄 Transaction Rollback Tests</h1>"
        html += f"<p><strong>Results: {results['passed_tests']}/{results['total_tests']} tests passed</strong></p>"
        html += "<div style='font-family: monospace; background: #f5f5f5; padding: 20px; margin: 20px 0;'>"
        
        for test in results['results']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            html += f"<p><strong>{status} {test['test']}</strong><br>"
            html += f"Expected: {test['expected']}, Got: {test['actual']}<br>"
            html += f"Message: {test['message']}</p>"
        
        html += "</div>"
        html += "<a href='/staff'>← Back to Dashboard</a> | "
        html += "<a href='/'>← Home</a>"
        
        return html
    except Exception as e:
        return f"<h1>Transaction Test Error</h1><p>{str(e)}</p><a href='/staff'>← Back to Dashboard</a>"


@app.route('/staff/setup-constraints')
def setup_constraints():
    """
    Set up database constraints for data integrity.
    """
    try:
        results = add_database_constraints()
        
        html = "<h1>🛡️ Database Constraints Setup</h1>"
        html += "<div style='font-family: monospace; background: #f5f5f5; padding: 20px; margin: 20px 0;'>"
        
        for result in results:
            html += f"<p>{result}</p>"
        
        html += "</div>"
        html += "<a href='/staff/test-constraints'>🧪 Test Constraints</a> | "
        html += "<a href='/staff'>← Back to Dashboard</a>"
        
        return html
    except Exception as e:
        return f"<h1>Constraint Setup Error</h1><p>{str(e)}</p><a href='/staff'>← Back to Dashboard</a>"


@app.route('/staff/test-constraints')
def test_constraints():
    """
    Test database constraints.
    """
    try:
        test_results = test_constraint_violations()
        status_info = get_constraint_status()
        
        html = "<h1>🧪 Database Constraint Tests</h1>"
        
        # Show constraint status
        if 'error' not in status_info:
            html += f"<p><strong>Status:</strong> {status_info['triggers_installed']} constraints installed, "
            html += f"{status_info['current_violations']} violations found</p>"
        
        # Show test results
        passed = sum(1 for test in test_results if test['passed'])
        total = len(test_results)
        html += f"<p><strong>Test Results: {passed}/{total} tests passed</strong></p>"
        
        html += "<div style='font-family: monospace; background: #f5f5f5; padding: 20px; margin: 20px 0;'>"
        
        for test in test_results:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            html += f"<p><strong>{status} {test['test']}</strong><br>"
            html += f"Expected: {test['expected']}, Got: {test['actual']}<br>"
            html += f"Message: {test['message']}</p>"
        
        html += "</div>"
        html += "<a href='/staff/setup-constraints'>🛡️ Setup Constraints</a> | "
        html += "<a href='/staff'>← Back to Dashboard</a>"
        
        return html
    except Exception as e:
        return f"<h1>Constraint Test Error</h1><p>{str(e)}</p><a href='/staff'>← Back to Dashboard</a>"


if __name__ == "__main__":
    # Run on all interfaces so localhost and other hosts can reach it if necessary
    app.run(debug=True, host="0.0.0.0", port=5000)
