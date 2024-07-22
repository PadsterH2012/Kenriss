from app import create_app, db
from models import AppSettings

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        AppSettings.initialize_settings()

if __name__ == '__main__':
    init_db()
