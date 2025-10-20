"""
Database Constraints Module
Adds advanced constraints and validation rules to ensure data integrity.
"""

from extensions import db
from sqlalchemy import text, event, CheckConstraint
from models import Pizza, Ingredient, PizzaIngredient, Customer, Order
from typing import Dict, Any, List


def add_database_constraints():
    """
    Add advanced database constraints for data integrity.
    """
    constraints_sql = [
        # Ensure ingredient costs are positive
        """
        CREATE TRIGGER IF NOT EXISTS check_ingredient_cost
        BEFORE INSERT ON ingredients
        WHEN NEW.cost_per_unit <= 0
        BEGIN
            SELECT RAISE(ABORT, 'Ingredient cost must be greater than 0');
        END;
        """,
        
        # Ensure ingredient costs are positive on update
        """
        CREATE TRIGGER IF NOT EXISTS check_ingredient_cost_update
        BEFORE UPDATE ON ingredients
        WHEN NEW.cost_per_unit <= 0
        BEGIN
            SELECT RAISE(ABORT, 'Ingredient cost must be greater than 0');
        END;
        """,
        
        # Ensure valid birth dates (not in future, not too old)
        """
        CREATE TRIGGER IF NOT EXISTS check_customer_birthday
        BEFORE INSERT ON customers
        WHEN NEW.birthday IS NOT NULL AND (
            NEW.birthday > date('now') OR 
            NEW.birthday < date('now', '-120 years')
        )
        BEGIN
            SELECT RAISE(ABORT, 'Invalid birth date: must be between 120 years ago and today');
        END;
        """,
        
        # Ensure valid birth dates on update
        """
        CREATE TRIGGER IF NOT EXISTS check_customer_birthday_update
        BEFORE UPDATE ON customers  
        WHEN NEW.birthday IS NOT NULL AND (
            NEW.birthday > date('now') OR 
            NEW.birthday < date('now', '-120 years')
        )
        BEGIN
            SELECT RAISE(ABORT, 'Invalid birth date: must be between 120 years ago and today');
        END;
        """,
        
        # Ensure order quantities are positive
        """
        CREATE TRIGGER IF NOT EXISTS check_order_item_quantity
        BEFORE INSERT ON order_items
        WHEN NEW.quantity <= 0
        BEGIN
            SELECT RAISE(ABORT, 'Order item quantity must be greater than 0');
        END;
        """,
        
        # Ensure pizza ingredient quantities are positive
        """
        CREATE TRIGGER IF NOT EXISTS check_pizza_ingredient_quantity
        BEFORE INSERT ON pizza_ingredients
        WHEN NEW.quantity <= 0
        BEGIN
            SELECT RAISE(ABORT, 'Pizza ingredient quantity must be greater than 0');
        END;
        """,
        
        # Prevent duplicate discount codes
        """
        CREATE TRIGGER IF NOT EXISTS check_duplicate_discount_codes
        BEFORE INSERT ON discount_codes
        WHEN EXISTS (SELECT 1 FROM discount_codes WHERE code = NEW.code)
        BEGIN
            SELECT RAISE(ABORT, 'Discount code already exists');
        END;
        """
    ]
    
    results = []
    for i, sql in enumerate(constraints_sql, 1):
        try:
            db.session.execute(text(sql))
            db.session.commit()
            results.append(f"✅ Constraint {i}: Applied successfully")
        except Exception as e:
            results.append(f"❌ Constraint {i}: Failed - {str(e)}")
    
    return results


def validate_vegetarian_pizza_constraint(pizza_id: int) -> Dict[str, Any]:
    """
    Check if a pizza marked as vegetarian actually contains only vegetarian ingredients.
    """
    try:
        sql = text("""
            SELECT 
                p.name as pizza_name,
                COUNT(CASE WHEN i.is_vegetarian = 0 THEN 1 END) as non_veg_ingredients,
                GROUP_CONCAT(CASE WHEN i.is_vegetarian = 0 THEN i.name END) as non_veg_list
            FROM pizzas p
            JOIN pizza_ingredients pi ON pi.pizza_id = p.id
            JOIN ingredients i ON i.id = pi.ingredient_id
            WHERE p.id = :pizza_id
            GROUP BY p.id, p.name
        """)
        
        result = db.session.execute(sql, {'pizza_id': pizza_id}).fetchone()
        
        if not result:
            return {'error': f'Pizza with ID {pizza_id} not found'}
        
        pizza_name = result[0]
        non_veg_count = result[1] or 0
        non_veg_ingredients = result[2] or ""
        
        is_valid = non_veg_count == 0
        
        return {
            'pizza_id': pizza_id,
            'pizza_name': pizza_name,
            'is_vegetarian_compliant': is_valid,
            'non_vegetarian_ingredients': non_veg_ingredients.split(',') if non_veg_ingredients else [],
            'violation_count': non_veg_count
        }
        
    except Exception as e:
        return {'error': str(e)}


def test_constraint_violations() -> List[Dict[str, Any]]:
    """
    Test various constraint violations to ensure they're properly enforced.
    """
    test_results = []
    
    # Test 1: Try to insert ingredient with negative cost
    try:
        sql = text("INSERT INTO ingredients (name, cost_per_unit, is_vegetarian) VALUES ('Test Bad Ingredient', -1.0, 1)")
        db.session.execute(sql)
        db.session.commit()
        test_results.append({
            'test': 'Negative ingredient cost',
            'expected': 'blocked',
            'actual': 'allowed',
            'passed': False,
            'message': 'Constraint failed - negative cost was allowed'
        })
    except Exception as e:
        db.session.rollback()
        test_results.append({
            'test': 'Negative ingredient cost',
            'expected': 'blocked', 
            'actual': 'blocked',
            'passed': True,
            'message': f'Correctly blocked: {str(e)}'
        })
    
    # Test 2: Try to insert customer with future birthday
    try:
        sql = text("INSERT INTO customers (name, email, phone, address, birthday) VALUES ('Future Baby', 'future@test.com', '1111111111', 'Test Address', '2030-01-01')")
        db.session.execute(sql)
        db.session.commit()
        test_results.append({
            'test': 'Future birthday',
            'expected': 'blocked',
            'actual': 'allowed', 
            'passed': False,
            'message': 'Constraint failed - future birthday was allowed'
        })
    except Exception as e:
        db.session.rollback()
        test_results.append({
            'test': 'Future birthday',
            'expected': 'blocked',
            'actual': 'blocked',
            'passed': True, 
            'message': f'Correctly blocked: {str(e)}'
        })
    
    # Test 3: Try to insert order item with zero quantity
    try:
        sql = text("INSERT INTO order_items (order_id, pizza_id, quantity) VALUES (1, 1, 0)")
        db.session.execute(sql)
        db.session.commit()
        test_results.append({
            'test': 'Zero quantity order item',
            'expected': 'blocked',
            'actual': 'allowed',
            'passed': False,
            'message': 'Constraint failed - zero quantity was allowed'
        })
    except Exception as e:
        db.session.rollback() 
        test_results.append({
            'test': 'Zero quantity order item',
            'expected': 'blocked',
            'actual': 'blocked',
            'passed': True,
            'message': f'Correctly blocked: {str(e)}'
        })
    
    # Test 4: Check vegetarian pizza compliance
    try:
        # Get a pizza and check its vegetarian compliance
        pizza = db.session.execute(text("SELECT id FROM pizzas LIMIT 1")).fetchone()
        if pizza:
            compliance = validate_vegetarian_pizza_constraint(pizza[0])
            test_results.append({
                'test': 'Vegetarian pizza compliance',
                'expected': 'validated',
                'actual': 'validated' if 'error' not in compliance else 'error',
                'passed': 'error' not in compliance,
                'message': f"Pizza {compliance.get('pizza_name', 'Unknown')}: {'Compliant' if compliance.get('is_vegetarian_compliant', False) else 'Non-compliant'}"
            })
    except Exception as e:
        test_results.append({
            'test': 'Vegetarian pizza compliance',
            'expected': 'validated',
            'actual': 'error',
            'passed': False,
            'message': f'Error: {str(e)}'
        })
    
    return test_results


def get_constraint_status() -> Dict[str, Any]:
    """Get current status of all database constraints."""
    try:
        # Check if triggers exist
        trigger_sql = text("""
            SELECT name FROM sqlite_master 
            WHERE type = 'trigger' 
            AND name LIKE 'check_%'
            ORDER BY name
        """)
        
        triggers = db.session.execute(trigger_sql).fetchall()
        trigger_names = [row[0] for row in triggers]
        
        # Check constraint violations in current data
        violations = []
        
        # Check for negative ingredient costs
        neg_cost_sql = text("SELECT name, cost_per_unit FROM ingredients WHERE cost_per_unit <= 0")
        neg_costs = db.session.execute(neg_cost_sql).fetchall()
        for row in neg_costs:
            violations.append(f"Ingredient '{row[0]}' has invalid cost: {row[1]}")
        
        # Check for future birthdays
        future_bday_sql = text("SELECT name, birthday FROM customers WHERE birthday > date('now')")
        future_bdays = db.session.execute(future_bday_sql).fetchall()
        for row in future_bdays:
            violations.append(f"Customer '{row[0]}' has future birthday: {row[1]}")
        
        # Check for zero quantities
        zero_qty_sql = text("SELECT id, quantity FROM order_items WHERE quantity <= 0")
        zero_qtys = db.session.execute(zero_qty_sql).fetchall()
        for row in zero_qtys:
            violations.append(f"Order item {row[0]} has invalid quantity: {row[1]}")
        
        return {
            'triggers_installed': len(trigger_names),
            'trigger_names': trigger_names,
            'current_violations': len(violations),
            'violations': violations,
            'status': 'healthy' if len(violations) == 0 else 'violations_found'
        }
        
    except Exception as e:
        return {'error': str(e)}


if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        print("🛡️  Database Constraints Setup and Testing\n")
        
        # Add constraints
        print("Adding database constraints...")
        constraint_results = add_database_constraints()
        for result in constraint_results:
            print(result)
        
        print("\n" + "="*50)
        print("Testing constraint violations...")
        
        # Test constraints
        test_results = test_constraint_violations()
        passed = sum(1 for test in test_results if test['passed'])
        total = len(test_results)
        
        print(f"\nResults: {passed}/{total} tests passed\n")
        
        for test in test_results:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} {test['test']}")
            print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            print(f"   {test['message']}\n")
        
        # Show constraint status
        print("="*50)
        print("Constraint Status:")
        status = get_constraint_status()
        if 'error' in status:
            print(f"❌ Error: {status['error']}")
        else:
            print(f"✅ {status['triggers_installed']} constraints installed")
            print(f"✅ {status['current_violations']} current violations")
            print(f"Status: {status['status'].upper()}")