#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试百度搜索爬虫，验证带引号的关键词
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dist.baidusearch.baidu_spider import BaiduSearchSpider

def test_baidu_spider_quoted():
    """测试百度搜索爬虫，验证带引号的关键词"""
    print("=== 测试百度搜索爬虫，验证带引号的关键词 ===")
    
    try:
        # 创建百度搜索爬虫实例
        spider = BaiduSearchSpider()
        print("✅ 百度搜索爬虫实例创建成功")
        
        # 测试1: 不带引号的关键词
        keyword1 = "四川美食"
        print(f"\n测试1 - 不带引号的关键词: {keyword1}")
        results1 = spider.search(keyword1, page=1, limit=5)
        print(f"搜索结果数量: {len(results1)}")
        
        # 测试2: 带单引号的关键词
        keyword2 = "'四川美食'"
        print(f"\n测试2 - 带单引号的关键词: {keyword2}")
        results2 = spider.search(keyword2, page=1, limit=5)
        print(f"搜索结果数量: {len(results2)}")
        
        # 测试3: 带双引号的关键词
        keyword3 = '"四川美食"'
        print(f"\n测试3 - 带双引号的关键词: {keyword3}")
        results3 = spider.search(keyword3, page=1, limit=5)
        print(f"搜索结果数量: {len(results3)}")
        
        # 测试4: 从参数字典中获取关键词
        print("\n测试4 - 从参数字典中获取关键词")
        params = {
            "wd": "'四川美食'"  # 模拟用户输入的带单引号的参数
        }
        keyword4 = params.get('keyword', params.get('wd', 'Python'))
        print(f"从参数字典中获取的关键词: {keyword4}")
        results4 = spider.search(keyword4, page=1, limit=5)
        print(f"搜索结果数量: {len(results4)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_baidu_spider_quoted()
    if success:
        print("\n✅ 百度搜索爬虫带引号关键词测试成功")
    else:
        print("\n❌ 百度搜索爬虫带引号关键词测试失败")
