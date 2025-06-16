from flask import request
from ..models import db, Review, MenuItem, User, Order
from .auth import token_required, admin_required
from datetime import datetime
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('reviews', description='Reviews management operations')

# Models for request/response documentation
review_model = api.model('Review', {
    'id': fields.Integer(description='Review ID'),
    'user_id': fields.Integer(description='User ID'),
    'menu_item_id': fields.Integer(description='Menu item ID'),
    'order_id': fields.Integer(description='Order ID'),
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'comment': fields.String(description='Review comment'),
    'images': fields.List(fields.String, description='Review image URLs'),
    'created_at': fields.DateTime(description='Review timestamp'),
    'updated_at': fields.DateTime(description='Review update timestamp'),
    'is_verified': fields.Boolean(description='Whether review is from verified purchase'),
    'likes_count': fields.Integer(description='Number of likes'),
    'response': fields.String(description='Staff response to review')
})

review_stats_model = api.model('ReviewStats', {
    'average_rating': fields.Float(description='Average rating'),
    'total_reviews': fields.Integer(description='Total number of reviews'),
    'rating_distribution': fields.Raw(description='Distribution of ratings')
})

@api.route('')
class ReviewList(Resource):
    @api.doc('list_reviews')
    @api.marshal_list_with(review_model)
    def get(self):
        """List all reviews"""
        menu_item_id = request.args.get('menu_item_id', type=int)
        rating = request.args.get('rating', type=int)
        verified_only = request.args.get('verified_only', type=bool, default=False)
        
        query = Review.query
        
        if menu_item_id:
            query = query.filter_by(menu_item_id=menu_item_id)
        if rating:
            query = query.filter_by(rating=rating)
        if verified_only:
            query = query.filter_by(is_verified=True)
            
        return query.order_by(Review.created_at.desc()).all()

    @api.doc('create_review')
    @api.expect(review_model)
    @api.marshal_with(review_model)
    @token_required
    def post(self, current_user):
        """Create a new review"""
        data = request.get_json()
        
        # Verify order exists and belongs to user
        order = Order.query.filter_by(
            id=data['order_id'],
            user_id=current_user.id
        ).first_or_404()
        
        # Verify menu item was in order
        menu_item = MenuItem.query.get_or_404(data['menu_item_id'])
        order_items = [item.menu_item_id for item in order.items]
        if menu_item.id not in order_items:
            return {'message': 'Menu item not found in order'}, 400
        
        # Check if user already reviewed this item for this order
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            menu_item_id=menu_item.id,
            order_id=order.id
        ).first()
        
        if existing_review:
            return {'message': 'You have already reviewed this item for this order'}, 400
        
        # Create review
        review = Review(
            user_id=current_user.id,
            menu_item_id=menu_item.id,
            order_id=order.id,
            rating=data['rating'],
            comment=data.get('comment'),
            images=data.get('images', []),
            created_at=datetime.utcnow(),
            is_verified=True
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Update menu item rating
        menu_item_reviews = Review.query.filter_by(menu_item_id=menu_item.id).all()
        menu_item.average_rating = sum(r.rating for r in menu_item_reviews) / len(menu_item_reviews)
        db.session.commit()
        
        return review

@api.route('/<int:id>')
@api.param('id', 'The review identifier')
class ReviewResource(Resource):
    @api.doc('get_review')
    @api.marshal_with(review_model)
    def get(self, id):
        """Get a review by ID"""
        return Review.query.get_or_404(id)

    @api.doc('update_review')
    @api.expect(review_model)
    @api.marshal_with(review_model)
    @token_required
    def put(self, current_user, id):
        """Update a review"""
        review = Review.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()
        
        data = request.get_json()
        
        # Only allow updating rating, comment and images
        if 'rating' in data:
            review.rating = data['rating']
        if 'comment' in data:
            review.comment = data['comment']
        if 'images' in data:
            review.images = data['images']
            
        review.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update menu item rating
        menu_item = MenuItem.query.get(review.menu_item_id)
        menu_item_reviews = Review.query.filter_by(menu_item_id=menu_item.id).all()
        menu_item.average_rating = sum(r.rating for r in menu_item_reviews) / len(menu_item_reviews)
        db.session.commit()
        
        return review

    @api.doc('delete_review')
    @token_required
    def delete(self, current_user, id):
        """Delete a review"""
        review = Review.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first_or_404()
        
        menu_item_id = review.menu_item_id
        db.session.delete(review)
        db.session.commit()
        
        # Update menu item rating
        menu_item = MenuItem.query.get(menu_item_id)
        menu_item_reviews = Review.query.filter_by(menu_item_id=menu_item_id).all()
        if menu_item_reviews:
            menu_item.average_rating = sum(r.rating for r in menu_item_reviews) / len(menu_item_reviews)
        else:
            menu_item.average_rating = None
        db.session.commit()
        
        return {'message': 'Review deleted'}

@api.route('/<int:id>/respond')
@api.param('id', 'The review identifier')
class ReviewResponse(Resource):
    @api.doc('respond_to_review')
    @api.expect({'response': fields.String(required=True)})
    @api.marshal_with(review_model)
    @admin_required
    def post(self, current_user, id):
        """Respond to a review (Admin only)"""
        review = Review.query.get_or_404(id)
        data = request.get_json()
        
        review.response = data['response']
        review.updated_at = datetime.utcnow()
        db.session.commit()
        
        return review

@api.route('/stats')
class ReviewStats(Resource):
    @api.doc('get_review_stats')
    @api.marshal_with(review_stats_model)
    def get(self):
        """Get review statistics"""
        menu_item_id = request.args.get('menu_item_id', type=int)
        
        query = Review.query
        if menu_item_id:
            query = query.filter_by(menu_item_id=menu_item_id)
        
        reviews = query.all()
        if not reviews:
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {str(i): 0 for i in range(1, 6)}
            }
        
        # Calculate stats
        total = len(reviews)
        average = sum(r.rating for r in reviews) / total
        distribution = {str(i): 0 for i in range(1, 6)}
        for review in reviews:
            distribution[str(review.rating)] += 1
        
        return {
            'average_rating': round(average, 2),
            'total_reviews': total,
            'rating_distribution': distribution
        } 