import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Define the UseCase model
class UseCase(db.Model):
    __tablename__ = 'use_cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    requestor = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(50), nullable=False)
    reviewed_by_ai_committee = db.Column(db.Boolean, default=False)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'requestor': self.requestor,
            'description': self.description,
            'rationale': self.rationale,
            'stage': self.stage,
            'reviewed_by_ai_committee': self.reviewed_by_ai_committee,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'updated_by': self.updated_by
        }

# Placeholder for a proper SSO token validation function
def validate_sso_token(token):
    """Simulates SSO token validation."""
    if token == "dummy_sso_token":
        return {"user_id": "testuser", "username": "testuser"}
    return None

# Decorator for protected routes
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        user_info = validate_sso_token(token)
        if not user_info:
            return jsonify({"error": "Token is invalid or expired!"}), 401

        return f(current_user_info=user_info, *args, **kwargs)
    return decorated_function

def create_app(config_override=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this in production!
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(app.instance_path, "use_cases.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if config_override:
        app.config.update(config_override) # Use update for overriding specific keys

    # Ensure the instance folder exists
    # This needs to happen before db.init_app and db.create_all
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        username = data.get('username')
        password = data.get('password')

        if username == "testuser" and password == "password":
            return jsonify({"message": "Login successful (simulated)", "sso_token": "dummy_sso_token"}), 200
        return jsonify({"error": "Invalid credentials (simulated)"}), 401

    @app.route('/use_cases', methods=['POST'])
    @token_required
    def create_use_case_route(current_user_info):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        required_fields = ['title', 'requestor', 'description', 'rationale', 'stage']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        new_case = UseCase(
            title=data['title'],
            requestor=data['requestor'],
            description=data['description'],
            rationale=data['rationale'],
            stage=data['stage'],
            reviewed_by_ai_committee=data.get('reviewed_by_ai_committee', False),
            updated_by=current_user_info['username']
        )
        db.session.add(new_case)
        db.session.commit()
        return jsonify({"message": "Use case created successfully", "id": new_case.id}), 201

    @app.route('/use_cases', methods=['GET'])
    @token_required
    def get_use_cases_route(current_user_info):
        cases = UseCase.query.all()
        return jsonify([case.to_dict() for case in cases]), 200

    @app.route('/use_cases/<int:id>', methods=['GET'])
    @token_required
    def get_use_case_route(current_user_info, id):
        case = db.session.get(UseCase, id) # Use db.session.get for SQLAlchemy 2.x
        if not case:
            return jsonify({"error": "Use case not found"}), 404
        return jsonify(case.to_dict()), 200

    @app.route('/use_cases/<int:id>', methods=['PUT'])
    @token_required
    def update_use_case_route(current_user_info, id):
        case = db.session.get(UseCase, id) # Use db.session.get for SQLAlchemy 2.x
        if not case:
            return jsonify({"error": "Use case not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        case.title = data.get('title', case.title)
        case.requestor = data.get('requestor', case.requestor)
        case.description = data.get('description', case.description)
        case.rationale = data.get('rationale', case.rationale)
        case.stage = data.get('stage', case.stage)
        case.reviewed_by_ai_committee = data.get('reviewed_by_ai_committee', case.reviewed_by_ai_committee)
        case.updated_by = current_user_info['username']
        case.date_updated = datetime.utcnow()

        db.session.commit()
        return jsonify({"message": "Use case updated successfully"}), 200

    @app.route('/use_cases/<int:id>', methods=['DELETE'])
    @token_required
    def delete_use_case_route(current_user_info, id):
        case = db.session.get(UseCase, id) # Use db.session.get for SQLAlchemy 2.x
        if not case:
            return jsonify({"error": "Use case not found"}), 404

        db.session.delete(case)
        db.session.commit()
        return jsonify({"message": "Use case deleted successfully"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
