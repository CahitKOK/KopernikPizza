"""
Staff Reports Module
Provides reporting functionality for restaurant staff including:
- Undelivered orders
- Top-selling pizzas (past month)
- Earnings reports by demographics (gender, age, postal code)
"""

from extensions import db
from models import Order, OrderItem, Pizza, Customer, DeliveryPerson
from sqlalchemy import text, func
from datetime import datetime, timedelta
from typing import List, Dict, Any


def get_undelivered_orders() -> List[Dict[str, Any]]:
    """
    Get all orders that haven't been delivered yet.
    Returns list of orders with customer and delivery person info.
    """
    sql = text("""
        SELECT 
            o.id as order_id,
            o.order_date,
            o.total,
            o.status,
            c.name as customer_name,
            c.phone as customer_phone,
            c.address as customer_address,
            dp.name as delivery_person,
            dp.last_delivery_time
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        LEFT JOIN delivery_persons dp ON dp.id = o.delivery_person_id
        WHERE o.status IN ('pending', 'confirmed', 'preparing')
        ORDER BY o.order_date ASC
    """)
    
    result = db.session.execute(sql).fetchall()
    
    orders = []
    for row in result:
        orders.append({
            'order_id': row[0],
            'order_date': row[1],
            'total': row[2],
            'status': row[3],
            'customer_name': row[4],
            'customer_phone': row[5],
            'customer_address': row[6],
            'delivery_person': row[7],
            'delivery_person_last_active': row[8]
        })
    
    return orders


def get_top_pizzas_past_month(limit: int = 3) -> List[Dict[str, Any]]:
    """
    Get top N pizzas sold in the past month.
    Returns pizza names with total quantities sold.
    """
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    sql = text("""
        SELECT 
            p.name as pizza_name,
            SUM(oi.quantity) as total_sold,
            COUNT(DISTINCT o.id) as orders_count,
            AVG(oi.quantity) as avg_per_order
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        JOIN pizzas p ON p.id = oi.pizza_id
        WHERE o.order_date >= :month_ago
        GROUP BY p.id, p.name
        ORDER BY total_sold DESC
        LIMIT :limit
    """)
    
    result = db.session.execute(sql, {
        'month_ago': one_month_ago,
        'limit': limit
    }).fetchall()
    
    pizzas = []
    for row in result:
        pizzas.append({
            'pizza_name': row[0],
            'total_sold': row[1],
            'orders_count': row[2],
            'avg_per_order': float(row[3]) if row[3] else 0
        })
    
    return pizzas


def get_earnings_by_gender() -> List[Dict[str, Any]]:
    """
    Get earnings breakdown by customer gender.
    Note: This is a mock implementation as we don't have gender field.
    In real implementation, you'd add a gender field to Customer model.
    """
    # Mock data for demonstration - in real app, add gender field to Customer
    sql = text("""
        SELECT 
            CASE 
                WHEN c.id % 2 = 0 THEN 'Female'
                ELSE 'Male' 
            END as gender,
            COUNT(DISTINCT o.id) as total_orders,
            SUM(o.total) as total_earnings,
            AVG(o.total) as avg_order_value
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE o.total IS NOT NULL
        GROUP BY (c.id % 2)
        ORDER BY total_earnings DESC
    """)
    
    result = db.session.execute(sql).fetchall()
    
    earnings = []
    for row in result:
        earnings.append({
            'gender': row[0],
            'total_orders': row[1],
            'total_earnings': float(row[2]) if row[2] else 0,
            'avg_order_value': float(row[3]) if row[3] else 0
        })
    
    return earnings


def get_earnings_by_age_group() -> List[Dict[str, Any]]:
    """
    Get earnings breakdown by customer age groups.
    Uses birthday field to calculate age ranges.
    """
    sql = text("""
        SELECT 
            CASE 
                WHEN c.birthday IS NULL THEN 'Unknown'
                WHEN DATE('now') - c.birthday < 25 THEN '18-25'
                WHEN DATE('now') - c.birthday < 35 THEN '26-35'
                WHEN DATE('now') - c.birthday < 45 THEN '36-45'
                WHEN DATE('now') - c.birthday < 55 THEN '46-55'
                ELSE '55+'
            END as age_group,
            COUNT(DISTINCT o.id) as total_orders,
            SUM(o.total) as total_earnings,
            AVG(o.total) as avg_order_value,
            COUNT(DISTINCT c.id) as unique_customers
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE o.total IS NOT NULL
        GROUP BY age_group
        ORDER BY total_earnings DESC
    """)
    
    result = db.session.execute(sql).fetchall()
    
    earnings = []
    for row in result:
        earnings.append({
            'age_group': row[0],
            'total_orders': row[1],
            'total_earnings': float(row[2]) if row[2] else 0,
            'avg_order_value': float(row[3]) if row[3] else 0,
            'unique_customers': row[4]
        })
    
    return earnings


def get_earnings_by_postal_code() -> List[Dict[str, Any]]:
    """
    Get earnings breakdown by customer postal codes.
    Extracts postal code from customer address.
    """
    sql = text("""
        SELECT 
            SUBSTR(c.address, -5) as postal_code,
            COUNT(DISTINCT o.id) as total_orders,
            SUM(o.total) as total_earnings,
            AVG(o.total) as avg_order_value,
            COUNT(DISTINCT c.id) as unique_customers
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE o.total IS NOT NULL
        GROUP BY postal_code
        HAVING total_orders >= 1
        ORDER BY total_earnings DESC
        LIMIT 10
    """)
    
    result = db.session.execute(sql).fetchall()
    
    earnings = []
    for row in result:
        earnings.append({
            'postal_code': row[0],
            'total_orders': row[1],
            'total_earnings': float(row[2]) if row[2] else 0,
            'avg_order_value': float(row[3]) if row[3] else 0,
            'unique_customers': row[4]
        })
    
    return earnings


def get_monthly_summary() -> Dict[str, Any]:
    """
    Get comprehensive monthly summary for management.
    """
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Total orders and revenue this month
    sql = text("""
        SELECT 
            COUNT(DISTINCT o.id) as total_orders,
            SUM(o.total) as total_revenue,
            AVG(o.total) as avg_order_value,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            SUM(oi.quantity) as total_pizzas_sold
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        WHERE o.order_date >= :month_ago
          AND o.total IS NOT NULL
    """)
    
    result = db.session.execute(sql, {'month_ago': one_month_ago}).fetchone()
    
    if result:
        return {
            'period': 'Past 30 days',
            'total_orders': result[0] or 0,
            'total_revenue': float(result[1]) if result[1] else 0,
            'avg_order_value': float(result[2]) if result[2] else 0,
            'unique_customers': result[3] or 0,
            'total_pizzas_sold': result[4] or 0
        }
    
    return {
        'period': 'Past 30 days',
        'total_orders': 0,
        'total_revenue': 0,
        'avg_order_value': 0,
        'unique_customers': 0,
        'total_pizzas_sold': 0
    }


if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        print("🍕 MAMMA MIA'S STAFF REPORTS 🍕\n")
        
        print("=== UNDELIVERED ORDERS ===")
        undelivered = get_undelivered_orders()
        for order in undelivered:
            print(f"Order #{order['order_id']} - {order['customer_name']} - €{order['total']:.2f}")
            print(f"   Status: {order['status']} | Address: {order['customer_address']}")
            print(f"   Delivery: {order['delivery_person'] or 'Not assigned'}")
            print()
        
        print("=== TOP 3 PIZZAS (PAST MONTH) ===")
        top_pizzas = get_top_pizzas_past_month(3)
        for i, pizza in enumerate(top_pizzas, 1):
            print(f"{i}. {pizza['pizza_name']}: {pizza['total_sold']} sold ({pizza['orders_count']} orders)")
        
        print("\n=== MONTHLY SUMMARY ===")
        summary = get_monthly_summary()
        print(f"Orders: {summary['total_orders']} | Revenue: €{summary['total_revenue']:.2f}")
        print(f"Avg Order: €{summary['avg_order_value']:.2f} | Customers: {summary['unique_customers']}")
        print(f"Pizzas Sold: {summary['total_pizzas_sold']}")
        
        print("\n=== EARNINGS BY AGE GROUP ===")
        age_earnings = get_earnings_by_age_group()
        for group in age_earnings:
            print(f"{group['age_group']}: €{group['total_earnings']:.2f} ({group['total_orders']} orders)")