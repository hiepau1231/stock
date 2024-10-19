# Tech Stack

## Backend
- Python: The primary programming language for the backend
- Django: Web framework used for building the application
- Django REST Framework: Used for building APIs (confirmed in settings.py)
- Django Channels: Used for real-time functionality (confirmed in settings.py)

## Frontend
- React (inferred): Based on the presence of frontend folder and package.json

## Database
- SQLite: Currently used as the default database (confirmed in settings.py)
- PostgreSQL: Configuration available but commented out (potential future use)

## Development Tools
- Virtual Environment: Used for Python dependency management
- npm: Node package manager (inferred from package.json)
- Docker: Container platform (inferred from Dockerfile and docker-compose.yml)

## Version Control
- Git: Used for version control

## Project Structure
- Django apps:
  - authentication
  - mock_api
  - predictions
  - real_time_services
  - stock_analysis

## Key Architectural Decisions
1. Modular structure using Django apps for different functionalities
2. Separation of frontend and backend
3. Use of Docker for containerization and easier deployment
4. Implementation of real-time services using Django Channels
5. Custom User Model for authentication
6. CORS configuration for development purposes

## Authentication and Security
- Custom User Model implemented
- Django's built-in authentication system
- Token-based authentication for API access
- CORS configuration for frontend-backend communication

## Additional Technologies
- Channels: For WebSocket support and real-time functionality
- CORS Headers: For handling Cross-Origin Resource Sharing

Note: Some of these details are inferred and may need verification as we proceed with the development.