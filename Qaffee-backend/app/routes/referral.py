from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, ReferralCode, ReferralUse, LoyaltyPoints
from .auth import token_required, admin_required
from flask_restx import Namespace, Resource, fields
import random
import string
import uuid
from datetime import datetime

# Create API namespace
api = Namespace('referral', description='Referral program operations')

# Models for request/response documentation
referral_code_model = api.model('ReferralCode', {
    'id': fields.Integer(description='Referral code ID'),
    'user_id': fields.Integer(description='User ID'),
    'code': fields.String(description='Referral code'),
    'points_reward': fields.Integer(description='Points reward for referrer'),
    'points_bonus': fields.Integer(description='Points bonus for referred user'),
    'uses': fields.Integer(description='Number of times used'),
    'max_uses': fields.Integer(description='Maximum number of uses'),
    'expiry_date': fields.DateTime(description='Code expiry date'),
    'is_active': fields.Boolean(description='Whether code is active')
})

referral_use_model = api.model('ReferralUse', {
    'id': fields.Integer(description='Referral use ID'),
    'referral_code_id': fields.Integer(description='Referral code ID'),
    'referred_user_id': fields.Integer(description='Referred user ID'),
    'used_at': fields.DateTime(description='When referral was used'),
    'points_awarded': fields.Integer(description='Points awarded to referrer'),
    'bonus_awarded': fields.Integer(description='Bonus points awarded to referred user')
})

referral_stats_model = api.model('ReferralStats', {
    'total_referrals': fields.Integer(description='Total number of referrals'),
    'active_referrals': fields.Integer(description='Number of active referrals'),
    'points_earned': fields.Integer(description='Total points earned from referrals'),
    'conversion_rate': fields.Float(description='Referral conversion rate')
})

leaderboard_entry_model = api.model('LeaderboardEntry', {
    'name': fields.String(description='User\'s name'),
    'referral_count': fields.Integer(description='Number of referrals'),
    'points_earned': fields.Integer(description='Points earned from referrals')
})

referral_bp = Blueprint('referral', __name__)

def generate_referral_code():
    """Generate a unique 8-character referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not User.query.filter_by(referral_code=code).first():
            return code

@referral_bp.route('/share', methods=['POST'])
@token_required
def share_referral(current_user):
    try:
        if not current_user.referral_code:
            current_user.referral_code = generate_referral_code()
            db.session.commit()
        
        share_message = (
            f"Join me on Qaffee! Use my referral code {current_user.referral_code} "
            "to get your first drink free. Download the app now: "
            "https://qaffee.com/app"
        )
        
        return jsonify({
            'referral_code': current_user.referral_code,
            'share_message': share_message,
            'share_links': {
                'whatsapp': f"https://wa.me/?text={share_message}",
                'twitter': f"https://twitter.com/intent/tweet?text={share_message}",
                'facebook': f"https://www.facebook.com/sharer/sharer.php?u=https://qaffee.com/referral/{current_user.referral_code}"
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error generating referral code', 'error': str(e)}), 500

@api.route('/code')
class ReferralCode(Resource):
    @api.doc('get_referral_code')
    @api.marshal_with(referral_code_model)
    @token_required
    def get(self, current_user):
        """Get user's referral code"""
        code = ReferralCode.query.filter_by(user_id=current_user.id).first()
        
        if not code:
            # Generate new referral code
            code = ReferralCode(
                user_id=current_user.id,
                code=str(uuid.uuid4())[:8].upper(),
                points_reward=current_app.config['REFERRAL_POINTS_REWARD'],
                points_bonus=current_app.config['REFERRAL_POINTS_BONUS'],
                max_uses=current_app.config['REFERRAL_MAX_USES'],
                is_active=True
            )
            db.session.add(code)
            db.session.commit()
            
        return code

    @api.doc('update_referral_code')
    @api.expect(referral_code_model)
    @api.marshal_with(referral_code_model)
    @admin_required
    def put(self, current_user):
        """Update referral code settings (Admin only)"""
        code = ReferralCode.query.filter_by(user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        # Only allow updating certain fields
        if 'points_reward' in data:
            code.points_reward = data['points_reward']
        if 'points_bonus' in data:
            code.points_bonus = data['points_bonus']
        if 'max_uses' in data:
            code.max_uses = data['max_uses']
        if 'expiry_date' in data:
            code.expiry_date = data['expiry_date']
        if 'is_active' in data:
            code.is_active = data['is_active']
            
        db.session.commit()
        return code

@api.route('/apply/<string:code>')
@api.param('code', 'The referral code to apply')
class ApplyReferral(Resource):
    @api.doc('apply_referral_code')
    @token_required
    def post(self, current_user, code):
        """Apply a referral code"""
        # Find referral code
        referral = ReferralCode.query.filter_by(code=code, is_active=True).first()
        if not referral:
            return {'message': 'Invalid referral code'}, 400
            
        # Check if code has expired
        if referral.expiry_date and referral.expiry_date < datetime.utcnow():
            return {'message': 'Referral code has expired'}, 400
            
        # Check if code has reached max uses
        if referral.max_uses and referral.uses >= referral.max_uses:
            return {'message': 'Referral code has reached maximum uses'}, 400
            
        # Check if user is trying to use their own code
        if referral.user_id == current_user.id:
            return {'message': 'Cannot use your own referral code'}, 400
            
        # Check if user has already used a referral code
        if ReferralUse.query.filter_by(referred_user_id=current_user.id).first():
            return {'message': 'You have already used a referral code'}, 400
            
        # Record referral use
        use = ReferralUse(
            referral_code_id=referral.id,
            referred_user_id=current_user.id,
            used_at=datetime.utcnow(),
            points_awarded=referral.points_reward,
            bonus_awarded=referral.points_bonus
        )
        
        # Award points to referrer
        referrer_points = LoyaltyPoints(
            user_id=referral.user_id,
            points=referral.points_reward,
            transaction_type='earned',
            source='referral',
            reference_id=str(use.id),
            created_at=datetime.utcnow()
        )
        
        # Award bonus points to referred user
        referred_points = LoyaltyPoints(
            user_id=current_user.id,
            points=referral.points_bonus,
            transaction_type='earned',
            source='referral_bonus',
            reference_id=str(use.id),
            created_at=datetime.utcnow()
        )
        
        # Update referral code uses
        referral.uses += 1
        
        db.session.add(use)
        db.session.add(referrer_points)
        db.session.add(referred_points)
        db.session.commit()
        
        return {
            'message': 'Referral code applied successfully',
            'points_awarded': referral.points_bonus
        }

@api.route('/stats')
class ReferralStats(Resource):
    @api.doc('get_referral_stats')
    @api.marshal_with(referral_stats_model)
    @token_required
    def get(self, current_user):
        """Get user's referral statistics"""
        code = ReferralCode.query.filter_by(user_id=current_user.id).first()
        if not code:
            return {
                'total_referrals': 0,
                'active_referrals': 0,
                'points_earned': 0,
                'conversion_rate': 0
            }
            
        uses = ReferralUse.query.filter_by(referral_code_id=code.id).all()
        points_earned = sum(use.points_awarded for use in uses)
        
        # Calculate conversion rate (users who made a purchase)
        total_referred = len(uses)
        active_referred = len([
            use for use in uses
            if User.query.get(use.referred_user_id).orders.filter_by(status='completed').first()
        ])
        
        conversion_rate = (active_referred / total_referred * 100) if total_referred > 0 else 0
        
        return {
            'total_referrals': total_referred,
            'active_referrals': active_referred,
            'points_earned': points_earned,
            'conversion_rate': round(conversion_rate, 2)
        }

@api.route('/leaderboard')
class ReferralLeaderboard(Resource):
    @api.doc('get_referral_leaderboard')
    @token_required
    def get(self, current_user):
        """Get referral program leaderboard"""
        # Get all referral codes with their use counts
        codes = ReferralCode.query.all()
        
        leaderboard = []
        for code in codes:
            user = User.query.get(code.user_id)
            uses = ReferralUse.query.filter_by(referral_code_id=code.id).count()
            points = sum(
                use.points_awarded
                for use in ReferralUse.query.filter_by(referral_code_id=code.id).all()
            )
            
            leaderboard.append({
                'user_name': f"{user.first_name} {user.last_name[0]}.",
                'referrals': uses,
                'points_earned': points
            })
            
        # Sort by referrals and points
        leaderboard.sort(key=lambda x: (x['referrals'], x['points_earned']), reverse=True)
        
        return {
            'leaderboard': leaderboard[:10],  # Top 10
            'user_rank': next(
                (i + 1 for i, entry in enumerate(leaderboard)
                if entry['user_name'] == f"{current_user.first_name} {current_user.last_name[0]}."),
                len(leaderboard)
            )
        } 