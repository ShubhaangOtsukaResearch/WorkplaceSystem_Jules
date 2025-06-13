# Project Documentation

## Overview

This document provides an overview of the project, focusing on the backend services.

**Purpose:**
[To be filled in - e.g., This project aims to provide a platform for managing and tracking AI use cases.]

**High-Level Features (Backend):**
- CRUD operations for AI use cases.
- User authentication (simulated SSO).
- RESTful API for interacting with use case data.

**Technologies Used (Backend):**
- Python
- Flask (web framework)
- SQLAlchemy (ORM for database interaction)
- SQLite (development database)

## Backend Setup and Installation

1.  **Prerequisites:**
    - Python 3.8+
    - pip (Python package installer)

2.  **Clone the repository (if not already done):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>/backend
    ```

3.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install dependencies:**
    ```bash
    pip install Flask Flask-SQLAlchemy
    ```
    *(Note: Add any other specific dependencies if known, e.g., from a requirements.txt file if one existed)*

## Running the Backend

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the `backend` directory.**
3.  **Run the Flask application:**
    ```bash
    flask run
    ```
    Or, if running directly via `app.py`:
    ```bash
    python app.py
    ```
4.  The backend API should now be running, typically at `http://127.0.0.1:5000/`.
