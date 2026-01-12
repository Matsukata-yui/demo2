#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试百度爬虫功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入百度爬虫
from dist.baidusearch.baidu_spider import BaiduSearchSpider

def test_baidu_spider():
    """测试百度爬虫功能"""
    print("=== 测试百度爬虫 ===")
    
    # 创建爬虫实例
    spider = BaiduSearchSpider()
    print("✅ 百度爬虫实例创建成功")
    
    # 测试搜索功能
    keyword = "Python 爬虫"
    page = 1
    limit = 5
    
    print(f"\n🔍 搜索关键词: {keyword}")
    print(f"📄 页码: {page}")
    print(f"📊 限制条数: {limit}")
    
    results = spider.search_with_retry(keyword, page, limit)
    
    print(f"\n📋 搜索结果数量: {len(results)}")
    
    if results:
        print("\n=== 搜索结果 ===")
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"标题: {result.get('title', '无')}")
            print(f"链接: {result.get('url', '无')}")
            if 'abstract' in result:
                print(f"摘要: {result['abstract']}")
        print("\n✅ 百度爬虫测试成功")
    else:
        print("\n❌ 百度爬虫未返回结果")
        print("可能原因:")
        print("1. 网络连接问题")
        print("2. 被百度反爬机制检测")
        print("3. 关键词无结果")

if __name__ == "__main__":
    test_baidu_spider()
