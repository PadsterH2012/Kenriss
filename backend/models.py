from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    nzb_id = db.Column(db.String(100), nullable=True)

class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)

    @classmethod
    def initialize_settings(cls):
        default_settings = [
            ('API_KEY', ''),
            ('BASE_URL', ''),
            ('MARKER', '')
        ]
        for key, value in default_settings:
            if not cls.query.filter_by(key=key).first():
                new_setting = cls(key=key, value=value)
                db.session.add(new_setting)
        db.session.commit()

    @classmethod
    def get_setting(cls, key):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else None
