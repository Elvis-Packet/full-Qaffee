from decouple import config

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID = "453649727294-k9pcg3llmnl2k542ktj8mtsamq2usl60.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth2 Scopes
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Allowed domains for admin/staff (restrict to your organization's domain)
ALLOWED_DOMAINS = [
    "qaffee.com",  # Replace with your organization's domain
]

# Default admin emails (these will be automatically assigned admin role)
DEFAULT_ADMIN_EMAILS = [
    "admin@qaffee.com",  # Replace with actual admin email
]

# Default staff emails (these will be automatically assigned staff role)
DEFAULT_STAFF_EMAILS = [
    "staff@qaffee.com",  # Replace with actual staff email
]

# OAuth2 redirect URI
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='http://localhost:5000/auth/google/callback') 