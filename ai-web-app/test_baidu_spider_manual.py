#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手动测试百度搜索爬虫
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dist.baidusearch.baidu_spider import BaiduSearchSpider
from app.services.crawler_source_manager import crawler_source_manager
from app.services.crawler_service import crawler_service
from app.models import db, CollectionTask, CollectedData
from app import create_app


def test_baidu_spider_directly():
    """直接测试百度搜索爬虫"""
    print("=== 直接测试百度搜索爬虫 ===")
    
    spider = BaiduSearchSpider()
    
    # 测试"四川美食"关键词
    keyword = "四川美食"
    print(f"测试关键词: {keyword}")
    
    # 测试search方法
    results = spider.search(keyword, page=1, limit=5)
    print(f"search方法返回结果数: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"\n结果 {i+1}:")
        print(f"标题: {result.get('title', '无')}")
        print(f"URL: {result.get('url', '无')}")
        print(f"摘要: {result.get('abstract', '无')}")
    
    # 测试run方法
    print("\n=== 测试run方法 ===")
    params = {
        "keyword": keyword,
        "page": 1,
        "limit": 5
    }
    run_results = spider.run(params)
    print(f"run方法返回结果数: {len(run_results)}")
    
    return len(results) > 0


def test_crawler_source_manager():
    """测试爬虫源管理器"""
    print("\n=== 测试爬虫源管理器 ===")
    
    keyword = "四川美食"
    params = {
        "keyword": keyword,
        "page": 1,
        "limit": 5
    }
    
    result = crawler_source_manager.run_crawler_by_source("baidu_search", params)
    print(f"爬虫源管理器返回结果: {result.get('success')}")
    print(f"错误信息: {result.get('error_message', '无')}")
    
    if result.get('success'):
        results = result.get('results', [])
        print(f"返回结果数: {len(results)}")
        for i, item in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"标题: {item.get('title', '无')}")
            print(f"URL: {item.get('url', '无')}")
            print(f"摘要: {item.get('abstract', '无')}")
    
    return result.get('success', False)


def test_full_crawler_process():
    """测试完整的爬虫流程"""
    print("\n=== 测试完整的爬虫流程 ===")
    
    app = create_app()
    
    with app.app_context():
        # 创建测试任务
        keyword = "四川美食"
        task_url = f"baidu_search:{keyword}:1:5"
        
        new_task = CollectionTask(
            name=f"测试任务: {keyword}",
            urls=task_url,
            interval=0,
            status='running',
            created_by='test'
        )
        db.session.add(new_task)
        db.session.commit()
        
        task_id = new_task.id
        print(f"创建测试任务ID: {task_id}")
        
        # 运行爬虫
        result = crawler_service.run_crawler(task_id)
        print(f"爬虫运行结果: {result}")
        
        # 检查数据库
        collected_data = CollectedData.query.filter_by(task_id=task_id).all()
        print(f"数据库中采集到的数据数: {len(collected_data)}")
        
        for i, item in enumerate(collected_data):
            print(f"\n数据库中的数据 {i+1}:")
            print(f"标题: {item.title}")
            print(f"URL: {item.url}")
            print(f"内容: {item.content[:100]}...")
        
        return len(collected_data) > 0


if __name__ == "__main__":
    print("开始测试百度搜索爬虫...")
    
    # 测试直接调用百度爬虫
    spider_success = test_baidu_spider_directly()
    print(f"\n百度爬虫测试结果: {'成功' if spider_success else '失败'}")
    
    # 测试爬虫源管理器
    manager_success = test_crawler_source_manager()
    print(f"\n爬虫源管理器测试结果: {'成功' if manager_success else '失败'}")
    
    # 测试完整流程
    full_success = test_full_crawler_process()
    print(f"\n完整流程测试结果: {'成功' if full_success else '失败'}")
    
    print("\n测试完成！")
