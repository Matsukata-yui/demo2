#!/usr/bin/env python3
"""
修复采集任务
验证并修复任务状态和数据采集问题
"""

import sys
import os
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import CollectionTask, CollectedData
from app import db
from app.services.crawler_service import crawler_service

# 打印测试信息
print("修复采集任务...")
print("-" * 60)

# 启动测试服务器
app = create_app()

# 直接在应用上下文中测试
with app.app_context():
    # 1. 检查所有采集任务
    print("\n1. 检查所有采集任务:")
    tasks = CollectionTask.query.all()
    
    if tasks:
        for task in tasks:
            print(f"\n任务ID: {task.id}")
            print(f"任务名称: {task.name}")
            print(f"任务URLs: {task.urls}")
            print(f"任务状态: {task.status}")
            print(f"已采集数量: {task.total_collected}")
            print(f"创建时间: {task.created_at}")
            print(f"最后运行时间: {task.last_run_time}")
            print(f"最后完成时间: {task.last_finish_time}")
            if task.error_message:
                print(f"错误信息: {task.error_message}")
    else:
        print("❌ 没有找到采集任务")
    
    # 2. 检查最新的任务
    print("\n2. 检查最新的任务:")
    latest_task = CollectionTask.query.order_by(CollectionTask.id.desc()).first()
    
    if latest_task:
        print(f"最新任务ID: {latest_task.id}")
        print(f"任务状态: {latest_task.status}")
        print(f"任务URLs: {latest_task.urls}")
        
        # 尝试修复任务
        print("\n3. 尝试修复任务...")
        
        # 检查任务URLs格式
        try:
            # 尝试解析JSON格式的URLs
            urls_data = json.loads(latest_task.urls)
            print(f"URLs是JSON格式: {urls_data}")
            
            # 提取关键词和爬虫源
            keyword = urls_data.get('keyword', '人工智能')
            crawlers = urls_data.get('crawlers', ['baidu_search'])
            
            print(f"提取的关键词: {keyword}")
            print(f"提取的爬虫源: {crawlers}")
            
            # 构建正确的任务URL格式
            if 'baidu_search' in crawlers:
                task_url = f"baidu_search:{keyword}:1:5"
                print(f"构建的任务URL: {task_url}")
                
                # 更新任务URLs
                latest_task.urls = task_url
                db.session.commit()
                print("✅ 任务URLs已更新")
                
                # 执行爬虫任务
                print("\n4. 执行爬虫任务...")
                result = crawler_service.run_crawler(latest_task.id)
                print(f"爬虫执行结果: {result}")
                
                # 检查任务状态
                updated_task = CollectionTask.query.get(latest_task.id)
                print(f"\n更新后的任务状态: {updated_task.status}")
                print(f"更新后的已采集数量: {updated_task.total_collected}")
                
                # 检查采集数据
                collected_items = CollectedData.query.filter_by(task_id=latest_task.id).all()
                print(f"\n找到 {len(collected_items)} 条采集数据")
                
                if collected_items:
                    for i, item in enumerate(collected_items, 1):
                        print(f"\n数据 {i}:")
                        print(f"ID: {item.id}")
                        print(f"标题: {item.title}")
                        print(f"URL: {item.url}")
                else:
                    print("❌ 仍然没有找到采集数据！")
            
        except json.JSONDecodeError:
            # URLs不是JSON格式，可能已经是正确的格式
            print("URLs不是JSON格式，可能已经是正确的格式")
            
            # 直接执行爬虫任务
            print("\n4. 执行爬虫任务...")
            result = crawler_service.run_crawler(latest_task.id)
            print(f"爬虫执行结果: {result}")
            
            # 检查任务状态
            updated_task = CollectionTask.query.get(latest_task.id)
            print(f"\n更新后的任务状态: {updated_task.status}")
            print(f"更新后的已采集数量: {updated_task.total_collected}")
            
            # 检查采集数据
            collected_items = CollectedData.query.filter_by(task_id=latest_task.id).all()
            print(f"\n找到 {len(collected_items)} 条采集数据")
            
            if collected_items:
                for i, item in enumerate(collected_items, 1):
                    print(f"\n数据 {i}:")
                    print(f"ID: {item.id}")
                    print(f"标题: {item.title}")
                    print(f"URL: {item.url}")
            else:
                print("❌ 仍然没有找到采集数据！")
    else:
        print("❌ 没有找到采集任务")

print("\n修复完成！")
