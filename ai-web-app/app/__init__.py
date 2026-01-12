from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config

# 初始化扩展
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    

    
    # 注册蓝图
    from app.routes.main_routes import main
    from app.routes.ai_routes import ai
    from app.routes.stream_routes import stream
    from app.routes.crawler_routes import crawler
    app.register_blueprint(main)
    app.register_blueprint(ai, url_prefix='/ai')
    app.register_blueprint(stream, url_prefix='/stream')
    app.register_blueprint(crawler)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
