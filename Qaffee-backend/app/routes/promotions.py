from flask import Blueprint, request, jsonify
from flask_restx import Resource, Namespace, fields
from ..models import db, Promotion
from ..utils.auth import token_required
from datetime import datetime

api = Namespace('promotions', description='Promotion operations')

@api.route('/validate')
class ValidatePromotion(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('ValidatePromotion', {
        'code': fields.String(required=True, description='Promotion code to validate')
    }))
    @api.response(200, 'Promotion validated successfully')
    @api.response(400, 'Invalid promotion code')
    @api.response(404, 'Promotion not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Validate a promotion code"""
        try:
            data = request.get_json()
            code = data.get('code', '').strip().upper()
            
            if not code:
                return {'message': 'Promotion code is required'}, 400
            
            # Find the promotion
            promotion = Promotion.query.filter_by(code=code).first()
            
            if not promotion:
                return {'message': 'Invalid promotion code'}, 404
            
            # Check if promotion is active
            if not promotion.is_active:
                return {'message': 'This promotion is not active'}, 400
            
            # Check if promotion has expired
            now = datetime.utcnow()
            if promotion.start_date > now:
                return {'message': 'This promotion has not started yet'}, 400
            if promotion.end_date < now:
                return {'message': 'This promotion has expired'}, 400
            
            # Check if promotion has reached max uses
            if promotion.max_uses and promotion.current_uses >= promotion.max_uses:
                return {'message': 'This promotion has reached its maximum usage limit'}, 400
            
            return {
                'message': 'Promotion code is valid',
                'promotion': {
                    'id': promotion.id,
                    'code': promotion.code,
                    'description': promotion.description,
                    'discount_type': promotion.discount_type,
                    'discount_value': promotion.discount_value,
                    'min_purchase_amount': promotion.min_purchase_amount
                }
            }, 200
            
        except Exception as e:
            return {'message': 'Error validating promotion code', 'error': str(e)}, 500

@api.route('/active')
class ActivePromotions(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get all active promotions"""
        try:
            now = datetime.utcnow()
            promotions = Promotion.query.filter(
                Promotion.is_active == True,
                Promotion.start_date <= now,
                Promotion.end_date >= now
            ).all()
            
            return {
                'promotions': [{
                    'id': promo.id,
                    'code': promo.code,
                    'description': promo.description,
                    'discount_type': promo.discount_type,
                    'discount_value': promo.discount_value,
                    'min_purchase_amount': promo.min_purchase_amount,
                    'start_date': promo.start_date.isoformat(),
                    'end_date': promo.end_date.isoformat()
                } for promo in promotions]
            }, 200
            
        except Exception as e:
            return {'message': 'Error fetching active promotions', 'error': str(e)}, 500 