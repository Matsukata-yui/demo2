#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫数据持久化功能
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
    
    print("=== 开始测试爬虫数据持久化功能 ===")
    
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
    
    # 4. 检查已采集数据
    print("\n4. 检查已采集数据...")
    collected_data_count = CollectedData.query.count()
    print(f"已采集数据总数: {collected_data_count}")
    
    # 5. 创建持久化测试任务并运行
    print("\n5. 创建持久化测试任务并运行...")
    try:
        # 创建测试任务
        test_task = CollectionTask(
            name="持久化测试任务 - Python 爬虫",
            urls="baidu_search:Python 爬虫:1:5",
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
            
            # 打印前3条采集数据
            if collected_data_after_run > 0:
                print("   \n前3条采集数据:")
                collected_data_items = CollectedData.query.filter_by(task_id=test_task.id).limit(3).all()
                for i, item in enumerate(collected_data_items, 1):
                    print(f"   数据 {i}:")
                    print(f"   - 标题: {item.title}")
                    print(f"   - URL: {item.url}")
                    print(f"   - 内容: {item.content[:100]}...")
        else:
            print(f"   错误信息: {run_result.get('error', '未知错误')}")
            
            # 检查任务错误信息
            task_after_run = CollectionTask.query.get(test_task.id)
            if task_after_run and task_after_run.error_message:
                print(f"   任务错误信息: {task_after_run.error_message}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    
    # 6. 再次检查已采集数据总数
    print("\n6. 再次检查已采集数据总数...")
    final_collected_data_count = CollectedData.query.count()
    print(f"已采集数据总数: {final_collected_data_count}")
    
    if final_collected_data_count > collected_data_count:
        print(f"✅ 数据持久化成功！新增了 {final_collected_data_count - collected_data_count} 条数据")
    else:
        print("❌ 数据持久化失败，没有新增数据")

print("\n=== 测试完成 ===")
print("注意：此测试任务不会被自动清理，您可以在爬虫管理界面中查看和管理此任务。")
