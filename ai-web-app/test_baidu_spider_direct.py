#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试百度搜索爬虫
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dist.baidusearch.baidu_spider import BaiduSearchSpider

def test_baidu_spider():
    """测试百度搜索爬虫"""
    print("=== 直接测试百度搜索爬虫 ===")
    
    try:
        # 创建百度搜索爬虫实例
        spider = BaiduSearchSpider()
        print("✅ 百度搜索爬虫实例创建成功")
        
        # 测试搜索功能
        keyword = "四川美食"
        print(f"\n测试关键词: {keyword}")
        
        # 执行搜索
        results = spider.search(keyword, page=1, limit=5)
        print(f"搜索结果数量: {len(results)}")
        
        if results:
            print("\n搜索结果详情:")
            for i, result in enumerate(results):
                print(f"\n结果 {i+1}:")
                print(f"标题: {result.get('title', '无')}")
                print(f"URL: {result.get('url', '无')}")
                print(f"摘要: {result.get('abstract', '无')}")
            return True
        else:
            print("❌ 搜索未返回结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_baidu_spider()
    if success:
        print("\n✅ 百度搜索爬虫测试成功")
    else:
        print("\n❌ 百度搜索爬虫测试失败")
