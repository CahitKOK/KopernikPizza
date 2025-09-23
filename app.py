from flask import Flask, render_template, request, jsonify
from config import Config
from extensions import db
from models import Pizza  # Import Pizza model
from models import Customer, Order, OrderItem, DiscountCode
from utils import apply_discounts, assign_delivery_person_sql

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
    return render_template('menu.html', pizzas=pizzas)


@app.route("/checkout")
def checkout():
    pizzas = Pizza.query.all()

    pizzas_data = []
    for p in pizzas:
        pizzas_data.append({
            "id": p.id,
            "name": p.name,
            "price": round(p.calculate_price(), 2) if hasattr(p, "calculate_price") else float(p.base_price or 0)
        })

    return render_template("checkout.html", pizzas=pizzas_data)



@app.route('/orders', methods=['POST'])
def create_order():
    """Create an order.

    Expected JSON:
    {
      "customer_id": <id> OR {"name":..., "email":..., "phone":..., "address":..., "birthday": "YYYY-MM-DD"},
      "items": [{"pizza_id": <id>, "quantity": <int>}],
      "discount_code": "CODE" (optional)
    }
    """
    data = request.get_json() or {}
    # basic validation
    items = data.get('items')
    if not items or not isinstance(items, list):
        return jsonify({"error": "items is required and must be a list"}), 400

    with app.app_context():
        # resolve or create customer
        cust = None
        if 'customer_id' in data:
            cust = Customer.query.get(data['customer_id'])
            if not cust:
                return jsonify({"error": "customer_id not found"}), 404
        else:
            cdata = data.get('customer') or {}
            try:
                birthday = None
                if cdata.get('birthday'):
                    from datetime import datetime
                    birthday = datetime.fromisoformat(cdata['birthday']).date()
                cust = Customer(name=cdata['name'], email=cdata['email'], phone=cdata['phone'], address=cdata['address'], birthday=birthday)
                db.session.add(cust)
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"invalid customer data: {e}"}), 400

        # create order skeleton
        from datetime import datetime
        order = Order(customer_id=cust.id, order_date=datetime.utcnow(), status='pending')
        db.session.add(order)
        db.session.flush()  # get order.id

        # create order items
        for it in items:
            pid = it.get('pizza_id')
            qty = int(it.get('quantity', 1))
            if qty <= 0:
                db.session.rollback()
                return jsonify({"error": "quantity must be > 0"}), 400
            pizza = Pizza.query.get(pid)
            if not pizza:
                db.session.rollback()
                return jsonify({"error": f"pizza_id {pid} not found"}), 404
            oi = OrderItem(order_id=order.id, pizza_id=pid, quantity=qty)
            db.session.add(oi)

        # resolve discount code if present
        code_obj = None
        code = data.get('discount_code')
        if code:
            code_obj = DiscountCode.query.get(code)
            if not code_obj:
                db.session.rollback()
                return jsonify({"error": "discount code not found"}), 404

        # compute total using apply_discounts
        total = apply_discounts(order, code_obj)
        order.total = total

        # if discount code is single-use, mark used (atomic)
        if code_obj and not code_obj.is_used:
            code_obj.is_used = True
            db.session.add(code_obj)

        db.session.add(order)
        db.session.commit()

        # assign delivery person (this updates last_delivery_time inside function)
        dp = assign_delivery_person_sql(order)

        result = {
            "order_id": order.id,
            "total": order.total,
            "delivery_person": dp.name if dp else None
        }
        return jsonify(result), 201

if __name__ == "__main__":
    # Run on all interfaces so localhost and other hosts can reach it if necessary
    app.run(debug=True, host="0.0.0.0", port=5000)
