from app import create_app
from app.services.crawler_source_manager import crawler_source_manager

app = create_app()

with app.app_context():
    print("=== 爬虫调度器功能验证 ===")
    print()
    
    # 1. 注册状态检查
    print("1. 注册状态检查")
    print("-" * 50)
    
    # 获取所有爬虫源配置
    configs = crawler_source_manager.get_all_crawler_configs(refresh=True)
    
    if not configs:
        print("❌ 错误: 没有可用的爬虫源配置!")
    else:
        print(f"✅ 成功注册 {len(configs)} 个爬虫源配置")
        print()
        
        for config_id, config in configs.items():
            print(f"  ID: {config_id}")
            print(f"  名称: {config['name']}")
            print(f"  类型: {config['source_type']}")
            print(f"  URL: {config['url']}")
            print()
    
    # 2. 调度触发测试
    print("2. 调度触发测试")
    print("-" * 50)
    
    # 测试按配置ID触发
    print("测试按配置ID触发:")
    
    if configs:
        # 测试第一个配置
        first_config_id = list(configs.keys())[0]
        print(f"  测试配置ID: {first_config_id} ({configs[first_config_id]['name']})")
        
        try:
            result = crawler_source_manager.run_crawler_by_config(first_config_id, {
                'keyword': '测试关键词',
                'page': 1,
                'limit': 3
            })
            
            if result.get('success'):
                print(f"  ✅ 调度触发成功，返回 {len(result.get('results', []))} 条结果")
            else:
                print(f"  ❌ 调度触发失败: {result.get('error_message', '未知错误')}")
        except Exception as e:
            print(f"  ❌ 调度触发异常: {str(e)}")
    else:
        print("  ⚠️  无可用配置进行测试")
    
    # 测试按数据源类型触发
    print("\n测试按数据源类型触发:")
    
    # 获取所有唯一的数据源类型
    source_types = set()
    for config in configs.values():
        source_types.add(config['source_type'])
    
    if source_types:
        for source_type in source_types:
            print(f"  测试数据源类型: {source_type}")
            
            try:
                result = crawler_source_manager.run_crawler_by_source(source_type, {
                    'keyword': '测试关键词',
                    'page': 1,
                    'limit': 3
                })
                
                if result.get('success'):
                    print(f"  ✅ 调度触发成功，返回 {len(result.get('results', []))} 条结果")
                else:
                    print(f"  ❌ 调度触发失败: {result.get('error_message', '未知错误')}")
            except Exception as e:
                print(f"  ❌ 调度触发异常: {str(e)}")
    else:
        print("  ⚠️  无可用数据源类型进行测试")
    
    print()
    print("=== 爬虫调度器功能验证完成 ===")
