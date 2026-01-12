#!/usr/bin/env python3
"""
测试前端和后端的交互
模拟前端发送请求到后端的过程
"""

import sys
import os
import json
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import CollectionTask, CollectedData
from app import db

# 打印测试信息
print("测试前端和后端交互...")
print("-" * 60)

# 启动测试服务器
app = create_app()

# 测试用户登录
print("\n1. 测试用户登录...")

# 直接在应用上下文中测试API
with app.app_context():
    # 2. 测试创建采集任务
    print("\n2. 测试创建采集任务...")
    
    # 模拟前端发送的请求数据
    test_data = {
        "keyword": "人工智能",
        "crawlers": ["baidu_search"]  # 假设前端传递的是这个值
    }
    
    print(f"模拟前端请求数据: {test_data}")
    
    # 导入后端API函数
    from app.routes.main_routes import start_keyword_collection
    
    # 创建模拟请求对象
    from flask import Request
    from werkzeug.test import EnvironBuilder
    
    # 创建环境构建器
    builder = EnvironBuilder(
        path='/api/collection/start',
        method='POST',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 创建环境
    env = builder.get_environ()
    
    # 创建请求对象
    req = Request(env)
    
    # 设置当前用户
    from flask_login import login_user
    from app.models import User
    
    # 获取测试用户
    user = User.query.first()
    if user:
        login_user(user)
        print(f"✅ 登录用户: {user.username}")
    else:
        print("❌ 没有找到用户")
    
    # 调用API函数
    print("\n3. 调用start_keyword_collection API...")
    try:
        # 保存原始请求
        original_request = getattr(sys, '_getframe').f_globals.get('request')
        
        # 设置全局请求对象
        setattr(sys, '_getframe', lambda: type('obj', (object,), {'f_globals': {'request': req}})())
        
        # 导入request
        from flask import request
        
        # 模拟request对象
        import builtins
        original_getattr = builtins.getattr
        
        def mock_getattr(obj, name):
            if name == 'get_json' and hasattr(obj, 'data'):
                return lambda: test_data
            return original_getattr(obj, name)
        
        builtins.getattr = mock_getattr
        
        # 直接调用函数
        result = start_keyword_collection()
        print(f"API返回结果: {result.get_data(as_text=True)}")
        
        # 恢复原始函数
        builtins.getattr = original_getattr
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
    
    # 4. 检查任务创建和执行
    print("\n4. 检查任务创建和执行...")
    
    # 获取最新的任务
    latest_task = CollectionTask.query.order_by(CollectionTask.id.desc()).first()
    if latest_task:
        print(f"最新任务ID: {latest_task.id}")
        print(f"任务名称: {latest_task.name}")
        print(f"任务URLs: {latest_task.urls}")
        print(f"任务状态: {latest_task.status}")
        
        # 检查任务是否有对应的采集数据
        collected_items = CollectedData.query.filter_by(task_id=latest_task.id).all()
        print(f"\n找到 {len(collected_items)} 条采集数据")
        
        if collected_items:
            for i, item in enumerate(collected_items, 1):
                print(f"\n数据 {i}:")
                print(f"ID: {item.id}")
                print(f"标题: {item.title}")
                print(f"URL: {item.url}")
        else:
            print("❌ 没有找到采集数据！")
    else:
        print("❌ 没有找到任务")

print("\n测试完成！")
