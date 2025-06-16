from decouple import config

# Database Configuration
SQLALCHEMY_DATABASE_URI = config(
    'DATABASE_URL',
    default='sqlite:///qaffee.db'
)

SQLALCHEMY_TRACK_MODIFICATIONS = False 