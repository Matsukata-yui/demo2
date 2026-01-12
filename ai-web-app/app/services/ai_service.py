import openai
import datetime
import json
from app.config import Config
from app.models import ModelConfig, TokenUsage, DeepCollectionData, CollectedData
from app import db
from app.utils.ai_utils import AIUtils
from app.services.database_tool_service import database_tool_service
from crawl4ai import AsyncWebCrawler
import asyncio

class AIService:
    def __init__(self):
        # 初始化默认配置
        self.ai_api_url = Config.AI_API_URL
        self.ai_api_key = Config.AI_API_KEY
        self.ai_model_name = Config.AI_MODEL_NAME
        
        # 配置默认OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.ai_api_key,
            base_url=self.ai_api_url
        )
        
        self.current_model = None
        self.current_model_id = None
    
    def get_model_config(self, model_id=None):
        """获取模型配置"""
        try:
            if model_id:
                model_config = ModelConfig.query.filter_by(id=model_id, enabled=True).first()
                if not model_config:
                    return None
            else:
                # 获取默认启用的模型
                model_config = ModelConfig.query.filter_by(enabled=True).first()
                if not model_config:
                    # 如果没有启用的模型，创建默认模型
                    model_config = self._create_default_model()
            return model_config
        except Exception as e:
            print(f"获取模型配置失败: {e}")
            return None
    
    def _create_default_model(self):
        """创建默认模型配置"""
        try:
            default_model = ModelConfig(
                name="默认模型",
                api_url=self.ai_api_url,
                model_name=self.ai_model_name,
                system_prompt="你是一个专业的AI助手，请根据用户的问题提供准确、详细的回答。",
                enabled=True
            )
            # 使用set_api_key方法加密API密钥
            if self.ai_api_key:
                default_model.set_api_key(self.ai_api_key)
            else:
                default_model.api_key = ""
            db.session.add(default_model)
            db.session.commit()
            return default_model
        except Exception as e:
            print(f"创建默认模型失败: {e}")
            return None
    
    def load_model_by_id(self, model_id):
        """按ID加载模型"""
        try:
            model_config = self.get_model_config(model_id)
            if not model_config:
                return {
                    "success": False,
                    "error": "模型不存在或未启用"
                }
            
            # 更新当前模型信息
            self.current_model = model_config
            self.current_model_id = model_id
            
            # 更新OpenAI客户端
            self.client = openai.OpenAI(
                api_key=model_config.get_api_key(),
                base_url=model_config.api_url
            )
            
            return {
                "success": True,
                "message": f"模型 {model_config.name} 加载成功",
                "model": {
                    "id": model_config.id,
                    "name": model_config.name,
                    "model_name": model_config.model_name,
                    "enabled": model_config.enabled
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_data(self, data, model_id=None):
        """分析数据并返回结果"""
        try:
            # 加载指定模型
            if model_id:
                load_result = self.load_model_by_id(model_id)
                if not load_result["success"]:
                    return load_result
            elif not self.current_model:
                # 自动加载默认模型
                model_config = self.get_model_config()
                if model_config:
                    self.load_model_by_id(model_config.id)
                else:
                    return {
                        "success": False,
                        "error": "没有可用的模型"
                    }
            
            # 数据预处理
            processed_text = AIUtils.preprocess_text(data)
            keywords = AIUtils.extract_keywords(processed_text)
            
            # 构建系统提示词
            system_prompt = self.current_model.system_prompt or "你是一个专业的数据分析助手，请对提供的文本进行情感分析，并给出情感倾向（positive/negative/neutral）和置信度。"
            
            # 调用AI模型API进行情感分析
            response = self.client.chat.completions.create(
                model=self.current_model.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": processed_text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # 解析API响应
            analysis_result = response.choices[0].message.content.strip()
            
            # 记录token使用量
            self._record_token_usage(response.usage, self.current_model_id, processed_text[:100])
            
            # 模拟解析情感分析结果
            # 在实际应用中，应该更精确地解析API响应
            sentiment = "positive"
            confidence = 0.92
            
            return {
                "success": True,
                "data": {
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "keywords": keywords,
                    "summary": analysis_result
                },
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_report(self, data, model_id=None):
        """生成AI分析报告"""
        try:
            # 加载指定模型
            if model_id:
                load_result = self.load_model_by_id(model_id)
                if not load_result["success"]:
                    return load_result
            elif not self.current_model:
                # 自动加载默认模型
                model_config = self.get_model_config()
                if model_config:
                    self.load_model_by_id(model_config.id)
                else:
                    return {
                        "success": False,
                        "error": "没有可用的模型"
                    }
            
            # 数据预处理
            processed_text = AIUtils.preprocess_text(data)
            keywords = AIUtils.extract_keywords(processed_text)
            
            # 构建系统提示词
            system_prompt = "你是一个专业的数据分析专家，请基于提供的数据生成一份详细的分析报告，包括数据概览、关键发现、趋势分析和建议。"
            
            # 调用AI模型API生成报告
            response = self.client.chat.completions.create(
                model=self.current_model.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": processed_text}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            # 解析API响应
            report_content = response.choices[0].message.content.strip()
            
            # 记录token使用量
            self._record_token_usage(response.usage, self.current_model_id, processed_text[:100])
            
            return {
                "success": True,
                "report": {
                    "title": "AI数据分析报告",
                    "content": report_content,
                    "keywords": keywords,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_model(self, message, model_id=None):
        """测试模型响应"""
        try:
            # 加载指定模型
            if model_id:
                load_result = self.load_model_by_id(model_id)
                if not load_result["success"]:
                    return load_result
            elif not self.current_model:
                # 自动加载默认模型
                model_config = self.get_model_config()
                if model_config:
                    self.load_model_by_id(model_config.id)
                else:
                    return {
                        "success": False,
                        "error": "没有可用的模型"
                    }
            
            # 构建系统提示词
            system_prompt = self.current_model.system_prompt or "你是一个专业的AI助手，请根据用户的问题提供准确、详细的回答。"
            
            # 调用AI模型API测试
            response = self.client.chat.completions.create(
                model=self.current_model.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # 记录token使用量
            self._record_token_usage(response.usage, self.current_model_id, message[:100])
            
            return {
                "success": True,
                "response": response.choices[0].message.content.strip(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _record_token_usage(self, usage, model_id, request_summary):
        """记录token使用量到数据库"""
        try:
            token_usage = TokenUsage(
                model_id=model_id,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                request_summary=request_summary,
                response_status="success"
            )
            db.session.add(token_usage)
            db.session.commit()
        except Exception as e:
            print(f"记录token使用量失败: {e}")
            db.session.rollback()
    
    def get_token_usage(self, model_id=None, start_time=None, end_time=None):
        """获取token使用统计"""
        try:
            query = TokenUsage.query
            
            if model_id:
                query = query.filter_by(model_id=model_id)
            
            if start_time:
                query = query.filter(TokenUsage.request_time >= start_time)
            
            if end_time:
                query = query.filter(TokenUsage.request_time <= end_time)
            
            usages = query.order_by(TokenUsage.request_time.desc()).all()
            
            # 统计总使用量
            total = {
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "requests": 0
            }
            
            usage_list = []
            for usage in usages:
                usage_data = {
                    "id": usage.id,
                    "model_id": usage.model_id,
                    "request_time": usage.request_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                    "request_summary": usage.request_summary,
                    "response_status": usage.response_status
                }
                usage_list.append(usage_data)
                
                # 累加统计
                total["prompt_tokens"] += usage.input_tokens
                total["output_tokens"] += usage.output_tokens
                total["total_tokens"] += usage.total_tokens
                total["requests"] += 1
            
            return {
                "success": True,
                "total": total,
                "usages": usage_list
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_model_list(self):
        """获取所有模型列表"""
        try:
            models = ModelConfig.query.all()
            model_list = []
            for model in models:
                model_list.append({
                    "id": model.id,
                    "name": model.name,
                    "model_name": model.model_name,
                    "api_url": model.api_url,
                    "enabled": model.enabled,
                    "created_at": model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": model.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            return {
                "success": True,
                "models": model_list
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def deep_collect(self, collected_data_id, url, model_id=None, progress_callback=None):
        """深度采集URL数据并分析"""
        try:
            # 检查collected_data是否存在
            collected_data = CollectedData.query.filter_by(id=collected_data_id).first()
            if not collected_data:
                return {
                    "success": False,
                    "error": "源数据不存在"
                }
            
            # 检查是否已存在深度采集数据
            existing_deep_data = DeepCollectionData.query.filter_by(
                collected_data_id=collected_data_id,
                url=url
            ).first()
            
            # 初始化进度
            if progress_callback:
                await progress_callback(10, "开始深度采集...")
            
            # 使用Crawl4AI采集数据
            if progress_callback:
                await progress_callback(30, "正在采集页面数据...")
            
            crawler = AsyncWebCrawler()
            result = await crawler.arun(url=url)
            
            if progress_callback:
                await progress_callback(60, "页面数据采集完成，正在处理...")
            
            # 提取采集结果
            title = result.metadata.get('title', '')
            # 检查CrawlResult对象的属性，使用正确的属性名
            if hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, 'text'):
                content = result.text
            elif hasattr(result, 'html'):
                content = result.html
            else:
                content = ''
            
            # 可选：使用AI模型分析数据
            ai_analysis = None
            model_used = None
            
            if model_id:
                if progress_callback:
                    await progress_callback(80, "正在使用AI模型分析数据...")
                
                model_config = self.get_model_config(model_id)
                if model_config:
                    model_used = model_config.name
                    # 调用AI模型分析内容
                    analysis_result = self.analyze_data(content, model_id)
                    if analysis_result.get("success"):
                        ai_analysis = analysis_result.get("data", {}).get("summary", "")
            
            # 保存或更新深度采集数据
            if existing_deep_data:
                # 更新现有数据
                existing_deep_data.title = title
                existing_deep_data.content = content
                existing_deep_data.ai_analysis = ai_analysis
                existing_deep_data.model_used = model_used
                existing_deep_data.status = "completed"
                existing_deep_data.updated_at = datetime.datetime.utcnow()
                action = "updated"
            else:
                # 创建新数据
                new_deep_data = DeepCollectionData(
                    collected_data_id=collected_data_id,
                    url=url,
                    title=title,
                    content=content,
                    ai_analysis=ai_analysis,
                    model_used=model_used,
                    status="completed"
                )
                db.session.add(new_deep_data)
                action = "created"
            
            db.session.commit()
            
            if progress_callback:
                await progress_callback(100, "深度采集完成")
            
            return {
                "success": True,
                "action": action,
                "data": {
                    "title": title,
                    "url": url,
                    "content_length": len(content),
                    "ai_analysis": ai_analysis is not None,
                    "model_used": model_used
                }
            }
        except Exception as e:
            print(f"深度采集失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_deep_collection_data(self, collected_data_id=None, page=1, limit=10, search=""):
        """获取深度采集数据列表"""
        try:
            query = DeepCollectionData.query
            
            if collected_data_id:
                query = query.filter_by(collected_data_id=collected_data_id)
            
            if search:
                query = query.filter(
                    (DeepCollectionData.title.like(f"%{search}%") | 
                     DeepCollectionData.content.like(f"%{search}%") |
                     DeepCollectionData.url.like(f"%{search}%"))
                )
            
            # 计算总数
            total = query.count()
            
            # 分页
            offset = (page - 1) * limit
            deep_data_list = query.order_by(DeepCollectionData.created_at.desc()).offset(offset).limit(limit).all()
            
            # 转换为字典列表
            data_list = []
            for data in deep_data_list:
                data_list.append({
                    "id": data.id,
                    "collected_data_id": data.collected_data_id,
                    "url": data.url,
                    "title": data.title,
                    "content": data.content[:100] + "..." if len(data.content) > 100 else data.content,
                    "ai_analysis": data.ai_analysis,
                    "model_used": data.model_used,
                    "status": data.status,
                    "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": data.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return {
                "success": True,
                "total": total,
                "data": data_list,
                "page": page,
                "limit": limit
            }
        except Exception as e:
            print(f"获取深度采集数据失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_tools_definitions(self):
        """获取工具定义"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_collected_data",
                    "description": "搜索CollectedData表数据。当用户询问关于采集数据、原始数据、或者需要查询特定内容时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"},
                            "limit": {"type": "integer", "description": "返回结果数量限制", "default": 5},
                            "offset": {"type": "integer", "description": "分页偏移量", "default": 0}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_deep_collection_data",
                    "description": "搜索DeepCollectionData表数据。当用户询问关于深度采集、详细分析数据、AI分析结果时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"},
                            "limit": {"type": "integer", "description": "返回结果数量限制", "default": 5},
                            "offset": {"type": "integer", "description": "分页偏移量", "default": 0}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_collected_data_statistics",
                    "description": "获取CollectedData表的统计信息。当用户询问关于采集数据的统计、概览、来源分布、情感分布时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_deep_collection_statistics",
                    "description": "获取DeepCollectionData表的统计信息。当用户询问关于深度采集数据的统计、模型使用分布时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_chart",
                    "description": "生成图表配置。当用户明确要求生成图表（如饼图、柱状图、折线图）时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chart_type": {"type": "string", "enum": ["pie", "bar", "line"], "description": "图表类型"},
                            "data_type": {"type": "string", "enum": ["collected", "deep"], "description": "数据来源类型"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["chart_type"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name, tool_args):
        """执行工具调用"""
        try:
            if tool_name == "search_collected_data":
                return database_tool_service.search_collected_data(**tool_args)
            elif tool_name == "search_deep_collection_data":
                return database_tool_service.search_deep_collection_data(**tool_args)
            elif tool_name == "get_collected_data_statistics":
                return database_tool_service.get_collected_data_statistics()
            elif tool_name == "get_deep_collection_statistics":
                return database_tool_service.get_deep_collection_statistics()
            elif tool_name == "generate_chart":
                # 图表生成逻辑
                chart_type = tool_args.get("chart_type", "pie")
                data_type = tool_args.get("data_type", "collected")
                
                if data_type == 'collected':
                    stats = database_tool_service.get_collected_data_statistics()
                else:
                    stats = database_tool_service.get_deep_collection_statistics()
                
                if not stats.get('success'):
                    return {"success": False, "error": "获取统计数据失败"}
                
                # 生成图表数据
                chart_data = {}
                if chart_type == 'pie':
                    if data_type == 'collected':
                        chart_data = {
                            "series": [{
                                "name": "数据来源",
                                "type": "pie",
                                "data": stats.get('source_stats', [])
                            }]
                        }
                    else:
                        chart_data = {
                            "series": [{
                                "name": "模型使用",
                                "type": "pie",
                                "data": stats.get('model_stats', [])
                            }]
                        }
                elif chart_type == 'bar':
                    if data_type == 'collected':
                        chart_data = {
                            "xAxis": {
                                "type": "category",
                                "data": [item['source'] for item in stats.get('source_stats', [])]
                            },
                            "yAxis": {"type": "value"},
                            "series": [{
                                "name": "数量",
                                "type": "bar",
                                "data": [item['count'] for item in stats.get('source_stats', [])]
                            }]
                        }
                    else:
                        chart_data = {
                            "xAxis": {
                                "type": "category",
                                "data": [item['model'] for item in stats.get('model_stats', [])]
                            },
                            "yAxis": {"type": "value"},
                            "series": [{
                                "name": "数量",
                                "type": "bar",
                                "data": [item['count'] for item in stats.get('model_stats', [])]
                            }]
                        }
                elif chart_type == 'line':
                    if data_type == 'collected':
                         chart_data = {
                            "xAxis": {
                                "type": "category",
                                "data": [item['date'] for item in stats.get('time_stats', [])]
                            },
                            "yAxis": {"type": "value"},
                            "series": [{
                                "name": "数量",
                                "type": "line",
                                "data": [item['count'] for item in stats.get('time_stats', [])]
                            }]
                        }
                    else:
                        chart_data = {
                            "xAxis": {
                                "type": "category",
                                "data": [item['date'] for item in stats.get('time_stats', [])]
                            },
                            "yAxis": {"type": "value"},
                            "series": [{
                                "name": "数量",
                                "type": "line",
                                "data": [item['count'] for item in stats.get('time_stats', [])]
                            }]
                        }

                return {
                    "success": True,
                    "is_chart": True,
                    "chart_data": chart_data,
                    "title": tool_args.get("title", "数据图表")
                }
            
            return {"success": False, "error": f"未知工具: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stream_chat_with_tools(self, messages, model_id=None):
        """带工具调用的流式对话"""
        try:
            # 获取模型配置 (总是获取最新的，避免Session detach问题)
            model_config = self.get_model_config(model_id)
            if not model_config:
                yield {"type": "error", "error": "没有可用的模型"}
                return
            
            # 为当前请求创建独立的客户端
            client = openai.OpenAI(
                api_key=model_config.get_api_key(),
                base_url=model_config.api_url
            )
            model_name = model_config.model_name
            
            tools = self.get_tools_definitions()
            
            # 第一次调用
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=True
            )
            
            tool_calls = []
            current_content = ""
            
            for chunk in response:
                delta = chunk.choices[0].delta
                
                # 处理内容
                if delta.content:
                    current_content += delta.content
                    yield {"type": "content", "content": delta.content}
                
                # 处理工具调用
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if len(tool_calls) <= tool_call.index:
                            tool_calls.append({
                                "id": tool_call.id,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": ""
                                }
                            })
                        
                        tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments or ""
            
            # 如果有工具调用
            if tool_calls:
                # 添加助手的回复到消息历史
                messages.append({
                    "role": "assistant",
                    "content": current_content,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": tc["function"]
                        } for tc in tool_calls
                    ]
                })
                
                # 执行工具
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args_str = tool_call["function"]["arguments"]
                    
                    try:
                        function_args = json.loads(function_args_str)
                    except json.JSONDecodeError:
                        yield {"type": "error", "error": f"工具参数解析失败: {function_args_str}"}
                        continue
                    
                    yield {"type": "status", "content": f"正在调用工具: {function_name}..."}
                    
                    tool_result = self.execute_tool(function_name, function_args)
                    
                    # 如果是图表，直接返回图表数据
                    if tool_result.get("is_chart"):
                        yield {
                            "type": "chart", 
                            "chart_data": tool_result.get("chart_data"),
                            "chart_title": tool_result.get("title")
                        }
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps({"success": True, "message": "Chart generated successfully"})
                        })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result)
                        })
                
                # 第二次调用（获取最终回答）
                response2 = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                for chunk in response2:
                    if chunk.choices[0].delta.content:
                        yield {"type": "content", "content": chunk.choices[0].delta.content}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    def delete_deep_collection_data(self, data_id):
        """删除深度采集数据"""
        try:
            deep_data = DeepCollectionData.query.filter_by(id=data_id).first()
            if not deep_data:
                return {
                    "success": False,
                    "error": "数据不存在"
                }
            
            db.session.delete(deep_data)
            db.session.commit()
            
            return {
                "success": True,
                "message": "数据删除成功"
            }
        except Exception as e:
            print(f"删除深度采集数据失败: {e}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

# 创建AI服务实例
ai_service = AIService()
