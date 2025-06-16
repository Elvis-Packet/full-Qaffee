from flask import request
from ..models import db, User, MenuItem, Category, Order, Payment, UserRole, Promotion
from .auth import token_required
from flask_restx import Namespace, Resource, fields
from datetime import datetime

# Create API namespace
api = Namespace('admin', description='Admin operations')

# Models for request/response documentation
user_stats_model = api.model('UserStats', {
    'total_users': fields.Integer(description='Total number of users'),
    'active_users': fields.Integer(description='Number of active users'),
    'new_users_today': fields.Integer(description='New users today')
})

order_stats_model = api.model('OrderStats', {
    'total_orders': fields.Integer(description='Total number of orders'),
    'orders_today': fields.Integer(description='Orders today'),
    'average_order_value': fields.Float(description='Average order value')
})

revenue_stats_model = api.model('RevenueStats', {
    'total_revenue': fields.Float(description='Total revenue'),
    'revenue_today': fields.Float(description='Revenue today'),
    'revenue_this_month': fields.Float(description='Revenue this month')
})

dashboard_model = api.model('Dashboard', {
    'user_stats': fields.Nested(user_stats_model),
    'order_stats': fields.Nested(order_stats_model),
    'revenue_stats': fields.Nested(revenue_stats_model)
})

@api.route('/dashboard')
class AdminDashboard(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', dashboard_model)
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get admin dashboard statistics"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            from datetime import datetime, timedelta
            
            today = datetime.utcnow().date()
            month_start = today.replace(day=1)
            
            # User statistics
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            new_users_today = User.query.filter(
                db.func.date(User.created_at) == today
            ).count()
            
            # Order statistics
            total_orders = Order.query.count()
            orders_today = Order.query.filter(
                db.func.date(Order.created_at) == today
            ).count()
            
            # Calculate average order value
            orders = Order.query.filter_by(status='delivered').all()
            if orders:
                average_order_value = sum(order.total_amount for order in orders) / len(orders)
            else:
                average_order_value = 0
            
            # Revenue statistics
            completed_payments = Payment.query.filter_by(status='completed').all()
            total_revenue = sum(payment.amount for payment in completed_payments)
            
            today_payments = Payment.query.filter(
                db.func.date(Payment.created_at) == today,
                Payment.status == 'completed'
            ).all()
            revenue_today = sum(payment.amount for payment in today_payments)
            
            month_payments = Payment.query.filter(
                Payment.created_at >= month_start,
                Payment.status == 'completed'
            ).all()
            revenue_this_month = sum(payment.amount for payment in month_payments)
            
            return {
                'user_stats': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users_today': new_users_today
                },
                'order_stats': {
                    'total_orders': total_orders,
                    'orders_today': orders_today,
                    'average_order_value': round(average_order_value, 2)
                },
                'revenue_stats': {
                    'total_revenue': round(total_revenue, 2),
                    'revenue_today': round(revenue_today, 2),
                    'revenue_this_month': round(revenue_this_month, 2)
                }
            }, 200
        except Exception as e:
            return {'message': 'Error fetching dashboard stats', 'error': str(e)}, 500

@api.route('/users')
class AdminUsers(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all users"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            users = User.query.all()
            # Get order count for each user
            user_order_counts = {
                user.id: len(user.customer_orders)
                for user in users
            }
            
            return {
                'users': [{
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'role': user.role.value,
                    'is_admin': user.is_admin,
                    'is_staff': user.is_staff,
                    'order_count': user_order_counts.get(user.id, 0)
                } for user in users],
                'total': len(users)
            }, 200
        except Exception as e:
            return {'message': 'Error fetching users', 'error': str(e)}, 500

@api.route('/user/<int:user_id>')
class AdminUserManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('UpdateUser', {
        'is_active': fields.Boolean(description='User active status'),
        'role': fields.String(description='User role (customer, staff, admin)')
    }))
    @api.response(200, 'User updated successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'User not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def put(self, current_user, user_id):
        """Update user details"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        try:
            user = User.query.get_or_404(user_id)
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            if 'role' in data:
                try:
                    new_role = UserRole(data['role'])
                    # Prevent self-demotion if last admin
                    if user.id == current_user.id and new_role != UserRole.ADMIN and user.role == UserRole.ADMIN:
                        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
                        if admin_count <= 1:
                            return {'message': 'Cannot demote the last admin'}, 400
                    user.role = new_role
                except ValueError:
                    return {'message': 'Invalid role'}, 400
            
            db.session.commit()
            
            return {
                'message': 'User updated successfully',
                'user': user.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating user', 'error': str(e)}, 500

@api.route('/orders')
class AdminOrders(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all orders with detailed information"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            orders = Order.query.order_by(Order.created_at.desc()).all()
            return [{
                'id': order.id,
                'user': {
                    'id': order.customer.id,
                    'name': f"{order.customer.first_name} {order.customer.last_name}",
                    'email': order.customer.email,
                    'phone': order.customer.phone
                },
                'status': order.status.value,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                'payment_status': order.payment_status,
                'is_delivery': order.is_delivery,
                'delivery_address': {
                    'address_line1': order.delivery_address.address_line1,
                    'address_line2': order.delivery_address.address_line2,
                    'city': order.delivery_address.city,
                    'state': order.delivery_address.state,
                    'postal_code': order.delivery_address.postal_code,
                    'country': order.delivery_address.country
                } if order.is_delivery and order.delivery_address else None,
                'items': [{
                    'id': item.id,
                    'menu_item': {
                        'id': item.menu_item.id,
                        'name': item.menu_item.name,
                        'price': item.menu_item.price
                    },
                    'quantity': item.quantity,
                    'customization': item.customization,
                    'subtotal': item.subtotal
                } for item in order.items],
                'applied_promotion': {
                    'code': order.applied_promotion.code,
                    'discount_type': order.applied_promotion.discount_type,
                    'discount_value': order.applied_promotion.discount_value
                } if order.applied_promotion else None
            } for order in orders], 200
        except Exception as e:
            return {'message': 'Error fetching orders', 'error': str(e)}, 500

@api.route('/order/<int:order_id>')
class AdminOrderManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('UpdateOrder', {
        'status': fields.String(description='Order status')
    }))
    @api.response(200, 'Order updated successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Order not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def put(self, current_user, order_id):
        """Update order status"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if not data or not data.get('status'):
            return {'message': 'Status is required'}, 400
        
        try:
            order = Order.query.get_or_404(order_id)
            order.status = data['status']
            db.session.commit()
            
            return {'message': 'Order status updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating order status', 'error': str(e)}, 500

@api.route('/menu')
class AdminMenu(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all menu items"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            items = MenuItem.query.all()
            return [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category_id': item.category_id,
                'is_available': item.is_available,
                'image_url': item.image_url
            } for item in items], 200
        except Exception as e:
            return {'message': 'Error fetching menu items', 'error': str(e)}, 500

@api.route('/menu/item')
class AdminMenuItem(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('MenuItem', {
        'name': fields.String(required=True, description='Item name'),
        'description': fields.String(description='Item description'),
        'price': fields.Float(required=True, description='Item price'),
        'category_id': fields.Integer(required=True, description='Category ID'),
        'image_url': fields.String(description='Item image URL'),
        'is_available': fields.Boolean(description='Item availability')
    }))
    @api.response(201, 'Menu item created successfully')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Create a new menu item"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('price') or not data.get('category_id'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            item = MenuItem(
                name=data['name'],
                description=data.get('description'),
                price=data['price'],
                category_id=data['category_id'],
                image_url=data.get('image_url'),
                is_available=data.get('is_available', True)
            )
            
            db.session.add(item)
            db.session.commit()
            
            return {
                'message': 'Menu item created successfully',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': item.price,
                    'category_id': item.category_id,
                    'is_available': item.is_available
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating menu item', 'error': str(e)}, 500

@api.route('/menu/item/<int:item_id>')
class AdminMenuItemManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('UpdateMenuItem', {
        'name': fields.String(description='Item name'),
        'description': fields.String(description='Item description'),
        'price': fields.Float(description='Item price'),
        'category_id': fields.Integer(description='Category ID'),
        'image_url': fields.String(description='Item image URL'),
        'is_available': fields.Boolean(description='Item availability')
    }))
    @api.response(200, 'Menu item updated successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Item not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def put(self, current_user, item_id):
        """Update a menu item"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        try:
            item = MenuItem.query.get_or_404(item_id)
            
            if 'name' in data:
                item.name = data['name']
            if 'description' in data:
                item.description = data['description']
            if 'price' in data:
                item.price = data['price']
            if 'category_id' in data:
                item.category_id = data['category_id']
            if 'image_url' in data:
                item.image_url = data['image_url']
            if 'is_available' in data:
                item.is_available = data['is_available']
            
            db.session.commit()
            
            return {'message': 'Menu item updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating menu item', 'error': str(e)}, 500
    
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Menu item deleted successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Item not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def delete(self, current_user, item_id):
        """Delete a menu item"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            item = MenuItem.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            
            return {'message': 'Menu item deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting menu item', 'error': str(e)}, 500

@api.route('/categories')
class AdminCategories(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all categories"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            categories = Category.query.all()
            return {
                'data': [{
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'image_url': category.image_url
                } for category in categories]
            }, 200
        except Exception as e:
            return {'message': 'Error fetching categories', 'error': str(e)}, 500

    @api.doc(security='Bearer Auth')
    @api.expect(api.model('Category', {
        'name': fields.String(required=True, description='Category name'),
        'description': fields.String(description='Category description'),
        'image_url': fields.String(description='Category image URL')
    }))
    @api.response(201, 'Category created successfully')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Create a new category"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if not data or not data.get('name'):
            return {'message': 'Name is required'}, 400
        
        try:
            category = Category(
                name=data['name'],
                description=data.get('description'),
                image_url=data.get('image_url')
            )
            
            db.session.add(category)
            db.session.commit()
            
            return {
                'message': 'Category created successfully',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'image_url': category.image_url
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating category', 'error': str(e)}, 500

@api.route('/categories/<int:category_id>')
class AdminCategoryManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('UpdateCategory', {
        'name': fields.String(description='Category name'),
        'description': fields.String(description='Category description'),
        'image_url': fields.String(description='Category image URL')
    }))
    @api.response(200, 'Category updated successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Category not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def put(self, current_user, category_id):
        """Update a category"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        try:
            category = Category.query.get_or_404(category_id)
            
            if 'name' in data:
                category.name = data['name']
            if 'description' in data:
                category.description = data['description']
            if 'image_url' in data:
                category.image_url = data['image_url']
            
            db.session.commit()
            
            return {
                'message': 'Category updated successfully',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'image_url': category.image_url
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating category', 'error': str(e)}, 500
    
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Category deleted successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Category not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def delete(self, current_user, category_id):
        """Delete a category"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            category = Category.query.get_or_404(category_id)
            db.session.delete(category)
            db.session.commit()
            
            return {'message': 'Category deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting category', 'error': str(e)}, 500

@api.route('/promotions')
class AdminPromotions(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all promotions"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            promotions = Promotion.query.all()
            return {
                'promotions': [{
                    'id': promo.id,
                    'code': promo.code,
                    'description': promo.description,
                    'discount_type': promo.discount_type,
                    'discount_value': promo.discount_value,
                    'min_purchase_amount': promo.min_purchase_amount,
                    'start_date': promo.start_date.isoformat() if promo.start_date else None,
                    'end_date': promo.end_date.isoformat() if promo.end_date else None,
                    'is_active': promo.is_active,
                    'max_uses': promo.max_uses,
                    'current_uses': promo.current_uses,
                    'created_at': promo.created_at.isoformat() if promo.created_at else None
                } for promo in promotions],
                'total': len(promotions)
            }, 200
        except Exception as e:
            return {'message': 'Error fetching promotions', 'error': str(e)}, 500

@api.route('/promotion')
class AdminPromotion(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('Promotion', {
        'code': fields.String(required=True, description='Promotion code'),
        'description': fields.String(description='Promotion description'),
        'discount_type': fields.String(required=True, description='Discount type (percentage or fixed_amount)'),
        'discount_value': fields.Float(required=True, description='Discount value'),
        'min_purchase_amount': fields.Float(description='Minimum purchase amount'),
        'start_date': fields.String(required=True, description='Start date (ISO format)'),
        'end_date': fields.String(required=True, description='End date (ISO format)'),
        'max_uses': fields.Integer(description='Maximum number of uses')
    }))
    @api.response(201, 'Promotion created successfully')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Create a new promotion"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        try:
            # Validate discount type
            if data['discount_type'] not in ['percentage', 'fixed_amount']:
                return {'message': 'Invalid discount type'}, 400
            
            # Parse dates
            try:
                start_date = datetime.fromisoformat(data['start_date'])
                end_date = datetime.fromisoformat(data['end_date'])
            except ValueError:
                return {'message': 'Invalid date format'}, 400
            
            # Create new promotion
            promotion = Promotion(
                code=data['code'],
                description=data.get('description'),
                discount_type=data['discount_type'],
                discount_value=data['discount_value'],
                min_purchase_amount=data.get('min_purchase_amount', 0),
                start_date=start_date,
                end_date=end_date,
                max_uses=data.get('max_uses'),
                is_active=True,
                current_uses=0
            )
            
            db.session.add(promotion)
            db.session.commit()
            
            return {
                'message': 'Promotion created successfully',
                'promotion': {
                    'id': promotion.id,
                    'code': promotion.code,
                    'description': promotion.description,
                    'discount_type': promotion.discount_type,
                    'discount_value': promotion.discount_value,
                    'min_purchase_amount': promotion.min_purchase_amount,
                    'start_date': promotion.start_date.isoformat(),
                    'end_date': promotion.end_date.isoformat(),
                    'is_active': promotion.is_active,
                    'max_uses': promotion.max_uses,
                    'current_uses': promotion.current_uses
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating promotion', 'error': str(e)}, 500

@api.route('/promotion/<int:promotion_id>')
class AdminPromotionManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('UpdatePromotion', {
        'description': fields.String(description='Promotion description'),
        'discount_type': fields.String(description='Discount type (percentage or fixed_amount)'),
        'discount_value': fields.Float(description='Discount value'),
        'min_purchase_amount': fields.Float(description='Minimum purchase amount'),
        'start_date': fields.String(description='Start date (ISO format)'),
        'end_date': fields.String(description='End date (ISO format)'),
        'is_active': fields.Boolean(description='Promotion active status'),
        'max_uses': fields.Integer(description='Maximum number of uses')
    }))
    @api.response(200, 'Promotion updated successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Promotion not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def put(self, current_user, promotion_id):
        """Update promotion details"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        try:
            promotion = Promotion.query.get_or_404(promotion_id)
            
            # Update fields if provided
            if 'description' in data:
                promotion.description = data['description']
            
            if 'discount_type' in data:
                if data['discount_type'] not in ['percentage', 'fixed_amount']:
                    return {'message': 'Invalid discount type'}, 400
                promotion.discount_type = data['discount_type']
            
            if 'discount_value' in data:
                promotion.discount_value = data['discount_value']
            
            if 'min_purchase_amount' in data:
                promotion.min_purchase_amount = data['min_purchase_amount']
            
            if 'start_date' in data:
                try:
                    promotion.start_date = datetime.fromisoformat(data['start_date'])
                except ValueError:
                    return {'message': 'Invalid start date format'}, 400
            
            if 'end_date' in data:
                try:
                    promotion.end_date = datetime.fromisoformat(data['end_date'])
                except ValueError:
                    return {'message': 'Invalid end date format'}, 400
            
            if 'is_active' in data:
                promotion.is_active = data['is_active']
            
            if 'max_uses' in data:
                promotion.max_uses = data['max_uses']
            
            db.session.commit()
            
            return {
                'message': 'Promotion updated successfully',
                'promotion': {
                    'id': promotion.id,
                    'code': promotion.code,
                    'description': promotion.description,
                    'discount_type': promotion.discount_type,
                    'discount_value': promotion.discount_value,
                    'min_purchase_amount': promotion.min_purchase_amount,
                    'start_date': promotion.start_date.isoformat(),
                    'end_date': promotion.end_date.isoformat(),
                    'is_active': promotion.is_active,
                    'max_uses': promotion.max_uses,
                    'current_uses': promotion.current_uses
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error updating promotion', 'error': str(e)}, 500
    
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Promotion deleted successfully')
    @api.response(403, 'Unauthorized')
    @api.response(404, 'Promotion not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def delete(self, current_user, promotion_id):
        """Delete a promotion"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            promotion = Promotion.query.get_or_404(promotion_id)
            db.session.delete(promotion)
            db.session.commit()
            
            return {'message': 'Promotion deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error deleting promotion', 'error': str(e)}, 500 