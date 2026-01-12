#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试百度爬虫功能
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
    print("1. 创建百度爬虫实例...")
    try:
        spider = BaiduSearchSpider()
        print("✅ 百度爬虫实例创建成功")
    except Exception as e:
        print(f"❌ 创建百度爬虫实例失败: {str(e)}")
        return False
    
    # 测试搜索功能
    print("\n2. 测试搜索功能...")
    try:
        keyword = "四川美食"
        page = 1
        limit = 5
        
        print(f"   搜索关键词: {keyword}")
        print(f"   页码: {page}")
        print(f"   限制条数: {limit}")
        
        # 调用search方法
        results = spider.search(keyword, page, limit)
        
        print(f"\n3. 搜索结果:")
        print(f"   找到 {len(results)} 条结果")
        
        if results:
            print("\n4. 结果详情:")
            for i, result in enumerate(results, 1):
                print(f"\n   结果 {i}:")
                print(f"   标题: {result.get('title', '无')}")
                print(f"   链接: {result.get('url', '无')}")
                if 'abstract' in result:
                    print(f"   摘要: {result['abstract'][:80]}...")
            print("\n✅ 百度爬虫搜索功能测试成功")
        else:
            print("\n❌ 百度爬虫未返回搜索结果")
            return False
    except Exception as e:
        print(f"\n❌ 百度爬虫搜索功能测试失败: {str(e)}")
        return False
    
    # 测试run方法
    print("\n5. 测试run方法...")
    try:
        params = {
            "keyword": "四川美食",
            "page": 1,
            "limit": 3
        }
        
        print(f"   测试参数: {params}")
        
        # 调用run方法
        run_results = spider.run(params)
        
        print(f"\n6. run方法结果:")
        print(f"   返回 {len(run_results)} 条结果")
        
        if run_results:
            print("\n7. run方法结果详情:")
            for i, result in enumerate(run_results[:2], 1):
                print(f"\n   结果 {i}:")
                print(f"   标题: {result.get('title', '无')}")
                print(f"   链接: {result.get('url', '无')}")
            print("\n✅ 百度爬虫run方法测试成功")
        else:
            print("\n❌ 百度爬虫run方法未返回结果")
            return False
    except Exception as e:
        print(f"\n❌ 百度爬虫run方法测试失败: {str(e)}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=== 开始测试百度爬虫 ===")
    
    test_result = test_baidu_spider()
    
    print("\n=== 测试结果 ===")
    if test_result:
        print("🎉 百度爬虫测试成功！")
        return True
    else:
        print("❌ 百度爬虫测试失败！")
        return False

if __name__ == "__main__":
    main()
