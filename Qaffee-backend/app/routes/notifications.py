from flask import request
from ..models import db, Notification, User, Order, NotificationType, OrderStatus
from .auth import token_required, admin_required
from twilio.rest import Client
from decouple import config
from datetime import datetime
from flask_restx import Namespace, Resource, fields
from ..utils.sms import send_sms, TWILIO_ENABLED

# Create API namespace
api = Namespace('notifications', description='Notification management operations')

# Models for request/response documentation
notification_model = api.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'user_id': fields.Integer(description='User ID'),
    'type': fields.String(description='Notification type'),
    'title': fields.String(description='Notification title'),
    'message': fields.String(description='Notification message'),
    'data': fields.Raw(description='Additional notification data'),
    'is_read': fields.Boolean(description='Whether notification has been read'),
    'created_at': fields.DateTime(description='Notification creation timestamp')
})

notification_create_model = api.model('NotificationCreate', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'type': fields.String(required=True, description='Notification type'),
    'title': fields.String(required=True, description='Notification title'),
    'message': fields.String(required=True, description='Notification message'),
    'data': fields.Raw(description='Additional notification data')
})

send_notification_model = api.model('SendNotification', {
    'user_id': fields.Integer(required=True, description='User ID to send notification to'),
    'title': fields.String(required=True, description='Notification title'),
    'message': fields.String(required=True, description='Notification message'),
    'type': fields.String(description='Notification type'),
    'send_sms': fields.Boolean(description='Whether to send SMS notification')
})

mark_read_model = api.model('MarkRead', {
    'notification_ids': fields.List(fields.Integer, required=True, description='List of notification IDs to mark as read')
})

order_update_model = api.model('OrderUpdate', {
    'order_id': fields.Integer(required=True, description='Order ID'),
    'status': fields.String(required=True, description='New order status')
})

# Twilio configuration (optional)
TWILIO_ENABLED = all([
    config('TWILIO_ACCOUNT_SID', default=None),
    config('TWILIO_AUTH_TOKEN', default=None),
    config('TWILIO_PHONE_NUMBER', default=None)
])

if TWILIO_ENABLED:
    twilio_client = Client(
        config('TWILIO_ACCOUNT_SID'),
        config('TWILIO_AUTH_TOKEN')
    )
    TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')

def send_sms(phone_number, message):
    if not TWILIO_ENABLED:
        return False
        
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

@api.route('')
class NotificationList(Resource):
    @api.doc('list_notifications')
    @api.marshal_list_with(notification_model)
    @token_required
    def get(self, current_user):
        """List user's notifications"""
        # Get query parameters for filtering
        is_read = request.args.get('is_read', type=bool)
        notification_type = request.args.get('type')
        
        # Build query
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        if notification_type:
            query = query.filter_by(type=notification_type)
        
        return query.order_by(Notification.created_at.desc()).all()

    @api.doc('create_notification')
    @api.expect(notification_create_model)
    @api.marshal_with(notification_model)
    @admin_required
    def post(self, current_user):
        """Create a new notification (Admin only)"""
        data = request.get_json()
        
        notification = Notification(
            user_id=data['user_id'],
            type=data['type'],
            title=data['title'],
            message=data['message'],
            data=data.get('data'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification

@api.route('/<int:id>')
@api.param('id', 'The notification identifier')
class NotificationResource(Resource):
    @api.doc('get_notification')
    @api.marshal_with(notification_model)
    @token_required
    def get(self, current_user, id):
        """Get a notification by ID"""
        return Notification.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()

    @api.doc('mark_notification_read')
    @api.marshal_with(notification_model)
    @token_required
    def put(self, current_user, id):
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        return notification

    @api.doc('delete_notification')
    @token_required
    def delete(self, current_user, id):
        """Delete a notification"""
        notification = Notification.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(notification)
        db.session.commit()
        return {'message': 'Notification deleted'}

@api.route('/mark-all-read')
class MarkAllRead(Resource):
    @api.doc('mark_all_read')
    @token_required
    def post(self, current_user):
        """Mark all notifications as read"""
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        return {'message': 'All notifications marked as read'}

@api.route('/unread-count')
class UnreadCount(Resource):
    @api.doc('get_unread_count')
    @token_required
    def get(self, current_user):
        """Get count of unread notifications"""
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        return {'unread_count': count}

@api.route('/types')
class NotificationTypes(Resource):
    @api.doc('get_notification_types')
    def get(self):
        """Get list of notification types"""
        return {
            'types': [
                {
                    'id': ntype.name,
                    'description': ntype.value
                } for ntype in NotificationType
            ]
        }

@api.route('/send')
class SendNotification(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(send_notification_model)
    @api.response(200, 'Notification sent successfully')
    @api.response(400, 'Validation Error')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Send a notification to a user"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if not data or not data.get('user_id') or not data.get('title') or not data.get('message'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            user = User.query.get_or_404(data['user_id'])
            
            # Create notification
            notification = Notification(
                user_id=user.id,
                title=data['title'],
                message=data['message'],
                type=data.get('type', 'system')
            )
            
            db.session.add(notification)
            
            # Send SMS if phone number available and SMS is requested
            sms_sent = False
            if user.phone and data.get('send_sms', False):
                if not TWILIO_ENABLED:
                    return {'message': 'SMS notifications are not configured'}, 400
                sms_sent = send_sms(user.phone, f"{data['title']}: {data['message']}")
            
            db.session.commit()
            
            return {
                'message': 'Notification sent successfully',
                'notification': {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.type,
                    'created_at': notification.created_at,
                    'sms_sent': sms_sent
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error sending notification', 'error': str(e)}, 500

@api.route('/mark-read')
class MarkNotificationsRead(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(mark_read_model)
    @api.response(200, 'Notifications marked as read')
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Mark notifications as read"""
        data = request.get_json()
        
        if not data or 'notification_ids' not in data:
            return {'message': 'Notification IDs are required'}, 400
        
        try:
            # Update notifications
            Notification.query.filter(
                Notification.id.in_(data['notification_ids']),
                Notification.user_id == current_user.id
            ).update(
                {'is_read': True},
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {'message': 'Notifications marked as read'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error marking notifications as read', 'error': str(e)}, 500

@api.route('/order-update')
class OrderUpdate(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(order_update_model)
    @api.response(200, 'Order update notification sent')
    @api.response(400, 'Validation Error')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Send order status update notification"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if not data or not data.get('order_id') or not data.get('status'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            order = Order.query.get_or_404(data['order_id'])
            user = User.query.get(order.user_id)
            
            # Create status update message
            status_messages = {
                OrderStatus.CONFIRMED.value: 'Your order has been confirmed and is being processed.',
                OrderStatus.PREPARING.value: 'Your order is now being prepared.',
                OrderStatus.OUT_FOR_DELIVERY.value: 'Your order is on the way!',
                OrderStatus.COMPLETED.value: 'Your order has been delivered. Enjoy!'
            }
            
            message = status_messages.get(data['status'], f"Your order status has been updated to: {data['status']}")
            
            # Create notification
            notification = Notification(
                user_id=user.id,
                title=f"Order #{order.id} Update",
                message=message,
                type='order_update'
            )
            
            db.session.add(notification)
            
            # Send SMS if phone number available
            sms_sent = False
            if user.phone and TWILIO_ENABLED:
                sms_sent = send_sms(user.phone, message)
            
            db.session.commit()
            
            return {
                'message': 'Notification sent successfully',
                'sms_sent': sms_sent
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error sending notification', 'error': str(e)}, 500 