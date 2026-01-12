from app import create_app
from app.services.crawler_source_manager import crawler_source_manager
from app.models import CrawlerConfig
import json

app = create_app()

with app.app_context():
    print("=== 爬虫调度执行链路检查 ===")
    print()
    
    # 1. 验证爬虫管理模块是否已将所有爬虫源正确注册至系统
    print("1. 验证爬虫源注册状态")
    print("-" * 50)
    
    # 从数据库获取所有爬虫源
    from app import db
    db_crawlers = CrawlerConfig.query.all()
    print(f"数据库中存在 {len(db_crawlers)} 个爬虫源记录")
    
    # 从爬虫管理模块获取所有注册的爬虫源
    registered_crawlers = crawler_source_manager.get_all_crawler_configs(refresh=True)
    print(f"爬虫管理模块已注册 {len(registered_crawlers)} 个爬虫源")
    print()
    
    # 检查注册状态
    if len(db_crawlers) == len(registered_crawlers):
        print("✅ 数据库记录与注册状态一致")
    else:
        print("❌ 数据库记录与注册状态不一致")
        print(f"  数据库记录数: {len(db_crawlers)}")
        print(f"  注册爬虫数: {len(registered_crawlers)}")
    
    # 打印详细信息
    print("\n详细信息:")
    for db_crawler in db_crawlers:
        is_registered = db_crawler.id in registered_crawlers
        status = "✅ 已注册" if is_registered else "❌ 未注册"
        print(f"  ID: {db_crawler.id}, 名称: {db_crawler.name}, 类型: {db_crawler.source_type}, 状态: {status}")
    
    # 2. 检查爬虫调度器是否能够准确映射并调用对应爬虫的执行方法
    print("\n2. 检查爬虫调度执行能力")
    print("-" * 50)
    
    # 测试每个注册的爬虫源
    if registered_crawlers:
        for config_id, config in registered_crawlers.items():
            print(f"测试爬虫源: {config['name']} (类型: {config['source_type']})")
            
            # 测试通过配置ID调用
            print("  测试通过配置ID调用")
            result = crawler_source_manager.run_crawler_by_config(config_id, {
                'keyword': 'Python',
                'page': 1,
                'limit': 3
            })
            
            print(f"  成功状态: {result.get('success')}")
            print(f"  结果数量: {len(result.get('results', []))}")
            
            # 测试通过数据源类型调用
            print("  测试通过数据源类型调用")
            result = crawler_source_manager.run_crawler_by_source(config['source_type'], {
                'keyword': 'Python',
                'page': 1,
                'limit': 3
            })
            
            print(f"  成功状态: {result.get('success')}")
            print(f"  结果数量: {len(result.get('results', []))}")
            print()
    else:
        print("  ⚠️  无已注册的爬虫源进行测试")
    
    # 3. 排查是否存在"数据库中存在爬虫源记录但代码层未实现对应执行逻辑"的情况
    print("\n3. 排查执行逻辑实现情况")
    print("-" * 50)
    
    # 获取所有唯一的数据源类型
    source_types = set()
    for config in registered_crawlers.values():
        source_types.add(config['source_type'])
    
    print(f"发现 {len(source_types)} 种不同的数据源类型:")
    for source_type in source_types:
        print(f"  - {source_type}")
    
    # 测试每种数据源类型的执行逻辑
    print("\n测试每种数据源类型的执行逻辑:")
    for source_type in source_types:
        print(f"  测试数据源类型: {source_type}")
        result = crawler_source_manager.run_crawler_by_source(source_type, {
            'keyword': 'Python',
            'page': 1,
            'limit': 3
        })
        
        if result.get('success'):
            print(f"  ✅ 执行逻辑已实现，返回 {len(result.get('results', []))} 条结果")
        else:
            error_message = result.get('error_message', '未知错误')
            print(f"  ❌ 执行逻辑存在问题: {error_message}")
    
    # 4. 检查调度过程日志记录
    print("\n4. 检查调度过程日志记录")
    print("-" * 50)
    
    # 这里可以添加日志记录检查逻辑
    # 例如：检查日志文件是否存在、是否包含调度相关的日志记录等
    print("  ⚠️  日志记录检查需要手动配置和验证")
    print("  建议：在爬虫调度器中添加详细的日志记录，确保调用链路可追踪")
    
    print()
    print("=== 检查完成 ===")
