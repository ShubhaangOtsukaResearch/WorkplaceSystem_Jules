import pytest
from backend.app import create_app, db

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create a Flask app configured for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use in-memory SQLite for tests
        'WTF_CSRF_ENABLED': False,  # Disable CSRF if you use WTForms and it interferes
        'LOGIN_DISABLED': False # Ensure login is not disabled for auth tests
    })

    # Establish an application context before running the tests.
    with app.app_context():
        db.create_all()  # Create all database tables

    yield app

    # Clean up / reset resources after the test module finishes
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Ensure the database is clean before each test function."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    return db # Not strictly necessary to return db, but can be useful
