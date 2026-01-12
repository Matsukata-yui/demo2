import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-secret-key-for-development'
    
    # 数据库配置
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(basedir, '..', 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(instance_dir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # AI模型配置
    AI_API_URL = os.environ.get('AI_API_URL') or 'https://api.siliconflow.cn/v1/'
    AI_API_KEY = os.environ.get('AI_API_KEY') or 'sk-ldqweaqhmbgnucxkzspamzjxpowpbwojlzzxqarhqgebviqg'
    AI_MODEL_NAME = os.environ.get('AI_MODEL_NAME') or 'Qwen/Qwen3-8B'
    
    # 静态文件配置
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # 禁用CSRF保护以方便测试
    WTF_CSRF_ENABLED = False
