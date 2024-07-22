# NZB Show Tracker

A Flask-based web application for tracking and managing TV shows using NZB files and SABnzbd integration.

## Features

- User registration and login system
- PostgreSQL database integration with SQLAlchemy ORM
- Docker containerization for easy deployment
- Responsive design with customizable CSS and dark mode support
- User dashboard for managing tracked shows
- Search functionality for finding NZB files
- Integration with SABnzbd for automatic NZB downloads
- Theme switching capability (light/dark mode)
- Flask-Migrate for database migrations
- Secure password hashing with Werkzeug
- Session-based authentication

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nzb-show-tracker.git
   cd nzb-show-tracker
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

3. Access the application at `http://localhost:5000`

## Project Structure

```
nzb-show-tracker/
├── backend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── user_settings.html
│   │   ├── app_settings.html
│   │   ├── episodes.html
│   │   └── search_results.html
│   ├── static/
│   │   └── css/
│   │       ├── base.css
│   │       ├── dashboard.css
│   │       └── dark-theme.css
│   ├── app.py
│   ├── routes.py
│   ├── app_routes.py
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

1. Visit the homepage and register a new user account
2. Log in with your credentials
3. Add shows to track from the dashboard
4. Search for episodes of your tracked shows
5. Send NZB files directly to SABnzbd for download
6. View and manage your tracked shows and episodes
7. Customize application settings, including SABnzbd integration

## Development

To make changes to the application:

1. Modify the Flask application in `backend/app.py`
2. Update routes in `backend/routes.py` and `backend/app_routes.py`
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
- GET `/search/<show_title>`: Search for episodes of a show
- GET `/episodes/<show_id>`: View episodes for a specific show
- POST `/send_to_sabnzbd`: Send an NZB file to SABnzbd

## Security Features

- Password hashing using Werkzeug's generate_password_hash and check_password_hash
- Session-based authentication
- API key management for external services

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
- SABnzbd
