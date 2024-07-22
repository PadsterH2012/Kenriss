# Py_Flask_Boilerplate

A robust boilerplate for Flask applications with user authentication, PostgreSQL database integration, and Docker containerization.

## Features

- User registration and login system
- PostgreSQL database integration with SQLAlchemy ORM
- Docker containerization for easy deployment
- Responsive design with customizable CSS
- User dashboard and settings pages
- Theme switching capability (light/dark mode)
- Flask-Migrate for database migrations
- Secure password hashing with Werkzeug
- Session-based authentication
- RESTful API structure

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Py_Flask_Boilerplate.git
   cd Py_Flask_Boilerplate
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

3. Access the application at `http://localhost:5000`

## Project Structure

```
Py_Flask_Boilerplate/
├── backend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── user_settings.html
│   │   └── app_settings.html
│   ├── static/
│   │   └── css/
│   │       ├── base.css
│   │       └── dark-theme.css
│   ├── app.py
│   ├── routes.py
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   └── init.sql
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Usage

1. Visit the homepage at `http://localhost:5000`
2. Register a new user account
3. Log in with your credentials
4. Access the dashboard
5. Explore user settings and app settings pages
6. Try switching between light and dark themes

## Development

To make changes to the application:

1. Modify the Flask application in `backend/app.py`
2. Update routes in `backend/routes.py`
3. Modify database models in `backend/models.py`
4. Update HTML templates in `backend/templates/`
5. Add or modify CSS in `backend/static/css/`
6. Rebuild and restart the Docker containers to see your changes:
   ```
   docker-compose down
   docker-compose up --build
   ```

## Database Migrations

This project uses Flask-Migrate for database migrations. To create and apply migrations:

1. Access the backend container:
   ```
   docker-compose exec backend bash
   ```

2. Initialize migrations (if not already done):
   ```
   flask db init
   ```

3. Create a new migration:
   ```
   flask db migrate -m "Description of changes"
   ```

4. Apply the migration:
   ```
   flask db upgrade
   ```

## API Endpoints

- POST `/register`: Register a new user
- POST `/login`: Authenticate a user
- POST `/logout`: Log out the current user
- GET `/dashboard`: Access user dashboard
- GET, POST `/user_settings`: View and update user settings
- GET, POST `/app_settings`: View and update application settings

## Security Features

- Password hashing using Werkzeug's generate_password_hash and check_password_hash
- Session-based authentication
- CSRF protection (to be implemented)
- Input validation and sanitization (to be implemented)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- Flask
- SQLAlchemy
- PostgreSQL
- Docker
- Werkzeug
