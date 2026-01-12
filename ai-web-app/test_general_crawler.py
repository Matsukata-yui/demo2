from app import create_app, db
from app.models import CrawlerConfig
from app.services.crawler_source_manager import crawler_source_manager
import json

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 通用爬虫引擎功能测试 ===")
    
    # 测试1：创建爬虫配置
    print("\n1. 测试创建爬虫配置")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    request_params = {
        "q": "测试"
    }
    parse_rules = {
        "item_selector": ".result",
        "fields": {
            "title": ".title a",
            "url": ".title a@href",
            "abstract": ".c-abstract"
        }
    }
    
    create_result = crawler_source_manager.create_crawler_config(
        name="测试通用爬虫",
        url="https://www.baidu.com/s",
        source_type="general_crawler",
        crawl_interval=3600,
        enabled=True,
        headers=headers,
        request_params=request_params,
        request_method="GET",
        parse_rules=parse_rules,
        timeout=10,
        retry_count=3
    )
    
    print(f"创建结果: {create_result}")
    
    if create_result["success"]:
        config_id = create_result["config_id"]
        
        # 测试2：获取单个爬虫配置
        print("\n2. 测试获取单个爬虫配置")
        get_result = crawler_source_manager.get_crawler_config(config_id)
        print(f"获取结果: {json.dumps(get_result, ensure_ascii=False, indent=2)}")
        
        # 测试3：更新爬虫配置
        print("\n3. 测试更新爬虫配置")
        update_result = crawler_source_manager.update_crawler_config(
            config_id,
            name="更新后的测试通用爬虫",
            crawl_interval=1800,
            enabled=False
        )
        print(f"更新结果: {update_result}")
        
        # 验证更新是否成功
        updated_config = crawler_source_manager.get_crawler_config(config_id)
        print(f"更新后的配置: {json.dumps(updated_config, ensure_ascii=False, indent=2)}")
        
        # 测试4：获取所有爬虫配置
        print("\n4. 测试获取所有爬虫配置")
        all_configs_result = crawler_source_manager.get_all_crawler_configs()
        print(f"所有配置数量: {len(all_configs_result['configs'])}")
        print(f"所有配置: {json.dumps(all_configs_result, ensure_ascii=False, indent=2)}")
        
        # 测试5：运行通用爬虫
        print("\n5. 测试运行通用爬虫")
        run_params = {
            "q": "通用爬虫测试"
        }
        run_result = crawler_source_manager.run_crawler_by_config(config_id, run_params)
        print(f"运行结果: {run_result}")
        
        if run_result["success"]:
            print(f"爬取结果数量: {len(run_result['results'])}")
            for i, result in enumerate(run_result['results'][:3]):  # 只显示前3个结果
                print(f"结果 {i+1}: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 测试6：删除爬虫配置
        print("\n6. 测试删除爬虫配置")
        delete_result = crawler_source_manager.delete_crawler_config(config_id)
        print(f"删除结果: {delete_result}")
        
        # 验证删除是否成功
        deleted_config = crawler_source_manager.get_crawler_config(config_id)
        print(f"删除后验证: {deleted_config}")
    
    print("\n=== 测试完成 ===")
