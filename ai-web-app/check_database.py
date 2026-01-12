#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库结构和内容
"""

import sqlite3
import json
import os

# 数据库绝对路径
DB_PATH = r"D:\1_pretraining\day\ai-web-app\instance\app.db"

print("=== 检查数据库结构和内容 ===")
print(f"数据库路径: {DB_PATH}")

# 检查数据库文件是否存在
if not os.path.exists(DB_PATH):
    print("❌ 数据库文件不存在")
    exit(1)

print("✅ 数据库文件存在")

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 检查所有表
print("\n1. 检查所有表...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"找到 {len(tables)} 个表:")

for table in tables:
    print(f"   - {table[0]}")

# 2. 检查crawler_config表
print("\n2. 检查crawler_config表...")
try:
    cursor.execute("SELECT * FROM crawler_config;")
    configs = cursor.fetchall()
    print(f"找到 {len(configs)} 条爬虫配置")
    
    # 打印表头
    cursor.execute("PRAGMA table_info(crawler_config);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"   表结构: {column_names}")
    
    # 打印每条配置
    for config in configs:
        config_dict = dict(zip(column_names, config))
        print(f"\n   配置ID: {config_dict['id']}")
        print(f"   名称: {config_dict['name']}")
        print(f"   URL: {config_dict['url']}")
        print(f"   数据源类型: {config_dict['source_type']}")
        print(f"   启用状态: {'启用' if config_dict['enabled'] else '禁用'}")
        print(f"   请求方法: {config_dict['request_method']}")
        if config_dict['request_params']:
            try:
                params = json.loads(config_dict['request_params'])
                print(f"   请求参数: {params}")
            except:
                print(f"   请求参数: {config_dict['request_params']}")
        if config_dict['headers']:
            try:
                headers = json.loads(config_dict['headers'])
                print(f"   请求头: {headers}")
            except:
                print(f"   请求头: {config_dict['headers']}")
except Exception as e:
    print(f"   表不存在或查询失败: {str(e)}")

# 3. 检查collection_task表
print("\n3. 检查collection_task表...")
try:
    cursor.execute("SELECT * FROM collection_task;")
    tasks = cursor.fetchall()
    print(f"找到 {len(tasks)} 条采集任务")
    
    # 打印表头
    cursor.execute("PRAGMA table_info(collection_task);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # 打印前5条任务
    for i, task in enumerate(tasks[:5]):
        task_dict = dict(zip(column_names, task))
        print(f"\n   任务ID: {task_dict['id']}")
        print(f"   名称: {task_dict['name']}")
        print(f"   URL: {task_dict['urls']}")
        print(f"   状态: {task_dict['status']}")
        print(f"   已采集: {task_dict['total_collected']} 条")
        if task_dict['error_message']:
            print(f"   错误信息: {task_dict['error_message']}")
    
    if len(tasks) > 5:
        print(f"\n   ... 还有 {len(tasks) - 5} 条任务未显示")
except Exception as e:
    print(f"   表不存在或查询失败: {str(e)}")

# 4. 检查collected_data表
print("\n4. 检查collected_data表...")
try:
    cursor.execute("SELECT COUNT(*) FROM collected_data;")
    count = cursor.fetchone()[0]
    print(f"找到 {count} 条采集数据")
    
    if count > 0:
        # 打印前3条数据
        cursor.execute("SELECT id, title, url, status FROM collected_data LIMIT 3;")
        data = cursor.fetchall()
        print("\n   前3条数据:")
        for item in data:
            print(f"   - ID: {item[0]}, 标题: {item[1]}, URL: {item[2]}, 状态: {item[3]}")
except Exception as e:
    print(f"   表不存在或查询失败: {str(e)}")

# 关闭连接
conn.close()

print("\n=== 检查完成 ===")
