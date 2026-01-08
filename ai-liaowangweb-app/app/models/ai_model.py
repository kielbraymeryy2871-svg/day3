from app import db
from datetime import datetime

class AIModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    api_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    system_prompt = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='inactive')  # active, inactive
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIModel {self.name}>'

class AITokenStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'), nullable=False)
    prompt_tokens = db.Column(db.Integer, nullable=False, default=0)
    completion_tokens = db.Column(db.Integer, nullable=False, default=0)
    total_tokens = db.Column(db.Integer, nullable=False, default=0)
    usage_type = db.Column(db.String(50), nullable=True)  # 如 'test', 'collection', 'chat'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AITokenStats model_id={self.model_id} tokens={self.total_tokens}>'
