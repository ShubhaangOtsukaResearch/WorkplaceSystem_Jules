import json
from backend.models import UseCase # Import UseCase if needed for context, though not directly for auth tests

VALID_USER = {"username": "testuser", "password": "password"}
INVALID_USER = {"username": "wronguser", "password": "wrongpassword"}

def get_auth_token(client):
    """Helper function to get an auth token."""
    response = client.post('/login', json=VALID_USER)
    data = json.loads(response.data.decode())
    return data.get('sso_token')

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

def test_protected_route_no_token(client, init_database): # Added init_database fixture
    """Test accessing /use_cases without a token."""
    response = client.get('/use_cases')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Token is missing!"

def test_protected_route_invalid_token(client, init_database): # Added init_database fixture
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
    assert isinstance(response.json, list) # Basic check that it returns a list (of use cases)
