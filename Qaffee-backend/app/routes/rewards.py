from flask import request, jsonify
from ..models import db, User, Order, Reward, RewardClaim, LoyaltyPoints
from .auth import token_required, admin_required
from flask_restx import Namespace, Resource, fields
from datetime import datetime

# Create API namespace
api = Namespace('rewards', description='Rewards and loyalty program operations')

# Constants
POINTS_PER_DOLLAR = 10
POINTS_FOR_REFERRAL = 100

# Models for request/response documentation
points_history_model = api.model('PointsHistory', {
    'order_id': fields.Integer(description='Order ID'),
    'points_earned': fields.Integer(description='Points earned'),
    'date': fields.DateTime(description='Date points were earned')
})

reward_model = api.model('Reward', {
    'id': fields.Integer(description='Reward ID'),
    'name': fields.String(required=True, description='Reward name'),
    'description': fields.String(required=True, description='Reward description'),
    'points_required': fields.Integer(required=True, description='Points required to claim'),
    'reward_type': fields.String(description='Reward type (discount/free_item/etc)'),
    'value': fields.Float(description='Reward value (if applicable)'),
    'is_active': fields.Boolean(description='Whether reward is active'),
    'start_date': fields.DateTime(description='Reward availability start date'),
    'end_date': fields.DateTime(description='Reward availability end date'),
    'quantity_available': fields.Integer(description='Number of rewards available'),
    'terms_conditions': fields.String(description='Terms and conditions')
})

points_balance_response = api.model('PointsBalanceResponse', {
    'current_points': fields.Integer(description='Current points balance'),
    'points_history': fields.List(fields.Nested(points_history_model)),
    'available_rewards': fields.List(fields.Nested(reward_model)),
    'points_per_dollar': fields.Integer(description='Points earned per dollar spent')
})

referral_share_response = api.model('ReferralShareResponse', {
    'referral_code': fields.String(description='User\'s referral code'),
    'points_per_referral': fields.Integer(description='Points earned per successful referral'),
    'share_message': fields.String(description='Pre-formatted share message')
})

referral_claim_input = api.model('ReferralClaimInput', {
    'referral_code': fields.String(required=True, description='Referral code to claim')
})

referral_claim_response = api.model('ReferralClaimResponse', {
    'message': fields.String(description='Success message'),
    'reward': fields.String(description='Reward description')
})

loyalty_points_model = api.model('LoyaltyPoints', {
    'id': fields.Integer(description='Points record ID'),
    'user_id': fields.Integer(description='User ID'),
    'points': fields.Integer(description='Points amount'),
    'transaction_type': fields.String(description='Transaction type (earned/redeemed)'),
    'source': fields.String(description='Points source (order/reward/referral)'),
    'reference_id': fields.String(description='Reference ID (order ID, etc.)'),
    'created_at': fields.DateTime(description='Transaction timestamp')
})

reward_claim_model = api.model('RewardClaim', {
    'id': fields.Integer(description='Claim ID'),
    'user_id': fields.Integer(description='User ID'),
    'reward_id': fields.Integer(description='Reward ID'),
    'claimed_at': fields.DateTime(description='Claim timestamp'),
    'status': fields.String(description='Claim status'),
    'used_at': fields.DateTime(description='When reward was used'),
    'expiry_date': fields.DateTime(description='Claim expiry date')
})

@api.route('/earn')
class EarnPoints(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('EarnPoints', {
        'order_id': fields.Integer(required=True, description='Order ID')
    }))
    @api.response(200, 'Points earned successfully')
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Earn points by completing an order"""
        data = request.get_json()
        
        if not data or not data.get('order_id'):
            return {'message': 'Order ID is required'}, 400
        
        try:
            order = Order.query.filter_by(
                id=data['order_id'],
                user_id=current_user.id,
                status='delivered'
            ).first()
            
            if not order:
                return {'message': 'Order not found or not eligible for points'}, 404
            
            # Calculate points (1 point per dollar spent)
            points_earned = int(order.total_amount * POINTS_PER_DOLLAR)
            
            # Update user's points
            current_user.reward_points += points_earned
            db.session.commit()
            
            return {
                'message': f'Earned {points_earned} points!',
                'points_earned': points_earned,
                'total_points': current_user.reward_points
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error awarding points', 'error': str(e)}, 500

@api.route('/redeem')
class RedeemReward(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(api.model('RedeemReward', {
        'reward_name': fields.String(required=True, description='Name of the reward to redeem')
    }))
    @api.response(200, 'Reward redeemed successfully')
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Redeem points for a reward"""
        data = request.get_json()
        
        if not data or not data.get('reward_name'):
            return {'message': 'Reward name is required'}, 400
        
        try:
            # Get reward details
            reward = next(
                (r for r in [
                    {
                        'name': 'Free Coffee',
                        'points_required': 500,
                        'code': 'FREE_COFFEE'
                    },
                    {
                        'name': '$5 Off',
                        'points_required': 1000,
                        'code': 'FIVE_OFF'
                    },
                    {
                        'name': 'Free Delivery',
                        'points_required': 750,
                        'code': 'FREE_DELIVERY'
                    }
                ] if r['name'] == data['reward_name']),
                None
            )
            
            if not reward:
                return {'message': 'Invalid reward name'}, 400
            
            if current_user.reward_points < reward['points_required']:
                return {'message': 'Insufficient points'}, 400
            
            # Deduct points and generate reward code
            current_user.reward_points -= reward['points_required']
            db.session.commit()
            
            return {
                'message': 'Reward redeemed successfully',
                'reward_code': reward['code'],
                'remaining_points': current_user.reward_points
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error redeeming reward', 'error': str(e)}, 500

@api.route('/balance')
class RewardsBalance(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', points_balance_response)
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get user's rewards points balance and history"""
        try:
            # Get points history (last 5 orders)
            recent_orders = Order.query.filter_by(
                user_id=current_user.id,
                status='delivered'
            ).order_by(
                Order.created_at.desc()
            ).limit(5).all()
            
            points_history = [{
                'order_id': order.id,
                'points_earned': int(order.total_amount * POINTS_PER_DOLLAR),
                'date': order.created_at
            } for order in recent_orders]
            
            # Calculate available rewards
            available_rewards = [
                {
                    'name': 'Free Coffee',
                    'points_required': 500,
                    'description': 'Get any regular coffee for free'
                },
                {
                    'name': '$5 Off',
                    'points_required': 1000,
                    'description': '$5 off your next order'
                },
                {
                    'name': 'Free Delivery',
                    'points_required': 750,
                    'description': 'Free delivery on your next order'
                }
            ]
            
            return {
                'current_points': current_user.reward_points,
                'points_history': points_history,
                'available_rewards': available_rewards,
                'points_per_dollar': POINTS_PER_DOLLAR
            }, 200
        except Exception as e:
            return {'message': 'Error fetching points balance', 'error': str(e)}, 500

@api.route('/referral/share')
class ReferralShare(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', referral_share_response)
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get user's referral code and share message"""
        try:
            if not current_user.referral_code:
                # Generate referral code if not exists
                import random
                import string
                
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                current_user.referral_code = code
                db.session.commit()
            
            return {
                'referral_code': current_user.referral_code,
                'points_per_referral': POINTS_FOR_REFERRAL,
                'share_message': f"Use my referral code {current_user.referral_code} at Qaffee and get your first drink free!"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error generating referral code', 'error': str(e)}, 500

@api.route('/referral/claim')
class ReferralClaim(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(referral_claim_input)
    @api.response(200, 'Success', referral_claim_response)
    @api.response(400, 'Validation Error')
    @api.response(404, 'Invalid referral code')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Claim a referral code"""
        data = request.get_json()
        
        if not data or not data.get('referral_code'):
            return {'message': 'Referral code is required'}, 400
        
        try:
            # Check if user has already claimed a referral
            if current_user.referral_claimed:
                return {'message': 'You have already claimed a referral'}, 400
            
            # Find referring user
            referring_user = User.query.filter_by(
                referral_code=data['referral_code']
            ).first()
            
            if not referring_user:
                return {'message': 'Invalid referral code'}, 404
            
            if referring_user.id == current_user.id:
                return {'message': 'Cannot use your own referral code'}, 400
            
            # Award points to referring user
            referring_user.reward_points += POINTS_FOR_REFERRAL
            
            # Mark current user as having claimed a referral
            current_user.referral_claimed = True
            
            db.session.commit()
            
            return {
                'message': 'Referral claimed successfully',
                'reward': 'Your first drink is free!'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error claiming referral', 'error': str(e)}, 500

@api.route('/points')
class LoyaltyPointsList(Resource):
    @api.doc('get_points_balance')
    @token_required
    def get(self, current_user):
        """Get user's loyalty points balance and history"""
        # Get points history
        history = LoyaltyPoints.query.filter_by(
            user_id=current_user.id
        ).order_by(LoyaltyPoints.created_at.desc()).all()
        
        # Calculate total points
        total_points = sum(
            record.points if record.transaction_type == 'earned' else -record.points
            for record in history
        )
        
        return {
            'total_points': total_points,
            'history': [{
                'id': record.id,
                'points': record.points,
                'transaction_type': record.transaction_type,
                'source': record.source,
                'reference_id': record.reference_id,
                'created_at': record.created_at
            } for record in history]
        }

@api.route('/rewards')
class RewardsList(Resource):
    @api.doc('list_rewards')
    @api.marshal_list_with(reward_model)
    @token_required
    def get(self, current_user):
        """List available rewards"""
        now = datetime.utcnow()
        return Reward.query.filter(
            Reward.is_active == True,
            (Reward.start_date <= now) | (Reward.start_date == None),
            (Reward.end_date >= now) | (Reward.end_date == None),
            (Reward.quantity_available > 0) | (Reward.quantity_available == None)
        ).all()

    @api.doc('create_reward')
    @api.expect(reward_model)
    @api.marshal_with(reward_model)
    @admin_required
    def post(self, current_user):
        """Create a new reward (Admin only)"""
        data = request.get_json()
        reward = Reward(**data)
        db.session.add(reward)
        db.session.commit()
        return reward

@api.route('/rewards/<int:id>')
@api.param('id', 'The reward identifier')
class RewardResource(Resource):
    @api.doc('get_reward')
    @api.marshal_with(reward_model)
    @token_required
    def get(self, current_user, id):
        """Get a reward by ID"""
        return Reward.query.get_or_404(id)

    @api.doc('update_reward')
    @api.expect(reward_model)
    @api.marshal_with(reward_model)
    @admin_required
    def put(self, current_user, id):
        """Update a reward (Admin only)"""
        reward = Reward.query.get_or_404(id)
        data = request.get_json()
        
        for key, value in data.items():
            setattr(reward, key, value)
            
        db.session.commit()
        return reward

@api.route('/rewards/<int:id>/claim')
@api.param('id', 'The reward identifier')
class ClaimReward(Resource):
    @api.doc('claim_reward')
    @api.marshal_with(reward_claim_model)
    @token_required
    def post(self, current_user, id):
        """Claim a reward"""
        reward = Reward.query.get_or_404(id)
        
        # Verify reward is available
        now = datetime.utcnow()
        if not reward.is_active:
            return {'message': 'Reward is not active'}, 400
        if reward.start_date and reward.start_date > now:
            return {'message': 'Reward is not yet available'}, 400
        if reward.end_date and reward.end_date < now:
            return {'message': 'Reward has expired'}, 400
        if reward.quantity_available is not None and reward.quantity_available <= 0:
            return {'message': 'Reward is out of stock'}, 400
        
        # Check user has enough points
        points_balance = sum(
            record.points if record.transaction_type == 'earned' else -record.points
            for record in LoyaltyPoints.query.filter_by(user_id=current_user.id).all()
        )
        
        if points_balance < reward.points_required:
            return {'message': 'Insufficient points'}, 400
        
        # Create points deduction record
        points_record = LoyaltyPoints(
            user_id=current_user.id,
            points=reward.points_required,
            transaction_type='redeemed',
            source='reward',
            reference_id=str(reward.id),
            created_at=now
        )
        
        # Create reward claim
        claim = RewardClaim(
            user_id=current_user.id,
            reward_id=reward.id,
            claimed_at=now,
            status='active',
            expiry_date=now + reward.validity_period if reward.validity_period else None
        )
        
        # Update reward quantity
        if reward.quantity_available is not None:
            reward.quantity_available -= 1
        
        db.session.add(points_record)
        db.session.add(claim)
        db.session.commit()
        
        return claim

@api.route('/claims')
class RewardClaims(Resource):
    @api.doc('list_claims')
    @api.marshal_list_with(reward_claim_model)
    @token_required
    def get(self, current_user):
        """List user's reward claims"""
        return RewardClaim.query.filter_by(
            user_id=current_user.id
        ).order_by(RewardClaim.claimed_at.desc()).all()

@api.route('/claims/<int:id>/use')
@api.param('id', 'The reward claim identifier')
class UseReward(Resource):
    @api.doc('use_reward')
    @api.marshal_with(reward_claim_model)
    @token_required
    def post(self, current_user, id):
        """Mark a reward claim as used"""
        claim = RewardClaim.query.filter_by(
            id=id,
            user_id=current_user.id,
            status='active'
        ).first_or_404()
        
        # Verify claim hasn't expired
        if claim.expiry_date and claim.expiry_date < datetime.utcnow():
            return {'message': 'Reward claim has expired'}, 400
        
        claim.status = 'used'
        claim.used_at = datetime.utcnow()
        db.session.commit()
        
        return claim 