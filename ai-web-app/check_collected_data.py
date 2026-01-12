#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查数据库中的采集数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models import db, CollectionTask, CollectedData
from app import create_app


def check_collected_data():
    """检查数据库中的采集数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 检查数据库中的采集数据 ===")
        
        # 查询所有采集任务
        all_tasks = CollectionTask.query.all()
        print(f"数据库中共有 {len(all_tasks)} 个采集任务")
        
        if not all_tasks:
            print("数据库中没有采集任务")
        else:
            print("\n采集任务列表：")
            for task in all_tasks:
                print(f"\n任务ID: {task.id}")
                print(f"任务名称: {task.name}")
                print(f"URLs: {task.urls}")
                print(f"状态: {task.status}")
                print(f"创建时间: {task.created_at}")
                print(f"最后运行时间: {task.last_run_time}")
                print(f"最后完成时间: {task.last_finish_time}")
                print(f"采集总数: {task.total_collected}")
                print(f"错误信息: {task.error_message}")
        
        # 查询所有采集数据
        all_collected_data = CollectedData.query.all()
        print(f"\n=== 采集数据统计 ===")
        print(f"数据库中共有 {len(all_collected_data)} 条采集数据")
        
        if not all_collected_data:
            print("数据库中没有采集数据")
        else:
            print("\n最近10条采集数据：")
            # 按时间倒序排序，显示最近10条
            recent_data = CollectedData.query.order_by(CollectedData.timestamp.desc()).limit(10).all()
            
            for data in recent_data:
                print(f"\n数据ID: {data.id}")
                print(f"任务ID: {data.task_id}")
                print(f"标题: {data.title}")
                print(f"URL: {data.url}")
                print(f"内容: {data.content[:100]}...")  # 只显示前100个字符
                print(f"来源: {data.source}")
                print(f"状态: {data.status}")
                print(f"时间戳: {data.timestamp}")
        
        # 检查是否有"四川美食"相关的采集数据
        print(f"\n=== 检查'四川美食'相关采集数据 ===")
        sichuan_data = CollectedData.query.filter(
            (CollectedData.title.contains('四川美食')) | 
            (CollectedData.content.contains('四川美食'))
        ).all()
        
        print(f"数据库中共有 {len(sichuan_data)} 条'四川美食'相关的采集数据")
        
        if sichuan_data:
            print("\n'四川美食'相关采集数据：")
            for data in sichuan_data:
                print(f"\n数据ID: {data.id}")
                print(f"任务ID: {data.task_id}")
                print(f"标题: {data.title}")
                print(f"URL: {data.url}")
                print(f"时间戳: {data.timestamp}")
        
        return len(all_collected_data) > 0


def check_task_data(task_id):
    """检查指定任务的采集数据"""
    app = create_app()
    
    with app.app_context():
        print(f"\n=== 检查任务 {task_id} 的采集数据 ===")
        
        # 查询指定任务
        task = CollectionTask.query.get(task_id)
        if not task:
            print(f"任务 {task_id} 不存在")
            return False
        
        print(f"任务名称: {task.name}")
        print(f"任务状态: {task.status}")
        print(f"采集总数: {task.total_collected}")
        
        # 查询该任务的采集数据
        task_data = CollectedData.query.filter_by(task_id=task_id).all()
        print(f"该任务共有 {len(task_data)} 条采集数据")
        
        if task_data:
            print("\n采集数据列表：")
            for data in task_data:
                print(f"\n数据ID: {data.id}")
                print(f"标题: {data.title}")
                print(f"URL: {data.url}")
                print(f"内容: {data.content[:50]}...")
                print(f"时间戳: {data.timestamp}")
        
        return len(task_data) > 0


if __name__ == "__main__":
    # 检查所有采集数据
    has_data = check_collected_data()
    
    # 如果有任务ID作为参数，检查指定任务
    if len(sys.argv) > 1:
        try:
            task_id = int(sys.argv[1])
            check_task_data(task_id)
        except ValueError:
            print("无效的任务ID")
