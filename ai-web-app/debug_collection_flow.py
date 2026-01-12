#!/usr/bin/env python3
"""
详细调试采集流程
验证从数据库连接到数据保存的完整过程
"""

import sys
import os
import time
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import CollectionTask, CollectedData
from app import db
from app.services.crawler_service import crawler_service
from app.config import Config

# 打印数据库配置信息
print("数据库配置信息:")
print(f"SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"Instance目录: {Config.instance_dir}")
print(f"Instance目录是否存在: {os.path.exists(Config.instance_dir)}")
print(f"数据库文件是否存在: {os.path.exists(os.path.join(Config.instance_dir, 'app.db'))}")

# 直接使用sqlite3检查数据库连接
print("\n直接检查数据库连接:")
try:
    db_path = os.path.join(Config.instance_dir, 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查collected_data表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collected_data';")
    table_exists = cursor.fetchone() is not None
    print(f"collected_data表是否存在: {table_exists}")
    
    # 检查当前数据行数
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM collected_data;")
        count = cursor.fetchone()[0]
        print(f"collected_data表当前数据行数: {count}")
    
    conn.close()
except Exception as e:
    print(f"直接检查数据库失败: {e}")

# 创建应用实例以初始化数据库连接
app = create_app()

with app.app_context():
    print("\n详细调试采集流程...")
    
    # 1. 检查数据库连接
    print("\n1. 检查数据库连接...")
    try:
        # 测试数据库会话
        db.session.execute(db.text("SELECT 1"))
        print("✅ 数据库会话连接正常")
    except Exception as e:
        print(f"❌ 数据库会话连接失败: {e}")
    
    # 2. 清理旧的测试数据
    print("\n2. 清理旧的测试数据...")
    try:
        # 清理测试任务
        old_tasks = CollectionTask.query.filter(CollectionTask.name.like("测试任务%"))
        old_task_count = old_tasks.count()
        if old_task_count > 0:
            for task in old_tasks:
                db.session.delete(task)
            db.session.commit()
            print(f"✅ 清理了 {old_task_count} 个旧测试任务")
        else:
            print("✅ 没有找到旧测试任务")
        
        # 检查当前数据行数
        current_count = CollectedData.query.count()
        print(f"✅ 当前collected_data表数据行数: {current_count}")
    except Exception as e:
        print(f"❌ 清理旧数据失败: {e}")
    
    # 3. 创建一个测试采集任务
    print("\n3. 创建测试采集任务...")
    try:
        # 创建新的测试任务
        test_task = CollectionTask(
            name="测试任务-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            urls="",  # 暂时为空，后续会更新
            created_by="test_user",
            status="running"
        )
        
        db.session.add(test_task)
        db.session.commit()
        
        print(f"✅ 测试任务创建成功！任务ID: {test_task.id}")
        print(f"任务状态: {test_task.status}")
        print(f"任务URLs: {test_task.urls}")
    except Exception as e:
        print(f"❌ 创建测试任务失败: {e}")
        sys.exit(1)
    
    # 4. 更新任务URL并执行采集
    print("\n4. 更新任务URL并执行采集...")
    try:
        # 更新任务URL
        keyword = "人工智能"
        task_url = f"baidu_search:{keyword}:1:5"
        test_task.urls = task_url
        db.session.commit()
        
        print(f"✅ 任务URL更新成功: {task_url}")
        
        # 执行采集
        print("开始执行爬虫任务...")
        start_time = time.time()
        result = crawler_service.run_crawler(test_task.id)
        end_time = time.time()
        
        print(f"爬虫执行结果: {result}")
        print(f"爬虫执行时间: {end_time - start_time:.2f} 秒")
    except Exception as e:
        print(f"❌ 执行采集失败: {e}")
    
    # 5. 检查任务状态和数据
    print("\n5. 检查任务状态和数据...")
    try:
        # 重新获取任务
        updated_task = CollectionTask.query.get(test_task.id)
        print(f"任务状态: {updated_task.status}")
        print(f"已采集数量: {updated_task.total_collected}")
        print(f"最后运行时间: {updated_task.last_run_time}")
        print(f"最后完成时间: {updated_task.last_finish_time}")
        if updated_task.error_message:
            print(f"错误信息: {updated_task.error_message}")
        
        # 检查采集数据
        collected_items = CollectedData.query.filter_by(task_id=test_task.id).all()
        print(f"\n找到 {len(collected_items)} 条采集数据")
        
        if collected_items:
            print("采集数据详情:")
            for i, item in enumerate(collected_items, 1):
                print(f"\n数据 {i}:")
                print(f"ID: {item.id}")
                print(f"标题: {item.title}")
                print(f"URL: {item.url}")
                print(f"内容: {item.content[:50]}...")
                print(f"状态: {item.status}")
                print(f"采集时间: {item.timestamp}")
        else:
            print("❌ 没有找到采集数据！")
        
        # 再次检查数据库中的实际数据
        print("\n直接从数据库检查数据:")
        db_path = os.path.join(Config.instance_dir, 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查任务表
        cursor.execute("SELECT id, name, status, total_collected FROM collection_task WHERE id = ?;", (test_task.id,))
        task_data = cursor.fetchone()
        if task_data:
            print(f"任务表数据: ID={task_data[0]}, 名称={task_data[1]}, 状态={task_data[2]}, 采集数量={task_data[3]}")
        else:
            print("❌ 任务表中未找到该任务")
        
        # 检查采集数据表
        cursor.execute("SELECT COUNT(*) FROM collected_data WHERE task_id = ?;", (test_task.id,))
        count = cursor.fetchone()[0]
        print(f"采集数据表中数据行数: {count}")
        
        # 如果有数据，打印前几条
        if count > 0:
            cursor.execute("SELECT id, title, url FROM collected_data WHERE task_id = ? LIMIT 3;", (test_task.id,))
            rows = cursor.fetchall()
            print("采集数据表前3条数据:")
            for row in rows:
                print(f"ID={row[0]}, 标题={row[1]}, URL={row[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查任务状态和数据失败: {e}")
    
    # 6. 检查整个数据库的统计信息
    print("\n6. 数据库统计信息:")
    try:
        db_path = os.path.join(Config.instance_dir, 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"- {table[0]}")
            # 检查每个表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"  行数: {count}")
        
        conn.close()
    except Exception as e:
        print(f"❌ 检查数据库统计信息失败: {e}")

print("\n调试完成！")
