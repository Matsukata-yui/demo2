#!/usr/bin/env python3
"""
测试爬虫集成功能
验证更新后的爬虫源管理器是否能正确使用真实的百度爬虫获取数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.services.crawler_source_manager import crawler_source_manager

# 创建应用实例以初始化数据库连接
app = create_app()

with app.app_context():
    print("测试爬虫源管理器的百度搜索功能...")
    
    # 测试使用百度搜索爬虫
    test_keyword = "人工智能"
    test_page = 1
    test_limit = 5
    
    print(f"\n搜索关键词: {test_keyword}")
    print(f"页码: {test_page}")
    print(f"结果数量: {test_limit}")
    print("-" * 60)
    
    # 调用爬虫源管理器
    result = crawler_source_manager.run_crawler_by_source(
        "baidu_search",
        {
            "keyword": test_keyword,
            "page": test_page,
            "limit": test_limit
        }
    )
    
    # 检查结果
    if result["success"]:
        print(f"✅ 爬虫运行成功！")
        print(f"找到 {len(result['results'])} 条结果")
        print("-" * 60)
        
        # 打印结果
        for i, item in enumerate(result['results'], 1):
            print(f"\n结果 {i}:")
            print(f"标题: {item['title']}")
            print(f"链接: {item['url']}")
            if 'abstract' in item:
                print(f"摘要: {item['abstract']}")
                
        print("\n✅ 测试完成！爬虫能够正确获取百度搜索结果。")
    else:
        print(f"❌ 爬虫运行失败:")
        print(f"错误代码: {result.get('error_code', 'UNKNOWN')}")
        print(f"错误信息: {result.get('error_message', '未知错误')}")
        print("\n❌ 测试失败！爬虫无法获取百度搜索结果。")
