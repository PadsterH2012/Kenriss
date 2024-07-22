from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import time
from sqlalchemy.exc import OperationalError
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder=os.path.abspath('templates'), static_folder=os.path.abspath('static'))
    app.secret_key = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/nzb_show_tracker_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import all models here
        from models import User, Show, Episode, AppSettings
        
        # Create the database if it doesn't exist
        from sqlalchemy_utils import database_exists, create_database
        if not database_exists(db.engine.url):
            create_database(db.engine.url)
        
        # Create tables for all models
        db.create_all()
        
        # Check if all tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        expected_tables = ['users', 'show', 'episode', 'app_settings']
        existing_tables = inspector.get_table_names()
        
        for table in expected_tables:
            if table not in existing_tables:
                app.logger.warning(f"Table '{table}' does not exist. Creating it now.")
                if table == 'users':
                    User.__table__.create(db.engine)
                elif table == 'show':
                    Show.__table__.create(db.engine)
                elif table == 'episode':
                    Episode.__table__.create(db.engine)
                elif table == 'app_settings':
                    AppSettings.__table__.create(db.engine)
        
        # Initialize app settings
        AppSettings.initialize_settings()
        
        from routes import bp as routes_bp
        from app_routes import bp as app_routes_bp
        app.register_blueprint(routes_bp, url_prefix='')
        app.register_blueprint(app_routes_bp, url_prefix='')

    return app

def connect_to_database(app, retries=5, delay=5):
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
            print("Successfully connected to the database and created tables!")
            return
        except OperationalError as e:
            if attempt < retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to the database after multiple attempts.")
                raise e

if __name__ == '__main__':
    app = create_app()
    connect_to_database(app)
    app.run(host='0.0.0.0', port=5000)

def connect_to_database(app, retries=5, delay=5):
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
            print("Successfully connected to the database and created tables!")
            return
        except OperationalError as e:
            if attempt < retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to the database after multiple attempts.")
                raise e

if __name__ == '__main__':
    app = create_app()
    connect_to_database(app)
    app.run(host='0.0.0.0', port=5000)

def connect_to_database(app, retries=10, delay=5):
    for attempt in range(retries):
        try:
            with app.app_context():
                db.engine.connect()
                db.create_all()
            print("Successfully connected to the database!")
            return
        except OperationalError as e:
            if attempt < retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect to the database after multiple attempts.")
                raise e

if __name__ == '__main__':
    app = create_app()
    connect_to_database(app)
    app.run(host='0.0.0.0', port=5000)
