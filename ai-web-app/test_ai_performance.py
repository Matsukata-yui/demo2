#!/usr/bin/env python3
"""
测试AI模型服务的性能和并发能力
模拟多个并发请求，测试服务层的响应时间和稳定性
"""

import sys
import os
import time
import threading
import concurrent.futures

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
print("测试AI模型服务的性能和并发能力...")
print("-" * 60)

# 启动测试应用
app = create_app()

# 测试配置
TEST_CONCURRENT_REQUESTS = 10  # 并发请求数
TEST_REQUESTS_PER_THREAD = 5   # 每个线程的请求数

# 测试结果
results = []
errors = []

# 测试函数
def test_ai_service(model_id):
    """测试AI服务的性能"""
    start_time = time.time()
    
    try:
        # 在每个线程中创建应用上下文
        with app.app_context():
            # 测试获取模型配置
            model_config = ai_service.get_model_config(model_id)
            if not model_config:
                raise Exception("获取模型配置失败")
            
            # 测试加载模型
            load_result = ai_service.load_model_by_id(model_id)
            if not load_result["success"]:
                raise Exception(f"加载模型失败: {load_result['error']}")
            
            # 测试获取Token使用统计
            usage_result = ai_service.get_token_usage(model_id)
            if not usage_result["success"]:
                raise Exception(f"获取Token使用统计失败: {usage_result['error']}")
            
            # 测试获取模型列表
            list_result = ai_service.get_model_list()
            if not list_result["success"]:
                raise Exception(f"获取模型列表失败: {list_result['error']}")
            
            end_time = time.time()
            response_time = end_time - start_time
            results.append(response_time)
            return f"✅ 测试成功，响应时间: {response_time:.4f}s"
        
    except Exception as e:
        errors.append(str(e))
        return f"❌ 测试失败: {e}"

# 并发测试函数
def concurrent_test():
    """执行并发测试"""
    print(f"\n开始并发测试，{TEST_CONCURRENT_REQUESTS} 个并发请求，每个请求执行 {TEST_REQUESTS_PER_THREAD} 次操作...")
    
    # 执行测试
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=TEST_CONCURRENT_REQUESTS) as executor:
        # 提交测试任务
        futures = []
        for i in range(TEST_CONCURRENT_REQUESTS):
            futures.append(executor.submit(test_ai_service, 1))
        
        # 收集测试结果
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 计算测试结果
    if results:
        avg_response_time = sum(results) / len(results)
        max_response_time = max(results)
        min_response_time = min(results)
        
        print(f"\n测试结果:")
        print(f"总执行时间: {total_time:.4f}s")
        print(f"平均响应时间: {avg_response_time:.4f}s")
        print(f"最大响应时间: {max_response_time:.4f}s")
        print(f"最小响应时间: {min_response_time:.4f}s")
        print(f"成功率: {len(results) / (len(results) + len(errors)):.2%}")
        print(f"成功请求数: {len(results)}")
        print(f"失败请求数: {len(errors)}")
        
        if errors:
            print(f"\n错误信息:")
            for error in errors[:5]:  # 只显示前5个错误
                print(f"- {error}")
            if len(errors) > 5:
                print(f"... 还有 {len(errors) - 5} 个错误")
    else:
        print(f"\n测试全部失败，错误数: {len(errors)}")
        if errors:
            print(f"错误信息:")
            for error in errors[:5]:
                print(f"- {error}")

# 内存使用测试
def test_memory_usage():
    """测试内存使用情况"""
    print("\n测试内存使用情况...")
    
    try:
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 测试前内存使用
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"测试前内存使用: {mem_before:.2f} MB")
        
        # 执行多次操作
        for i in range(100):
            model_config = ai_service.get_model_config(1)
            usage_result = ai_service.get_token_usage(1)
        
        # 测试后内存使用
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"测试后内存使用: {mem_after:.2f} MB")
        print(f"内存变化: {mem_after - mem_before:.2f} MB")
        
        if mem_after - mem_before < 50:  # 内存增长小于50MB
            print("✅ 内存使用测试通过，无明显内存泄漏")
        else:
            print("⚠️  内存使用测试警告，内存增长较大")
            
    except ImportError:
        print("⚠️  无法测试内存使用，psutil 模块未安装")
    except Exception as e:
        print(f"❌ 内存测试失败: {e}")

# 主测试函数
def main():
    with app.app_context():
        # 清理测试数据
        print("清理测试数据...")
        TokenUsage.query.delete()
        ModelConfig.query.delete()
        db.session.commit()
        print("✅ 测试数据清理完成")
        
        # 创建测试模型
        print("\n创建测试模型...")
        test_model = ModelConfig(
            name="性能测试模型",
            api_url="https://api.example.com/v1/",
            model_name="gpt-3.5-turbo",
            system_prompt="你是一个性能测试助手",
            enabled=True
        )
        test_model.set_api_key("sk-test1234567890abcdef")
        db.session.add(test_model)
        db.session.commit()
        print(f"✅ 创建测试模型成功，ID: {test_model.id}")
        
        # 添加测试Token使用记录
        print("添加测试Token使用记录...")
        for i in range(10):
            test_usage = TokenUsage(
                model_id=test_model.id,
                input_tokens=100 + i * 10,
                output_tokens=200 + i * 20,
                total_tokens=300 + i * 30,
                request_summary=f"测试请求 {i+1}",
                response_status="success"
            )
            db.session.add(test_usage)
        db.session.commit()
        print("✅ 添加测试Token使用记录成功")
        
        # 执行并发测试
        concurrent_test()
        
        # 执行内存使用测试
        test_memory_usage()
        
        # 清理测试数据
        print("\n清理测试数据...")
        TokenUsage.query.delete()
        ModelConfig.query.delete()
        db.session.commit()
        print("✅ 测试数据清理完成")

if __name__ == "__main__":
    main()
    print("\n性能测试完成！")
    print("-" * 60)
