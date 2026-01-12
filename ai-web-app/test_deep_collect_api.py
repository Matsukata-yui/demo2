import requests
import json

# 测试深度采集API端点
url = "http://127.0.0.1:5000/api/data/deep_collect/1"

# 发送POST请求
try:
    response = requests.post(url, json={}, headers={"Content-Type": "application/json"}, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Response Content: {response.text[:500]}")  # 只显示前500个字符
    
    # 尝试解析JSON
    try:
        data = response.json()
        print("Response is valid JSON")
        print(f"Success: {data.get('success')}")
        print(f"Error: {data.get('error')}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("响应可能是HTML")
        
except Exception as e:
    print(f"请求错误: {e}")
