from extensions import db
from models import Order, DiscountCode, DeliveryPerson, DeliveryZone, Customer
from typing import Optional
from datetime import datetime, timedelta
import re
from sqlalchemy import text


def calculate_order_total(order: Order, discount_code: Optional[DiscountCode] = None) -> float:
    total = 0.0
    for item in order.items:
        # Handle both old and new OrderItem formats
        if hasattr(item, 'item_price'):
            # New format with item_price property
            total += item.item_price * item.quantity
        elif hasattr(item, 'pizza') and item.pizza:
            # Legacy format with pizza relationship
            total += item.pizza.calculate_price() * item.quantity
        else:
            # Fallback: calculate manually based on item_type
            if item.item_type == 'pizza':
                from models import Pizza
                pizza = Pizza.query.get(item.item_id)
                if pizza:
                    total += pizza.calculate_price() * item.quantity
            elif item.item_type == 'drink':
                from models import Drink
                drink = Drink.query.get(item.item_id)
                if drink:
                    total += float(drink.price) * item.quantity
            elif item.item_type == 'dessert':
                from models import Dessert
                dessert = Dessert.query.get(item.item_id)
                if dessert:
                    total += float(dessert.price) * item.quantity
    
    if discount_code and not discount_code.is_used:
        try:
            percent = float(discount_code.percent_off)
            if 0 <= percent <= 100:
                total = total * (1 - percent / 100.0)
        except Exception:
            pass
    return round(total, 2)


def apply_discounts(order: Order, discount_code: Optional[DiscountCode] = None) -> float:
    base_total = calculate_order_total(order, None)

    loyalty_discount = 0.0
    if order.customer:
        sql = text(
            """
            SELECT COALESCE(SUM(oi.quantity),0) FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.customer_id = :cid
            """
        )
        res = db.session.execute(sql, {"cid": order.customer.id}).scalar()
        if res and res >= 10:
            loyalty_discount = 0.10

    birthday_deduction = 0.0
    if order.customer and order.customer.birthday:
        today = datetime.utcnow().date()
        b = order.customer.birthday
        if (b.month, b.day) == (today.month, today.day):
            cheapest_pizza = None
            cheapest_drink = None
            
            # Find cheapest pizza and cheapest drink in order
            for item in order.items:
                if item.item_type == 'pizza' or (hasattr(item, 'pizza') and item.pizza):
                    # Handle both new and old format
                    if hasattr(item, 'pizza') and item.pizza:
                        price = item.pizza.calculate_price()
                    else:
                        # New format - get pizza object
                        from models import Pizza
                        pizza = Pizza.query.get(item.item_id)
                        price = pizza.calculate_price() if pizza else 0
                    
                    if cheapest_pizza is None or price < cheapest_pizza:
                        cheapest_pizza = price
                        
                elif item.item_type == 'drink':
                    # Handle drinks
                    from models import Drink
                    drink = Drink.query.get(item.item_id)
                    price = float(drink.price) if drink else 0
                    
                    if cheapest_drink is None or price < cheapest_drink:
                        cheapest_drink = price
            
            # Apply birthday discount: FREE cheapest pizza + FREE cheapest drink
            # BUT ONLY if customer orders BOTH pizza AND drink
            birthday_deduction = 0.0
            if cheapest_pizza is not None and cheapest_drink is not None:
                # Customer has both pizza and drink - give both free!
                birthday_deduction = cheapest_pizza + cheapest_drink

    code_discount = 0.0
    if discount_code and not discount_code.is_used:
        try:
            pct = float(discount_code.percent_off)
            if 0 <= pct <= 100:
                code_discount = pct / 100.0
        except Exception:
            code_discount = 0.0

    total = base_total
    if loyalty_discount:
        total = total * (1 - loyalty_discount)
    if code_discount:
        total = total * (1 - code_discount)
    total = total - birthday_deduction
    if total < 0:
        total = 0.0
    return round(total, 2)


from extensions import db
from models import DeliveryPerson, DeliveryZone, Order
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import re

def assign_delivery_person_sql(order: Order) -> Optional[DeliveryPerson]:
    cust = order.customer
    if not cust or not cust.address:
        print("❌ No customer or address")
        return None

    m = re.search(r"(\d{5})", cust.address)
    if not m:
        print(f"❌ No postcode match in address: {cust.address}")
        return None

    prefix = m.group(1)[:3]
    print(f"✅ Extracted prefix: {prefix} from address: {cust.address}")

    cutoff_dt = datetime.utcnow() - timedelta(minutes=30)
    sql = text(
        """
        SELECT dp.id 
        FROM delivery_persons dp
        JOIN delivery_zones dz ON dz.delivery_person_id = dp.id
        WHERE dz.postcode_prefix = :prefix
          AND (dp.last_delivery_time IS NULL OR dp.last_delivery_time <= :cutoff)
        ORDER BY dp.last_delivery_time ASC
        LIMIT 1
        """
    )
    row = db.session.execute(sql, {"prefix": prefix, "cutoff": cutoff_dt}).fetchone()
    print("🔎 SQL row:", row)

    if not row:
        return None

    dp_id = row[0]
    dp = DeliveryPerson.query.get(dp_id)
    print("✅ Assigned delivery person:", dp)

    if not dp:
        return None

    order.delivery_person_id = dp.id
    dp.last_delivery_time = datetime.utcnow()
    db.session.add(order)
    db.session.add(dp)
    db.session.commit()
    return dp
from flask import Flask, request, jsonify
from extensions import db