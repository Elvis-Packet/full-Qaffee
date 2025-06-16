# app package initialization

from flask import Flask, json, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from decouple import Config, RepositoryEnv, config
from .config.database import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
import cloudinary
import stripe
from flask_restx import Api, fields
from flask_migrate import Migrate
import os
from datetime import timedelta, datetime, timezone
import json
from flask.json.provider import DefaultJSONProvider
import enum

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, enum.Enum):
                return obj.value
            return super().default(obj)
        except TypeError:
            return str(obj)

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Use custom JSON encoder
    app.json_encoder = CustomJSONEncoder
    app.config['RESTX_JSON'] = {'cls': CustomJSONEncoder}
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def serve_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Enable CORS with support for OPTIONS preflight requests
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Range", "X-Content-Range"],
             "supports_credentials": True,
             "send_wildcard": False
         }})
    
    # Add OPTIONS method handling for all routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            # Add CORS headers to response
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        env_config = Config(RepositoryEnv(env_path))
    else:
        from decouple import AutoConfig
        env_config = AutoConfig(search_path=os.path.dirname(os.path.dirname(__file__)))
    
    # Configure the Flask application
    app.config['SECRET_KEY'] = env_config('SECRET_KEY', default='dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    
    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    mail.init_app(app)
    
    # Initialize Cloudinary
    cloudinary.config(
        cloud_name=env_config('CLOUDINARY_CLOUD_NAME', default=''),
        api_key=env_config('CLOUDINARY_API_KEY', default=''),
        api_secret=env_config('CLOUDINARY_API_SECRET', default='')
    )
    
    # Initialize Stripe
    stripe.api_key = env_config('STRIPE_SECRET_KEY', default='')
    
    # Create API
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add a JWT token to the header with Bearer prefix'
        }
    }
    
    api = Api(
        title='Qaffee API',
        version='1.0',
        description='A modern coffee shop management API',
        authorizations=authorizations,
        security='Bearer Auth',
        doc='/docs',  # Swagger UI documentation path
        validate=True,
        catch_all_404s=True,
        serve_challenge_on_401=True,
        default_mediatype='application/json'
    )
    
    # Import and register namespaces
    from .routes.auth import api as auth_ns
    from .routes.menu import api as menu_ns
    from .routes.orders import api as orders_ns
    from .routes.locations import api as locations_ns
    from .routes.notifications import api as notifications_ns
    from .routes.support import api as support_ns
    from .routes.rewards import api as rewards_ns
    from .routes.reviews import api as reviews_ns
    from .routes.referral import api as referral_ns
    from .routes.admin import api as admin_ns
    from .routes.analytics import api as analytics_ns
    from .routes.cart import api as cart_ns
    from .routes.health import api as health_ns
    from .routes.payment import api as payment_ns
    
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(menu_ns, path='/menu')
    api.add_namespace(orders_ns, path='/orders')
    api.add_namespace(locations_ns, path='/locations')
    api.add_namespace(notifications_ns, path='/notifications')
    api.add_namespace(support_ns, path='/support')
    api.add_namespace(rewards_ns, path='/rewards')
    api.add_namespace(reviews_ns, path='/reviews')
    api.add_namespace(referral_ns, path='/referral')
    api.add_namespace(admin_ns, path='/admin')
    api.add_namespace(analytics_ns, path='/analytics')
    api.add_namespace(cart_ns, path='/cart')
    api.add_namespace(health_ns, path='/health')
    api.add_namespace(payment_ns, path='/api/payments')
    
    # Initialize API with app
    api.init_app(app)
    
    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        
        # Create admin user with environment config
        try:
            from .models import User, UserRole
            if User.query.count() == 0:
                admin = User(
                    email=env_config('ADMIN_EMAIL', default='admin@qaffee.com'),
                    first_name='Admin',
                    last_name='User',
                    role=UserRole.ADMIN,
                    is_active=True
                )
                admin.set_password(env_config('ADMIN_PASSWORD', default='admin123'))
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {str(e)}")
    
    return app

def create_admin_user():
    """Create admin user if no users exist"""
    from .models import User, UserRole
    
    try:
        if User.query.count() == 0:
            admin = User(
                email=config('ADMIN_EMAIL', default='admin@qaffee.com'),
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                is_active=True
            )
            admin.set_password(config('ADMIN_PASSWORD', default='admin123'))
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")
