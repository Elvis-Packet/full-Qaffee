from flask import request, Blueprint, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, db, UserRole
from ..utils.auth import generate_token, generate_refresh_token, decode_token, get_token_from_header
from ..utils.google_auth import handle_google_auth, GoogleAuthError, get_google_auth_url
import jwt
from datetime import datetime, timedelta
from functools import wraps
from decouple import config
import re
from flask_restx import Namespace, Resource, fields
from flask import current_app

# Create API namespace
api = Namespace('auth', description='Authentication operations')

# Models for request/response documentation
user_model = api.model('User', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
    'phone': fields.String(required=False, description='User phone number')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
})

google_auth_model = api.model('GoogleAuth', {
    'token': fields.String(required=True, description='Google ID token')
})

auth_response = api.model('AuthResponse', {
    'token': fields.String(description='JWT token'),
    'user': fields.Nested(api.model('UserInfo', {
        'id': fields.Integer(description='User ID'),
        'email': fields.String(description='User email'),
        'first_name': fields.String(description='First name'),
        'last_name': fields.String(description='Last name'),
        'role': fields.String(description='User role'),
        'is_google_user': fields.Boolean(description='Whether user is authenticated via Google'),
        'picture': fields.String(description='Google profile picture URL')
    }))
})

profile_model = api.model('Profile', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'phone': fields.String(description='Phone number')
})

admin_model = api.model('AdminManagement', {
    'email': fields.String(required=True, description='User email to promote/demote')
})

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return {'message': 'Token is missing'}, 401
        
        payload = decode_token(token)
        if not payload:
            return {'message': 'Invalid token'}, 401
        
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return {'message': 'Invalid token'}, 401
        
        if not current_user.is_admin:
            return {'message': 'Admin privileges required'}, 403
        
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    
    return decorated

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return {'message': 'Token is missing'}, 401
        
        payload = decode_token(token)
        if not payload:
            return {'message': 'Invalid token'}, 401
        
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return {'message': 'Invalid token'}, 401
        
        if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
            return {'message': 'Staff privileges required'}, 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return {'message': 'Token is missing'}, 401
        
        payload = decode_token(token)
        if not payload:
            return {'message': 'Invalid token'}, 401
        
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return {'message': 'Invalid token'}, 401
        
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    
    return decorated

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

auth_bp = Blueprint('auth', __name__)

@api.route('/signup')
class Signup(Resource):
    @api.expect(user_model)
    @api.response(201, 'User created successfully', auth_response)
    @api.response(400, 'Validation Error')
    def post(self):
        """Register a new user"""
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        if not all(field in data for field in required_fields):
            return {'message': 'Missing required fields'}, 400
        
        # Validate email format
        if not validate_email(data['email']):
            return {'message': 'Invalid email format'}, 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        # Validate password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return {'message': message}, 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=UserRole.CUSTOMER
        )
        user.set_password(data['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            access_token = generate_token(user)
            refresh_token = generate_refresh_token(user)
            
            return {
                'message': 'User registered successfully',
                'token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating user'}, 500

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful', auth_response)
    @api.response(400, 'Validation Error')
    @api.response(401, 'Authentication Error')
    def post(self):
        """Login a user"""
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return {'message': 'Missing email or password'}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid email or password'}, 401
        
        # Generate tokens
        access_token = generate_token(user)
        refresh_token = generate_refresh_token(user)
        
        return {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

@api.route('/admin-login')
class AdminLogin(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful', auth_response)
    @api.response(400, 'Validation Error')
    @api.response(401, 'Authentication Error')
    @api.response(403, 'Not an admin')
    def post(self):
        """Login as admin"""
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return {'message': 'Missing email or password'}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid email or password'}, 401
        
        if not user.is_admin:
            return {'message': 'Admin privileges required'}, 403
        
        # Generate tokens
        access_token = generate_token(user)
        refresh_token = generate_refresh_token(user)
        
        return {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

@api.route('/refresh')
class RefreshToken(Resource):
    @api.expect(api.model('RefreshTokenRequest', {
        'refresh_token': fields.String(required=True, description='Refresh token')
    }))
    @api.response(200, 'Token refreshed successfully', auth_response)
    @api.response(400, 'Validation Error')
    @api.response(401, 'Authentication Error')
    def post(self):
        """Refresh access token using refresh token"""
        data = request.get_json()
        
        if not data or not data.get('refresh_token'):
            return {'message': 'Refresh token is required'}, 400
        
        refresh_token = data['refresh_token']
        
        try:
            payload = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            if payload.get('type') != 'refresh':
                return {'message': 'Invalid token type'}, 401
            
            user = User.query.get(payload['user_id'])
            if not user:
                return {'message': 'Invalid token'}, 401
            
            access_token = generate_token(user)
            return {'access_token': access_token}, 200
        except jwt.ExpiredSignatureError:
            return {'message': 'Refresh token expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid refresh token'}, 401
        except Exception as e:
            return {'message': 'Error processing token', 'error': str(e)}, 401

@api.route('/me')
class UserProfile(Resource):
    @api.doc('get_user_profile')
    @api.response(200, 'Success', auth_response)
    @api.response(401, 'Authentication Error')
    @token_required
    def get(self, current_user):
        """Get current user's profile"""
        return {
            'user': current_user.to_dict()
        }, 200
