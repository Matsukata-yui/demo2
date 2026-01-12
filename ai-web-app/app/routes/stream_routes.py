from flask import Blueprint, Response
from flask_login import login_required
import time
import json
from app.utils.ws_sse_utils import sse_manager

stream = Blueprint('stream', __name__)

@stream.route('/data-updates')
@login_required
def stream_data_updates():
    """实时数据流更新"""
    def generate():
        while True:
            data = sse_manager.get_messages('data_updates')
            if data:
                for message in data:
                    yield 'data: ' + json.dumps(message) + '\n\n'
            time.sleep(1)  # 每秒轮询一次消息
    return Response(generate(), mimetype='text/event-stream')

@stream.route('/crawler-status')

@login_required
def stream_crawler_status():
    """实时爬虫状态更新"""
    def generate():
        while True:
            data = sse_manager.get_messages('crawler_status')
            if data:
                for message in data:
                    yield 'data: ' + json.dumps(message) + '\n\n'
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

@stream.route('/analysis-results')
@login_required
def stream_analysis_results():
    """实时分析结果更新"""
    def generate():
        while True:
            data = sse_manager.get_messages('analysis_results')
            if data:
                for message in data:
                    yield 'data: ' + json.dumps(message) + '\n\n'
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

@stream.route('/chat-messages')
@login_required
def stream_chat_messages():
    """实时聊天消息更新"""
    def generate():
        while True:


            data = sse_manager.get_messages('chat_messages')
            if data:
                for message in data:
                    yield 'data: ' + json.dumps(message) + '\n\n'
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')
