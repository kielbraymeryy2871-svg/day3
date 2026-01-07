from app import db
from datetime import datetime

class CollectData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cover_image = db.Column(db.String(500), nullable=True)
    crawler_id = db.Column(db.Integer, nullable=True)
    keyword = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(50), nullable=True, default='未知类型')
    status = db.Column(db.String(20), nullable=True, default='completed')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CollectData {self.title}>'
