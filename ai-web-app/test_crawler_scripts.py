from app import create_app
from app.services.crawler_source_manager import crawler_source_manager
import json

app = create_app()

with app.app_context():
    print("=== 爬虫脚本独立运行验证 ===")
    print()
    
    # 1. 测试 run_crawler_by_config 方法
    print("1. 测试 run_crawler_by_config 方法")
    print("-" * 50)
    
    # 获取所有爬虫源配置
    configs = crawler_source_manager.get_all_crawler_configs(refresh=True)
    
    if configs:
        for config_id, config in configs.items():
            print(f"测试配置ID: {config_id} ({config['name']})")
            
            # 测试场景1: 正常参数
            print("  测试场景1: 正常参数")
            result = crawler_source_manager.run_crawler_by_config(config_id, {
                'keyword': 'Python',
                'page': 1,
                'limit': 5
            })
            
            print(f"  成功状态: {result.get('success')}")
            print(f"  结果类型: {type(result.get('results'))}")
            print(f"  结果数量: {len(result.get('results', []))}")
            print(f"  响应格式: {'✅ 标准化' if 'success' in result else '❌ 非标准化'}")
            
            # 测试场景2: 空参数
            print("  测试场景2: 空参数")
            result = crawler_source_manager.run_crawler_by_config(config_id, {})
            
            print(f"  成功状态: {result.get('success')}")
            print(f"  结果类型: {type(result.get('results'))}")
            print(f"  结果数量: {len(result.get('results', []))}")
            
            # 测试场景3: None参数
            print("  测试场景3: None参数")
            result = crawler_source_manager.run_crawler_by_config(config_id, None)
            
            print(f"  成功状态: {result.get('success')}")
            print(f"  结果类型: {type(result.get('results'))}")
            print(f"  结果数量: {len(result.get('results', []))}")
            
            print()
    else:
        print("  ⚠️  无可用配置进行测试")
    
    # 2. 测试 run_crawler_by_source 方法
    print("2. 测试 run_crawler_by_source 方法")
    print("-" * 50)
    
    # 获取所有唯一的数据源类型
    source_types = set()
    for config in configs.values():
        source_types.add(config['source_type'])
    
    # 添加一些常见的数据源类型进行测试
    source_types.add('baidu_search')
    source_types.add('google_search')
    
    for source_type in source_types:
        print(f"测试数据源类型: {source_type}")
        
        # 测试场景1: 正常参数
        print("  测试场景1: 正常参数")
        result = crawler_source_manager.run_crawler_by_source(source_type, {
            'keyword': 'Python',
            'page': 1,
            'limit': 5
        })
        
        print(f"  成功状态: {result.get('success')}")
        print(f"  结果类型: {type(result.get('results'))}")
        print(f"  结果数量: {len(result.get('results', []))}")
        print(f"  响应格式: {'✅ 标准化' if 'success' in result else '❌ 非标准化'}")
        
        # 测试场景2: 空参数
        print("  测试场景2: 空参数")
        result = crawler_source_manager.run_crawler_by_source(source_type, {})
        
        print(f"  成功状态: {result.get('success')}")
        print(f"  结果类型: {type(result.get('results'))}")
        print(f"  结果数量: {len(result.get('results', []))}")
        
        # 测试场景3: None参数
        print("  测试场景3: None参数")
        result = crawler_source_manager.run_crawler_by_source(source_type, None)
        
        print(f"  成功状态: {result.get('success')}")
        print(f"  结果类型: {type(result.get('results'))}")
        print(f"  结果数量: {len(result.get('results', []))}")
        
        print()
    
    # 3. 测试错误处理
    print("3. 测试错误处理")
    print("-" * 50)
    
    # 测试场景1: 不存在的配置ID
    print("  测试场景1: 不存在的配置ID")
    result = crawler_source_manager.run_crawler_by_config(999, {
        'keyword': 'Python'
    })
    
    print(f"  成功状态: {result.get('success')}")
    print(f"  错误信息: {result.get('error_message', 'N/A')}")
    print(f"  错误代码: {result.get('error_code', 'N/A')}")
    
    # 测试场景2: 不存在的数据源类型
    print("  测试场景2: 不存在的数据源类型")
    result = crawler_source_manager.run_crawler_by_source('non_existent_source', {
        'keyword': 'Python'
    })
    
    print(f"  成功状态: {result.get('success')}")
    print(f"  错误信息: {result.get('error_message', 'N/A')}")
    print(f"  错误代码: {result.get('error_code', 'N/A')}")
    
    print()
    print("=== 验证完成 ===")
