from flask import request
from ..models import db, Feedback
from .auth import token_required
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('feedback', description='Feedback operations')

# Models for request/response documentation
feedback_input_model = api.model('FeedbackInput', {
    'rating': fields.Integer(required=True, description='Rating (1-5)', min=1, max=5),
    'comment': fields.String(description='Feedback comment'),
    'category': fields.String(description='Feedback category', enum=['service', 'food', 'app', 'delivery', 'other'])
})

feedback_model = api.model('Feedback', {
    'id': fields.Integer(description='Feedback ID'),
    'user_id': fields.Integer(description='User ID'),
    'rating': fields.Integer(description='Rating'),
    'comment': fields.String(description='Comment'),
    'category': fields.String(description='Category'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

@api.route('')
class FeedbackManagement(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(feedback_input_model)
    @api.response(201, 'Feedback submitted successfully')
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Submit feedback"""
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return {'message': 'Rating is required'}, 400
        
        if not 1 <= data['rating'] <= 5:
            return {'message': 'Rating must be between 1 and 5'}, 400
        
        try:
            feedback = Feedback(
                user_id=current_user.id,
                rating=data['rating'],
                comment=data.get('comment'),
                category=data.get('category', 'other')
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            return {
                'message': 'Feedback submitted successfully',
                'feedback': {
                    'id': feedback.id,
                    'rating': feedback.rating,
                    'comment': feedback.comment,
                    'category': feedback.category,
                    'created_at': feedback.created_at
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error submitting feedback', 'error': str(e)}, 500
    
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', [feedback_model])
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get user's feedback history"""
        try:
            if not current_user.is_admin:
                # Regular users can only see their own feedback
                feedbacks = Feedback.query.filter_by(
                    user_id=current_user.id
                ).order_by(
                    Feedback.created_at.desc()
                ).all()
            else:
                # Admins can see all feedback
                feedbacks = Feedback.query.order_by(
                    Feedback.created_at.desc()
                ).all()
            
            return [{
                'id': feedback.id,
                'user_id': feedback.user_id,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'category': feedback.category,
                'created_at': feedback.created_at
            } for feedback in feedbacks], 200
        except Exception as e:
            return {'message': 'Error fetching feedback', 'error': str(e)}, 500

@api.route('/stats')
class FeedbackStats(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(403, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get feedback statistics (Admin only)"""
        if not current_user.is_admin:
            return {'message': 'Unauthorized'}, 403
        
        try:
            # Calculate average rating
            feedbacks = Feedback.query.all()
            total_feedbacks = len(feedbacks)
            
            if total_feedbacks > 0:
                average_rating = sum(f.rating for f in feedbacks) / total_feedbacks
            else:
                average_rating = 0
            
            # Get rating distribution
            rating_distribution = {
                rating: Feedback.query.filter_by(rating=rating).count()
                for rating in range(1, 6)
            }
            
            # Get category distribution
            category_distribution = {}
            for feedback in feedbacks:
                category = feedback.category or 'other'
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            return {
                'total_feedbacks': total_feedbacks,
                'average_rating': round(average_rating, 2),
                'rating_distribution': rating_distribution,
                'category_distribution': category_distribution
            }, 200
        except Exception as e:
            return {'message': 'Error fetching feedback statistics', 'error': str(e)}, 500 