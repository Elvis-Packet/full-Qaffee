from flask import request, jsonify
from ..models import db, User, SupportTicket as SupportTicketModel, FAQ, TicketStatus, TicketPriority
from .auth import token_required, staff_required
from decouple import config
from flask_restx import Namespace, Resource, fields
from datetime import datetime

# Create API namespace
api = Namespace('support', description='Customer support operations')

# Models for request/response documentation
ticket_input_model = api.model('TicketInput', {
    'subject': fields.String(required=True, description='Ticket subject'),
    'description': fields.String(required=True, description='Ticket description'),
    'priority': fields.String(description='Ticket priority', enum=['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
    'category': fields.String(description='Ticket category', enum=['order', 'delivery', 'product', 'payment', 'other'])
})

ticket_update_model = api.model('TicketUpdate', {
    'status': fields.String(description='Ticket status', enum=['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']),
    'priority': fields.String(description='Ticket priority', enum=['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
    'assigned_to': fields.Integer(description='Staff ID to assign the ticket to'),
    'message': fields.String(description='Message to add to the ticket')
})

ticket_message_model = api.model('TicketMessage', {
    'id': fields.Integer(description='Message ID'),
    'content': fields.String(required=True, description='Message content'),
    'sender_id': fields.Integer(description='Sender user ID'),
    'is_staff': fields.Boolean(description='Whether sender is staff'),
    'created_at': fields.DateTime(description='Message timestamp')
})

ticket_model = api.model('Ticket', {
    'id': fields.Integer(description='Ticket ID'),
    'user_id': fields.Integer(description='User ID'),
    'subject': fields.String(description='Ticket subject'),
    'description': fields.String(description='Ticket description'),
    'status': fields.String(description='Ticket status'),
    'priority': fields.String(description='Ticket priority'),
    'category': fields.String(description='Ticket category'),
    'assigned_to': fields.Integer(description='Staff ID assigned to ticket'),
    'created_at': fields.DateTime(description='Ticket creation time'),
    'updated_at': fields.DateTime(description='Ticket last update time'),
    'messages': fields.List(fields.Raw, description='Ticket messages')
})

faq_model = api.model('FAQ', {
    'id': fields.Integer(description='FAQ ID'),
    'question': fields.String(required=True, description='FAQ question'),
    'answer': fields.String(required=True, description='FAQ answer'),
    'category': fields.String(description='FAQ category'),
    'is_published': fields.Boolean(description='Whether FAQ is published'),
    'order': fields.Integer(description='Display order')
})

whatsapp_response = api.model('WhatsAppResponse', {
    'whatsapp_link': fields.String(description='WhatsApp chat link')
})

contact_input = api.model('ContactInput', {
    'subject': fields.String(required=True, description='Contact subject'),
    'message': fields.String(required=True, description='Contact message')
})

contact_response = api.model('ContactResponse', {
    'message': fields.String(description='Response message'),
    'ticket_id': fields.String(description='Generated ticket ID'),
    'support_email': fields.String(description='Support email address')
})

feedback_input = api.model('FeedbackInput', {
    'feedback_type': fields.String(required=True, description='Type of feedback', enum=['general', 'product', 'service', 'app', 'other']),
    'message': fields.String(required=True, description='Feedback message')
})

feedback_response = api.model('FeedbackResponse', {
    'message': fields.String(description='Response message'),
    'feedback_id': fields.String(description='Generated feedback ID')
})

@api.route('/tickets')
class TicketList(Resource):
    @api.doc('create_ticket')
    @api.expect(ticket_input_model)
    @token_required
    def post(self, current_user):
        data = request.get_json()
        
        ticket = SupportTicketModel(
            user_id=current_user.id,
            subject=data['subject'],
            description=data['description'],
            priority=TicketPriority[data.get('priority', 'MEDIUM')],
            category=data.get('category', 'other')
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return ticket.to_dict(), 201

    @api.doc('list_tickets')
    @token_required
    def get(self, current_user):
        tickets = SupportTicketModel.query.filter_by(user_id=current_user.id).order_by(SupportTicketModel.created_at.desc()).all()
        return [ticket.to_dict() for ticket in tickets]

@api.route('/tickets/<int:ticket_id>')
class Ticket(Resource):
    @api.doc('get_ticket')
    @token_required
    def get(self, current_user, ticket_id):
        ticket = SupportTicketModel.query.get_or_404(ticket_id)
        if ticket.user_id != current_user.id and not current_user.is_staff:
            return {'message': 'Access denied'}, 403
        return ticket.to_dict()

    @api.doc('update_ticket')
    @api.expect(ticket_update_model)
    @token_required
    def put(self, current_user, ticket_id):
        ticket = SupportTicketModel.query.get_or_404(ticket_id)
        if ticket.user_id != current_user.id and not current_user.is_staff:
            return {'message': 'Access denied'}, 403
            
        data = request.get_json()
        
        if current_user.is_staff:
            if 'status' in data:
                ticket.status = TicketStatus[data['status']]
            if 'priority' in data:
                ticket.priority = TicketPriority[data['priority']]
            if 'assigned_to' in data:
                ticket.assigned_to = data['assigned_to']
        
        if 'message' in data:
            if not ticket.messages:
                ticket.messages = []
            ticket.messages.append({
                'user_id': current_user.id,
                'message': data['message'],
                'timestamp': datetime.utcnow().isoformat()
            })
        
        db.session.commit()
        return ticket.to_dict()

@api.route('/staff/tickets')
class StaffTicketList(Resource):
    @api.doc('list_staff_tickets')
    @staff_required
    def get(self, current_user):
        status = request.args.get('status')
        assigned_to = request.args.get('assigned_to', type=int)
        
        query = SupportTicketModel.query
        
        if status:
            query = query.filter_by(status=TicketStatus[status.upper()])
        if assigned_to:
            query = query.filter_by(assigned_to=assigned_to)
        
        tickets = query.order_by(SupportTicketModel.created_at.desc()).all()
        return [ticket.to_dict() for ticket in tickets]

@api.route('/faqs')
class FAQList(Resource):
    @api.doc('list_faqs')
    def get(self):
        category = request.args.get('category')
        query = FAQ.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
            
        faqs = query.order_by(FAQ.order.asc()).all()
        return [{
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category': faq.category
        } for faq in faqs]

    @api.doc('create_faq')
    @api.expect(faq_model)
    @api.marshal_with(faq_model)
    @staff_required
    def post(self, current_user):
        """Create a new FAQ (Staff only)"""
        data = request.get_json()
        
        faq = FAQ(**data)
        db.session.add(faq)
        db.session.commit()
        return faq

@api.route('/faqs/<int:id>')
@api.param('id', 'The FAQ identifier')
class FAQResource(Resource):
    @api.doc('get_faq')
    @api.marshal_with(faq_model)
    def get(self, id):
        """Get a FAQ by ID"""
        return FAQ.query.get_or_404(id)

    @api.doc('update_faq')
    @api.expect(faq_model)
    @api.marshal_with(faq_model)
    @staff_required
    def put(self, current_user, id):
        """Update a FAQ (Staff only)"""
        faq = FAQ.query.get_or_404(id)
        data = request.get_json()
        
        for key, value in data.items():
            setattr(faq, key, value)
            
        db.session.commit()
        return faq

    @api.doc('delete_faq')
    @staff_required
    def delete(self, current_user, id):
        """Delete a FAQ (Staff only)"""
        faq = FAQ.query.get_or_404(id)
        db.session.delete(faq)
        db.session.commit()
        return {'message': 'FAQ deleted'}

@api.route('/whatsapp-link')
class WhatsAppLink(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', whatsapp_response)
    @api.response(500, 'Internal Server Error')
    @token_required
    def get(self, current_user):
        """Get WhatsApp support chat link"""
        try:
            # Get WhatsApp business number from config
            whatsapp_number = config('WHATSAPP_BUSINESS_NUMBER')
            
            # Create dynamic message with user info
            message = f"Hi! I'm {current_user.first_name} {current_user.last_name}. I need support with my order."
            
            # Format WhatsApp link
            whatsapp_link = f"https://wa.me/{whatsapp_number}?text={message}"
            
            return {
                'whatsapp_link': whatsapp_link
            }, 200
        except Exception as e:
            return {'message': 'Error generating WhatsApp link', 'error': str(e)}, 500

@api.route('/contact')
class Contact(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(contact_input)
    @api.response(200, 'Success', contact_response)
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Submit a contact form"""
        data = request.get_json()
        
        if not data or not data.get('subject') or not data.get('message'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            # Here you would typically integrate with your preferred ticketing system
            # For now, we'll just return a success message
            
            return {
                'message': 'Support request submitted successfully',
                'ticket_id': 'TICKET-123',  # This would be generated by your ticketing system
                'support_email': config('SUPPORT_EMAIL', default='support@qaffee.com')
            }, 200
        except Exception as e:
            return {'message': 'Error submitting support request', 'error': str(e)}, 500

@api.route('/feedback')
class Feedback(Resource):
    @api.doc(security='Bearer Auth')
    @api.expect(feedback_input)
    @api.response(200, 'Success', feedback_response)
    @api.response(400, 'Validation Error')
    @api.response(500, 'Internal Server Error')
    @token_required
    def post(self, current_user):
        """Submit feedback"""
        data = request.get_json()
        
        if not data or not data.get('feedback_type') or not data.get('message'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            # Here you would typically store the feedback in your database
            # and potentially notify relevant staff
            
            feedback_types = ['general', 'product', 'service', 'app', 'other']
            if data['feedback_type'] not in feedback_types:
                return {'message': 'Invalid feedback type'}, 400
            
            return {
                'message': 'Thank you for your feedback!',
                'feedback_id': 'FEEDBACK-123'  # This would be generated by your system
            }, 200
        except Exception as e:
            return {'message': 'Error submitting feedback', 'error': str(e)}, 500 