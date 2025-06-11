import pytest
import json
from backend.app import db  # Assuming db is initialized in app.py and accessible
from backend.models import UseCase

# Test data
VALID_USER = {"username": "testuser", "password": "password"}
VALID_TOKEN = None # Will be populated by get_auth_token

def get_auth_token(client):
    """Helper function to get an auth token if not already fetched."""
    global VALID_TOKEN
    if VALID_TOKEN is None:
        response = client.post('/login', json=VALID_USER)
        data = json.loads(response.data.decode())
        VALID_TOKEN = data.get('sso_token')
    return VALID_TOKEN

# --- CRUD Tests for Use Cases ---

def test_create_use_case_success(client, app, init_database):
    """Test successful creation of a new use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    use_case_data = {
        "title": "AI Powered Search",
        "requestor": "R&D Department",
        "description": "Implement an AI-powered search for internal documents.",
        "rationale": "Improve knowledge discovery and efficiency.",
        "stage": "Planning"
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
        assert uc.title == "AI Powered Search"
        assert uc.requestor == "R&D Department"
        assert uc.updated_by == VALID_USER["username"]
        assert uc.reviewed_by_ai_committee is False # Default value

def test_create_use_case_missing_title(client, init_database):
    """Test creating a use case with a missing title."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    use_case_data = {
        # "title": "This is missing",
        "requestor": "Test User",
        "description": "This is a test description.",
        "rationale": "To ensure functionality.",
        "stage": "Development"
    }
    response = client.post('/use_cases', headers=headers, json=use_case_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Missing required field: title" in data["error"]

def test_create_use_case_unauthorized(client, init_database):
    """Test creating a use case without a token."""
    use_case_data = {
        "title": "Unauthorized Case",
        "requestor": "No One",
        "description": "This should fail.",
        "rationale": "Testing security.",
        "stage": "Idea"
    }
    response = client.post('/use_cases', json=use_case_data)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Token is missing!"

def test_get_all_use_cases_success(client, app, init_database):
    """Test retrieving all use cases."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    with app.app_context():
        uc1 = UseCase(title="Case Alpha", requestor="User A", description="Desc 1", rationale="Rationale 1", stage="Idea", updated_by="testuser")
        uc2 = UseCase(title="Case Beta", requestor="User B", description="Desc 2", rationale="Rationale 2", stage="Development", updated_by="testuser")
        db.session.add_all([uc1, uc2])
        db.session.commit()

    response = client.get('/use_cases', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['title'] == "Case Alpha"
    assert data[1]['title'] == "Case Beta"

def test_get_all_use_cases_unauthorized(client, init_database):
    """Test fetching all use cases without a token."""
    response = client.get('/use_cases')
    assert response.status_code == 401

def test_get_single_use_case_exists(client, app, init_database):
    """Test retrieving a single existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    uc_id = None
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

def test_get_single_use_case_not_found(client, init_database):
    """Test retrieving a non-existent use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/use_cases/99999', headers=headers) # Assuming ID 99999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_get_single_use_case_unauthorized(client, app, init_database):
    """Test retrieving a single use case without a token."""
    uc_id = None
    with app.app_context():
        uc = UseCase(title="Unauthorized Access Test Case", requestor="Test", description="Test", rationale="Test", stage="Test", updated_by="testuser")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    response = client.get(f'/use_cases/{uc_id}')
    assert response.status_code == 401

def test_update_use_case_success(client, app, init_database):
    """Test successfully updating an existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    uc_id = None
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
    response = client.put('/use_cases/99999', headers=headers, json=update_data)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_update_use_case_invalid_data(client, app, init_database):
    """Test updating a use case with invalid data (e.g., missing title)."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    uc_id = None
    with app.app_context():
        uc = UseCase(title="Valid Title", requestor="User", description="Desc", rationale="Rationale", stage="Idea", updated_by="testuser")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    invalid_data = {
        "title": "" # Empty title, which is not allowed
    }
    response = client.put(f'/use_cases/{uc_id}', headers=headers, json=invalid_data)
    assert response.status_code == 400 # Assuming validation catches empty title
    data = json.loads(response.data)
    assert "error" in data
    # This assertion depends on how your backend handles validation for empty strings on required fields
    # For instance, if it returns "Missing required field: title" or a more specific validation error.
    # Let's assume it returns a generic bad request for now if not specifically handled.
    # Or, if it's a more specific message like:
    # assert "title" in data["error"].lower() # or a more specific message
    # For the current backend implementation, it might be "Missing required field: title" if title is removed,
    # or it might allow empty string if not explicitly validated as non-empty.
    # Let's assume the backend's `data.get('title', case.title)` would use the old title if "" is passed.
    # To properly test this, the backend should validate non-empty strings for required fields.
    # For now, we'll check for a 400 and that the title was NOT updated to empty.
    with app.app_context():
        uc_after_attempt = db.session.get(UseCase, uc_id)
        assert uc_after_attempt.title == "Valid Title" # Title should not have changed to empty

def test_update_use_case_unauthorized(client, app, init_database):
    """Test updating a use case without a token."""
    uc_id = None
    with app.app_context():
        uc = UseCase(title="Update Auth Test", requestor="User", description="Desc", rationale="Rationale", stage="Idea", updated_by="testuser")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    update_data = {"title": "New Title"}
    response = client.put(f'/use_cases/{uc_id}', json=update_data)
    assert response.status_code == 401

def test_delete_use_case_success(client, app, init_database):
    """Test successfully deleting an existing use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    uc_id = None
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

def test_delete_use_case_not_found(client, init_database):
    """Test deleting a non-existent use case."""
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete('/use_cases/99999', headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "Use case not found"

def test_delete_use_case_unauthorized(client, app, init_database):
    """Test deleting a use case without a token."""
    uc_id = None
    with app.app_context():
        uc = UseCase(title="Delete Auth Test", requestor="User", description="Desc", rationale="Rationale", stage="Idea", updated_by="testuser")
        db.session.add(uc)
        db.session.commit()
        uc_id = uc.id

    response = client.delete(f'/use_cases/{uc_id}')
    assert response.status_code == 401
```
