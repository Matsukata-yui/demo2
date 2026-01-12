from app import create_app
from app.models import CrawlerConfig

app = create_app()

with app.app_context():
    print("=== 检查爬虫源enabled状态 ===")
    print()
    
    # 从数据库获取所有爬虫源
    from app import db
    db_crawlers = CrawlerConfig.query.all()
    
    print(f"数据库中存在 {len(db_crawlers)} 个爬虫源记录")
    print()
    
    for db_crawler in db_crawlers:
        print(f"ID: {db_crawler.id}")
        print(f"名称: {db_crawler.name}")
        print(f"类型: {db_crawler.source_type}")
        print(f"URL: {db_crawler.url}")
        print(f"启用状态: {db_crawler.enabled}")
        print(f"启用状态类型: {type(db_crawler.enabled)}")
        print(f"创建时间: {db_crawler.created_at}")
        print(f"更新时间: {db_crawler.updated_at}")
        print("-" * 50)
    
    # 特别查询enabled=True的爬虫源
    enabled_crawlers = CrawlerConfig.query.filter_by(enabled=True).all()
    print(f"\nenabled=True的爬虫源数量: {len(enabled_crawlers)}")
    for crawler in enabled_crawlers:
        print(f"  - {crawler.name} (ID: {crawler.id})")
