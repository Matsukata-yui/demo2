from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
import base64
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class CrawlerConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    crawl_interval = db.Column(db.Integer, default=3600)
    enabled = db.Column(db.Boolean, default=True)
    headers = db.Column(db.Text, nullable=True)  # JSON格式存储请求头
    request_params = db.Column(db.Text, nullable=True)  # JSON格式存储请求参数
    request_method = db.Column(db.String(10), default='GET')  # 请求方法
    parse_rules = db.Column(db.Text, nullable=True)  # JSON格式存储解析规则
    timeout = db.Column(db.Integer, default=10)  # 请求超时时间
    retry_count = db.Column(db.Integer, default=3)  # 重试次数
    proxy = db.Column(db.Text, nullable=True)  # JSON格式存储代理配置
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"CrawlerConfig('{self.name}', '{self.url}')"

class CollectionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    urls = db.Column(db.Text, nullable=False)
    interval = db.Column(db.Integer, default=3600)
    status = db.Column(db.String(50), default='pending')
    created_by = db.Column(db.String(20), nullable=False)
    last_run_time = db.Column(db.DateTime, nullable=True)
    last_finish_time = db.Column(db.DateTime, nullable=True)
    total_collected = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"CollectionTask('{self.name}', '{self.status}')"

class CollectedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('collection_task.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), default='collected')
    sentiment = db.Column(db.String(20), nullable=True)
    keywords = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)  # 爬虫源
    image = db.Column(db.String(255), nullable=True)  # 图片URL
    deep_collected = db.Column(db.Boolean, default=False)  # 是否已深度采集
    deep_collected_at = db.Column(db.DateTime, nullable=True)  # 深度采集时间
    
    collection_task = db.relationship('CollectionTask', backref=db.backref('collected_data', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f"CollectedData('{self.title}', '{self.url}')"

class AIAnalysisTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='pending')
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"AIAnalysisTask('{self.name}', '{self.status}')"

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_analysis_task_id = db.Column(db.Integer, db.ForeignKey('ai_analysis_task.id'), nullable=False)
    result_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    ai_analysis_task = db.relationship('AIAnalysisTask', backref=db.backref('analysis_results', lazy=True))
    
    def __repr__(self):
        return f"AnalysisResult('{self.result_type}', '{self.ai_analysis_task.name}')"

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_analysis_task_id = db.Column(db.Integer, db.ForeignKey('ai_analysis_task.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    ai_analysis_task = db.relationship('AIAnalysisTask', backref=db.backref('reports', lazy=True))
    
    def __repr__(self):
        return f"Report('{self.title}', '{self.generated_at}')"

class ModelConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    api_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    system_prompt = db.Column(db.Text, nullable=True)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_api_key(self, api_key):
        # 使用base64编码API密钥，生产环境应使用更安全的加密方法
        encrypted = base64.b64encode(api_key.encode()).decode()
        self.api_key = encrypted
    
    def get_api_key(self):
        # 解密API密钥
        try:
            decrypted = base64.b64decode(self.api_key.encode()).decode()
            return decrypted
        except:
            return self.api_key
    
    def __repr__(self):
        return f"ModelConfig('{self.name}', '{self.model_name}')"

class TokenUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model_config.id'), nullable=False)
    request_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    input_tokens = db.Column(db.Integer, nullable=False)
    output_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)
    request_summary = db.Column(db.Text, nullable=True)
    response_status = db.Column(db.String(50), nullable=False)
    
    model_config = db.relationship('ModelConfig', backref=db.backref('token_usages', lazy=True))
    
    def __repr__(self):
        return f"TokenUsage('{self.model_id}', '{self.request_time}')"

class DeepCollectionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collected_data_id = db.Column(db.Integer, db.ForeignKey('collected_data.id', ondelete='CASCADE'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text, nullable=True)
    model_used = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='completed')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    collected_data = db.relationship('CollectedData', backref=db.backref('deep_collection_data', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f"DeepCollectionData('{self.title}', '{self.url}')"
