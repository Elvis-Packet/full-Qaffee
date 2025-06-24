from flask import request
from ..models import db, Branch, DeliveryAddress, Order, StoreLocation
from .auth import token_required, admin_required
import requests
from decouple import config
from math import radians, sin, cos, sqrt, atan2
from flask_restx import Namespace, Resource, fields

# Create API namespace
api = Namespace('locations', description='Location management operations')

# Models for request/response documentation
branch_model = api.model('Branch', {
    'id': fields.Integer(description='Branch ID'),
    'name': fields.String(description='Branch name'),
    'address': fields.String(description='Branch address'),
    'latitude': fields.Float(description='Branch latitude'),
    'longitude': fields.Float(description='Branch longitude'),
    'contact_number': fields.String(description='Branch contact number'),
    'distance': fields.Float(description='Distance from user location (if provided)'),
    'opening_hours': fields.Raw(description='Branch opening hours'),
    'features': fields.List(fields.String, description='Available features at branch')
})

delivery_address_model = api.model('DeliveryAddress', {
    'id': fields.Integer(description='Address ID'),
    'address_line1': fields.String(required=True, description='Address line 1'),
    'address_line2': fields.String(description='Address line 2'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(required=True, description='State'),
    'postal_code': fields.String(required=True, description='Postal code'),
    'country': fields.String(required=True, description='Country'),
    'latitude': fields.Float(description='Address latitude'),
    'longitude': fields.Float(description='Address longitude'),
    'is_default': fields.Boolean(description='Whether this is the default address'),
    'label': fields.String(description='Address label (e.g. Home, Work)')
})

map_coordinates_model = api.model('MapCoordinates', {
    'delivery': fields.Nested(api.model('DeliveryLocation', {
        'latitude': fields.Float(description='Delivery location latitude'),
        'longitude': fields.Float(description='Delivery location longitude'),
        'address': fields.String(description='Delivery address')
    })),
    'pickup': fields.Nested(api.model('PickupLocation', {
        'latitude': fields.Float(description='Pickup location latitude'),
        'longitude': fields.Float(description='Pickup location longitude'),
        'address': fields.String(description='Pickup address'),
        'name': fields.String(description='Branch name'),
        'distance': fields.Float(description='Distance in km from delivery location')
    })),
    'map_url': fields.String(description='Google Maps directions URL')
})

store_location_model = api.model('StoreLocation', {
    'id': fields.Integer(description='Store location ID'),
    'name': fields.String(required=True, description='Store name'),
    'address': fields.String(required=True, description='Store address'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(required=True, description='State'),
    'postal_code': fields.String(required=True, description='Postal code'),
    'country': fields.String(required=True, description='Country'),
    'phone': fields.String(description='Store phone number'),
    'email': fields.String(description='Store email'),
    'latitude': fields.Float(description='Store latitude'),
    'longitude': fields.Float(description='Store longitude'),
    'is_active': fields.Boolean(description='Whether store is active'),
    'opening_hours': fields.Raw(description='Store opening hours')
})

# Predefined branch locations (including The Oval Building)
PREDEFINED_BRANCHES = {
    'nairobi': {
        'name': 'Qaffee Point - Nairobi Westlands',
        'address': 'THE OVAL BUILDING, RING ROAD, PRR4+G5H, Nairobi',
        'latitude': -1.2648,
        'longitude': 36.8050,
        'features': ['Dine-in', 'Takeaway', 'WiFi', 'Modern Ambiance', 'Outdoor Seating']
    },
    'mombasa': {
        'name': 'Qaffee Point - Mombasa',
        'address': 'Nyerere Avenue, Mombasa, Kenya',
        'latitude': -4.0435,
        'longitude': 39.6682,
        'features': ['Dine-in', 'Takeaway', 'Delivery', 'WiFi', 'VIP Lounge']
    }
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two coordinates in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return round(distance, 2)

def get_google_maps_url(origin_lat, origin_lng, dest_lat, dest_lng, dest_name=None):
    """Generate Google Maps directions URL"""
    base_url = "https://www.google.com/maps/dir/?api=1"
    params = {
        'origin': f"{origin_lat},{origin_lng}",
        'destination': f"{dest_lat},{dest_lng}",
        'travelmode': 'driving'
    }
    if dest_name:
        params['destination'] += f"({dest_name})"
    return f"{base_url}&origin={params['origin']}&destination={params['destination']}&travelmode={params['travelmode']}"

@api.route('/branches')
class Branches(Resource):
    @api.response(200, 'Success', [branch_model])
    @api.response(500, 'Internal Server Error')
    @api.param('latitude', 'User\'s latitude')
    @api.param('longitude', 'User\'s longitude')
    def get(self):
        """Get all active branches, optionally sorted by distance from user"""
        try:
            # Get user's location from query parameters
            user_lat = request.args.get('latitude', type=float)
            user_lon = request.args.get('longitude', type=float)
            
            branches = Branch.query.filter_by(is_active=True).all()
            
            # If no branches in DB, use predefined ones
            if not branches:
                branches = [
                    Branch(**PREDEFINED_BRANCHES['nairobi']),
                    Branch(**PREDEFINED_BRANCHES['mombasa'])
                ]
            
            branch_list = []
            for branch in branches:
                branch_data = {
                    'id': branch.id,
                    'name': branch.name,
                    'address': branch.address,
                    'latitude': branch.latitude,
                    'longitude': branch.longitude,
                    'contact_number': branch.contact_number,
                    'features': branch.features or []
                }
                
                # Calculate distance if user location provided
                if user_lat and user_lon:
                    distance = calculate_distance(
                        user_lat, user_lon,
                        branch.latitude, branch.longitude
                    )
                    branch_data['distance'] = distance
                
                branch_list.append(branch_data)
            
            # Sort by distance if available
            if user_lat and user_lon:
                branch_list.sort(key=lambda x: x.get('distance', float('inf')))
            
            return branch_list, 200
        except Exception as e:
            return {'message': 'Error fetching branches', 'error': str(e)}, 500

@api.route('/map-coordinates')
class MapCoordinates(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, 'Success', map_coordinates_model)
    @api.response(400, 'Validation Error')
    @api.response(404, 'Order not found')
    @api.response(500, 'Internal Server Error')
    @api.param('order_id', 'Order ID')
    @token_required
    def get(self, current_user):
        """Get delivery and pickup coordinates for an order with map URL"""
        try:
            order_id = request.args.get('order_id', type=int)
            
            if not order_id:
                return {'message': 'Order ID is required'}, 400
            
            order = Order.query.filter_by(
                id=order_id,
                user_id=current_user.id
            ).first_or_404()
            
            if not order.delivery_address:
                return {'message': 'No delivery address for this order'}, 400
            
            # Get all active branches
            branches = Branch.query.filter_by(is_active=True).all()
            
            # If no branches in DB, use predefined ones
            if not branches:
                branches = [
                    Branch(**PREDEFINED_BRANCHES['nairobi']),
                    Branch(**PREDEFINED_BRANCHES['mombasa'])
                ]
            
            # Find nearest branch
            nearest_branch = min(
                branches,
                key=lambda b: calculate_distance(
                    b.latitude, b.longitude,
                    order.delivery_address.latitude,
                    order.delivery_address.longitude
                )
            )
            
            distance = calculate_distance(
                order.delivery_address.latitude,
                order.delivery_address.longitude,
                nearest_branch.latitude,
                nearest_branch.longitude
            )
            
            # Generate Google Maps URL
            map_url = get_google_maps_url(
                order.delivery_address.latitude,
                order.delivery_address.longitude,
                nearest_branch.latitude,
                nearest_branch.longitude,
                nearest_branch.name
            )
            
            return {
                'delivery': {
                    'latitude': order.delivery_address.latitude,
                    'longitude': order.delivery_address.longitude,
                    'address': f"{order.delivery_address.address_line1}, {order.delivery_address.city}"
                },
                'pickup': {
                    'latitude': nearest_branch.latitude,
                    'longitude': nearest_branch.longitude,
                    'address': nearest_branch.address,
                    'name': nearest_branch.name,
                    'distance': distance
                },
                'map_url': map_url
            }, 200
        except Exception as e:
            return {'message': 'Error fetching map coordinates', 'error': str(e)}, 500

@api.route('/delivery-addresses')
class DeliveryAddressList(Resource):
    @api.expect(delivery_address_model)
    @token_required
    def post(self, current_user):
        data = request.get_json()
        # Validate and create DeliveryAddress
        address = DeliveryAddress(
            user_id=current_user.id,
            address_line1=data['address_line1'],
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country=data['country'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            # ... other fields
        )
        db.session.add(address)
        db.session.commit()
        return {'id': address.id}, 201

# ... (keep the rest of your existing endpoints: StoreLocations, DeliveryAddresses, etc.)