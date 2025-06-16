from flask import Blueprint, request, jsonify
from ..models import db, User, UserRole
from ..utils.auth import login_required, role_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    user = request.user
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role.value
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user's profile"""
    user = request.user
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'role': user.role.value
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating profile'}), 500

@user_bp.route('/admin/users', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_users():
    """List all users (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    }), 200

@user_bp.route('/admin/users/<int:user_id>/role', methods=['PATCH'])
@role_required(UserRole.ADMIN)
def update_user_role(user_id):
    """Update user role (admin only)"""
    data = request.get_json()
    
    if not data or 'role' not in data:
        return jsonify({'message': 'Role not provided'}), 400
    
    try:
        new_role = UserRole(data['role'])
    except ValueError:
        return jsonify({'message': 'Invalid role'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-demotion for admin
    if user.id == request.user.id and new_role != UserRole.ADMIN:
        return jsonify({'message': 'Cannot demote yourself'}), 403
    
    user.role = new_role
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'User role updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role.value
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating user role'}), 500 