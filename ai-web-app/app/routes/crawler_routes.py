from flask import Blueprint, jsonify, request
from app.models import CrawlerConfig
from app import db
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

crawler = Blueprint('crawler', __name__, url_prefix='/api/crawler')

@crawler.route('/config', methods=['GET'])
def get_crawler_configs():
    """获取所有爬虫配置"""
    try:
        configs = CrawlerConfig.query.all()
        config_list = []
        
        for config in configs:
            config_data = {
                'id': config.id,
                'name': config.name,
                'url': config.url,
                'request_method': config.request_method,
                'crawl_interval': config.crawl_interval,
                'source_type': config.source_type,
                'enabled': config.enabled,
                'headers': config.headers,
                'request_params': config.request_params,
                'created_at': config.created_at.isoformat() if config.created_at else None
            }
            config_list.append(config_data)
        
        return jsonify({'success': True, 'configs': config_list})
    except Exception as e:
        logger.error(f"获取爬虫配置列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取爬虫配置列表失败'}), 500

@crawler.route('/config/<int:config_id>', methods=['GET'])
def get_crawler_config(config_id):
    """获取单个爬虫配置"""
    try:
        config = CrawlerConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
        
        config_data = {
            'id': config.id,
            'name': config.name,
            'url': config.url,
            'request_method': config.request_method,
            'crawl_interval': config.crawl_interval,
            'source_type': config.source_type,
            'enabled': config.enabled,
            'headers': config.headers,
            'request_params': config.request_params,
            'created_at': config.created_at.isoformat() if config.created_at else None
        }
        
        return jsonify({'success': True, 'config': config_data})
    except Exception as e:
        logger.error(f"获取爬虫配置失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取爬虫配置失败'}), 500

@crawler.route('/config', methods=['POST'])
def create_crawler_config():
    """创建新的爬虫配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['name', 'url', 'request_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} 是必填字段'}), 400
        
        # 验证URL格式
        import re
        url_pattern = r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$'
        if not re.match(url_pattern, data['url']):
            return jsonify({'success': False, 'error': 'URL格式不正确'}), 400
        
        # 验证爬虫源名称长度
        if not (1 <= len(data['name']) <= 50):
            return jsonify({'success': False, 'error': '爬虫源名称长度必须在1-50字符之间'}), 400
        
        # 检查爬虫源名称是否已存在
        existing_config = CrawlerConfig.query.filter_by(name=data['name']).first()
        if existing_config:
            return jsonify({'success': False, 'error': '爬虫源名称已存在'}), 400
        
        # 创建新配置
        new_config = CrawlerConfig(
            name=data['name'],
            url=data['url'],
            request_method=data['request_method'],
            crawl_interval=data.get('crawl_interval', 3600),
            source_type=data.get('source_type', 'website'),
            enabled=data.get('enabled', True),
            headers=data.get('headers', '{}'),
            request_params=data.get('request_params', '{}')
        )
        
        db.session.add(new_config)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '配置创建成功', 'config_id': new_config.id})
    except Exception as e:
        logger.error(f"创建爬虫配置失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': '创建爬虫配置失败'}), 500

@crawler.route('/config/<int:config_id>', methods=['PUT'])
def update_crawler_config(config_id):
    """更新爬虫配置"""
    try:
        config = CrawlerConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['name', 'url', 'request_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} 是必填字段'}), 400
        
        # 验证URL格式
        import re
        url_pattern = r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$'
        if not re.match(url_pattern, data['url']):
            return jsonify({'success': False, 'error': 'URL格式不正确'}), 400
        
        # 验证爬虫源名称长度
        if not (1 <= len(data['name']) <= 50):
            return jsonify({'success': False, 'error': '爬虫源名称长度必须在1-50字符之间'}), 400
        
        # 检查爬虫源名称是否已存在（排除当前配置）
        existing_config = CrawlerConfig.query.filter_by(name=data['name']).filter(CrawlerConfig.id != config_id).first()
        if existing_config:
            return jsonify({'success': False, 'error': '爬虫源名称已存在'}), 400
        
        # 更新配置
        config.name = data['name']
        config.url = data['url']
        config.request_method = data['request_method']
        config.crawl_interval = data.get('crawl_interval', 3600)
        config.source_type = data.get('source_type', 'website')
        config.enabled = data.get('enabled', True)
        config.headers = data.get('headers', '{}')
        config.request_params = data.get('request_params', '{}')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '配置更新成功'})
    except Exception as e:
        logger.error(f"更新爬虫配置失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': '更新爬虫配置失败'}), 500

@crawler.route('/config/<int:config_id>', methods=['DELETE'])
def delete_crawler_config(config_id):
    """删除爬虫配置"""
    try:
        config = CrawlerConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '配置删除成功'})
    except Exception as e:
        logger.error(f"删除爬虫配置失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': '删除爬虫配置失败'}), 500

@crawler.route('/config/<int:config_id>/status', methods=['PATCH'])
def toggle_crawler_status(config_id):
    """切换爬虫配置状态"""
    try:
        config = CrawlerConfig.query.get(config_id)
        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
        
        data = request.get_json()
        if not data or 'enabled' not in data:
            return jsonify({'success': False, 'error': 'enabled 是必填字段'}), 400
        
        config.enabled = data['enabled']
        db.session.commit()
        
        return jsonify({'success': True, 'message': '配置状态更新成功'})
    except Exception as e:
        logger.error(f"更新爬虫配置状态失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': '更新爬虫配置状态失败'}), 500