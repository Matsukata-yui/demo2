import requests
import json
import time

class FullCollectionFlowTest:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.session = requests.Session()
        self.task_id = None
    
    def login(self):
        """登录系统获取认证"""
        print("=== 测试登录 ===")
        
        # 首先获取登录页面，获取CSRF令牌
        login_page = self.session.get(f'{self.base_url}/login')
        
        # 提取CSRF令牌（简化版，实际应该解析HTML）
        # 这里直接使用固定的测试用户
        
        # 提交登录表单
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember': 'y'
        }
        
        response = self.session.post(f'{self.base_url}/login', data=login_data)
        
        if response.status_code == 200:
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
    
    def test_get_crawler_configs(self):
        """测试获取爬虫源配置"""
        print("\n=== 测试获取爬虫源配置 ===")
        
        response = self.session.get(f'{self.base_url}/api/crawler/config')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取爬虫源配置成功")
            print(f"总共有 {len(data.get('configs', []))} 个爬虫源配置")
            
            # 显示启用的配置
            enabled_configs = [config for config in data.get('configs', []) if config.get('enabled')]
            print(f"启用的配置: {len(enabled_configs)}")
            
            for config in enabled_configs:
                print(f"\n启用的配置详情:")
                print(f"ID: {config.get('id')}")
                print(f"名称: {config.get('name')}")
                print(f"URL: {config.get('url')}")
                print(f"数据源类型: {config.get('source_type')}")
                print(f"请求参数: {config.get('request_params')}")
                print(f"请求头: {config.get('headers')}")
            
            return True
        else:
            print(f"❌ 获取爬虫源配置失败: {response.status_code}")
            return False
    
    def test_start_collection(self):
        """测试开始采集"""
        print("\n=== 测试开始采集 ===")
        
        # 构建采集请求数据
        collection_data = {
            "keyword": "四川美食",
            "crawlers": ["baidu_search"],
            "page": 1,
            "limit": 5
        }
        
        print(f"提交采集请求参数: {json.dumps(collection_data, ensure_ascii=False, indent=2)}")
        
        response = self.session.post(
            f'{self.base_url}/api/collection/start',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(collection_data, ensure_ascii=False)
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 开始采集请求成功")
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                if data.get('success'):
                    self.task_id = data.get('task_id')
                    print(f"任务ID: {self.task_id}")
                    return True
                else:
                    print(f"❌ 采集任务创建失败: {data.get('error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ 响应不是JSON格式: {response.text[:200]}...")
                return False
        else:
            print(f"❌ 开始采集请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return False
    
    def test_get_collection_results(self):
        """测试获取采集结果"""
        if not self.task_id:
            print("❌ 没有任务ID，无法获取结果")
            return False
        
        print(f"\n=== 测试获取采集结果 (任务ID: {self.task_id}) ===")
        
        # 轮询获取结果
        max_retries = 10
        retry_interval = 2
        
        for i in range(max_retries):
            response = self.session.get(f'{self.base_url}/api/collection/results/{self.task_id}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get('success'):
                        print(f"✅ 获取采集结果成功 (尝试 {i+1}/{max_retries})")
                        print(f"任务状态: {data.get('status')}")
                        print(f"进度: {data.get('progress')}%")
                        print(f"已采集: {data.get('total_collected')} 条")
                        
                        # 显示采集结果
                        results = data.get('results', [])
                        if results:
                            print(f"\n采集到的结果:")
                            for j, result in enumerate(results[:3]):  # 只显示前3条
                                print(f"\n结果 {j+1}:")
                                print(f"标题: {result.get('title')}")
                                print(f"URL: {result.get('url')}")
                                print(f"来源: {result.get('source')}")
                            
                            if len(results) > 3:
                                print(f"... 还有 {len(results) - 3} 条结果")
                        else:
                            print("暂无采集结果")
                        
                        # 检查任务是否完成
                        if data.get('status') in ['completed', 'stopped', 'failed']:
                            print(f"\n任务已结束，状态: {data.get('status')}")
                            return True
                        else:
                            print(f"任务仍在运行，{retry_interval}秒后重试...")
                            time.sleep(retry_interval)
                    else:
                        print(f"❌ 获取结果失败: {data.get('error')}")
                        return False
                except json.JSONDecodeError:
                    print(f"❌ 响应不是JSON格式: {response.text[:200]}...")
                    return False
            else:
                print(f"❌ 获取采集结果失败: {response.status_code}")
                return False
        
        print(f"❌ 超过最大重试次数，无法获取完整采集结果")
        return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("开始完整的采集管理→后端→爬虫执行流程测试\n")
        
        # 步骤1: 登录
        if not self.login():
            print("测试失败: 登录失败")
            return False
        
        # 步骤2: 获取爬虫源配置
        if not self.test_get_crawler_configs():
            print("测试失败: 获取爬虫源配置失败")
            return False
        
        # 步骤3: 开始采集
        if not self.test_start_collection():
            print("测试失败: 开始采集失败")
            return False
        
        # 步骤4: 获取采集结果
        if not self.test_get_collection_results():
            print("测试失败: 获取采集结果失败")
            return False
        
        print("\n🎉 完整测试流程成功完成！")
        return True

if __name__ == '__main__':
    test = FullCollectionFlowTest()
    test.run_full_test()
