import os
print('Current directory:', os.getcwd())

from app import app, db
print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])

from app.models.collect_data import CollectData
print('CollectData model imported')

with app.app_context():
    db.create_all()
    print('Tables created')
    print('Database file exists:', os.path.exists('ai-liaowang.db'))
    print('Current directory files:', os.listdir('.'))
