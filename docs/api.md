# Backend API Documentation

This document details the API endpoints available in the backend service.

**Authentication:**
Most endpoints (except `/login`) require a Bearer token in the `Authorization` header. This token is obtained via the `/login` endpoint using dummy credentials.
Example: `Authorization: Bearer dummy_sso_token`

---

## Endpoints

### 1. Login

*   **POST /login**
    *   **Description:** Authenticates a user (simulated).
    *   **Request Body:** JSON object
        ```json
        {
            "username": "testuser",
            "password": "password"
        }
        ```
    *   **Success Response (200 OK):**
        ```json
        {
            "message": "Login successful (simulated)",
            "sso_token": "dummy_sso_token"
        }
        ```
    *   **Error Response (400 Bad Request):** If no input data provided.
        ```json
        {
            "error": "No input data provided"
        }
        ```
    *   **Error Response (401 Unauthorized):** If credentials are invalid.
        ```json
        {
            "error": "Invalid credentials (simulated)"
        }
        ```

### 2. Create Use Case

*   **POST /use_cases**
    *   **Description:** Creates a new use case.
    *   **Authentication:** Required.
    *   **Request Body:** JSON object representing the use case.
        ```json
        {
            "title": "New Use Case Title",
            "requestor": "User Name",
            "description": "Detailed description of the use case.",
            "rationale": "Rationale behind this use case.",
            "stage": "Initial Idea",
            "reviewed_by_ai_committee": false
        }
        ```
        *   `title`, `requestor`, `description`, `rationale`, `stage` are required.
        *   `reviewed_by_ai_committee` is optional and defaults to `false`.
    *   **Success Response (201 Created):**
        ```json
        {
            "message": "Use case created successfully",
            "id": 123
        }
        ```
        *   `id` is the ID of the newly created use case.
    *   **Error Response (400 Bad Request):** If input is invalid or missing required fields.
        ```json
        {
            "error": "Invalid input"
        }
        ```
        or
        ```json
        {
            "error": "Missing required fields: title, requestor, ..."
        }
        ```
    *   **Error Response (401 Unauthorized):** If token is missing or invalid.

### 3. Get All Use Cases

*   **GET /use_cases**
    *   **Description:** Retrieves a list of all use cases.
    *   **Authentication:** Required.
    *   **Success Response (200 OK):**
        ```json
        [
            {
                "id": 1,
                "title": "Use Case 1",
                "requestor": "User A",
                "description": "...",
                "rationale": "...",
                "stage": "Development",
                "reviewed_by_ai_committee": true,
                "date_updated": "YYYY-MM-DDTHH:MM:SS.ffffff",
                "updated_by": "testuser"
            },
            {
                "id": 2,
                "title": "Use Case 2",
                "...": "..."
            }
        ]
        ```
    *   **Error Response (401 Unauthorized):** If token is missing or invalid.

### 4. Get Specific Use Case

*   **GET /use_cases/<int:id>**
    *   **Description:** Retrieves a single use case by its ID.
    *   **Authentication:** Required.
    *   **Path Parameters:**
        *   `id` (integer): The ID of the use case to retrieve.
    *   **Success Response (200 OK):**
        ```json
        {
            "id": 1,
            "title": "Use Case 1",
            "requestor": "User A",
            "description": "...",
            "rationale": "...",
            "stage": "Development",
            "reviewed_by_ai_committee": true,
            "date_updated": "YYYY-MM-DDTHH:MM:SS.ffffff",
            "updated_by": "testuser"
        }
        ```
    *   **Error Response (401 Unauthorized):** If token is missing or invalid.
    *   **Error Response (404 Not Found):** If the use case with the given ID does not exist.
        ```json
        {
            "error": "Use case not found"
        }
        ```

### 5. Update Use Case

*   **PUT /use_cases/<int:id>**
    *   **Description:** Updates an existing use case by its ID.
    *   **Authentication:** Required.
    *   **Path Parameters:**
        *   `id` (integer): The ID of the use case to update.
    *   **Request Body:** JSON object with fields to update. All fields are optional; only provided fields will be updated.
        ```json
        {
            "title": "Updated Title",
            "stage": "Review"
        }
        ```
    *   **Success Response (200 OK):**
        ```json
        {
            "message": "Use case updated successfully"
        }
        ```
    *   **Error Response (400 Bad Request):** If input data is invalid.
        ```json
        {
            "error": "Invalid input"
        }
        ```
    *   **Error Response (401 Unauthorized):** If token is missing or invalid.
    *   **Error Response (404 Not Found):** If the use case with the given ID does not exist.
        ```json
        {
            "error": "Use case not found"
        }
        ```

### 6. Delete Use Case

*   **DELETE /use_cases/<int:id>**
    *   **Description:** Deletes a use case by its ID.
    *   **Authentication:** Required.
    *   **Path Parameters:**
        *   `id` (integer): The ID of the use case to delete.
    *   **Success Response (200 OK):**
        ```json
        {
            "message": "Use case deleted successfully"
        }
        ```
    *   **Error Response (401 Unauthorized):** If token is missing or invalid.
    *   **Error Response (404 Not Found):** If the use case with the given ID does not exist.
        ```json
        {
            "error": "Use case not found"
        }
        ```
