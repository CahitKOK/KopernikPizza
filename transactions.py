"""
Transaction Management Module
Provides safe transaction handling with rollback capabilities
for order placement and other critical operations.
"""

from extensions import db
from models import Order, OrderItem, Customer, Pizza, DiscountCode, Drink, Dessert
from utils import apply_discounts, assign_delivery_person_sql
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderTransactionError(Exception):
    """Custom exception for order transaction failures."""
    pass


def create_order_transaction(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an order using proper database transactions with rollback capability.
    
    Args:
        order_data: Dictionary containing order information
        
    Returns:
        Dictionary with order result or error information
        
    Raises:
        OrderTransactionError: When order creation fails
    """
    try:
        # Start transaction
        db.session.begin()
        logger.info("🔄 Starting order transaction")
        
        # Step 1: Resolve or create customer
        customer = _resolve_customer(order_data)
        logger.info(f"✅ Customer resolved: {customer.name} (ID: {customer.id})")
        
        # Step 2: Validate items
        items = order_data.get('items', [])
        if not items:
            raise OrderTransactionError("No items in order")
            
        _validate_order_items(items)
        logger.info(f"✅ Validated {len(items)} order items")
        
        # Step 3: Create order
        order = Order(
            customer_id=customer.id, 
            order_date=datetime.utcnow(), 
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order.id
        logger.info(f"✅ Order created with ID: {order.id}")
        
        # Step 4: Create order items
        for item_data in items:
            quantity = int(item_data['quantity'])
            
            # Support both old format (pizza_id) and new format (item_id, item_type)
            if 'item_id' in item_data and 'item_type' in item_data:
                item_id = item_data['item_id']
                item_type = item_data['item_type']
            elif 'pizza_id' in item_data:
                # Convert old format to new format
                item_id = item_data['pizza_id']
                item_type = 'pizza'
            else:
                raise OrderTransactionError("Invalid item format")
            
            # Validate item exists
            if item_type == 'pizza':
                item_obj = Pizza.query.get(item_id)
                if not item_obj:
                    raise OrderTransactionError(f"Pizza with ID {item_id} not found")
            elif item_type == 'drink':
                item_obj = Drink.query.get(item_id)
                if not item_obj:
                    raise OrderTransactionError(f"Drink with ID {item_id} not found")
            elif item_type == 'dessert':
                item_obj = Dessert.query.get(item_id)
                if not item_obj:
                    raise OrderTransactionError(f"Dessert with ID {item_id} not found")
            else:
                raise OrderTransactionError(f"Invalid item type: {item_type}")
                
            order_item = OrderItem(
                order_id=order.id,
                item_type=item_type,
                item_id=item_id,
                pizza_id=item_id if item_type == 'pizza' else None,  # Legacy compatibility
                quantity=quantity
            )
            db.session.add(order_item)
        
        logger.info(f"✅ Created {len(items)} order items")
        
        # Step 5: Handle discount code
        discount_code = None
        if order_data.get('discount_code'):
            discount_code = _validate_discount_code(order_data['discount_code'])
            logger.info(f"✅ Discount code validated: {discount_code.code}")
        
        # Step 6: Calculate total with discounts
        total = apply_discounts(order, discount_code)
        order.total = total
        logger.info(f"✅ Order total calculated: €{total:.2f}")
        
        # Step 7: Mark discount code as used (if applicable)
        if discount_code and not discount_code.is_used:
            discount_code.is_used = True
            db.session.add(discount_code)
            logger.info("✅ Discount code marked as used")
        
        # Step 8: Assign delivery person
        delivery_person = assign_delivery_person_sql(order)
        if delivery_person:
            logger.info(f"✅ Delivery person assigned: {delivery_person.name}")
        else:
            logger.warning("⚠️  No delivery person available")
        
        # Step 9: Final validation before commit
        if total < 0:
            raise OrderTransactionError("Order total cannot be negative")
            
        if not order.items:
            raise OrderTransactionError("Order must contain at least one item")
        
        # Commit transaction
        db.session.commit()
        logger.info("✅ Transaction committed successfully")
        
        return {
            'success': True,
            'order_id': order.id,
            'customer_id': customer.id,
            'customer_name': customer.name,
            'total': total,
            'delivery_person': delivery_person.name if delivery_person else None,
            'discount_applied': discount_code.code if discount_code else None,
            'items_count': len(items)
        }
        
    except Exception as e:
        # Rollback transaction on any error
        db.session.rollback()
        logger.error(f"❌ Transaction rolled back: {str(e)}")
        
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def _resolve_customer(order_data: Dict[str, Any]) -> Customer:
    """Resolve or create customer from order data."""
    if 'customer_id' in order_data:
        customer = Customer.query.get(order_data['customer_id'])
        if not customer:
            raise OrderTransactionError(f"Customer with ID {order_data['customer_id']} not found")
        return customer
    
    # Create new customer
    customer_data = order_data.get('customer', {})
    if not customer_data:
        raise OrderTransactionError("Customer information required")
    
    # Check if customer already exists
    existing = Customer.query.filter(
        (Customer.email == customer_data.get('email')) | 
        (Customer.phone == customer_data.get('phone'))
    ).first()
    
    if existing:
        return existing
    
    # Create new customer
    birthday = None
    if customer_data.get('birthday'):
        try:
            birthday = datetime.fromisoformat(customer_data['birthday']).date()
        except ValueError:
            raise OrderTransactionError("Invalid birthday format. Use YYYY-MM-DD")
    
    customer = Customer(
        name=customer_data.get('name'),
        email=customer_data.get('email'),
        phone=customer_data.get('phone'),
        address=customer_data.get('address'),
        birthday=birthday
    )
    
    db.session.add(customer)
    db.session.flush()
    return customer


def _validate_order_items(items: list) -> None:
    """Validate order items data."""
    if not isinstance(items, list):
        raise OrderTransactionError("Items must be a list")
    
    # Business Rule: Every order MUST contain at least one pizza
    has_pizza = False
    
    for item in items:
        if not isinstance(item, dict):
            raise OrderTransactionError("Each item must be a dictionary")
            
        # Support both old format (pizza_id) and new format (item_id, item_type)
        has_old_format = 'pizza_id' in item
        has_new_format = 'item_id' in item and 'item_type' in item
        
        if not (has_old_format or has_new_format):
            raise OrderTransactionError("Each item must have either pizza_id or (item_id and item_type)")
            
        # Check if this item is a pizza
        if has_old_format or (has_new_format and item.get('item_type') == 'pizza'):
            has_pizza = True
            
        # Validate item type if provided
        if 'item_type' in item and item['item_type'] not in ['pizza', 'drink', 'dessert']:
            raise OrderTransactionError("Item type must be 'pizza', 'drink', or 'dessert'")
            
        try:
            quantity = int(item.get('quantity', 1))
            if quantity <= 0:
                raise OrderTransactionError("Quantity must be greater than 0")
        except (ValueError, TypeError):
            raise OrderTransactionError("Invalid quantity value")
    
    # MANDATORY PIZZA RULE: Every order must contain at least one pizza
    if not has_pizza:
        raise OrderTransactionError("Every order must contain at least one pizza! You cannot order only drinks or desserts.")


def _validate_discount_code(code: str) -> DiscountCode:
    """Validate and return discount code."""
    discount = DiscountCode.query.get(code)
    if not discount:
        raise OrderTransactionError(f"Discount code '{code}' not found")
        
    if discount.is_used:
        raise OrderTransactionError(f"Discount code '{code}' has already been used")
    
    return discount


def test_transaction_rollback() -> Dict[str, Any]:
    """
    Test transaction rollback functionality by intentionally causing failures.
    """
    test_results = []
    
    # Test 1: Invalid pizza ID should rollback
    try:
        result = create_order_transaction({
            'customer': {
                'name': 'Test Customer',
                'email': 'test@rollback.com',
                'phone': '9999999999',
                'address': 'Test Address, 12345'
            },
            'items': [
                {'pizza_id': 99999, 'quantity': 1}  # Invalid pizza ID
            ]
        })
        test_results.append({
            'test': 'Invalid Pizza ID',
            'expected': 'failure',
            'actual': 'failure' if not result['success'] else 'success',
            'passed': not result['success'],
            'message': result.get('error', 'No error')
        })
    except Exception as e:
        test_results.append({
            'test': 'Invalid Pizza ID',
            'expected': 'failure', 
            'actual': 'exception',
            'passed': True,
            'message': str(e)
        })
    
    # Test 2: Empty items should rollback
    try:
        result = create_order_transaction({
            'customer': {
                'name': 'Test Customer 2',
                'email': 'test2@rollback.com', 
                'phone': '8888888888',
                'address': 'Test Address 2, 54321'
            },
            'items': []  # Empty items
        })
        test_results.append({
            'test': 'Empty Items List',
            'expected': 'failure',
            'actual': 'failure' if not result['success'] else 'success',
            'passed': not result['success'],
            'message': result.get('error', 'No error')
        })
    except Exception as e:
        test_results.append({
            'test': 'Empty Items List',
            'expected': 'failure',
            'actual': 'exception', 
            'passed': True,
            'message': str(e)
        })
    
    # Test 3: Invalid discount code should rollback
    try:
        result = create_order_transaction({
            'customer': {
                'name': 'Test Customer 3',
                'email': 'test3@rollback.com',
                'phone': '7777777777', 
                'address': 'Test Address 3, 11111'
            },
            'items': [
                {'pizza_id': 1, 'quantity': 1}
            ],
            'discount_code': 'INVALID_CODE'  # Invalid code
        })
        test_results.append({
            'test': 'Invalid Discount Code',
            'expected': 'failure',
            'actual': 'failure' if not result['success'] else 'success',
            'passed': not result['success'],
            'message': result.get('error', 'No error')
        })
    except Exception as e:
        test_results.append({
            'test': 'Invalid Discount Code', 
            'expected': 'failure',
            'actual': 'exception',
            'passed': True,
            'message': str(e)
        })
    
    return {
        'total_tests': len(test_results),
        'passed_tests': sum(1 for test in test_results if test['passed']),
        'results': test_results
    }


if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        print("🔄 Testing Transaction Rollback Functionality\n")
        
        test_results = test_transaction_rollback()
        
        print(f"Results: {test_results['passed_tests']}/{test_results['total_tests']} tests passed\n")
        
        for test in test_results['results']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} {test['test']}")
            print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            print(f"   Message: {test['message']}\n")