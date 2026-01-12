from app import db
from app.models import CollectedData, DeepCollectionData
import json
from datetime import datetime

class DatabaseToolService:
    def __init__(self):
        pass
    
    def search_collected_data(self, query=None, limit=100, offset=0):
        """搜索CollectedData表数据"""
        try:
            db_query = CollectedData.query
            
            if query:
                # 按关键词搜索
                search_term = f'%{query}%'
                db_query = db_query.filter(
                    (CollectedData.title.ilike(search_term)) |
                    (CollectedData.content.ilike(search_term)) |
                    (CollectedData.keywords.ilike(search_term)) |
                    (CollectedData.source.ilike(search_term)) |
                    (CollectedData.sentiment.ilike(search_term)) |
                    (CollectedData.status.ilike(search_term))
                )
            
            # 按时间戳降序排序
            db_query = db_query.order_by(CollectedData.timestamp.desc())
            
            # 执行分页查询
            total = db_query.count()
            results = db_query.offset(offset).limit(limit).all()
            
            # 转换结果为字典列表
            data = []
            for item in results:
                data.append({
                    'id': item.id,
                    'task_id': item.task_id,
                    'title': item.title,
                    'url': item.url,
                    'content': item.content[:500] + '...' if len(item.content) > 500 else item.content,
                    'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else None,
                    'status': item.status,
                    'sentiment': item.sentiment,
                    'keywords': item.keywords,
                    'source': item.source,
                    'image': item.image
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_deep_collection_data(self, query=None, limit=100, offset=0):
        """搜索DeepCollectionData表数据"""
        try:
            db_query = DeepCollectionData.query
            
            if query:
                # 按关键词搜索
                search_term = f'%{query}%'
                db_query = db_query.filter(
                    (DeepCollectionData.title.ilike(search_term)) |
                    (DeepCollectionData.content.ilike(search_term)) |
                    (DeepCollectionData.ai_analysis.ilike(search_term)) |
                    (DeepCollectionData.model_used.ilike(search_term)) |
                    (DeepCollectionData.status.ilike(search_term)) |
                    (DeepCollectionData.url.ilike(search_term))
                )
            
            # 按创建时间降序排序
            db_query = db_query.order_by(DeepCollectionData.created_at.desc())
            
            # 执行分页查询
            total = db_query.count()
            results = db_query.offset(offset).limit(limit).all()
            
            # 转换结果为字典列表
            data = []
            for item in results:
                data.append({
                    'id': item.id,
                    'collected_data_id': item.collected_data_id,
                    'url': item.url,
                    'title': item.title,
                    'content': item.content[:500] + '...' if len(item.content) > 500 else item.content,
                    'ai_analysis': item.ai_analysis[:300] + '...' if item.ai_analysis and len(item.ai_analysis) > 300 else item.ai_analysis,
                    'model_used': item.model_used,
                    'status': item.status,
                    'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': item.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return {
                'success': True,
                'data': data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_collected_data_statistics(self):
        """获取CollectedData表统计信息"""
        try:
            # 总数据量
            total_count = CollectedData.query.count()
            
            # 按来源统计
            from sqlalchemy import func
            source_stats = db.session.query(
                CollectedData.source,
                func.count(CollectedData.id).label('count')
            ).group_by(CollectedData.source).all()
            
            # 按状态统计
            status_stats = db.session.query(
                CollectedData.status,
                func.count(CollectedData.id).label('count')
            ).group_by(CollectedData.status).all()
            
            # 按情感统计
            sentiment_stats = db.session.query(
                CollectedData.sentiment,
                func.count(CollectedData.id).label('count')
            ).group_by(CollectedData.sentiment).all()
            
            # 按时间统计（最近7天）
            from datetime import datetime, timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)
            time_stats = db.session.query(
                func.date(CollectedData.timestamp).label('date'),
                func.count(CollectedData.id).label('count')
            ).filter(CollectedData.timestamp >= seven_days_ago).group_by(func.date(CollectedData.timestamp)).order_by(func.date(CollectedData.timestamp)).all()
            
            # 转换为字典
            source_data = [{'source': item.source or '未知', 'count': item.count} for item in source_stats]
            status_data = [{'status': item.status or '未知', 'count': item.count} for item in status_stats]
            sentiment_data = [{'sentiment': item.sentiment or '未知', 'count': item.count} for item in sentiment_stats]
            time_data = [{'date': item.date if isinstance(item.date, str) else item.date.strftime('%Y-%m-%d'), 'count': item.count} for item in time_stats]
            
            return {
                'success': True,
                'total_count': total_count,
                'source_stats': source_data,
                'status_stats': status_data,
                'sentiment_stats': sentiment_data,
                'time_stats': time_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_deep_collection_statistics(self):
        """获取DeepCollectionData表统计信息"""
        try:
            # 总数据量
            total_count = DeepCollectionData.query.count()
            
            # 按模型统计
            from sqlalchemy import func
            model_stats = db.session.query(
                DeepCollectionData.model_used,
                func.count(DeepCollectionData.id).label('count')
            ).group_by(DeepCollectionData.model_used).all()
            
            # 按状态统计
            status_stats = db.session.query(
                DeepCollectionData.status,
                func.count(DeepCollectionData.id).label('count')
            ).group_by(DeepCollectionData.status).all()
            
            # 按时间统计（最近7天）
            from datetime import datetime, timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)
            time_stats = db.session.query(
                func.date(DeepCollectionData.created_at).label('date'),
                func.count(DeepCollectionData.id).label('count')
            ).filter(DeepCollectionData.created_at >= seven_days_ago).group_by(func.date(DeepCollectionData.created_at)).order_by(func.date(DeepCollectionData.created_at)).all()
            
            # 转换为字典
            model_data = [{'model': item.model_used or '未知', 'count': item.count} for item in model_stats]
            status_data = [{'status': item.status or '未知', 'count': item.count} for item in status_stats]
            time_data = [{'date': item.date if isinstance(item.date, str) else item.date.strftime('%Y-%m-%d'), 'count': item.count} for item in time_stats]
            
            return {
                'success': True,
                'total_count': total_count,
                'model_stats': model_data,
                'status_stats': status_data,
                'time_stats': time_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# 创建服务实例
database_tool_service = DatabaseToolService()
