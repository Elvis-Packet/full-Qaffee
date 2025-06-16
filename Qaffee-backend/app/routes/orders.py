from flask import request
from ..models import db, Order, OrderItem, MenuItem, DeliveryAddress, OrderStatus
from .auth import token_required, staff_required
from datetime import datetime
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('orders', description='Order management operations')

# Models for request/response documentation
menu_item_model = api.model('OrderMenuItem', {
    'id': fields.Integer(description='Menu item ID'),
    'name': fields.String(description='Item name'),
    'price': fields.Float(description='Item price')
})

order_item_model = api.model('OrderItem', {
    'id': fields.Integer(description='Order item ID'),
    'menu_item_id': fields.Integer(description='Menu item ID'),
    'name': fields.String(description='Item name'),
    'quantity': fields.Integer(description='Quantity'),
    'price': fields.Float(description='Item price'),
    'subtotal': fields.Float(description='Item subtotal'),
    'customization': fields.Raw(description='Customization options')
})

delivery_address_model = api.model('DeliveryAddress', {
    'address_line1': fields.String(description='Address line 1'),
    'address_line2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude')
})

order_model = api.model('Order', {
    'id': fields.Integer(description='Order ID'),
    'status': fields.String(description='Order status'),
    'total_amount': fields.Float(description='Total order amount'),
    'items': fields.List(fields.Nested(order_item_model)),
    'created_at': fields.DateTime(description='Order creation timestamp'),
    'updated_at': fields.DateTime(description='Order last update timestamp'),
    'delivery_address_id': fields.Integer(description='Delivery address ID'),
    'is_delivery': fields.Boolean(description='Whether order is for delivery'),
    'payment_status': fields.String(description='Payment status')
})

order_update_model = api.model('OrderUpdate', {
    'status': fields.String(required=True, description='New order status'),
    'notes': fields.String(description='Status update notes')
})

pagination_model = api.model('Pagination', {
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages'),
    'current_page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page')
})

orders_response = api.model('OrdersResponse', {
    'orders': fields.List(fields.Nested(order_model)),
    'pagination': fields.Nested(pagination_model)
})

@api.route('')
class OrderList(Resource):
    @api.doc('list_orders')
    @api.marshal_list_with(order_model)
    @token_required
    def get(self, current_user):
        """List user's orders"""
        return Order.query.filter_by(
            user_id=current_user.id
        ).filter(
            Order.status != OrderStatus.DRAFT
        ).order_by(Order.created_at.desc()).all()

    @api.doc('create_order')
    @api.marshal_with(order_model)
    @token_required
    def post(self, current_user):
        """Create a new order from cart"""
        # Get current cart
        cart = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.DRAFT
        ).first_or_404()
        
        if not cart.items:
            return {'message': 'Cart is empty'}, 400
        
        # Update cart to pending order
        cart.status = OrderStatus.PENDING
        cart.created_at = db.func.now()
        
        db.session.commit()
        return cart

@api.route('/<int:id>')
@api.param('id', 'The order identifier')
class OrderResource(Resource):
    @api.doc('get_order')
    @api.marshal_with(order_model)
    @token_required
    def get(self, current_user, id):
        """Get an order by ID"""
        return Order.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()

    @api.doc('update_order')
    @api.expect(api.model('UpdateOrder', {
        'status': fields.String(required=True, description='New order status')
    }))
    @api.marshal_with(order_model)
    @api.response(200, 'Order updated successfully')
    @api.response(400, 'Invalid status')
    @api.response(404, 'Order not found')
    @staff_required
    def put(self, current_user, id):
        """Update order status (staff only)"""
        data = request.get_json()
        
        if not data or 'status' not in data:
            return {'message': 'No status provided'}, 400
            
        try:
            new_status = OrderStatus[data['status'].upper()]
        except KeyError:
            return {'message': 'Invalid status'}, 400
            
        order = Order.query.get_or_404(id)
        order.status = new_status
        order.updated_at = db.func.now()
        db.session.commit()
        
        return order

@api.route('/staff')
class StaffOrders(Resource):
    @api.doc('list_all_orders')
    @api.marshal_list_with(order_model)
    @staff_required
    def get(self, current_user):
        """List all orders (staff only)"""
        status = request.args.get('status')
        if status:
            try:
                status = OrderStatus[status.upper()]
                return Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all()
            except KeyError:
                return {'message': 'Invalid status'}, 400
        return Order.query.filter(Order.status != OrderStatus.DRAFT).order_by(Order.created_at.desc()).all()

@api.route('/<int:id>/cancel')
@api.param('id', 'The order identifier')
class CancelOrder(Resource):
    @api.doc('cancel_order')
    @api.marshal_with(order_model)
    @token_required
    def post(self, current_user, id):
        """Cancel an order"""
        order = Order.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.AWAITING_PAYMENT]:
            return {'message': 'Order cannot be cancelled'}, 400
        
        order.status = OrderStatus.CANCELLED_BY_USER
        order.updated_at = db.func.now()
        
        db.session.commit()
        return order

@api.route('/stats')
class OrderStats(Resource):
    @api.doc('get_order_stats')
    @staff_required
    def get(self, current_user):
        """Get order statistics (staff only)"""
        total_orders = Order.query.filter(Order.status != 'draft').count()
        pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
        completed_orders = Order.query.filter_by(status=OrderStatus.COMPLETED).count()
        cancelled_orders = Order.query.filter(
            Order.status.in_([OrderStatus.CANCELLED_BY_USER, OrderStatus.CANCELLED_BY_ADMIN])
        ).count()
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders
        }

@api.route('/checkout')
class Checkout(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('CheckoutRequest', {
        'is_delivery': fields.Boolean(description='Whether this is a delivery order'),
        'delivery_address_id': fields.Integer(description='Delivery address ID')
    }))
    @api.response(200, 'Order placed successfully')
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Place an order"""
        data = request.get_json()
        
        if not data:
            return {'message': 'No data provided'}, 400
        
        try:
            # Get current cart
            cart = Order.query.filter_by(
                user_id=current_user.id,
                status=OrderStatus.DRAFT
            ).first()
            
            if not cart or not cart.items:
                return {'message': 'Cart is empty'}, 400
            
            # Validate delivery address if delivery is requested
            if data.get('is_delivery', True):
                if not data.get('delivery_address_id'):
                    return {'message': 'Delivery address is required'}, 400
                
                address = DeliveryAddress.query.filter_by(
                    id=data['delivery_address_id'],
                    user_id=current_user.id
                ).first()
                
                if not address:
                    return {'message': 'Invalid delivery address'}, 400
                
                cart.delivery_address_id = address.id
            
            cart.is_delivery = data.get('is_delivery', True)
            cart.status = OrderStatus.CONFIRMED
            
            db.session.commit()
            
            return {
                'message': 'Order placed successfully',
                'order_id': cart.id,
                'total_amount': cart.total_amount
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error placing order', 'error': str(e)}, 500