from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from decouple import config
from ..models import User, UserRole

def generate_token(user, expires_delta=timedelta(minutes=15)):
    """Generate a short-lived JWT access token for the user"""
    payload = {
        'user_id': user.id,
        'role': user.role.value,
        'exp': datetime.utcnow() + expires_delta
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def generate_refresh_token(user, expires_delta=timedelta(days=7)):
    """Generate a long-lived JWT refresh token for the user"""
    payload = {
        'user_id': user.id,
        'role': user.role.value,
        'exp': datetime.utcnow() + expires_delta,
        'type': 'refresh'
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'message': 'Missing authentication token'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'message': 'User not found or inactive'}), 401
        
        request.user = user
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """Decorator to require specific roles for routes"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if not request.user.role or request.user.role.value not in [r.value if isinstance(r, UserRole) else r for r in roles]:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def is_admin():
    """Check if current user is admin"""
    return request.user.role == UserRole.ADMIN

def is_staff_or_admin():
    """Check if current user is staff or admin"""
    return request.user.role in [UserRole.STAFF, UserRole.ADMIN]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token format'}, 401
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return {'message': 'Invalid token'}, 401
                
            return f(current_user, *args, **kwargs)
        except:
            return {'message': 'Invalid token'}, 401
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token format'}, 401
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return {'message': 'Invalid token'}, 401
            
            if not current_user.is_admin:
                return {'message': 'Admin privileges required'}, 403
            
            return f(current_user=current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        except Exception as e:
            return {'message': 'Error processing token', 'error': str(e)}, 401
    
    return decorated

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token format'}, 401
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return {'message': 'Invalid token'}, 401
            
            if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
                return {'message': 'Staff privileges required'}, 403
                
            return f(current_user, *args, **kwargs)
        except:
            return {'message': 'Invalid token'}, 401
    
    return decorated 