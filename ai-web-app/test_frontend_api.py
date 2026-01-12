#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端API调用
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000"

# 测试获取爬虫源配置
def test_get_crawler_configs():
    print("测试获取爬虫源配置...")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/crawler/config"
    response = requests.get(url)
    
    print(f"请求URL: {url}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            configs = data.get('configs', [])
            enabled_configs = [config for config in configs if config.get('enabled')]
            print(f"总共有 {len(configs)} 个爬虫源配置")
            print(f"启用的配置: {len(enabled_configs)}")
            print()
            print("启用的配置详情:")
            for config in enabled_configs:
                print(f"ID: {config.get('id')}")
                print(f"名称: {config.get('name')}")
                print(f"URL: {config.get('url')}")
                print(f"数据源类型: {config.get('source_type')}")
                print(f"请求参数: {config.get('request_params')}")
                print(f"请求头: {config.get('headers')}")
                print("-" * 60)
            return True
        else:
            print(f"获取爬虫源配置失败: {data.get('error')}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 测试开始采集
def test_start_collection():
    print("测试开始采集...")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/collection/start"
    data = {
        "keyword": "人工智能",
        "crawlers": ["baidu_search"],
        "page": 1,
        "limit": 5
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            task_id = data.get('task_id')
            print(f"采集任务创建成功！任务ID: {task_id}")
            return task_id
        else:
            print(f"创建采集任务失败: {data.get('error')}")
            return None
    else:
        print(f"请求失败: {response.status_code}")
        return None

# 测试获取采集结果
def test_get_collection_results(task_id):
    if not task_id:
        return
    
    print(f"测试获取采集结果 (任务ID: {task_id})...")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/collection/results/{task_id}"
    response = requests.get(url)
    
    print(f"请求URL: {url}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            results = data.get('results', [])
            status = data.get('status')
            total_collected = data.get('total_collected', 0)
            print(f"任务状态: {status}")
            print(f"已采集数量: {total_collected}")
            print()
            if results:
                print("采集结果:")
                for i, result in enumerate(results, 1):
                    print(f"结果 {i}:")
                    print(f"标题: {result.get('title')}")
                    print(f"URL: {result.get('url')}")
                    print(f"来源: {result.get('source')}")
                    print(f"时间: {result.get('timestamp')}")
                    print("-" * 60)
            else:
                print("暂无采集结果")
        else:
            print(f"获取采集结果失败: {data.get('error')}")
    else:
        print(f"请求失败: {response.status_code}")

if __name__ == "__main__":
    print("开始测试前端API调用...")
    print()
    
    # 测试获取爬虫源配置
    test_get_crawler_configs()
    print()
    
    # 测试开始采集
    task_id = test_start_collection()
    print()
    
    # 等待一段时间，让采集任务执行
    if task_id:
        import time
        print("等待采集任务执行...")
        time.sleep(10)
        print()
        
        # 测试获取采集结果
        test_get_collection_results(task_id)
    
    print("测试完成！")
