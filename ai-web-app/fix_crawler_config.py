#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改爬虫配置的source_type为baidu_search
"""

import sqlite3
import os

# 数据库绝对路径
DB_PATH = r"D:\1_pretraining\day\ai-web-app\instance\app.db"

print("=== 修改爬虫配置 ===")
print(f"数据库路径: {DB_PATH}")

# 检查数据库文件是否存在
if not os.path.exists(DB_PATH):
    print("❌ 数据库文件不存在")
    exit(1)

print("✅ 数据库文件存在")

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 修改爬虫配置的source_type为baidu_search
print("\n1. 修改爬虫配置...")
try:
    # 修改配置ID为1的百度搜索配置
    cursor.execute("UPDATE crawler_config SET source_type='baidu_search' WHERE id=1;")
    # 修改配置ID为2的百度搜索-四川美食配置
    cursor.execute("UPDATE crawler_config SET source_type='baidu_search' WHERE id=2;")
    # 启用配置ID为1的百度搜索配置
    cursor.execute("UPDATE crawler_config SET enabled=1 WHERE id=1;")
    # 修改配置ID为2的URL为正确的百度搜索地址
    cursor.execute("UPDATE crawler_config SET url='https://www.baidu.com/s' WHERE id=2;")
    
    # 提交修改
    conn.commit()
    print("✅ 成功修改爬虫配置")
    print("   - 配置ID 1: source_type 改为 baidu_search，状态改为 启用")
    print("   - 配置ID 2: source_type 改为 baidu_search，URL 改为 https://www.baidu.com/s")
except Exception as e:
    print(f"❌ 修改失败: {str(e)}")
    conn.rollback()

# 验证修改结果
print("\n2. 验证修改结果...")
try:
    cursor.execute("SELECT id, name, source_type, enabled, url FROM crawler_config;")
    configs = cursor.fetchall()
    print(f"找到 {len(configs)} 条爬虫配置")
    
    for config in configs:
        print(f"   - ID: {config[0]}, 名称: {config[1]}, 类型: {config[2]}, 状态: {'启用' if config[3] else '禁用'}, URL: {config[4]}")
except Exception as e:
    print(f"❌ 验证失败: {str(e)}")

# 关闭连接
conn.close()

print("\n=== 修改完成 ===")
