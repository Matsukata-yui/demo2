from app import create_app, db
from app.models import CrawlerConfig
from sqlalchemy import inspect

# 创建应用实例
app = create_app()

with app.app_context():
    # 检查数据库中是否有CrawlerConfig表
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"数据库中的表: {tables}")
    
    if 'crawler_config' in tables:
        # 获取表的结构
        columns = inspector.get_columns('crawler_config')
        print("\ncrawler_config表的列:")
        for column in columns:
            print(f"- {column['name']}: {column['type']}")
        
        # 查询现有记录
        configs = CrawlerConfig.query.all()
        print(f"\n现有CrawlerConfig记录数: {len(configs)}")
        for config in configs:
            print(f"- ID: {config.id}, Name: {config.name}, Type: {config.source_type}")
    else:
        print("\ncrawler_config表不存在")
