import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Define the UseCase model
class UseCase(db.Model):
    """
    Represents an AI use case tracked by the system.

    Attributes:
        id (int): Primary key, unique identifier for the use case.
        title (str): The title of the use case (max 100 chars).
        requestor (str): The person or entity requesting the use case (max 100 chars).
        description (str): A detailed description of the use case.
        rationale (str): The justification or reasons for implementing the use case.
        stage (str): The current stage of development or review for the use case (max 50 chars)
                     (e.g., 'Initial Idea', 'Development', 'Review', 'Approved').
        reviewed_by_ai_committee (bool): Flag indicating if the AI committee has reviewed this use case.
                                         Defaults to False.
        date_updated (datetime): Timestamp of the last update. Automatically set on update.
        updated_by (str): Identifier of the user who last updated the use case (max 100 chars).
    """
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
        """Serializes the UseCase SQLAlchemy model object to a Python dictionary."""
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
    """
    Simulates SSO token validation.

    In a real application, this function would integrate with an
    SSO provider to validate the token and retrieve user information.
    For this example, it checks for a dummy token.

    Args:
        token (str): The SSO token to validate.

    Returns:
        dict: A dictionary containing user information (e.g., user_id, username)
              if the token is valid, None otherwise.
    """
    if token == "dummy_sso_token":
        return {"user_id": "testuser", "username": "testuser"}
    return None

# Decorator for protected routes
def token_required(f):
    """
    Decorator to protect routes that require authentication.

    Checks for a 'Bearer' token in the 'Authorization' header,
    validates it using `validate_sso_token`, and passes the
    user information to the decorated function.

    Args:
        f (function): The view function to decorate.

    Returns:
        function: The decorated function, which includes token validation logic.
                  Returns a 401 error response if the token is missing or invalid.
    """
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
    """
    Factory function to create and configure the Flask application.

    Initializes the Flask app, sets up default configuration,
    overrides with `config_override` if provided, initializes SQLAlchemy,
    creates database tables if they don't exist, and registers API routes.

    Args:
        config_override (dict, optional): A dictionary of configuration values
                                          to override defaults. Defaults to None.

    Returns:
        Flask: The configured Flask application instance.
    """
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
        """
        Handles POST requests to /login for (simulated) user authentication.

        Expects a JSON body with 'username' and 'password'.
        On successful authentication with dummy credentials ("testuser", "password"),
        it returns a dummy SSO token.

        Returns:
            Response: JSON response with a success message and SSO token (200 OK),
                      or an error message (400 Bad Request for missing data,
                      401 Unauthorized for invalid credentials).
        """
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
        """
        Handles POST requests to /use_cases to create a new use case.

        Requires a valid SSO token for authentication. The request body must be a
        JSON object containing the details of the use case. Required fields are
        'title', 'requestor', 'description', 'rationale', and 'stage'.
        'reviewed_by_ai_committee' is optional.

        The 'updated_by' field is automatically set from the authenticated user's info.

        Args:
            current_user_info (dict): Information about the authenticated user,
                                      provided by the @token_required decorator.

        Returns:
            Response: JSON response indicating success (201 Created) with the new
                      use case ID, or an error message (400 Bad Request for invalid input,
                      401 Unauthorized for auth issues).
        """
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
        """
        Handles GET requests to /use_cases to retrieve all use cases.

        Requires a valid SSO token for authentication.

        Args:
            current_user_info (dict): Information about the authenticated user.

        Returns:
            Response: JSON list of all use cases (200 OK), or 401 if unauthorized.
        """
        cases = UseCase.query.all()
        return jsonify([case.to_dict() for case in cases]), 200

    @app.route('/use_cases/<int:id>', methods=['GET'])
    @token_required
    def get_use_case_route(current_user_info, id):
        """
        Handles GET requests to /use_cases/<id> to retrieve a specific use case.

        Requires a valid SSO token for authentication.

        Args:
            current_user_info (dict): Information about the authenticated user.
            id (int): The ID of the use case to retrieve.

        Returns:
            Response: JSON object of the use case (200 OK),
                      404 if not found, or 401 if unauthorized.
        """
        case = db.session.get(UseCase, id) # Use db.session.get for SQLAlchemy 2.x
        if not case:
            return jsonify({"error": "Use case not found"}), 404
        return jsonify(case.to_dict()), 200

    @app.route('/use_cases/<int:id>', methods=['PUT'])
    @token_required
    def update_use_case_route(current_user_info, id):
        """
        Handles PUT requests to /use_cases/<id> to update an existing use case.

        Requires a valid SSO token for authentication. The request body should be a
        JSON object containing the fields to update.
        The 'updated_by' field is automatically set from the authenticated user's info.

        Args:
            current_user_info (dict): Information about the authenticated user.
            id (int): The ID of the use case to update.

        Returns:
            Response: JSON message confirming update (200 OK),
                      400 for invalid input, 404 if not found, or 401 if unauthorized.
        """
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
        """
        Handles DELETE requests to /use_cases/<id> to delete a use case.

        Requires a valid SSO token for authentication.

        Args:
            current_user_info (dict): Information about the authenticated user.
            id (int): The ID of the use case to delete.

        Returns:
            Response: JSON message confirming deletion (200 OK),
                      404 if not found, or 401 if unauthorized.
        """
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
