# Qaffee Point Backend

A Flask-based backend for the Qaffee Point coffee shop management system.

## Features

- 👥 User Management
  - Customer registration and authentication
  - Admin and staff role management
  - Profile management

- 🛍️ Menu Management
  - Categories and items
  - Price and stock management
  - Item customization

- 📦 Order Management
  - Order creation and tracking
  - Status updates
  - Order history

- 💳 Payment Processing
  - Stripe integration
  - Payment status tracking
  - Revenue analytics

## Prerequisites

- Python 3.8+
- PostgreSQL
- Stripe account (for payments)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/qaffee-backend.git
cd qaffee-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/qaffee

# Stripe Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# M-Pesa Configuration
MPESA_CONSUMER_KEY=ZzEqDAMIrOhLPcKG2oWwFQ9A5dwanJUzfhfPPh34kLoJwrqq
MPESA_CONSUMER_SECRET=5yJNzoKGxqOrv3UZhIUHZG03vKk1s1bPJwm4MDw93alnIvoiMRr5o6q1UL146L06
MPESA_PASSKEY=your-mpesa-passkey
MPESA_SHORTCODE=174379

# Admin Configuration
ADMIN_EMAIL=admin@qaffee.com
ADMIN_PASSWORD=secure-admin-password
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## API Documentation

### Authentication

#### Register a new customer
```http
POST /auth/signup
Content-Type: application/json

{
    "email": "customer@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
}
```

#### Customer login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "customer@example.com",
    "password": "SecurePass123"
}
```

#### Admin/Staff login
```http
POST /auth/admin-login
Content-Type: application/json

{
    "email": "admin@qaffee.com",
    "password": "admin-password"
}
```

### Menu Management

#### Get menu categories
```http
GET /menu/categories
```

#### Get menu items
```http
GET /menu/items?category_id=1&page=1&per_page=10
```

#### Create menu item (Admin)
```http
POST /menu/admin/item
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Espresso",
    "description": "Strong Italian coffee",
    "price": 3.50,
    "category_id": 1,
    "image_url": "https://example.com/espresso.jpg",
    "ingredients": "100% Arabica beans"
}
```

### Order Management

#### Create new order
```http
POST /orders/checkout
Authorization: Bearer <token>
Content-Type: application/json

{
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 2,
            "customization": {
                "sugar": "less",
                "milk": "oat"
            }
        }
    ],
    "delivery_address_id": 1,
    "is_delivery": true
}
```

#### Get active orders
```http
GET /orders/current
Authorization: Bearer <token>
```

#### Update order status (Admin/Staff)
```http
PATCH /orders/admin/orders/1/status
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "preparing"
}
```

### Payment Processing

#### Initiate Stripe payment
```http
POST /payment/initiate
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 1,
    "payment_method": "stripe"
}
```

#### Initiate M-Pesa payment
```http
POST /payment/initiate
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 1,
    "payment_method": "mpesa",
    "phone_number": "254712345678"
}
```

#### Verify M-Pesa payment status
```http
GET /payment/verify-mpesa/<checkout_request_id>
Authorization: Bearer <token>
```

#### Get revenue stats (Admin)
```http
GET /payment/admin/revenue-stats?period=month
Authorization: Bearer <token>
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message:
```json
{
    "message": "Error description"
}
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create a migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade
```

## Security

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- Rate limiting
- CORS protection
- Input validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 