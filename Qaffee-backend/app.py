from flask import Flask
from flask_migrate import Migrate
from app.models import db
from app import create_app
from flask_cors import CORS


app = create_app()
migrate = Migrate(app, db)
CORS(app, origins=["http://localhost:8080"])

if __name__ == '__main__':
    app.run(debug=True) 