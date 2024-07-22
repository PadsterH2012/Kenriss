import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@db:5432/flask_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = ''
    API_KEY = ''
    MARKER = ''  # Set the marker variable here
