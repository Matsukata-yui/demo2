from flask import Blueprint, render_template, jsonify, request, Response, stream_with_context
from flask_login import login_required
from app.services.ai_service import ai_service
from app.services.database_tool_service import database_tool_service
from app.models import ModelConfig, TokenUsage
from app import db
import datetime
import json
import time

ai = Blueprint('ai', __name__)

@ai.route('/')
@login_required
def ai_index():
    return render_template('ai_page.html')

@ai.route('/analyze', methods=['POST'])
@login_required
def analyze_data():
    data = request.get_json()
    content = data.get('content', '')
    model_id = data.get('model_id', None)
    result = ai_service.analyze_data(content, model_id)
    return jsonify(result)

@ai.route('/models')
@login_required
def models():
    return render_template('ai_models.html')

@ai.route('/api/models', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def manage_models():
    """模型管理接口"""
    if request.method == 'GET':
        # 获取模型列表
        result = ai_service.get_model_list()
        return jsonify(result)
    
    elif request.method == 'POST':
        # 新增模型
        try:
            data = request.get_json()
            required_fields = ['name', 'api_url', 'api_key', 'model_name']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"缺少必要字段: {field}"
                    })
            
            new_model = ModelConfig(
                name=data['name'],
                api_url=data['api_url'],
                model_name=data['model_name'],
                system_prompt=data.get('system_prompt', ''),
                enabled=data.get('enabled', True)
            )
            # 使用set_api_key方法加密API密钥
            new_model.set_api_key(data['api_key'])
            
            db.session.add(new_model)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "模型创建成功",
                "model": {
                    "id": new_model.id,
                    "name": new_model.name,
                    "model_name": new_model.model_name,
                    "enabled": new_model.enabled
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    elif request.method == 'PUT':
        # 编辑模型
        try:
            data = request.get_json()
            model_id = data.get('id')
            
            if not model_id:
                return jsonify({
                    "success": False,
                    "error": "缺少模型ID"
                })
            
            model = ModelConfig.query.get(model_id)
            if not model:
                return jsonify({
                    "success": False,
                    "error": "模型不存在"
                })
            
            # 更新模型信息
            if 'name' in data:
                model.name = data['name']
            if 'api_url' in data:
                model.api_url = data['api_url']
            if 'api_key' in data:
                model.set_api_key(data['api_key'])
            if 'model_name' in data:
                model.model_name = data['model_name']
            if 'system_prompt' in data:
                model.system_prompt = data['system_prompt']
            if 'enabled' in data:
                model.enabled = data['enabled']
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "模型更新成功",
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "model_name": model.model_name,
                    "enabled": model.enabled
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    elif request.method == 'DELETE':
        # 删除模型
        try:
            data = request.get_json()
            model_id = data.get('id')
            
            if not model_id:
                return jsonify({
                    "success": False,
                    "error": "缺少模型ID"
                })
            
            model = ModelConfig.query.get(model_id)
            if not model:
                return jsonify({
                    "success": False,
                    "error": "模型不存在"
                })
            
            db.session.delete(model)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "模型删除成功"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            })

@ai.route('/api/test-model', methods=['POST'])
@login_required
def test_model():
    """测试模型响应"""
    data = request.get_json()
    message = data.get('message', '')
    model_id = data.get('model_id', None)
    
    result = ai_service.test_model(message, model_id)
    return jsonify(result)

@ai.route('/api/token-usage')
@login_required
def get_token_usage():
    """获取token使用统计"""
    model_id = request.args.get('model_id', None)
    start_time_str = request.args.get('start_time', None)
    end_time_str = request.args.get('end_time', None)
    
    start_time = None
    end_time = None
    
    if start_time_str:
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str)
        except Exception:
            pass
    
    if end_time_str:
        try:
            end_time = datetime.datetime.fromisoformat(end_time_str)
        except Exception:
            pass
    
    result = ai_service.get_token_usage(model_id, start_time, end_time)
    return jsonify(result)

@ai.route('/api/model/<int:model_id>')
@login_required
def get_model_detail(model_id):
    """获取模型详情"""
    try:
        model = ModelConfig.query.get(model_id)
        if not model:
            return jsonify({
                "success": False,
                "error": "模型不存在"
            })
        
        return jsonify({
                "success": True,
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "api_url": model.api_url,
                    "api_key": "***" + model.api_key[-4:] if model.api_key else "",  # 只返回后4位，其余掩码
                    "model_name": model.model_name,
                    "system_prompt": model.system_prompt,
                    "enabled": model.enabled,
                    "created_at": model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": model.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@ai.route('/api/model/<int:model_id>/toggle', methods=['POST'])
@login_required
def toggle_model_status(model_id):
    """切换模型启用/停用状态"""
    try:
        model = ModelConfig.query.get(model_id)
        if not model:
            return jsonify({
                "success": False,
                "error": "模型不存在"
            })
        
        model.enabled = not model.enabled
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"模型已{'启用' if model.enabled else '停用'}",
            "enabled": model.enabled
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        })

@ai.route('/deep-collect', methods=['POST'])
@login_required
def deep_collect():
    """AI深度采集接口"""
    data = request.get_json()
    # 这里可以实现与AI深度采集功能的对接
    # 暂时返回成功消息
    return jsonify({
        "success": True,
        "message": "AI深度采集任务已启动"
    })

@ai.route('/api/analysis/chat', methods=['POST'])
@login_required
def analysis_chat():
    """大模型对话互动接口"""
    data = request.get_json()
    message = data.get('message', '')
    model_id = data.get('model_id', None)
    
    if not message:
        return jsonify({"success": False, "error": "消息内容不能为空"})
    
    # 调用AI服务进行对话
    result = ai_service.test_model(message, model_id)
    return jsonify(result)

@ai.route('/api/analysis/database-query', methods=['POST'])
@login_required
def database_query():
    """数据库查询接口"""
    data = request.get_json()
    query_type = data.get('query_type', 'collected')  # collected 或 deep
    query = data.get('query', '')
    limit = data.get('limit', 100)
    offset = data.get('offset', 0)
    
    try:
        if query_type == 'collected':
            result = database_tool_service.search_collected_data(query, limit, offset)
        else:
            result = database_tool_service.search_deep_collection_data(query, limit, offset)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@ai.route('/api/analysis/get-statistics', methods=['GET'])
@login_required
def get_analysis_statistics():
    """获取分析统计数据"""
    try:
        collected_stats = database_tool_service.get_collected_data_statistics()
        deep_stats = database_tool_service.get_deep_collection_statistics()
        
        return jsonify({
            "success": True,
            "collected_stats": collected_stats,
            "deep_stats": deep_stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@ai.route('/api/analysis/generate-chart', methods=['POST'])
@login_required
def generate_chart():
    """生成图表数据"""
    data = request.get_json()
    chart_type = data.get('chart_type', 'pie')  # pie, bar, line
    data_type = data.get('data_type', 'collected')  # collected 或 deep
    
    try:
        if data_type == 'collected':
            stats = database_tool_service.get_collected_data_statistics()
        else:
            stats = database_tool_service.get_deep_collection_statistics()
        
        if not stats.get('success'):
            return jsonify({"success": False, "error": "获取统计数据失败"})
        
        # 根据图表类型生成数据
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
                    "yAxis": {
                        "type": "value"
                    },
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
                    "yAxis": {
                        "type": "value"
                    },
                    "series": [{
                        "name": "数量",
                        "type": "bar",
                        "data": [item['count'] for item in stats.get('model_stats', [])]
                    }]
                }
        else:
            # 折线图默认返回空数据
            chart_data = {
                "xAxis": {
                    "type": "category",
                    "data": []
                },
                "yAxis": {
                    "type": "value"
                },
                "series": [{
                    "name": "数量",
                    "type": "line",
                    "data": []
                }]
            }
        
        return jsonify({"success": True, "chart_data": chart_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@ai.route('/chat')
@login_required
def ai_chat():
    """AI对话分析页面"""
    return render_template('ai_chat.html')

@ai.route('/api/analysis/chat-stream')
@login_required
def chat_stream():
    """大模型对话SSE接口"""
    
    message = request.args.get('message', '')
    model_id = request.args.get('model_id', '')
    chat_id = request.args.get('chat_id', '')
    
    if not message:
        return Response("data: " + json.dumps({"type": "error", "error": "消息内容不能为空"}) + "\n\n", mimetype='text/event-stream')
    
    def generate():
        try:
            # 开始回复
            yield f"data: {json.dumps({'type': 'start'})}\n\n"
            
            # 构建消息历史
            # 在实际应用中，应该从数据库加载历史记录
            messages = [
                {"role": "system", "content": """你是一个智能数据分析助手，可以帮助用户查询和分析数据库中的采集数据。
你拥有以下工具：
1. search_collected_data: 搜索原始采集数据 (collected_data表)。
2. search_deep_collection_data: 搜索深度分析数据 (deep_collection_data表)。

3. get_collected_data_statistics: 获取采集数据统计。
4. get_deep_collection_statistics: 获取深度数据统计。
5. generate_chart: 生成图表 (支持pie, bar, line)。

当用户要求查询数据时，优先使用搜索工具。
当用户要求生成报表或图表时，使用generate_chart工具。
如果用户的问题需要数据库中的数据才能回答，请务必调用相应的工具。
请根据工具返回的数据回答用户问题。
"""},
                {"role": "user", "content": message}
            ]
            
            # 调用AI服务进行流式对话
            for event in ai_service.stream_chat_with_tools(messages, model_id):
                yield f"data: {json.dumps(event)}\n\n"
            
            # 回复结束
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            # 发送错误信息
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
