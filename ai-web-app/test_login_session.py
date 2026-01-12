import requests
import json

class LoginSessionTest:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.session = requests.Session()
    
    def test_login_flow(self):
        """测试登录流程和session管理"""
        print("开始测试登录流程和session管理\n")
        
        # 步骤1: 获取登录页面，查看是否有CSRF令牌
        print("=== 步骤1: 获取登录页面 ===")
        response = self.session.get(f'{self.base_url}/login')
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 检查是否有set-cookie头
        if 'Set-Cookie' in response.headers:
            print(f"\n收到的Cookie: {response.headers['Set-Cookie']}")
        else:
            print("\n未收到Cookie")
        
        # 步骤2: 提交登录表单
        print("\n=== 步骤2: 提交登录表单 ===")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember': 'y'
        }
        
        response = self.session.post(f'{self.base_url}/login', data=login_data)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 检查是否有set-cookie头
        if 'Set-Cookie' in response.headers:
            print(f"\n收到的Cookie: {response.headers['Set-Cookie']}")
        else:
            print("\n未收到Cookie")
        
        # 检查session cookie
        print(f"\n当前session的cookies: {dict(self.session.cookies)}")
        
        # 步骤3: 访问需要认证的页面
        print("\n=== 步骤3: 访问dashboard页面 ===")
        response = self.session.get(f'{self.base_url}/dashboard')
        print(f"状态码: {response.status_code}")
        print(f"响应内容前200字符: {response.text[:200]}...")
        
        # 步骤4: 访问/api/collection/start端点
        print("\n=== 步骤4: 访问/api/collection/start端点 ===")
        collection_data = {
            "keyword": "四川美食",
            "crawlers": ["baidu_search"],
            "page": 1,
            "limit": 5
        }
        
        response = self.session.post(
            f'{self.base_url}/api/collection/start',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(collection_data, ensure_ascii=False)
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容前200字符: {response.text[:200]}...")
        
        # 检查是否返回登录页面
        if 'login' in response.url or '<title>Login</title>' in response.text or '登录' in response.text:
            print("\n❌ 被重定向到登录页面，session认证失败")
        else:
            print("\n✅ session认证成功，未被重定向到登录页面")
        
        # 步骤5: 访问/api/crawler/config端点（无认证）
        print("\n=== 步骤5: 访问/api/crawler/config端点 ===")
        response = self.session.get(f'{self.base_url}/api/crawler/config')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 获取成功，配置数量: {len(data.get('configs', []))}")
            except json.JSONDecodeError:
                print(f"❌ 响应不是JSON格式: {response.text[:200]}...")
        else:
            print(f"❌ 获取失败: {response.status_code}")

if __name__ == '__main__':
    test = LoginSessionTest()
    test.test_login_flow()
