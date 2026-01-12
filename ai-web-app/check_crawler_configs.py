#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查爬虫源配置
"""

from app import create_app, db
from app.models import CrawlerConfig

# 创建应用实例
app = create_app()

with app.app_context():
    print("检查爬虫源配置...")
    print("=" * 60)
    
    # 获取所有爬虫源配置
    all_configs = CrawlerConfig.query.all()
    print(f"总共有 {len(all_configs)} 个爬虫源配置")
    print()
    
    # 按启用状态分组
    enabled_configs = [config for config in all_configs if config.enabled]
    disabled_configs = [config for config in all_configs if not config.enabled]
    
    print(f"启用的配置: {len(enabled_configs)}")
    print(f"禁用的配置: {len(disabled_configs)}")
    print()
    
    # 详细显示每个配置
    print("所有配置详情:")
    print("-" * 60)
    
    for config in all_configs:
        print(f"ID: {config.id}")
        print(f"名称: {config.name}")
        print(f"URL: {config.url}")
        print(f"数据源类型: {config.source_type}")
        print(f"启用状态: {'✓ 启用' if config.enabled else '✗ 禁用'}")
        print(f"请求参数: {config.request_params}")
        print(f"请求头: {config.headers}")
        print("-" * 60)
    
    # 检查是否有baidu_search类型的配置
    baidu_configs = [config for config in all_configs if config.source_type == 'baidu_search']
    print(f"\n百度搜索类型的配置: {len(baidu_configs)}")
    
    if baidu_configs:
        print("百度搜索配置详情:")
        for config in baidu_configs:
            print(f"ID: {config.id}, 名称: {config.name}, 启用: {config.enabled}")
    else:
        print("警告: 没有找到百度搜索类型的配置！")
    
    print("\n检查完成！")
