import os

class Config:
    SECRET_KEY = 'your-secret-key'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "ai-liaowang.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
