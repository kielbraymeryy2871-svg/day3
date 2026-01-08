from app import app, db
from app.models.user import User
from app.models.crawler import Crawler
from app.models.collect_data import CollectData
from app.models.ai_model import AIModel, AITokenStats
from werkzeug.security import generate_password_hash

with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查是否已存在管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建管理员用户
        admin = User(
            username='admin',
            password=generate_password_hash('admin')
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员用户创建成功')
    else:
        print('管理员用户已存在')
