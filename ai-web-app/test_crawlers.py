from app import create_app
from app.services.crawler_source_manager import crawler_source_manager

app = create_app()

with app.app_context():
    print("=== 爬虫源独立调用测试 ===")
    print()
    
    # 获取所有爬虫源配置
    configs = crawler_source_manager.get_all_crawler_configs(refresh=True)
    
    if not configs:
        print("❌ 错误: 没有可用的爬虫源配置!")
    else:
        print(f"发现 {len(configs)} 个爬虫源配置")
        print()
        
        # 对每个爬虫源执行测试
        for config_id, config in configs.items():
            print(f"=== 测试爬虫源: {config['name']} (ID: {config_id}) ===")
            print(f"URL: {config['url']}")
            print(f"类型: {config['source_type']}")
            print()
            
            try:
                # 执行爬虫源调用测试
                result = crawler_source_manager.run_crawler_by_config(config_id, {
                    'keyword': '测试关键词',
                    'page': 1,
                    'limit': 5
                })
                
                print(f"测试结果: {'✅ 成功' if result.get('success') else '❌ 失败'}")
                
                if result.get('success'):
                    results = result.get('results', [])
                    print(f"返回结果数量: {len(results)}")
                    
                    # 检查结果结构
                    if isinstance(results, list):
                        print("✅ results 字段是有效的数组")
                        if results:
                            print("✅ results 数组不为空")
                            # 打印第一个结果作为示例
                            print("示例结果:")
                            print(f"  标题: {results[0].get('title', 'N/A')}")
                            print(f"  URL: {results[0].get('url', 'N/A')}")
                        else:
                            print("⚠️ results 数组为空")
                    else:
                        print("❌ results 字段不是有效的数组")
                else:
                    error = result.get('error', '未知错误')
                    print(f"错误信息: {error}")
                
            except Exception as e:
                print(f"❌ 测试执行失败: {str(e)}")
            
            print("-" * 50)
        
        print("=== 测试完成 ===")
