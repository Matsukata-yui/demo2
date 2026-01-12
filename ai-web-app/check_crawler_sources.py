#!/usr/bin/env python3
"""
检查爬虫源配置和前端传递的值
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import CrawlerConfig
from app import db

# 打印测试信息
print("检查爬虫源配置和前端传递的值...")
print("-" * 60)

# 启动测试服务器
app = create_app()

# 直接在应用上下文中测试
with app.app_context():
    # 获取所有爬虫源配置
    print("\n1. 数据库中的爬虫源配置:")
    crawler_configs = CrawlerConfig.query.all()
    
    if crawler_configs:
        for config in crawler_configs:
            print(f"\nID: {config.id}")
            print(f"名称: {config.name}")
            print(f"URL: {config.url}")
            print(f"源类型: {config.source_type}")
            print(f"是否启用: {config.enabled}")
    else:
        print("❌ 没有找到爬虫源配置")
    
    # 2. 检查前端代码中使用的爬虫源值
    print("\n2. 前端代码中使用的爬虫源值:")
    print("根据前端代码分析，前端使用 config.source_type 作为爬虫源的值")
    print("然后在 startCollection 函数中获取选中的爬虫源并传递给后端")
    
    # 3. 检查后端代码如何处理
    print("\n3. 后端代码如何处理:")
    print("在 run_keyword_collection 函数中，后端只检查了 crawler == 'baidu_search'")
    print("如果前端传递的不是这个值，后端不会执行采集")
    
    # 4. 检查前端可能传递的值
    print("\n4. 前端可能传递的值:")
    print("根据数据库中的爬虫源配置，前端可能传递的值是:")
    for config in crawler_configs:
        print(f"- {config.source_type} (来自爬虫源: {config.name})")
    
    # 5. 解决方案
    print("\n5. 解决方案:")
    print("修改 run_keyword_collection 函数，使其能够处理前端传递的所有可能的爬虫源值")
    print("并确保使用正确的爬虫服务来执行采集")

print("\n检查完成！")
