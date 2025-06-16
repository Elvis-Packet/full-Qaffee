from flask import Blueprint, request, jsonify
from ..models import db, Order, OrderItem, MenuItem, OrderStatus, UserRole
from ..utils.auth import login_required, role_required
from datetime import datetime
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('order', description='Order operations')

# API Models
order_item_model = api.model('OrderItem', {
    'menu_item_id': fields.Integer(required=True, description='Menu item ID'),
    'quantity': fields.Integer(required=True, description='Quantity'),
    'customization': fields.Raw(description='Customization options')
})

create_order_model = api.model('CreateOrder', {
    'items': fields.List(fields.Nested(order_item_model), required=True, description='Order items'),
    'delivery_address_id': fields.Integer(description='Delivery address ID'),
    'is_delivery': fields.Boolean(default=True, description='Whether order is for delivery')
})

order_response_model = api.model('OrderResponse', {
    'id': fields.Integer(description='Order ID'),
    'status': fields.String(description='Order status'),
    'total_amount': fields.Float(description='Total order amount'),
    'created_at': fields.DateTime(description='Order creation time'),
    'items': fields.List(fields.Nested(api.model('OrderItemResponse', {
        'id': fields.Integer(description='Order item ID'),
        'menu_item_id': fields.Integer(description='Menu item ID'),
        'quantity': fields.Integer(description='Quantity'),
        'subtotal': fields.Float(description='Subtotal amount'),
        'customization': fields.Raw(description='Customization details')
    })))
})

order_status_update_model = api.model('OrderStatusUpdate', {
    'status': fields.String(required=True, description='New order status')
})

# Initialize blueprint
order_bp = Blueprint('order', __name__)

@api.route('/checkout')
class CreateOrder(Resource):
    @api.doc('create_order',
             security='Bearer Auth',
             body=create_order_model,
             responses={
                 201: ('Order created successfully', order_response_model),
                 400: 'Validation Error',
                 401: 'Unauthorized',
                 500: 'Server Error'
             })
    @login_required
    def post(self):
        """Submit a new order"""
        data = request.get_json()
        
        if not data or 'items' not in data:
            return {'message': 'No items provided'}, 400
        
        # Validate items and calculate total
        total_amount = 0
        order_items = []
        
        for item in data['items']:
            if 'menu_item_id' not in item or 'quantity' not in item:
                return {'message': 'Invalid item format'}, 400
            
            menu_item = MenuItem.query.get(item['menu_item_id'])
            if not menu_item or not menu_item.is_available:
                return {'message': f'Item {item["menu_item_id"]} not available'}, 400
            
            subtotal = menu_item.price * item['quantity']
            total_amount += subtotal
            
            order_items.append({
                'menu_item_id': menu_item.id,
                'quantity': item['quantity'],
                'subtotal': subtotal,
                'customization': item.get('customization', {})
            })
        
        # Create order
        order = Order(
            user_id=request.user.id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            delivery_address_id=data.get('delivery_address_id'),
            is_delivery=data.get('is_delivery', True)
        )
        
        try:
            db.session.add(order)
            db.session.flush()  # Get order ID without committing
            
            # Create order items
            for item in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item['menu_item_id'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal'],
                    customization=item['customization']
                )
                db.session.add(order_item)
            
            db.session.commit()
            return {
                'message': 'Order created successfully',
                'order': {
                    'id': order.id,
                    'status': order.status.value,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at.isoformat(),
                    'items': [{
                        'id': item.id,
                        'menu_item_id': item.menu_item_id,
                        'quantity': item.quantity,
                        'subtotal': item.subtotal,
                        'customization': item.customization
                    } for item in order.items]
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating order'}, 500

@api.route('/current')
class CurrentOrders(Resource):
    @api.doc('get_current_orders',
             security='Bearer Auth',
             responses={
                 200: ('Success', {'type': 'array', 'items': order_response_model}),
                 401: 'Unauthorized'
             })
    @login_required
    def get(self):
        """View user's active orders"""
        active_statuses = [
            OrderStatus.PENDING,
            OrderStatus.AWAITING_PAYMENT,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.READY_FOR_PICKUP,
            OrderStatus.OUT_FOR_DELIVERY
        ]
        
        orders = Order.query.filter(
            Order.user_id == request.user.id,
            Order.status.in_(active_statuses)
        ).order_by(Order.created_at.desc()).all()
        
        return {
            'orders': [{
                'id': order.id,
                'status': order.status.value,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'items': [{
                    'id': item.id,
                    'menu_item_id': item.menu_item_id,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                    'customization': item.customization
                } for item in order.items]
            } for order in orders]
        }, 200

@api.route('/history')
class OrderHistory(Resource):
    @api.doc('get_order_history',
             security='Bearer Auth',
             responses={
                 200: ('Success', {'type': 'array', 'items': order_response_model}),
                 401: 'Unauthorized'
             })
    @login_required
    def get(self):
        """View user's past orders"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        completed_statuses = [
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED_BY_USER,
            OrderStatus.CANCELLED_BY_ADMIN,
            OrderStatus.FAILED
        ]
        
        orders = Order.query.filter(
            Order.user_id == request.user.id,
            Order.status.in_(completed_statuses)
        ).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return {
            'orders': [{
                'id': order.id,
                'status': order.status.value,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'items': [{
                    'id': item.id,
                    'menu_item_id': item.menu_item_id,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                    'customization': item.customization
                } for item in order.items]
            } for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': orders.page
        }, 200

@api.route('/<int:order_id>/cancel')
class CancelOrder(Resource):
    @api.doc('cancel_order',
             security='Bearer Auth',
             responses={
                 200: 'Order cancelled successfully',
                 400: 'Order cannot be cancelled',
                 401: 'Unauthorized',
                 404: 'Order not found'
             })
    @login_required
    def delete(self, order_id):
        """Cancel user's pending/unpaid order"""
        order = Order.query.get_or_404(order_id)
        
        # Check if order belongs to user
        if order.user_id != request.user.id:
            return {'message': 'Order not found'}, 404
        
        # Check if order can be cancelled
        if order.status not in [OrderStatus.PENDING, OrderStatus.AWAITING_PAYMENT]:
            return {'message': 'Order cannot be cancelled'}, 400
        
        try:
            order.status = OrderStatus.CANCELLED_BY_USER
            db.session.commit()
            return {'message': 'Order cancelled successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error cancelling order'}, 500

@api.route('/admin/orders')
class AdminOrders(Resource):
    @api.doc('list_orders',
             security='Bearer Auth',
             responses={
                 200: ('Success', {'type': 'array', 'items': order_response_model}),
                 401: 'Unauthorized',
                 403: 'Forbidden'
             })
    @role_required(UserRole.ADMIN, UserRole.STAFF)
    def get(self):
        """List all orders with filtering options"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Order.query
        
        if status:
            try:
                query = query.filter_by(status=OrderStatus(status))
            except ValueError:
                return {'message': 'Invalid status'}, 400
        
        orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return {
            'orders': [{
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status.value,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'is_delivery': order.is_delivery,
                'items': [{
                    'id': item.id,
                    'menu_item_id': item.menu_item_id,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                    'customization': item.customization
                } for item in order.items]
            } for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': orders.page
        }, 200

@api.route('/admin/orders/<int:order_id>/status')
class UpdateOrderStatus(Resource):
    @api.doc('update_order_status',
             security='Bearer Auth',
             body=order_status_update_model,
             responses={
                 200: 'Order status updated successfully',
                 400: 'Invalid status',
                 401: 'Unauthorized',
                 403: 'Forbidden',
                 404: 'Order not found'
             })
    @role_required(UserRole.ADMIN, UserRole.STAFF)
    def patch(self, order_id):
        """Update order status"""
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        if not data or 'status' not in data:
            return {'message': 'New status not provided'}, 400
        
        try:
            new_status = OrderStatus(data['status'])
        except ValueError:
            return {'message': 'Invalid status'}, 400
        
        # Staff can only update status in certain flow
        if request.user.role == UserRole.STAFF:
            allowed_transitions = {
                OrderStatus.CONFIRMED: [OrderStatus.PREPARING],
                OrderStatus.PREPARING: [OrderStatus.READY_FOR_PICKUP, OrderStatus.OUT_FOR_DELIVERY],
                OrderStatus.READY_FOR_PICKUP: [OrderStatus.COMPLETED],
                OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.COMPLETED]
            }
            
            if order.status not in allowed_transitions or new_status not in allowed_transitions[order.status]:
                return {'message': 'Status transition not allowed'}, 403
        
        try:
            order.status = new_status
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return {
                'message': 'Order status updated successfully',
                'order': {
                    'id': order.id,
                    'status': order.status.value,
                    'updated_at': order.updated_at.isoformat()
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating order status'}, 500

@api.route('/admin/orders/<int:order_id>')
class AdminCancelOrder(Resource):
    @api.doc('force_cancel_order',
             security='Bearer Auth',
             responses={
                 200: 'Order cancelled successfully',
                 400: 'Cannot cancel completed order',
                 401: 'Unauthorized',
                 403: 'Forbidden',
                 404: 'Order not found'
             })
    @role_required(UserRole.ADMIN)
    def delete(self, order_id):
        """Force cancel any order (admin only)"""
        order = Order.query.get_or_404(order_id)
        
        if order.status == OrderStatus.COMPLETED:
            return {'message': 'Cannot cancel completed order'}, 400
        
        try:
            order.status = OrderStatus.CANCELLED_BY_ADMIN
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return {'message': 'Order cancelled successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error cancelling order'}, 500 