from flask import request, Blueprint, jsonify, current_app
from ..models import Category, MenuItem, db, UserRole
from .auth import token_required
from flask_restx import Namespace, Resource, fields
from ..utils.auth import login_required, role_required, admin_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Create API namespace
api = Namespace('menu', description='Menu operations')

# Models for request/response documentation
category_model = api.model('Category', {
    'id': fields.Integer(readonly=True, description='Category ID'),
    'name': fields.String(required=True, description='Category name'),
    'description': fields.String(description='Category description'),
    'image_url': fields.String(description='Category image URL')
})

ingredient_model = api.model('Ingredient', {
    'name': fields.String(required=True, description='Ingredient name'),
    'quantity': fields.String(description='Ingredient quantity'),
    'unit': fields.String(description='Unit of measurement')
})

menu_item_model = api.model('MenuItem', {
    'id': fields.Integer(readonly=True, description='Menu item ID'),
    'name': fields.String(required=True, description='Item name'),
    'description': fields.String(description='Item description'),
    'price': fields.Float(required=True, description='Item price'),
    'image_url': fields.String(description='Item image URL'),
    'category_id': fields.Integer(required=True, description='Category ID'),
    'is_available': fields.Boolean(description='Item availability status'),
    'ingredients': fields.List(fields.Nested(ingredient_model), description='Item ingredients')
})

customization_model = api.model('Customization', {
    'item_id': fields.Integer(required=True, description='Menu item ID'),
    'sugar_level': fields.String(description='Sugar level preference'),
    'milk_type': fields.String(description='Type of milk'),
    'add_ons': fields.List(fields.String, description='List of add-ons'),
    'special_instructions': fields.String(description='Special preparation instructions')
})

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all menu categories"""
    categories = Category.query.all()
    return jsonify({
        'categories': [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'image_url': cat.image_url
        } for cat in categories]
    }), 200

@menu_bp.route('/items', methods=['GET'])
def get_menu_items():
    """Get menu items with optional category filter"""
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = MenuItem.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    items = query.filter_by(is_available=True).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'image_url': item.image_url,
            'category_id': item.category_id,
            'ingredients': item.ingredients
        } for item in items.items],
        'total': items.total,
        'pages': items.pages,
        'current_page': items.page
    }), 200

@menu_bp.route('/item/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get menu item details"""
    item = MenuItem.query.get_or_404(item_id)
    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'image_url': item.image_url,
        'category_id': item.category_id,
        'ingredients': item.ingredients,
        'is_available': item.is_available
    }), 200

# Admin routes for menu management
@menu_bp.route('/admin/category', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_category():
    """Create a new menu category (admin only)"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'Name is required'}), 400
    
    category = Category(
        name=data['name'],
        description=data.get('description'),
        image_url=data.get('image_url')
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify({
            'message': 'Category created successfully',
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'image_url': category.image_url
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating category'}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image_file, folder='menu_items'):
    """Save image and return the file path"""
    if not image_file:
        return None
    
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        # Add timestamp to filename to make it unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)
        
        # Return the URL path
        return f"/uploads/{folder}/{filename}"
    
    return None

@menu_bp.route('/admin/item', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_menu_item():
    """Add a new menu item (admin only)"""
    # Handle multipart form data
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    ingredients = request.form.get('ingredients')  # JSON string of ingredients
    is_available = request.form.get('is_available', 'true').lower() == 'true'
    
    # Validate required fields
    if not all([name, price, category_id]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        price = float(price)
        category_id = int(category_id)
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid price or category_id format'}), 400
    
    # Handle image upload
    image_url = None
    if 'image' in request.files:
        image_url = save_image(request.files['image'])
    
    try:
        item = MenuItem(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            image_url=image_url,
            ingredients=ingredients,
            is_available=is_available
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Menu item created successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category_id': item.category_id,
                'image_url': item.image_url,
                'ingredients': item.ingredients,
                'is_available': item.is_available
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating menu item', 'error': str(e)}), 500

@menu_bp.route('/admin/item/<int:item_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_menu_item(item_id):
    """Update a menu item (admin only)"""
    item = MenuItem.query.get_or_404(item_id)
    
    # Handle multipart form data
    if 'name' in request.form:
        item.name = request.form.get('name')
    if 'description' in request.form:
        item.description = request.form.get('description')
    if 'price' in request.form:
        try:
            item.price = float(request.form.get('price'))
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid price format'}), 400
    if 'category_id' in request.form:
        try:
            item.category_id = int(request.form.get('category_id'))
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid category_id format'}), 400
    if 'ingredients' in request.form:
        item.ingredients = request.form.get('ingredients')
    if 'is_available' in request.form:
        item.is_available = request.form.get('is_available').lower() == 'true'
    
    # Handle image upload
    if 'image' in request.files:
        # Delete old image if it exists
        if item.image_url:
            old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_url.lstrip('/uploads/'))
            try:
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            except Exception:
                pass  # Ignore errors when deleting old image
        
        # Save new image
        image_url = save_image(request.files['image'])
        if image_url:
            item.image_url = image_url
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Menu item updated successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category_id': item.category_id,
                'image_url': item.image_url,
                'ingredients': item.ingredients,
                'is_available': item.is_available
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating menu item'}), 500

@menu_bp.route('/admin/item/<int:item_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_menu_item(item_id):
    """Delete a menu item (admin only)"""
    item = MenuItem.query.get_or_404(item_id)
    
    try:
        # Delete image file if it exists
        if item.image_url:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_url.lstrip('/uploads/'))
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception:
                pass  # Ignore errors when deleting image
        
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Menu item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting menu item', 'error': str(e)}), 500

@api.route('/customize')
class CustomizeItem(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(customization_model)
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Item not found')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Customize a menu item"""
        data = request.get_json()
        
        if not data or not data.get('item_id'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            item = MenuItem.query.get_or_404(data.get('item_id'))
            customization = {
                'sugar_level': data.get('sugar_level', 'normal'),
                'milk_type': data.get('milk_type', 'regular'),
                'add_ons': data.get('add_ons', []),
                'special_instructions': data.get('special_instructions', '')
            }
            
            # Calculate additional cost based on add-ons
            add_on_prices = {
                'extra_shot': 0.50,
                'whipped_cream': 0.75,
                'caramel': 0.50,
                'chocolate': 0.50
            }
            
            additional_cost = sum(add_on_prices.get(add_on, 0) for add_on in customization['add_ons'])
            total_price = item.price + additional_cost
            
            return {
                'item_id': item.id,
                'customization': customization,
                'base_price': item.price,
                'additional_cost': additional_cost,
                'total_price': total_price
            }, 200
        except Exception as e:
            return {'message': 'Error customizing item', 'error': str(e)}, 500

@api.route('/categories')
class Categories(Resource):
    @api.doc('list_categories')
    @api.marshal_list_with(category_model)
    def get(self):
        """List all menu categories"""
        return Category.query.all()

    @api.doc('create_category')
    @api.expect(category_model)
    @api.marshal_with(category_model)
    @admin_required
    def post(self, current_user):
        """Create a new category (Admin only)"""
        data = request.get_json()
        category = Category(**data)
        db.session.add(category)
        db.session.commit()
        return category

@api.route('/categories/<int:id>')
@api.param('id', 'The category identifier')
class CategoryResource(Resource):
    @api.doc('get_category')
    @api.marshal_with(category_model)
    def get(self, id):
        """Get a category by ID"""
        return Category.query.get_or_404(id)

    @api.doc('update_category')
    @api.expect(category_model)
    @api.marshal_with(category_model)
    @admin_required
    def put(self, current_user, id):
        """Update a category"""
        category = Category.query.get_or_404(id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.image_url = data.get('image_url', category.image_url)
        
        db.session.commit()
        return category

    @api.doc('delete_category')
    @api.response(204, 'Category deleted')
    @admin_required
    def delete(self, current_user, id):
        """Delete a category"""
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return '', 204

@api.route('/items')
class MenuItems(Resource):
    @api.doc('list_items')
    @api.marshal_list_with(menu_item_model)
    def get(self):
        """List all menu items"""
        category_id = request.args.get('category_id', type=int)
        available_only = request.args.get('available_only', type=bool, default=True)
        
        query = MenuItem.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if available_only:
            query = query.filter_by(is_available=True)
            
        return query.all()

    @api.doc('create_item')
    @api.expect(menu_item_model)
    @api.marshal_with(menu_item_model)
    @admin_required
    def post(self, current_user):
        """Create a new menu item (Admin only)"""
        data = request.get_json()
        
        # Verify category exists
        category = Category.query.get_or_404(data['category_id'])
        
        item = MenuItem(**data)
        db.session.add(item)
        db.session.commit()
        return item

@api.route('/items/<int:id>')
@api.param('id', 'The menu item identifier')
class MenuItemResource(Resource):
    @api.doc('get_item')
    @api.marshal_with(menu_item_model)
    def get(self, id):
        """Get a menu item by ID"""
        return MenuItem.query.get_or_404(id)

    @api.doc('update_item')
    @api.expect(menu_item_model)
    @api.marshal_with(menu_item_model)
    @admin_required
    def put(self, current_user, id):
        """Update a menu item (Admin only)"""
        item = MenuItem.query.get_or_404(id)
        data = request.get_json()
        
        # Verify category if changing
        if 'category_id' in data:
            Category.query.get_or_404(data['category_id'])
        
        for key, value in data.items():
            setattr(item, key, value)
            
        db.session.commit()
        return item

    @api.doc('delete_item')
    @admin_required
    def delete(self, current_user, id):
        """Delete a menu item (Admin only)"""
        item = MenuItem.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Menu item deleted'}

@api.route('/items/<int:id>/customize')
@api.param('id', 'The menu item identifier')
class MenuItemCustomization(Resource):
    @api.doc('get_customization_options')
    @api.marshal_with(customization_model)
    def get(self, id):
        """Get customization options for a menu item"""
        item = MenuItem.query.get_or_404(id)
        return {
            'item_id': item.id,
            'sugar_level': ['none', 'light', 'normal', 'extra'],
            'milk_type': ['none', 'whole', 'skim', 'almond', 'soy', 'oat'],
            'add_ons': ['extra_shot', 'whipped_cream', 'caramel', 'chocolate'],
            'special_instructions': ''
        }

@api.route('/categories/<int:id>/items')
@api.param('id', 'The category identifier')
class CategoryItems(Resource):
    @api.doc('list_category_items')
    @api.marshal_list_with(menu_item_model)
    def get(self, id):
        """List all items in a category"""
        Category.query.get_or_404(id)  # Verify category exists
        return MenuItem.query.filter_by(category_id=id).all() 