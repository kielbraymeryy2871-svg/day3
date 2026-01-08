from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'

# 先导入模型，确保所有模型都已加载
from app.models.user import User
from app.models.crawler import Crawler
from app.models.collect_data import CollectData
from app.models.ai_model import AIModel, AITokenStats

# 然后导入蓝图
from app.routes import main, ai_routes, crawler_bp
app.register_blueprint(main)
app.register_blueprint(ai_routes, url_prefix='/ai')
app.register_blueprint(crawler_bp)
