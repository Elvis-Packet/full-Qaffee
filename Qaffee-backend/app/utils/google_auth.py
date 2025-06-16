from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app, url_for
from ..models import User, UserRole, db
from ..config.oauth import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    ALLOWED_DOMAINS,
    DEFAULT_ADMIN_EMAILS,
    DEFAULT_STAFF_EMAILS,
    GOOGLE_SCOPES
)
import requests as http_requests
from oauthlib.oauth2 import WebApplicationClient
import json
from .auth import generate_token

class GoogleAuthError(Exception):
    pass

def get_google_provider_cfg():
    try:
        return http_requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
    except Exception as e:
        raise GoogleAuthError(f"Failed to get Google provider config: {str(e)}")

def get_google_auth_url():
    """Get Google OAuth2 authorization URL"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=url_for("auth.google_callback", _external=True),
            scope=GOOGLE_SCOPES,
        )
        return request_uri
    except Exception as e:
        raise GoogleAuthError(f"Failed to generate auth URL: {str(e)}")

def get_google_token(code):
    """Exchange authorization code for tokens"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=code,
            redirect_url=url_for("auth.google_callback", _external=True),
            client_secret=GOOGLE_CLIENT_SECRET,
        )
        
        response = http_requests.post(token_url, headers=headers, data=body)
        return client.parse_request_body_response(response.text)
    except Exception as e:
        raise GoogleAuthError(f"Failed to get token: {str(e)}")

def get_google_user_info(token):
    """Get user info from Google"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        
        response = http_requests.get(
            userinfo_endpoint,
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.ok:
            return response.json()
        else:
            raise GoogleAuthError("Failed to get user info")
    except Exception as e:
        raise GoogleAuthError(f"Failed to get user info: {str(e)}")

def verify_google_token(token):
    """Verify Google ID token"""
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise GoogleAuthError("Invalid token issuer")
        
        return idinfo
    except Exception as e:
        raise GoogleAuthError(f"Token verification failed: {str(e)}")

def determine_user_role(email, domain):
    """Determine user role based on email and domain"""
    if email in DEFAULT_ADMIN_EMAILS:
        return UserRole.ADMIN
    elif email in DEFAULT_STAFF_EMAILS:
        return UserRole.STAFF
    elif domain in ALLOWED_DOMAINS:
        return UserRole.STAFF
    return UserRole.CUSTOMER

def get_or_create_google_user(user_info):
    """Get existing user or create new one from Google info"""
    try:
        email = user_info.get('email')
        if not email:
            raise GoogleAuthError("Email not provided by Google")
        
        user = User.query.filter_by(email=email).first()
        email_domain = email.split('@')[1] if '@' in email else None
        
        if user:
            # Update existing user's Google information
            user.is_google_user = True
            user.google_picture = user_info.get('picture')
            user.last_login = db.func.now()
        else:
            # Create new user
            role = determine_user_role(email, email_domain)
            user = User(
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_google_user=True,
                google_picture=user_info.get('picture'),
                role=role,
                is_active=True
            )
            db.session.add(user)
        
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise GoogleAuthError(f"Error saving user: {str(e)}")

def handle_google_auth(auth_code=None, id_token=None):
    """Main function to handle Google authentication"""
    try:
        if auth_code:
            # Handle OAuth2 flow
            tokens = get_google_token(auth_code)
            user_info = get_google_user_info(tokens['access_token'])
        elif id_token:
            # Handle ID token verification
            user_info = verify_google_token(id_token)
        else:
            raise GoogleAuthError("No authentication credentials provided")
        
        # Get or create user
        user = get_or_create_google_user(user_info)
        
        # Generate JWT token
        token = generate_token(user)
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.value,
                'is_google_user': True,
                'picture': user.google_picture
            }
        }
    except Exception as e:
        raise GoogleAuthError(f"Authentication failed: {str(e)}") 