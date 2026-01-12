import re

# 读取文件内容
with open('d:/1_pretraining/day/ai-web-app/app/services/crawler_service.py', 'r', encoding='utf-8') as file:
    content = file.read()

# 定义正则表达式模式来匹配 SSE 事件发送代码块
pattern = r'\s*# 发送.*?事件\s*try:\s*with current_app\.app_context\(\):\s*sse\.publish\({[^}]*}, type=\'[^\']*\'\)\s*except Exception as e:\s*current_app\.logger\.warning\(f"Failed to send SSE event: \{str\(e\)}\"\)'

# 替换所有匹配的代码块为空字符串
new_content = re.sub(pattern, '', content, flags=re.DOTALL)

# 写入修改后的内容
with open('d:/1_pretraining/day/ai-web-app/app/services/crawler_service.py', 'w', encoding='utf-8') as file:
    file.write(new_content)

print("已成功移除所有 SSE 事件发送代码块")