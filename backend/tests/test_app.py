import pytest
import json
from backend.app import create_app, db
from backend.models import UseCase
from datetime import datetime

# Test data
VALID_USER = {"username": "testuser", "password": "password"}
INVALID_USER = {"username": "wronguser", "password": "wrongpassword"}

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False
    })
    with app.app_context():
        db.create_all()
        yield app
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
        yield db

def get_auth_token(client):
    """Helper function to get an auth token."""
    response = client.post('/login', json=VALID_USER)
    data = json.loads(response.data.decode())
    return data.get('sso_token')

# --- Authentication Tests ---
def test_login_success(client):
    """Test successful login."""
    response = client.post('/login', json=VALID_USER)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "sso_token" in data
    assert data["sso_token"] == "dummy_sso_token"

def test_login_failure(client):
    """Test failed login with incorrect credentials."""
    response = client.post('/login', json=INVALID_USER)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Invalid credentials (simulated)"

def test_protected_route_no_token(client, init_database):
    """Test accessing /use_cases without a token."""
    response = client.get('/use_cases')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Token is missing!"

def test_protected_route_invalid_token(client, init_database):
    """Test accessing a protected route with an invalid token."""
    headers = {'Authorization': 'Bearer invalidtoken'}
    response = client.get('/use_cases', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Token is invalid or expired!"

def test_protected_route_valid_token(client, init_database):
    """Test accessing a protected route with a valid token."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/use_cases', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
# --- End of Authentication Tests ---

# --- CRUD Tests for Use Cases ---

def test_create_use_case_success(client, app, init_database):
    """Test successful creation of a new use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    use_case_data = {
        "title": "New AI Initiative",
        "requestor": "Test User",
        "description": "Develop an AI to improve customer service.",
        "rationale": "To ensure functionality.",
        "stage": "Development"
        # reviewed_by_ai_committee defaults to False, updated_by is set by token_required
    }
    response = client.post('/use_cases', headers=headers, json=use_case_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Use case created successfully"
    assert "id" in data
    new_id = data["id"]

    with app.app_context():
        uc = db.session.get(UseCase, new_id)
        assert uc is not None
        assert uc.title == "New AI Initiative"
        assert uc.requestor == "Test User"
        assert uc.updated_by == VALID_USER["username"]
        assert uc.reviewed_by_ai_committee is False # Check default value

def test_create_use_case_missing_fields(client, init_database):
    """Test creating a use case with missing required fields."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    incomplete_data = {
        "requestor": "Test User",
        "description": "This is a test description.",
        "rationale": "To ensure functionality.",
        "stage": "Development"
        # Missing title
    }
    response = client.post('/use_cases', headers=headers, json=incomplete_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Missing required field: title" in data["error"]

def test_get_all_use_cases(client, app, init_database):
    """Test retrieving all use cases."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    with app.app_context():
        uc1 = UseCase(title="Case 1", requestor="User A", description="Desc 1", rationale="Rationale 1", stage="Idea", updated_by="testuser")
        uc2 = UseCase(title="Case 2", requestor="User B", description="Desc 2", rationale="Rationale 2", stage="Development", updated_by="testuser")
        db.session.add_all([uc1, uc2])
        db.session.commit()

    response = client.get('/use_cases', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['title'] == "Case 1"
    assert data[1]['title'] == "Case 2"

def test_get_single_use_case_exists(client, app, init_database):
    """Test retrieving a single existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    with app.app_context():
        uc = UseCase(title="Specific Case", requestor="Specific User", description="Details", rationale="Reasons", stage="Testing", updated_by="testuser")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    response = client.get(f'/use_cases/{uc_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == uc_id
    assert data['title'] == "Specific Case"

def test_get_nonexistent_use_case(client, init_database):
    """Test retrieving a non-existent use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/use_cases/99999', headers=headers) # Assuming ID 99999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_update_use_case_success(client, app, init_database):
    """Test successfully updating an existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    with app.app_context():
        uc = UseCase(title="Original Title", requestor="Original User", description="Original Desc", rationale="Original Rationale", stage="Initial", updated_by="initial_user")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    update_data = {
        "title": "Updated Title",
        "description": "Updated description.",
        "stage": "Production",
        "reviewed_by_ai_committee": True
    }
    response = client.put(f'/use_cases/{uc_id}', headers=headers, json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Use case updated successfully"

    with app.app_context():
        updated_uc = db.session.get(UseCase, uc_id)
        assert updated_uc is not None
        assert updated_uc.title == "Updated Title"
        assert updated_uc.description == "Updated description."
        assert updated_uc.stage == "Production"
        assert updated_uc.requestor == "Original User" # Should not change if not provided
        assert updated_uc.reviewed_by_ai_committee is True
        assert updated_uc.updated_by == VALID_USER["username"] # Should be updated by the current user

def test_update_use_case_not_found(client, init_database):
    """Test updating a non-existent use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    update_data = {"title": "NonExistent Update"}
    response = client.put('/use_cases/99999', headers=headers, json=update_data) # Assuming 99999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_delete_use_case_success(client, app, init_database):
    """Test successfully deleting an existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    with app.app_context():
        uc = UseCase(title="To Be Deleted", requestor="Delete User", description="Delete me", rationale="Delete Rationale", stage="Obsolete", updated_by="deleter")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    response = client.delete(f'/use_cases/{uc_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Use case deleted successfully"

    with app.app_context():
        deleted_uc = db.session.get(UseCase, uc_id)
        assert deleted_uc is None

def test_delete_nonexistent_use_case(client, init_database):
    """Test deleting a non-existent use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete('/use_cases/99999', headers=headers) # Assuming 99999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_create_use_case_invalid_data_type(client, init_database):
    """Test creating a use case with invalid data type (e.g., reviewed_by_ai_committee as string)."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    invalid_type_data = {
        "title": "Type Test Case",
        "requestor": "Type Tester",
        "description": "Description",
        "rationale": "Rationale",
        "stage": "Idea",
        "reviewed_by_ai_committee": "not_a_boolean"
    }
    response = client.post('/use_cases', headers=headers, json=invalid_type_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    # The backend should ideally validate boolean types more strictly.
    # For now, checking if it's handled as an invalid input or if the default (False) is applied.
    # Given the current backend logic, it might coerce "not_a_boolean" to True or False depending on Python's bool() behavior for strings.
    # A more robust backend would validate this.
    # For this test, we'll assume it might lead to a generic error or unexpected behavior if not handled.
    # A better check would be if the backend returns a specific validation error for the field type.
    # For now, we check if the backend sets it to False (default) or if it errors out.
    # Let's assume it should error out or default to False. If it creates the record, check the value.
    if response.status_code == 201: # if it surprisingly creates it
        with app.app_context():
            uc = db.session.get(UseCase, data["id"])
            assert uc.reviewed_by_ai_committee is False # Default behavior if string doesn't parse to True
    else: # Expected path
        assert "Invalid input" in data["error"] or "validation error" in data["error"].lower()


def test_update_use_case_partial(client, app, init_database):
    """Test updating a use case with partial data (only some fields)."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    with app.app_context():
        uc = UseCase(title="Partial Update Case", requestor="Original Requestor", description="Original Desc", rationale="Original Rationale", stage="Initial", updated_by="initial_user")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    partial_update_data = {"stage": "Testing"}
    response = client.put(f'/use_cases/{uc_id}', headers=headers, json=partial_update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Use case updated successfully"

    with app.app_context():
        updated_uc = db.session.get(UseCase, uc_id)
        assert updated_uc is not None
        assert updated_uc.title == "Partial Update Case" # Unchanged
        assert updated_uc.stage == "Testing" # Changed
        assert updated_uc.updated_by == VALID_USER["username"] # Updated by current user
```
