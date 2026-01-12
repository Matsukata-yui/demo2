#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫数据采集功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入Flask应用
from app import create_app
app = create_app()

with app.app_context():
    # 导入相关模块
    from app.models import db, CollectionTask, CollectedData, CrawlerConfig
    from app.services.crawler_service import crawler_service
    from app.services.crawler_source_manager import crawler_source_manager
    
    print("=== 开始测试爬虫数据采集功能 ===")
    
    # 1. 检查数据库连接
    print("\n1. 检查数据库连接...")
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        sys.exit(1)
    
    # 2. 检查爬虫配置
    print("\n2. 检查爬虫配置...")
    crawler_configs = CrawlerConfig.query.all()
    print(f"找到 {len(crawler_configs)} 个爬虫配置")
    
    for config in crawler_configs:
        print(f"   - {config.name} (类型: {config.source_type}, 状态: {'启用' if config.enabled else '禁用'})")
    
    # 3. 检查现有任务
    print("\n3. 检查现有任务...")
    tasks = CollectionTask.query.all()
    print(f"找到 {len(tasks)} 个采集任务")
    
    for task in tasks:
        print(f"   - {task.name} (状态: {task.status}, 已采集: {task.total_collected} 条)")
    
    # 4. 检查已采集数据
    print("\n4. 检查已采集数据...")
    collected_data_count = CollectedData.query.count()
    print(f"已采集数据总数: {collected_data_count}")
    
    # 5. 测试爬虫源管理器
    print("\n5. 测试爬虫源管理器...")
    try:
        result = crawler_source_manager.run_crawler_by_source("baidu_search", {
            "keyword": "Python 爬虫",
            "page": 1,
            "limit": 3
        })
        
        print(f"   爬虫源管理器运行结果: {'成功' if result.get('success') else '失败'}")
        
        if result.get('success'):
            print(f"   返回结果数量: {len(result.get('results', []))}")
        else:
            print(f"   错误信息: {result.get('error_message', '未知错误')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    # 6. 创建测试任务并运行
    print("\n6. 创建测试任务并运行...")
    try:
        # 创建测试任务
        test_task = CollectionTask(
            name="测试任务 - Python 爬虫",
            urls="baidu_search:Python 爬虫:1:3",
            interval=3600,
            created_by="admin"
        )
        db.session.add(test_task)
        db.session.commit()
        
        print(f"   创建测试任务成功，ID: {test_task.id}")
        
        # 运行爬虫任务
        run_result = crawler_service.run_crawler(test_task.id)
        print(f"   爬虫任务运行结果: {'成功' if run_result.get('success') else '失败'}")
        
        if run_result.get('success'):
            print(f"   采集数据数量: {run_result.get('data_count', 0)}")
            
            # 检查数据是否已保存
            task_after_run = CollectionTask.query.get(test_task.id)
            print(f"   任务状态: {task_after_run.status}")
            print(f"   任务已采集数据: {task_after_run.total_collected} 条")
            
            # 检查CollectedData表
            collected_data_after_run = CollectedData.query.filter_by(task_id=test_task.id).count()
            print(f"   CollectedData表中数据: {collected_data_after_run} 条")
        else:
            print(f"   错误信息: {run_result.get('error', '未知错误')}")
            
            # 检查任务错误信息
            task_after_run = CollectionTask.query.get(test_task.id)
            if task_after_run and task_after_run.error_message:
                print(f"   任务错误信息: {task_after_run.error_message}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    finally:
        # 清理测试任务
        try:
            test_task = CollectionTask.query.filter_by(name="测试任务 - Python 爬虫").first()
            if test_task:
                db.session.delete(test_task)
                db.session.commit()
                print("\n   清理测试任务成功")
        except Exception as e:
            print(f"\n   清理测试任务失败: {str(e)}")

print("\n=== 测试完成 ===")
