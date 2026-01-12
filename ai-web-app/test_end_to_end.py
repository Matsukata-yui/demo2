from app import create_app
from app.services.crawler_source_manager import crawler_source_manager
from app.models import CollectionTask, CollectedData
import time
import json

app = create_app()

with app.app_context():
    print("=== 端到端集成测试 ===")
    print()
    
    # 1. 测试爬虫源管理模块
    print("1. 测试爬虫源管理模块")
    print("-" * 50)
    
    # 获取所有注册的爬虫源
    registered_crawlers = crawler_source_manager.get_all_crawler_configs(refresh=True)
    print(f"已注册的爬虫源数量: {len(registered_crawlers)}")
    
    if registered_crawlers:
        for config_id, config in registered_crawlers.items():
            print(f"  - {config['name']} (类型: {config['source_type']})")
    else:
        print("  ❌ 没有已注册的爬虫源")
    
    # 2. 测试爬虫执行能力
    print("\n2. 测试爬虫执行能力")
    print("-" * 50)
    
    if registered_crawlers:
        # 选择第一个爬虫源进行测试
        config_id, config = list(registered_crawlers.items())[0]
        print(f"测试爬虫源: {config['name']}")
        
        # 测试正常参数
        print("  测试场景1: 正常参数")
        result = crawler_source_manager.run_crawler_by_config(config_id, {
            'keyword': 'Python',
            'page': 1,
            'limit': 5
        })
        
        print(f"  成功状态: {result.get('success')}")
        print(f"  结果数量: {len(result.get('results', []))}")
        print(f"  响应格式: {'✅ 标准化' if 'success' in result else '❌ 非标准化'}")
        
        # 测试边界条件
        print("  测试场景2: 边界条件")
        result = crawler_source_manager.run_crawler_by_config(config_id, {
            'keyword': '',  # 空关键词
            'page': 0,  # 页码为0
            'limit': 200  # 超出限制的数量
        })
        
        print(f"  成功状态: {result.get('success')}")
        print(f"  错误代码: {result.get('error_code')}")
        print(f"  错误信息: {result.get('error_message')}")
    else:
        print("  ❌ 没有可用的爬虫源进行测试")
    
    # 3. 测试采集管理模块
    print("\n3. 测试采集管理模块")
    print("-" * 50)
    
    # 从app.routes.main_routes导入run_keyword_collection函数
    from app.routes.main_routes import run_keyword_collection
    
    # 创建一个测试采集任务
    from app import db
    
    # 清理之前的测试数据
    test_tasks = CollectionTask.query.filter(CollectionTask.name.like('%测试%')).all()
    for task in test_tasks:
        db.session.delete(task)
    db.session.commit()
    
    # 创建新的测试任务
    new_task = CollectionTask(
        name='测试采集任务',
        urls=json.dumps({'keyword': 'Python', 'crawlers': ['website']}),
        interval=0,
        status='pending',
        created_by='test_user'
    )
    db.session.add(new_task)
    db.session.commit()
    
    print(f"创建测试采集任务，ID: {new_task.id}")
    
    # 执行采集任务
    print("  执行采集任务...")
    run_keyword_collection(new_task.id, 'Python', ['website'])
    
    # 等待采集完成
    time.sleep(2)
    
    # 检查任务状态
    updated_task = CollectionTask.query.get(new_task.id)
    print(f"  任务状态: {updated_task.status}")
    
    # 检查采集到的数据
    collected_data = CollectedData.query.filter_by(task_id=new_task.id).all()
    print(f"  采集到的数据数量: {len(collected_data)}")
    
    if collected_data:
        # 打印第一条数据作为示例
        first_data = collected_data[0]
        print("  示例数据:")
        print(f"    标题: {first_data.title}")
        print(f"    URL: {first_data.url}")
        print(f"    来源: {first_data.source}")
    
    # 4. 测试错误处理机制
    print("\n4. 测试错误处理机制")
    print("-" * 50)
    
    # 测试不存在的爬虫源
    print("  测试场景1: 不存在的爬虫源")
    result = crawler_source_manager.run_crawler_by_config(999, {
        'keyword': 'Python'
    })
    
    print(f"  成功状态: {result.get('success')}")
    print(f"  错误代码: {result.get('error_code')}")
    print(f"  错误信息: {result.get('error_message')}")
    
    # 测试不存在的数据源类型
    print("  测试场景2: 不存在的数据源类型")
    result = crawler_source_manager.run_crawler_by_source('non_existent_source', {
        'keyword': 'Python'
    })
    
    print(f"  成功状态: {result.get('success')}")
    print(f"  错误代码: {result.get('error_code')}")
    print(f"  错误信息: {result.get('error_message')}")
    
    # 5. 清理测试数据
    print("\n5. 清理测试数据")
    print("-" * 50)
    
    # 删除测试任务及其关联的数据
    db.session.delete(updated_task)
    db.session.commit()
    print("  ✅ 测试数据已清理")
    
    print()
    print("=== 端到端集成测试完成 ===")
