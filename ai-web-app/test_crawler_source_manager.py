#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫源管理器功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入爬虫源管理器
from app.services.crawler_source_manager import crawler_source_manager

def test_get_all_configs():
    """测试获取所有爬虫配置"""
    print("=== 测试获取所有爬虫配置 ===")
    configs = crawler_source_manager.get_all_crawler_configs(refresh=True)
    print(f"✅ 获取到 {len(configs)} 个爬虫配置")
    
    for config_id, config in configs.items():
        print(f"\n配置ID: {config_id}")
        print(f"名称: {config.get('name')}")
        print(f"URL: {config.get('url')}")
        print(f"数据源类型: {config.get('source_type')}")
        print(f"启用状态: {config.get('enabled')}")
        
    return configs

def test_run_crawler_by_config(config_id):
    """测试通过配置ID运行爬虫"""
    print(f"\n=== 测试通过配置ID运行爬虫 (ID: {config_id}) ===")
    
    # 运行爬虫，设置limit=5
    result = crawler_source_manager.run_crawler_by_config(
        config_id=config_id,
        params={"limit": 5}
    )
    
    print(f"✅ 运行结果: {'成功' if result.get('success') else '失败'}")
    
    if result.get('success'):
        print(f"📋 结果数量: {result.get('total_results', 0)}")
        print(f"📄 消息: {result.get('message')}")
        
        # 打印前3条结果
        results = result.get('results', [])
        if results:
            print("\n=== 部分结果 ===")
            for i, item in enumerate(results[:3], 1):
                print(f"\n结果 {i}:")
                print(f"标题: {item.get('title', '无')}")
                print(f"链接: {item.get('url', '无')}")
                if 'content' in item:
                    print(f"内容: {item['content'][:100]}...")
    else:
        print(f"❌ 错误代码: {result.get('error_code')}")
        print(f"❌ 错误信息: {result.get('error_message')}")
    
    return result

def test_run_crawler_by_source(source_name):
    """测试通过数据源类型运行爬虫"""
    print(f"\n=== 测试通过数据源类型运行爬虫 (类型: {source_name}) ===")
    
    # 运行爬虫，设置limit=5
    result = crawler_source_manager.run_crawler_by_source(
        source_name=source_name,
        params={"keyword": "Python 爬虫", "limit": 5}
    )
    
    print(f"✅ 运行结果: {'成功' if result.get('success') else '失败'}")
    
    if result.get('success'):
        print(f"📋 结果数量: {result.get('total_results', 0)}")
        print(f"📄 消息: {result.get('message')}")
        
        # 打印前3条结果
        results = result.get('results', [])
        if results:
            print("\n=== 部分结果 ===")
            for i, item in enumerate(results[:3], 1):
                print(f"\n结果 {i}:")
                print(f"标题: {item.get('title', '无')}")
                print(f"链接: {item.get('url', '无')}")
                if 'abstract' in item:
                    print(f"摘要: {item['abstract'][:100]}...")
    else:
        print(f"❌ 错误代码: {result.get('error_code')}")
        print(f"❌ 错误信息: {result.get('error_message')}")
    
    return result

def main():
    """主测试函数"""
    print("=== 开始测试爬虫源管理器 ===")
    
    # 测试获取所有配置
    configs = test_get_all_configs()
    
    # 如果有配置，测试运行第一个配置
    if configs:
        first_config_id = list(configs.keys())[0]
        test_run_crawler_by_config(first_config_id)
    
    # 测试通过数据源类型运行爬虫
    test_run_crawler_by_source("baidu_search")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
