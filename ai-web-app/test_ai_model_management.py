#!/usr/bin/env python3
"""
测试AI模型管理功能
包括模型的创建、读取、更新、删除，以及Token使用统计等功能
"""

import sys
import os
import json
import base64

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 设置环境变量，避免API密钥错误
os.environ['AI_API_KEY'] = 'sk-test1234567890abcdef'
os.environ['AI_API_URL'] = 'https://api.example.com/v1/'
os.environ['AI_MODEL_NAME'] = 'gpt-3.5-turbo'

from app import create_app
from app.models import ModelConfig, TokenUsage
from app import db
from app.services.ai_service import ai_service

# 打印测试信息
print("测试AI模型管理功能...")
print("-" * 60)

# 启动测试应用
app = create_app()

with app.app_context():
    # 清理所有测试数据，确保测试环境干净
    print("清理测试数据...")
    TokenUsage.query.delete()
    ModelConfig.query.delete()
    db.session.commit()
    print("✅ 测试数据清理完成")
    
    # 1. 测试模型配置的加密和解密功能
    print("\n1. 测试模型配置的加密和解密功能...")
    
    # 创建测试模型
    test_model = ModelConfig(
        name="测试模型",
        api_url="https://api.example.com/v1/",
        model_name="gpt-3.5-turbo",
        system_prompt="你是一个测试助手",
        enabled=True
    )
    
    # 测试API密钥加密
    test_api_key = "sk-test1234567890abcdef"
    test_model.set_api_key(test_api_key)
    
    # 检查加密结果
    print(f"原始API密钥: {test_api_key}")
    print(f"加密后API密钥: {test_model.api_key}")
    print(f"解密后API密钥: {test_model.get_api_key()}")
    
    # 验证加密和解密是否正确
    if test_model.get_api_key() == test_api_key:
        print("✅ API密钥加密和解密功能测试通过")
    else:
        print("❌ API密钥加密和解密功能测试失败")
    
    # 2. 测试模型的创建和管理
    print("\n2. 测试模型的创建和管理...")
    
    # 清理测试数据
    ModelConfig.query.filter_by(name="测试模型").delete()
    db.session.commit()
    
    # 创建测试模型
    test_model = ModelConfig(
        name="测试模型",
        api_url="https://api.example.com/v1/",
        model_name="gpt-3.5-turbo",
        system_prompt="你是一个测试助手",
        enabled=True
    )
    test_model.set_api_key("sk-test1234567890abcdef")
    db.session.add(test_model)
    db.session.commit()
    
    print(f"✅ 创建测试模型成功，ID: {test_model.id}")
    
    # 测试获取模型列表
    model_list_result = ai_service.get_model_list()
    if model_list_result["success"]:
        print(f"✅ 获取模型列表成功，共 {len(model_list_result['models'])} 个模型")
    else:
        print(f"❌ 获取模型列表失败: {model_list_result['error']}")
    
    # 测试按ID加载模型
    load_result = ai_service.load_model_by_id(test_model.id)
    if load_result["success"]:
        print(f"✅ 按ID加载模型成功: {load_result['message']}")
    else:
        print(f"❌ 按ID加载模型失败: {load_result['error']}")
    
    # 3. 测试Token使用统计功能
    print("\n3. 测试Token使用统计功能...")
    
    # 清理测试数据
    TokenUsage.query.filter_by(model_id=test_model.id).delete()
    db.session.commit()
    
    # 创建测试Token使用记录
    test_usage = TokenUsage(
        model_id=test_model.id,
        input_tokens=100,
        output_tokens=200,
        total_tokens=300,
        request_summary="测试请求",
        response_status="success"
    )
    db.session.add(test_usage)
    db.session.commit()
    
    # 测试获取Token使用统计
    usage_result = ai_service.get_token_usage(test_model.id)
    if usage_result["success"]:
        print(f"✅ 获取Token使用统计成功")
        print(f"总请求数: {usage_result['total']['requests']}")
        print(f"总Token消耗: {usage_result['total']['total_tokens']}")
        print(f"输入Token: {usage_result['total']['prompt_tokens']}")
        print(f"输出Token: {usage_result['total']['output_tokens']}")
    else:
        print(f"❌ 获取Token使用统计失败: {usage_result['error']}")
    
    # 4. 测试模型的更新和删除
    print("\n4. 测试模型的更新和删除...")
    
    # 更新模型
    test_model.name = "更新后的测试模型"
    test_model.enabled = False
    db.session.commit()
    
    # 验证更新
    updated_model = ModelConfig.query.get(test_model.id)
    if updated_model and updated_model.name == "更新后的测试模型" and not updated_model.enabled:
        print("✅ 更新模型成功")
    else:
        print("❌ 更新模型失败")
    
    # 删除关联的TokenUsage记录
    TokenUsage.query.filter_by(model_id=updated_model.id).delete()
    db.session.commit()
    
    # 删除模型
    db.session.delete(updated_model)
    db.session.commit()
    
    # 验证删除
    deleted_model = ModelConfig.query.get(test_model.id)
    if not deleted_model:
        print("✅ 删除模型成功")
    else:
        print("❌ 删除模型失败")
    
    # 5. 测试默认模型的创建
    print("\n5. 测试默认模型的创建...")
    
    # 清理所有模型
    ModelConfig.query.delete()
    db.session.commit()
    
    # 获取默认模型
    default_model = ai_service.get_model_config()
    if default_model:
        print(f"✅ 创建默认模型成功，ID: {default_model.id}")
        print(f"默认模型名称: {default_model.name}")
        print(f"默认模型状态: {'启用' if default_model.enabled else '禁用'}")
    else:
        print("❌ 创建默认模型失败")
    
    # 6. 测试模型服务的错误处理
    print("\n6. 测试模型服务的错误处理...")
    
    # 测试加载不存在的模型
    error_result = ai_service.load_model_by_id(999999)
    if not error_result["success"] and "模型不存在或未启用" in error_result["error"]:
        print("✅ 错误处理测试通过: 正确处理了不存在的模型ID")
    else:
        print("❌ 错误处理测试失败")
    
    # 清理测试数据
    ModelConfig.query.delete()
    TokenUsage.query.delete()
    db.session.commit()
    
print("\n测试完成！")
print("-" * 60)
