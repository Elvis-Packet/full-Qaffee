from flask import request
from ..models import db, Order, MenuItem, Category, User, Review
from .auth import token_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('analytics', description='Business analytics operations')

# Models for request/response documentation
sales_stats_model = api.model('SalesStats', {
    'total_revenue': fields.Float(description='Total revenue'),
    'total_orders': fields.Integer(description='Total number of orders'),
    'average_order_value': fields.Float(description='Average order value'),
    'revenue_by_period': fields.Raw(description='Revenue breakdown by period'),
    'orders_by_period': fields.Raw(description='Orders breakdown by period')
})

menu_stats_model = api.model('MenuStats', {
    'total_items': fields.Integer(description='Total number of menu items'),
    'top_sellers': fields.Raw(description='Top selling items'),
    'category_performance': fields.Raw(description='Performance by category'),
    'average_ratings': fields.Raw(description='Average ratings by item')
})

customer_stats_model = api.model('CustomerStats', {
    'total_customers': fields.Integer(description='Total number of customers'),
    'active_customers': fields.Integer(description='Number of active customers'),
    'new_customers': fields.Integer(description='New customers in period'),
    'customer_segments': fields.Raw(description='Customer segments data')
})

time_series_model = api.model('TimeSeries', {
    'date': fields.String(description='Date'),
    'value': fields.Float(description='Value')
})

popular_items_model = api.model('PopularItems', {
    'item_id': fields.Integer(description='Menu item ID'),
    'name': fields.String(description='Item name'),
    'total_orders': fields.Integer(description='Total number of orders'),
    'total_revenue': fields.Float(description='Total revenue generated')
})

category_stats_model = api.model('CategoryStats', {
    'category_id': fields.Integer(description='Category ID'),
    'name': fields.String(description='Category name'),
    'total_orders': fields.Integer(description='Total orders from this category'),
    'total_revenue': fields.Float(description='Total revenue from this category')
})

@api.route('/sales')
class SalesAnalytics(Resource):
    @api.doc('get_sales_analytics')
    @api.marshal_with(sales_stats_model)
    @token_required
    def get(self, current_user):
        """Get sales analytics"""
        # Get query parameters
        period = request.args.get('period', 'daily')  # daily, weekly, monthly
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        if not start_date:
            if period == 'daily':
                start_date = end_date - timedelta(days=30)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=12)
            else:
                start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Query orders within date range
        orders = Order.query.filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).all()
        
        # Calculate basic metrics
        total_revenue = sum(order.total_amount for order in orders)
        total_orders = len(orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Calculate period breakdowns
        revenue_by_period = {}
        orders_by_period = {}
        
        for order in orders:
            if period == 'daily':
                key = order.created_at.strftime('%Y-%m-%d')
            elif period == 'weekly':
                key = order.created_at.strftime('%Y-W%W')
            else:
                key = order.created_at.strftime('%Y-%m')
                
            revenue_by_period[key] = revenue_by_period.get(key, 0) + order.total_amount
            orders_by_period[key] = orders_by_period.get(key, 0) + 1
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders,
            'average_order_value': round(avg_order_value, 2),
            'revenue_by_period': revenue_by_period,
            'orders_by_period': orders_by_period
        }

@api.route('/menu')
class MenuAnalytics(Resource):
    @api.doc('get_menu_analytics')
    @api.marshal_with(menu_stats_model)
    @token_required
    def get(self, current_user):
        """Get menu analytics"""
        # Get query parameters
        period = request.args.get('period', 'last_30_days')
        
        # Set date range
        end_date = datetime.utcnow()
        if period == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif period == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Get all menu items
        menu_items = MenuItem.query.all()
        total_items = len(menu_items)
        
        # Calculate item sales
        item_sales = {}
        orders = Order.query.filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).all()
        
        for order in orders:
            for item in order.items:
                if item.menu_item_id not in item_sales:
                    menu_item = MenuItem.query.get(item.menu_item_id)
                    item_sales[item.menu_item_id] = {
                        'name': menu_item.name,
                        'category': menu_item.category,
                        'quantity': 0,
                        'revenue': 0
                    }
                item_sales[item.menu_item_id]['quantity'] += item.quantity
                item_sales[item.menu_item_id]['revenue'] += item.subtotal
        
        # Get top sellers
        top_sellers = sorted(
            item_sales.values(),
            key=lambda x: x['quantity'],
            reverse=True
        )[:10]
        
        # Calculate category performance
        category_performance = {}
        for item in item_sales.values():
            if item['category'] not in category_performance:
                category_performance[item['category']] = {
                    'items_sold': 0,
                    'revenue': 0
                }
            category_performance[item['category']]['items_sold'] += item['quantity']
            category_performance[item['category']]['revenue'] += item['revenue']
        
        # Calculate average ratings
        ratings = {}
        for item in menu_items:
            reviews = Review.query.filter_by(menu_item_id=item.id).all()
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
                ratings[item.name] = round(avg_rating, 2)
        
        return {
            'total_items': total_items,
            'top_sellers': top_sellers,
            'category_performance': category_performance,
            'average_ratings': ratings
        }

@api.route('/customers')
class CustomerAnalytics(Resource):
    @api.doc('get_customer_analytics')
    @api.marshal_with(customer_stats_model)
    @token_required
    def get(self, current_user):
        """Get customer analytics"""
        # Get query parameters
        period = request.args.get('period', 'last_30_days')
        
        # Set date range
        end_date = datetime.utcnow()
        if period == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif period == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Get all customers
        total_customers = User.query.count()
        
        # Get active customers (made at least one order in period)
        active_customers = db.session.query(
            User.id
        ).join(
            Order
        ).filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).distinct().count()
        
        # Get new customers in period
        new_customers = User.query.filter(
            User.created_at.between(start_date, end_date)
        ).count()
        
        # Calculate customer segments
        customer_segments = {
            'new': new_customers,
            'returning': active_customers - new_customers,
            'inactive': total_customers - active_customers
        }
        
        # Calculate order frequency distribution
        order_counts = db.session.query(
            User.id,
            func.count(Order.id).label('order_count')
        ).join(
            Order
        ).filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).group_by(
            User.id
        ).all()
        
        frequency_distribution = {
            '1_order': len([c for c in order_counts if c.order_count == 1]),
            '2_3_orders': len([c for c in order_counts if 2 <= c.order_count <= 3]),
            '4_plus_orders': len([c for c in order_counts if c.order_count >= 4])
        }
        
        customer_segments['frequency'] = frequency_distribution
        
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'new_customers': new_customers,
            'customer_segments': customer_segments
        }

@api.route('/dashboard')
class AnalyticsDashboard(Resource):
    @api.doc('get_analytics_dashboard')
    @token_required
    def get(self, current_user):
        """Get analytics dashboard overview"""
        # Get today's date and previous periods
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        last_week_start = today - timedelta(days=7)
        last_month_start = today - timedelta(days=30)
        
        # Get key metrics
        metrics = {
            'revenue': {
                'today': sum(o.total_amount for o in Order.query.filter(
                    func.date(Order.created_at) == func.date(today),
                    Order.status == 'completed'
                ).all()),
                'yesterday': sum(o.total_amount for o in Order.query.filter(
                    func.date(Order.created_at) == func.date(yesterday),
                    Order.status == 'completed'
                ).all()),
                'last_7_days': sum(o.total_amount for o in Order.query.filter(
                    Order.created_at >= last_week_start,
                    Order.status == 'completed'
                ).all()),
                'last_30_days': sum(o.total_amount for o in Order.query.filter(
                    Order.created_at >= last_month_start,
                    Order.status == 'completed'
                ).all())
            },
            'orders': {
                'today': Order.query.filter(
                    func.date(Order.created_at) == func.date(today)
                ).count(),
                'yesterday': Order.query.filter(
                    func.date(Order.created_at) == func.date(yesterday)
                ).count(),
                'last_7_days': Order.query.filter(
                    Order.created_at >= last_week_start
                ).count(),
                'last_30_days': Order.query.filter(
                    Order.created_at >= last_month_start
                ).count()
            },
            'customers': {
                'total': User.query.count(),
                'new_today': User.query.filter(
                    func.date(User.created_at) == func.date(today)
                ).count(),
                'new_last_7_days': User.query.filter(
                    User.created_at >= last_week_start
                ).count(),
                'new_last_30_days': User.query.filter(
                    User.created_at >= last_month_start
                ).count()
            }
        }
        
        # Calculate trends
        metrics['trends'] = {
            'revenue_vs_yesterday': calculate_trend(
                metrics['revenue']['today'],
                metrics['revenue']['yesterday']
            ),
            'orders_vs_yesterday': calculate_trend(
                metrics['orders']['today'],
                metrics['orders']['yesterday']
            ),
            'customers_vs_last_week': calculate_trend(
                metrics['customers']['new_today'],
                metrics['customers']['new_last_7_days'] / 7
            )
        }
        
        return metrics

def calculate_trend(current, previous):
    """Calculate percentage change"""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 2)

@api.route('/sales/daily')
class DailySales(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', [time_series_model])
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @api.param('days', 'Number of days to look back')
    @token_required
    def get(self, current_user):
        """Get daily sales for the last N days"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            days = int(request.args.get('days', 30))
            start_date = datetime.utcnow() - timedelta(days=days)
            
            daily_sales = db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(Order.total_amount).label('total')
            ).filter(
                Order.status == 'delivered',
                Order.created_at >= start_date
            ).group_by(
                func.date(Order.created_at)
            ).order_by(
                'date'
            ).all()
            
            return [{
                'date': date.strftime('%Y-%m-%d'),
                'value': float(total)
            } for date, total in daily_sales], 200
        except Exception as e:
            return {'message': 'Error fetching daily sales', 'error': str(e)}, 500

@api.route('/items/popular')
class PopularItems(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', [popular_items_model])
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @api.param('limit', 'Number of items to return')
    @token_required
    def get(self, current_user):
        """Get most popular menu items"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            limit = int(request.args.get('limit', 10))
            
            popular_items = db.session.query(
                MenuItem,
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('revenue')
            ).join(
                Order, MenuItem.orders
            ).filter(
                Order.status == 'delivered'
            ).group_by(
                MenuItem.id
            ).order_by(
                func.count(Order.id).desc()
            ).limit(limit).all()
            
            return [{
                'item_id': item.id,
                'name': item.name,
                'total_orders': int(order_count),
                'total_revenue': float(revenue)
            } for item, order_count, revenue in popular_items], 200
        except Exception as e:
            return {'message': 'Error fetching popular items', 'error': str(e)}, 500

@api.route('/categories/performance')
class CategoryPerformance(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', [category_stats_model])
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get performance statistics by category"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            category_stats = db.session.query(
                Category,
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('revenue')
            ).join(
                MenuItem, Category.items
            ).join(
                Order, MenuItem.orders
            ).filter(
                Order.status == 'delivered'
            ).group_by(
                Category.id
            ).order_by(
                func.sum(Order.total_amount).desc()
            ).all()
            
            return [{
                'category_id': category.id,
                'name': category.name,
                'total_orders': int(order_count),
                'total_revenue': float(revenue)
            } for category, order_count, revenue in category_stats], 200
        except Exception as e:
            return {'message': 'Error fetching category statistics', 'error': str(e)}, 500

@api.route('/users/activity')
class UserActivity(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get user activity statistics"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            # Get active users (placed at least one order)
            active_users = db.session.query(
                func.count(func.distinct(Order.user_id))
            ).filter(
                Order.status == 'delivered'
            ).scalar()
            
            # Get average orders per user
            total_orders = Order.query.filter_by(status='delivered').count()
            total_users = User.query.count()
            avg_orders_per_user = total_orders / total_users if total_users > 0 else 0
            
            # Get user retention (users who ordered more than once)
            repeat_customers = db.session.query(
                func.count(func.distinct(Order.user_id))
            ).filter(
                Order.status == 'delivered'
            ).group_by(
                Order.user_id
            ).having(
                func.count(Order.id) > 1
            ).count()
            
            retention_rate = (repeat_customers / total_users * 100) if total_users > 0 else 0
            
            return {
                'active_users': active_users,
                'total_users': total_users,
                'average_orders_per_user': round(avg_orders_per_user, 2),
                'repeat_customers': repeat_customers,
                'retention_rate': round(retention_rate, 2)
            }, 200
        except Exception as e:
            return {'message': 'Error fetching user activity', 'error': str(e)}, 500 