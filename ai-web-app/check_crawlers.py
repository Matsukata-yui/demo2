from app import create_app, db
from app.models import CrawlerConfig

app = create_app()

with app.app_context():
    # 查询所有爬虫源记录
    crawler_configs = CrawlerConfig.query.all()
    
    print("=== 爬虫源数据库验证 ===")
    print(f"总爬虫源数量: {len(crawler_configs)}")
    print()
    
    if not crawler_configs:
        print("❌ 错误: 数据库中没有爬虫源记录!")
    else:
        enabled_count = 0
        disabled_count = 0
        
        for config in crawler_configs:
            print(f"ID: {config.id}")
            print(f"名称: {config.name}")
            print(f"URL: {config.url}")
            print(f"类型: {config.source_type}")
            print(f"启用状态: {'✅ 启用' if config.enabled else '❌ 禁用'}")
            print(f"创建时间: {config.created_at}")
            print(f"更新时间: {config.updated_at}")
            print("-" * 50)
            
            if config.enabled:
                enabled_count += 1
            else:
                disabled_count += 1
        
        print(f"=== 统计信息 ===")
        print(f"启用的爬虫源: {enabled_count}")
        print(f"禁用的爬虫源: {disabled_count}")
        
        if enabled_count == 0:
            print("❌ 错误: 没有启用的爬虫源!")
        else:
            print("✅ 验证完成: 数据库中有启用的爬虫源")