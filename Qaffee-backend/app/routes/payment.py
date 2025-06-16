from flask import Blueprint, request, jsonify, current_app, url_for
from ..models import db, Payment, Order, OrderStatus, UserRole
from ..utils.auth import login_required, role_required, token_required
from ..utils.mpesa import MpesaAPI
import stripe
import os
from datetime import datetime, timedelta
from flask_restx import Namespace, Resource, fields
from decouple import config

# Create blueprint
payment_bp = Blueprint('payment', __name__)

# Create API namespace
api = Namespace('payment', description='Payment operations')

# Initialize Stripe
stripe.api_key = config('STRIPE_SECRET_KEY', default='your-stripe-secret-key')

# API Models
payment_initiate_model = api.model('PaymentInitiate', {
    'order_id': fields.Integer(required=True, description='Order ID'),
    'payment_method': fields.String(required=True, description='Payment method (stripe/mpesa)'),
    'phone_number': fields.String(required=False, description='Phone number for M-Pesa payment')
})

mpesa_verify_model = api.model('MpesaVerify', {
    'status': fields.String(description='Status of the verification'),
    'message': fields.String(description='User-friendly message'),
    'result_code': fields.String(description='M-Pesa result code'),
    'result_desc': fields.String(description='M-Pesa result description'),
    'payment_status': fields.String(description='Payment status')
})

payment_response_model = api.model('PaymentResponse', {
    'payment_id': fields.Integer(description='Payment ID'),
    'status': fields.String(description='Payment status'),
    'message': fields.String(description='User-friendly message'),
    'checkout_request_id': fields.String(description='M-Pesa checkout request ID'),
    'merchant_request_id': fields.String(description='M-Pesa merchant request ID'),
    'client_secret': fields.String(description='Stripe client secret')
})

payment_list_item = api.model('PaymentListItem', {
    'id': fields.Integer(description='Payment ID'),
    'order_id': fields.Integer(description='Order ID'),
    'amount': fields.Float(description='Payment amount'),
    'payment_method': fields.String(description='Payment method'),
    'transaction_id': fields.String(description='Transaction ID'),
    'status': fields.String(description='Payment status'),
    'created_at': fields.DateTime(description='Payment creation time')
})

payment_list_model = api.model('PaymentList', {
    'payments': fields.List(fields.Nested(payment_list_item)),
    'total': fields.Integer(description='Total number of payments'),
    'pages': fields.Integer(description='Total number of pages'),
    'current_page': fields.Integer(description='Current page number')
})

revenue_stats_model = api.model('RevenueStats', {
    'period': fields.String(description='Time period'),
    'total_revenue': fields.Float(description='Total revenue'),
    'payment_count': fields.Integer(description='Number of payments'),
    'avg_order_value': fields.Float(description='Average order value'),
    'start_date': fields.DateTime(description='Start date'),
    'end_date': fields.DateTime(description='End date')
})

# Initialize payment services
mpesa = MpesaAPI()

# Models for request/response documentation
payment_intent_model = api.model('PaymentIntent', {
    'order_id': fields.Integer(required=True, description='Order ID'),
    'payment_method': fields.String(required=True, description='Payment method (stripe, mpesa)'),
    'currency': fields.String(default='USD', description='Payment currency')
})

payment_confirm_model = api.model('PaymentConfirm', {
    'payment_intent_id': fields.String(required=True, description='Stripe Payment Intent ID')
})

payment_response = api.model('PaymentResponse', {
    'id': fields.Integer(description='Payment ID'),
    'order_id': fields.Integer(description='Order ID'),
    'amount': fields.Float(description='Payment amount'),
    'status': fields.String(description='Payment status'),
    'payment_method': fields.String(description='Payment method used'),
    'transaction_id': fields.String(description='Payment transaction ID'),
    'created_at': fields.DateTime(description='Payment timestamp')
})

@api.route('/mpesa')
class MpesaPayment(Resource):
    def post(self):
        """Initiate M-Pesa payment via STK Push"""
        data = request.get_json()
        phone = data.get('phone')
        amount = data.get('amount')
        location = data.get('location')
        method = data.get('method')

        if not phone or not amount or not location or not method:
            return {'message': 'Missing required fields'}, 400

        # Generate callback URL for M-Pesa STK push
        callback_url = url_for('payment_mpesa_callback', _external=True)

        # Initiate STK push
        result, error = mpesa.initiate_stk_push(
            phone_number=phone,
            amount=amount,
            reference=location,
            callback_url=callback_url
        )

        if error:
            return {'message': error}, 400

        return {'message': 'Payment initiated', 'result': result}, 200

@api.route('/initiate')
class InitiatePayment(Resource):
    @api.doc('initiate_payment',
             security='Bearer Auth',
             body=payment_initiate_model,
             responses={
                 200: ('Success', payment_response_model),
                 400: 'Validation Error',
                 401: 'Unauthorized',
                 404: 'Order not found',
                 500: 'Server Error'
             })
    @login_required
    def post(self):
        """Initiate a payment for an order"""
        data = request.get_json()
        
        if not data or 'order_id' not in data or 'payment_method' not in data:
            return {'message': 'Order ID and payment method required'}, 400
        
        order = Order.query.get_or_404(data['order_id'])
        
        # Verify order belongs to user
        if order.user_id != request.user.id:
                return {'message': 'Order not found'}, 404
            
        # Check if order is in correct status
        if order.status != OrderStatus.PENDING:
            return {'message': 'Order cannot be paid'}, 400
            
        try:
            if data['payment_method'] == 'stripe':
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id
                    }
                )
                
                payment_data = {
                    'client_secret': intent.client_secret,
                    'transaction_id': intent.id,
                    'status': 'pending',
                    'message': 'Please complete payment using your card'
                }
                
            elif data['payment_method'] == 'mpesa':
                if not data.get('phone_number'):
                    return {
                        'message': 'Phone number required for M-Pesa payment',
                        'error_type': 'MISSING_PHONE'
                    }, 400
                    
                # Generate callback URL
                callback_url = url_for('payment.mpesa_callback', _external=True)
                
                # Initiate M-Pesa STK Push
                result, error = mpesa.initiate_stk_push(
                    phone_number=data['phone_number'],
                    amount=order.total_amount,
                    reference=str(order.id),
                    callback_url=callback_url
                )
                
                if error:
                    return {
                        'message': error,
                        'error_type': 'MPESA_ERROR'
                    }, 400
                    
                payment_data = {
                    'checkout_request_id': result['CheckoutRequestID'],
                    'merchant_request_id': result['MerchantRequestID'],
                    'status': 'pending',
                    'message': result['user_message'],
                    'phone_number': data['phone_number']
                }
                
            else:
                return {'message': 'Invalid payment method'}, 400
            
            # Update order status
            order.status = OrderStatus.AWAITING_PAYMENT
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method=data['payment_method'],
                transaction_id=payment_data.get('transaction_id') or payment_data.get('checkout_request_id'),
                status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return {
                'payment_id': payment.id,
                **payment_data
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'Error initiating payment: {str(e)}',
                'error_type': 'SYSTEM_ERROR'
            }, 500

@api.route('/mpesa/callback')
class MpesaCallback(Resource):
    @api.doc('mpesa_callback')
    def post(self):
        """Handle M-Pesa payment callback"""
        data = request.get_json()
        
        try:
            # Extract relevant information from callback data
            callback_data = data['Body']['stkCallback']
            result_code = callback_data['ResultCode']
            merchant_request_id = callback_data['MerchantRequestID']
            checkout_request_id = callback_data['CheckoutRequestID']
            
            # Find payment by transaction ID (checkout_request_id)
            payment = Payment.query.filter_by(transaction_id=checkout_request_id).first()
            
            if not payment:
                return {'message': 'Payment not found'}, 404
            
            if result_code == 0:  # Successful payment
                # Get payment details from callback
                payment_details = callback_data.get('CallbackMetadata', {}).get('Item', [])
                amount = next((item['Value'] for item in payment_details if item['Name'] == 'Amount'), None)
                mpesa_receipt = next((item['Value'] for item in payment_details if item['Name'] == 'MpesaReceiptNumber'), None)
                
                # Update payment status and details
                payment.status = 'completed'
                payment.transaction_details = {
                    'receipt_number': mpesa_receipt,
                    'amount': amount,
                    'completed_at': datetime.utcnow().isoformat()
                }
                
                # Update order status
                order = Order.query.get(payment.order_id)
                if order:
                    order.status = OrderStatus.CONFIRMED
                
                db.session.commit()
                
                return {
                    'message': 'Payment completed successfully',
                    'receipt_number': mpesa_receipt
                }, 200
            else:
                # Payment failed
                payment.status = 'failed'
                payment.transaction_details = {
                    'result_code': result_code,
                    'result_desc': callback_data.get('ResultDesc', 'Payment failed'),
                    'failed_at': datetime.utcnow().isoformat()
                }
                db.session.commit()
                
                return {
                    'message': 'Payment failed',
                    'error': callback_data.get('ResultDesc', 'Unknown error')
                }, 200
            
        except Exception as e:
            return {'message': f'Error processing callback: {str(e)}'}, 500

@api.route('/verify-mpesa/<string:checkout_request_id>')
class VerifyMpesaPayment(Resource):
    @api.doc('verify_mpesa_payment',
             security='Bearer Auth',
             responses={
                 200: ('Success', mpesa_verify_model),
                 400: 'Validation Error',
                 401: 'Unauthorized',
                 404: 'Payment not found',
                 500: 'Server Error'
             })
    @login_required
    def get(self, checkout_request_id):
        """Verify M-Pesa payment status"""
        try:
            result, error = mpesa.verify_transaction(checkout_request_id)
            
            if error:
                return {
                    'message': error,
                    'status': 'error',
                    'error_type': 'VERIFICATION_ERROR'
                }, 400
                
            # Find payment record
            payment = Payment.query.filter_by(transaction_id=checkout_request_id).first()
            if not payment:
                return {
                    'message': 'Payment not found',
                    'status': 'error',
                    'error_type': 'PAYMENT_NOT_FOUND'
                }, 404
                
            return {
                'status': 'success',
                'message': result.get('user_message', 'Verification completed'),
                'result_code': result.get('ResultCode'),
                'result_desc': result.get('ResultDesc'),
                'payment_status': payment.status
            }, 200
            
        except Exception as e:
            return {
                'message': 'Error verifying payment',
                'error_type': 'SYSTEM_ERROR',
                'error': str(e)
            }, 500

@api.route('/admin/payments')
class AdminPayments(Resource):
    @api.doc('list_payments',
             security='Bearer Auth',
             responses={
                 200: ('Success', payment_list_model),
                 401: 'Unauthorized',
                 403: 'Forbidden'
             })
    @role_required(UserRole.ADMIN)
    def get(self):
        """List all payments (admin only)"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return {
            'payments': [{
                'id': payment.id,
                'order_id': payment.order_id,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'created_at': payment.created_at.isoformat()
            } for payment in payments.items],
            'total': payments.total,
            'pages': payments.pages,
            'current_page': payments.page
        }, 200

@api.route('/admin/revenue-stats')
class RevenueStats(Resource):
    @api.doc('get_revenue_stats',
             security='Bearer Auth',
             responses={
                 200: ('Success', revenue_stats_model),
                 401: 'Unauthorized',
                 403: 'Forbidden',
                 400: 'Invalid period'
             })
    @role_required(UserRole.ADMIN)
    def get(self):
        """Get revenue analytics (admin only)"""
        period = request.args.get('period', 'day')  # day, week, month, year
        
        if period == 'day':
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.utcnow() - timedelta(days=365)
        else:
            return {'message': 'Invalid period'}, 400
        
        # Get completed payments
        completed_payments = Payment.query.filter(
            Payment.status == 'completed',
            Payment.created_at >= start_date
        ).all()
        
        total_revenue = sum(payment.amount for payment in completed_payments)
        payment_count = len(completed_payments)
        
        # Get average order value
        avg_order_value = total_revenue / payment_count if payment_count > 0 else 0
        
        return {
            'period': period,
            'total_revenue': total_revenue,
            'payment_count': payment_count,
            'avg_order_value': avg_order_value,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat()
            }, 200

@api.route('/create-intent')
class CreatePaymentIntent(Resource):
    @api.doc('create_payment_intent')
    @api.expect(payment_intent_model)
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Order not found')
    @token_required
    def post(self, current_user):
        """Create a payment intent"""
        data = request.get_json()
        
        # Get order
        order = Order.query.filter_by(
            id=data['order_id'],
            user_id=current_user.id
        ).first_or_404()
        
        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency=data.get('currency', 'USD'),
                metadata={
                    'order_id': order.id,
                    'user_id': current_user.id
                }
            )
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method=data['payment_method'],
                transaction_id=intent.id,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            return {
                'client_secret': intent.client_secret,
                'payment_id': payment.id
            }
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@api.route('/confirm')
class ConfirmPayment(Resource):
    @api.doc('confirm_payment')
    @api.expect(payment_confirm_model)
    @api.response(200, 'Payment confirmed')
    @api.response(400, 'Validation Error')
    @token_required
    def post(self, current_user):
        """Confirm a payment"""
        data = request.get_json()
        
        try:
            # Retrieve PaymentIntent
            intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
            
            # Update payment record
            payment = Payment.query.filter_by(transaction_id=intent.id).first_or_404()
            payment.status = intent.status
            
            # Update order status if payment successful
            if intent.status == 'succeeded':
                order = Order.query.get(payment.order_id)
                order.status = OrderStatus.CONFIRMED
                order.payment_status = 'paid'
            
            db.session.commit()
            
            return {'status': intent.status}
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

@api.route('/webhook')
class StripeWebhook(Resource):
    @api.doc('stripe_webhook')
    def post(self):
        """Handle Stripe webhook events"""
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, config('STRIPE_WEBHOOK_SECRET')
            )
            
            # Handle the event
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                # Update payment and order status
                payment = Payment.query.filter_by(transaction_id=payment_intent.id).first()
                if payment:
                    payment.status = 'succeeded'
                    order = Order.query.get(payment.order_id)
                    order.status = OrderStatus.CONFIRMED
                    order.payment_status = 'paid'
                    db.session.commit()
            
            return {'status': 'success'}
        except Exception as e:
            return {'message': str(e)}, 400

@api.route('/methods')
class PaymentMethods(Resource):
    @api.doc('get_payment_methods')
    @token_required
    def get(self, current_user):
        """Get available payment methods"""
        return {
            'methods': [
                {
                    'id': 'stripe',
                    'name': 'Credit/Debit Card',
                    'description': 'Pay with Stripe',
                    'enabled': True
                },
                {
                    'id': 'mpesa',
                    'name': 'M-PESA',
                    'description': 'Pay with M-PESA',
                    'enabled': True
                }
            ]
        }

@api.route('/history')
class PaymentHistory(Resource):
    @api.doc('get_payment_history')
    @api.marshal_list_with(payment_response)
    @token_required
    def get(self, current_user):
        """Get user's payment history"""
        payments = Payment.query.join(Order).filter(
            Order.user_id == current_user.id
        ).order_by(Payment.created_at.desc()).all()
        return payments