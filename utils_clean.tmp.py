from extensions import db
from models import Order, DiscountCode, DeliveryPerson, DeliveryZone, Customer
from typing import Optional
from datetime import datetime, timedelta
import re
from sqlalchemy import text


def calculate_order_total(order: Order, discount_code: Optional[DiscountCode] = None) -> float:
    total = 0.0
    for item in order.items:
        total += item.pizza.calculate_price() * item.quantity
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
            cheapest = None
            for item in order.items:
                price = item.pizza.calculate_price()
                if cheapest is None or price < cheapest:
                    cheapest = price
            if cheapest:
                birthday_deduction = cheapest

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


def assign_delivery_person_sql(order: Order) -> Optional[DeliveryPerson]:
    cust = order.customer
    if not cust or not cust.address:
        return None
    m = re.search(r"(\d{5})", cust.address)
    if not m:
        return None
    prefix = m.group(1)[:3]
    sql = text(
        """
        SELECT dp.id FROM delivery_persons dp
        JOIN delivery_zones dz ON dz.delivery_person_id = dp.id
        WHERE dz.postcode_prefix = :prefix
          AND (dp.last_delivery_time IS NULL OR dp.last_delivery_time <= :cutoff)
        ORDER BY dp.last_delivery_time ASC
        LIMIT 1
        """
    )
    cutoff_dt = datetime.utcnow() - timedelta(minutes=30)
    row = db.session.execute(sql, {"prefix": prefix, "cutoff": cutoff_dt}).fetchone()
    if not row:
        return None
    dp_id = row[0]
    dp = DeliveryPerson.query.get(dp_id)
    if not dp:
        return None
    order.delivery_person_id = dp.id
    dp.last_delivery_time = datetime.utcnow()
    db.session.add(order)
    db.session.add(dp)
    db.session.commit()
    return dp


def assign_delivery_person(order: Order) -> Optional[DeliveryPerson]:
    cust = order.customer
    if not cust or not cust.address:
        return None
    m = re.search(r"(\d{5})", cust.address)
    if not m:
        return None
    prefix = m.group(1)[:3]
    zone = DeliveryZone.query.filter_by(postcode_prefix=prefix).first()
    if not zone:
        return None
    return zone.delivery_person
