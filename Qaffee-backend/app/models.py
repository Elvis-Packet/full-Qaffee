from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class NotificationType(enum.Enum):
    ORDER_UPDATE = "order_update"
    PROMOTION = "promotion"
    SYSTEM = "system"
    PAYMENT = "payment"
    DELIVERY = "delivery"

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google users
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)  # New field for email verification
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Google OAuth fields
    is_google_user = db.Column(db.Boolean, default=False)
    google_picture = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:  # Google users don't have a password
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_staff(self):
        return self.role in [UserRole.STAFF, UserRole.ADMIN]

    def promote_to_admin(self):
        self.role = UserRole.ADMIN
        db.session.commit()

    def demote_from_admin(self):
        self.role = UserRole.CUSTOMER
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_google_user': self.is_google_user,
            'google_picture': self.google_picture,
            'is_admin': self.is_admin,
            'is_staff': self.is_staff
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    
    items = db.relationship('MenuItem', back_populates='category', lazy=True, cascade='all, delete-orphan')

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    ingredients = db.Column(db.Text)
    
    category = db.relationship('Category', back_populates='items')

class OrderStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting_payment"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    COMPLETED = "completed"
    CANCELLED_BY_USER = "cancelled_by_user"
    CANCELLED_BY_ADMIN = "cancelled_by_admin"
    FAILED = "failed"

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('delivery_addresses.id'))
    is_delivery = db.Column(db.Boolean, default=True)
    payment_status = db.Column(db.String(20), default='pending')
    applied_promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.id'))
    
    customer = db.relationship('User', backref='customer_orders')
    delivery_address = db.relationship('DeliveryAddress', backref='delivery_orders')
    applied_promotion = db.relationship('Promotion', backref='promotion_orders')
    items = db.relationship('OrderItem', lazy='dynamic', cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customization = db.Column(db.JSON)
    subtotal = db.Column(db.Float, nullable=False)
    
    parent_order = db.relationship('Order', back_populates='items')
    menu_item = db.relationship('MenuItem', backref='menu_item_orders')

class DeliveryAddress(db.Model):
    __tablename__ = 'delivery_addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_default = db.Column(db.Boolean, default=False)
    label = db.Column(db.String(50))  # e.g., 'Home', 'Work'
    
    customer = db.relationship('User', backref='delivery_addresses')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reviewer = db.relationship('User', backref='user_reviews')
    menu_item = db.relationship('MenuItem', backref='menu_item_reviews')

class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, mpesa
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='order_payments')

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False, default=NotificationType.SYSTEM)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recipient = db.relationship('User', backref='user_notifications')

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_support_ticket_user'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = db.Column(db.Enum(TicketPriority), default=TicketPriority.MEDIUM)
    category = db.Column(db.String(50), default='other')  # order, delivery, product, payment, other
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_support_ticket_assignee'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = db.Column(db.JSON, default=list)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='tickets')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tickets')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'category': self.category,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'messages': self.messages or []
        }

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    comment = db.Column(db.Text)
    category = db.Column(db.String(50))  # service, food, app, delivery, other
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    submitter = db.relationship('User', backref='user_feedback')

class Promotion(db.Model):
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    min_purchase_amount = db.Column(db.Float, default=0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    max_uses = db.Column(db.Integer)
    current_uses = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StoreLocation(db.Model):
    __tablename__ = 'store_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    opening_hours = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # ordering, payment, delivery, account, product
    is_published = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)  # For controlling display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReferralCode(db.Model):
    __tablename__ = 'referral_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points_reward = db.Column(db.Integer, nullable=False, default=100)  # Points awarded for successful referral
    max_uses = db.Column(db.Integer, default=10)  # Maximum number of times this code can be used
    current_uses = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner = db.relationship('User', backref='referral_codes')

class ReferralUse(db.Model):
    __tablename__ = 'referral_uses'
    
    id = db.Column(db.Integer, primary_key=True)
    referral_code_id = db.Column(db.Integer, db.ForeignKey('referral_codes.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    referral_code = db.relationship('ReferralCode', backref='uses')
    referred_user = db.relationship('User', backref='referral_uses')

    def complete_referral(self):
        """Complete the referral and award points"""
        if self.status != 'pending':
            return False
            
        try:
            # Update referral use status
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            
            # Increment the code usage counter
            self.referral_code.current_uses += 1
            
            # Update user reward points
            referrer = self.referral_code.owner
            referred_user = self.referred_user
            
            referrer.reward_points += self.points_awarded
            referred_user.reward_points += self.points_awarded
            
            # Create loyalty transactions for both users
            referrer_points = LoyaltyTransaction(
                user_id=self.referral_code.user_id,
                points=self.points_awarded,
                transaction_type=LoyaltyPoints.REFERRAL_BONUS,
                description=f"Referral bonus for referring user {self.referred_user.email}"
            )
            
            referred_points = LoyaltyTransaction(
                user_id=self.referred_user_id,
                points=self.points_awarded,
                transaction_type=LoyaltyPoints.SIGNUP_BONUS,
                description="Welcome bonus for signing up with referral"
            )
            
            db.session.add(referrer_points)
            db.session.add(referred_points)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            self.status = 'failed'
            db.session.commit()
            return False 