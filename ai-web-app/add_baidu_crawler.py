#!/usr/bin/env python3
"""
添加百度搜索爬虫源配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import CrawlerConfig
from app import db

# 创建应用实例以初始化数据库连接
app = create_app()

with app.app_context():
    print("添加百度搜索爬虫源配置...")
    
    # 检查是否已存在百度搜索爬虫配置
    existing_config = CrawlerConfig.query.filter_by(source_type='baidu_search').first()
    
    if existing_config:
        print(f"✅ 百度搜索爬虫配置已存在，ID: {existing_config.id}")
        print(f"名称: {existing_config.name}")
        print(f"URL: {existing_config.url}")
        print(f"状态: {'启用' if existing_config.enabled else '禁用'}")
    else:
        # 创建百度搜索爬虫配置
        new_config = CrawlerConfig(
            name='百度搜索',
            url='https://www.baidu.com/s',
            request_method='GET',
            crawl_interval=3600,
            source_type='baidu_search',
            enabled=True,
            headers='{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}',
            request_params='{"wd": "Python", "pn": 0, "ie": "utf-8"}'
        )
        
        db.session.add(new_config)
        db.session.commit()
        
        print(f"✅ 百度搜索爬虫配置创建成功！")
        print(f"ID: {new_config.id}")
        print(f"名称: {new_config.name}")
        print(f"URL: {new_config.url}")
        print(f"源类型: {new_config.source_type}")
        print(f"状态: {'启用' if new_config.enabled else '禁用'}")
    
    # 打印所有爬虫配置
    print("\n所有爬虫配置:")
    print("-" * 60)
    
    all_configs = CrawlerConfig.query.all()
    
    for config in all_configs:
        print(f"ID: {config.id}")
        print(f"名称: {config.name}")
        print(f"URL: {config.url}")
        print(f"源类型: {config.source_type}")
        print(f"状态: {'启用' if config.enabled else '禁用'}")
        print("-" * 60)
