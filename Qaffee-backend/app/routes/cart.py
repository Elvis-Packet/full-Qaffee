from flask import request
from ..models import db, MenuItem, Order, OrderItem, OrderStatus
from .auth import token_required
from flask_restx import Namespace, Resource, fields
import json

# Create API namespace
api = Namespace('cart', description='Shopping cart operations')

# Models for request/response documentation
add_to_cart_model = api.model('AddToCart', {
    'item_id': fields.Integer(required=True, description='Menu item ID'),
    'quantity': fields.Integer(required=True, description='Quantity to add'),
    'customization': fields.Raw(description='Customization options')
})

update_cart_model = api.model('UpdateCart', {
    'quantity': fields.Integer(required=True, description='New quantity'),
    'customization': fields.Raw(description='Updated customization options')
})

cart_item_model = api.model('CartItem', {
    'menu_item_id': fields.Integer(required=True, description='Menu item ID'),
    'quantity': fields.Integer(required=True, description='Item quantity'),
    'customization': fields.Raw(description='Customization options')
})

cart_response = api.model('CartResponse', {
    'id': fields.Integer(description='Cart ID'),
    'items': fields.List(fields.Nested(api.model('CartItemDetail', {
        'id': fields.Integer(description='Order item ID'),
        'menu_item_id': fields.Integer(description='Menu item ID'),
        'name': fields.String(attribute=lambda x: x.menu_item.name if x.menu_item else None, description='Item name'),
        'price': fields.Float(attribute=lambda x: x.menu_item.price if x.menu_item else None, description='Item price'),
        'quantity': fields.Integer(description='Quantity'),
        'subtotal': fields.Float(description='Item subtotal'),
        'customization': fields.Raw(description='Customization options')
    }))),
    'total_amount': fields.Float(description='Total cart amount')
})

@api.route('')
class Cart(Resource):
    @api.doc('get_cart')
    @api.marshal_with(cart_response)
    @token_required
    def get(self, current_user):
        """Get current user's cart"""
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first()
        
        if not cart:
            cart = Order(user_id=current_user.id, status=OrderStatus.DRAFT, total_amount=0)
            db.session.add(cart)
            db.session.commit()
        
        return cart

    @api.doc('add_to_cart')
    @api.expect(cart_item_model)
    @api.marshal_with(cart_response)
    @token_required
    def post(self, current_user):
        """Add item to cart"""
        data = request.get_json()
        
        # Get or create cart
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first()
        
        if not cart:
            cart = Order(user_id=current_user.id, status=OrderStatus.DRAFT, total_amount=0)
            db.session.add(cart)
            db.session.flush()  # Get cart ID without committing
        
        # Get menu item
        menu_item = MenuItem.query.get_or_404(data['menu_item_id'])
        
        # Convert customization to string for comparison
        customization_str = json.dumps(data.get('customization', {}), sort_keys=True)
        
        # Check if item already exists in cart with same customization
        existing_item = None
        for item in cart.items:
            if (item.menu_item_id == menu_item.id and 
                json.dumps(item.customization or {}, sort_keys=True) == customization_str):
                existing_item = item
                break
        
        if existing_item:
            # Update quantity and subtotal
            old_subtotal = existing_item.subtotal
            existing_item.quantity += data['quantity']
            existing_item.subtotal = menu_item.price * existing_item.quantity
            cart.total_amount = cart.total_amount - old_subtotal + existing_item.subtotal
        else:
            # Calculate subtotal
            subtotal = menu_item.price * data['quantity']
            
            # Create order item
            order_item = OrderItem(
                order_id=cart.id,
                menu_item_id=menu_item.id,
                quantity=data['quantity'],
                customization=data.get('customization'),
                subtotal=subtotal
            )
            db.session.add(order_item)
            
            # Update cart total
            cart.total_amount += subtotal
        
        db.session.commit()
        return cart

@api.route('/items/<int:item_id>')
class CartItem(Resource):
    @api.doc('update_cart_item')
    @api.expect(cart_item_model)
    @api.marshal_with(cart_response)
    @token_required
    def put(self, current_user, item_id):
        """Update cart item quantity or customization"""
        data = request.get_json()
        
        # Get cart
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first_or_404()
        
        # Get order item
        order_item = OrderItem.query.filter_by(
            id=item_id,
            order_id=cart.id
        ).first_or_404()
        
        # Calculate price difference
        old_subtotal = order_item.subtotal
        new_subtotal = order_item.menu_item.price * data['quantity']
        
        # Update order item
        order_item.quantity = data['quantity']
        order_item.customization = data.get('customization', order_item.customization)
        order_item.subtotal = new_subtotal
        
        # Update cart total
        cart.total_amount = cart.total_amount - old_subtotal + new_subtotal
        
        db.session.commit()
        return cart

    @api.doc('remove_from_cart')
    @api.marshal_with(cart_response)
    @token_required
    def delete(self, current_user, item_id):
        """Remove item from cart"""
        # Get cart
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first_or_404()
        
        # Get order item
        order_item = OrderItem.query.filter_by(
            id=item_id,
            order_id=cart.id
        ).first_or_404()
        
        # Update cart total
        cart.total_amount -= order_item.subtotal
        
        # Remove item
        db.session.delete(order_item)
        db.session.commit()
        
        return cart

@api.route('/clear')
class ClearCart(Resource):
    @api.doc('clear_cart')
    @api.marshal_with(cart_response)
    @token_required
    def post(self, current_user):
        """Clear all items from cart"""
        # Get cart
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first_or_404()
        
        # Remove all items
        OrderItem.query.filter_by(order_id=cart.id).delete()
        
        # Reset cart total
        cart.total_amount = 0
        
        db.session.commit()
        return cart 