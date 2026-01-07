from app import db
from datetime import datetime

class Crawler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 爬虫类型，如'baidu'、'custom'等
    status = db.Column(db.String(20), nullable=False, default='inactive')  # 状态：active, inactive
    config = db.Column(db.Text, nullable=False)  # 爬虫配置，JSON格式
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = db.Column(db.DateTime, nullable=True)
    run_count = db.Column(db.Integer, nullable=False, default=0)
    success_count = db.Column(db.Integer, nullable=False, default=0)
    failure_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<Crawler {self.name}>'
