#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的采集流程
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models import db, CollectionTask, CollectedData
from app import create_app
from app.services.crawler_service import crawler_service

def test_full_collection():
    """测试完整的采集流程"""
    print("=== 测试完整的采集流程 ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 创建采集任务
            keyword = "四川美食"
            crawlers = ["baidu_search"]
            
            print(f"测试关键词: {keyword}")
            print(f"选择的爬虫源: {crawlers}")
            
            # 创建任务
            new_task = CollectionTask(
                name=f'关键词采集: {keyword}',
                urls=f"baidu_search:{keyword}:1:5",
                interval=0,
                status='running',
                created_by='test'
            )
            db.session.add(new_task)
            db.session.commit()
            
            task_id = new_task.id
            print(f"\n✅ 采集任务创建成功，任务ID: {task_id}")
            
            # 2. 执行采集
            print("\n开始执行采集任务...")
            result = crawler_service.run_crawler(task_id)
            print(f"采集任务执行结果: {result}")
            
            # 3. 检查任务状态
            task = CollectionTask.query.get(task_id)
            print(f"\n任务状态: {task.status}")
            print(f"采集总数: {task.total_collected}")
            
            # 4. 检查采集数据
            collected_data = CollectedData.query.filter_by(task_id=task_id).all()
            print(f"\n采集到的数据数量: {len(collected_data)}")
            
            if collected_data:
                print("\n采集数据详情:")
                for i, data in enumerate(collected_data):
                    print(f"\n数据 {i+1}:")
                    print(f"标题: {data.title}")
                    print(f"URL: {data.url}")
                    print(f"内容: {data.content[:100]}...")
                return True
            else:
                print("\n❌ 未采集到任何数据")
                return False
                
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_full_collection()
    if success:
        print("\n✅ 完整采集流程测试成功")
    else:
        print("\n❌ 完整采集流程测试失败")
