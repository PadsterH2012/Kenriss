from flask import Flask
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
