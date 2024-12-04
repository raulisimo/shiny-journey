# Installation
## Clone the repository

```
git clone git@github.com:raulisimo/shiny-journey.git
cd shiny-journey
```

Inside the project folder there are two folders:
1. **backend**: with the Fastapi code.
2. **frontend**: with the vue 3 code.

## Create a Virtual Environment

Navigate to the backend directory.

    cd backend

It’s recommended to use a virtual environment for your Python project.

```
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
````

## Install Dependencies

```
pip install -r requirements.txt
```

## Install Frontend (Vue 3)

If you are also working with the frontend, you need to install the Vue 3 dependencies.

1. Navigate to the frontend directory.

```
cd frontend
```

2.Install the Vue dependencies:
```
npm install
```

# Environment Setup

Before running the app, ensure the following environment variables are set up:
Local Development (.env file)

In your project root, create a .env file with the following content:

### General settings
    APP_TITLE="BRITE MOVIES"
    OMDB_API_KEY="your_omdb_api_key"
    DEBUG="true"  # Set to false for production

# Database settings (for development)
    DATABASE_URL="sqlite:///./test.db"  # For SQLite in development

# Google Cloud settings (for production)
    GCP_PROJECT_ID="your_gcp_project_id"
    CLOUD_SQL_CONNECTION_NAME="your_cloud_sql_connection_name"
    DB_USER="root"  # MySQL user
    DB_NAME="brite-movies"
    DB_PASSWORD="your_database_password"

Note: If you're running in production, use Google Cloud Secret Manager to securely manage your sensitive information.

## Google Cloud Secret Manager Configuration (for Production)

If using Google Cloud in production:

Set up Google Cloud Secret Manager for your configuration keys (DB_PASSWORD, OMDB_API_KEY, etc.).
Make sure the GCP service account used has the necessary permissions to access the secrets.

## Database Configuration

This app supports both local development (with SQLite) and production using Google Cloud SQL (MySQL). The relevant database configuration is chosen dynamically based on the ENV environment variable (DEV for development, PRO for production).

### Local Development Database (SQLite)

For local development, the database is configured through the DATABASE_URL environment variable, which should be set to the appropriate SQLite connection string.

### Production Database (Cloud SQL)

For production, the app will connect to Google Cloud SQL. The database credentials (DB_PASSWORD) should be fetched securely from Google Cloud Secret Manager.

# Running the Application

## Local Development

To run the app locally in development mode:

    uvicorn app.main:app --reload  # This starts the FastAPI server with hot reloading


## Production

For production, ensure that all secrets are properly stored in Google Cloud Secret Manager, or in the app.yaml
    
    entrypoint: uvicorn main:app --host 0.0.0.0 --port 8080

## Frontend Integration

The frontend is a Vue 3 application that communicates with the FastAPI backend to display and manipulate movie data.

## Running the Vue 3 App

To start the Vue 3 frontend locally:

Navigate to the frontend directory.
Run the development server:

    npm run serve

The Vue app will be available at http://localhost:3000.

Note: The frontend sends HTTP requests to the backend to fetch movie details and perform updates or deletions. Ensure CORS is configured properly in FastAPI to allow communication between the frontend and backend.

# API Endpoints
1. Get Movie Details

- Endpoint: GET api/movies/{movie_id}
- Description: Fetch details of a movie by ID.
- Authorization: None.
- Example: GET http://localhost:8000/api/movies/1

2. Update Movie

- Endpoint: PATCH api/movies/{movie_id}
- Description: Update an existing movie's details.
- Example: PATCH http://localhost:8000/api/movies/1
- Content-Type: application/json

    {
      "title": "New Title",
      "director": "New Director"
    }

3. Delete Movie

- Endpoint: DELETE api/movies/{movie_id} 
- Description: Delete a movie by ID.
- Authorization: Requires an authenticated admin user.
- Example: DELETE http://localhost:8000/api/movies/1

4. Authentication

To perform admin-only actions (like deleting a movie), an admin token is required. The token should be sent in the Authorization header as a Bearer token.

Example of Authorization Header:

    Authorization: Bearer <your_token>