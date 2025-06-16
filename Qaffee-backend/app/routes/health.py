from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource

# Create API namespace
api = Namespace('health', description='Health check operations')

@api.route('')
class HealthCheck(Resource):
    @api.doc('health_check')
    def get(self):
        """Check API health status"""
        return {
            'status': 'ok',
            'message': 'Qaffee API is running',
            'version': '1.0.0'
        }, 200

health_bp = Blueprint('health', __name__)
