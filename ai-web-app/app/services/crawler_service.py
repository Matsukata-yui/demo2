import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import os
from datetime import datetime
from app.config import Config
from app.models import db, CollectionTask, CollectedData, CrawlerConfig
from flask import current_app

# 导入爬虫源管理器
from app.services.crawler_source_manager import crawler_source_manager

class CrawlerService:
    def __init__(self):
        # 初始化爬虫配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
        self.retry_count = 3
    
    def fetch_content(self, url):
        """获取网页内容"""
        try:
            for i in range(self.retry_count):
                try:
                    response = requests.get(url, headers=self.headers, timeout=self.timeout)
                    response.raise_for_status()
                    return response.text
                except requests.RequestException as e:
                    if i < self.retry_count - 1:
                        time.sleep(random.uniform(1, 3))
                        continue
                    raise
        except Exception as e:
            return None
    
    def parse_content(self, html_content, url):
        """解析网页内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取基本信息
            title = soup.title.string if soup.title else ""
            
            # 提取正文内容
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
            
            # 提取链接
            links = [a['href'] for a in soup.find_all('a', href=True)]
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return None
    
    def extract_data(self, parsed_content):
        """从解析后的内容中提取相关数据"""
        if not parsed_content:
            return None
        
        # 这里可以根据需要实现更复杂的数据提取逻辑
        # 例如：提取特定标签的内容、结构化数据等
        
        return {
            'url': parsed_content['url'],
            'title': parsed_content['title'],
            'content': parsed_content['content'],
            'keywords': [],  # 可以调用AI服务提取关键词
            'timestamp': parsed_content['timestamp']
        }
    
    def run_crawler(self, task_id):
        """运行爬虫任务"""
        import traceback
        try:
            # 获取任务配置
            task = CollectionTask.query.get(task_id)
            if not task:
                return {'success': False, 'error': '任务不存在'}
            
            # 更新任务状态为运行中
            task.status = 'running'
            task.last_run_time = datetime.utcnow()
            db.session.commit()
            
            # 执行爬虫任务
            results = []
            
            # 检查是否为百度搜索任务（通过urls格式判断：baidu_search:关键词:页码:数量）
            if task.urls.startswith('baidu_search:'):
                # 百度搜索任务格式：baidu_search:关键词:页码:数量
                search_params = task.urls.split(':')
                if len(search_params) < 2:
                    raise ValueError("百度搜索任务格式错误，应为：baidu_search:关键词[:页码][:数量]")
                
                keyword = search_params[1]
                page = int(search_params[2]) if len(search_params) > 2 and search_params[2] else 1
                limit = int(search_params[3]) if len(search_params) > 3 and search_params[3] else 10
                
                print(f"crawler_service.run_crawler: 准备调用crawler_source_manager.run_crawler_by_source")
                print(f"参数: source=baidu_search, params={{keyword: {keyword}, page: {page}, limit: {limit}}}")
                
                # 使用爬虫源管理器调用百度搜索爬虫
                result = crawler_source_manager.run_crawler_by_source("baidu_search", {
                    "keyword": keyword,
                    "page": page,
                    "limit": limit
                })
                
                print(f"crawler_service.run_crawler: crawler_source_manager.run_crawler_by_source返回结果: {result}")
                
                if not result.get("success", False):
                    error_msg = result.get("error_message", result.get("error", "百度搜索失败"))
                    print(f"❌ 百度搜索失败: {error_msg}")
                    # 抛出异常，确保任务状态更新为失败
                    raise Exception(f"百度搜索失败: {error_msg}")
                
                search_results = result.get("results", [])
                
                if not search_results:
                    print(f"❌ 百度搜索未返回结果")
                    # 抛出异常，确保任务状态更新为失败
                    raise Exception("百度搜索未返回结果")
                
                print(f"百度搜索返回 {len(search_results)} 条结果")
                
                # 处理搜索结果
                for i, search_result in enumerate(search_results):
                    
                    # 提取数据
                    extracted_data = {
                        'url': search_result.get('url', ''),
                        'title': search_result.get('title', ''),
                        'content': search_result.get('abstract') or search_result.get('content', '')
                    }
                    
                    print(f"处理结果 {i+1}: {extracted_data['title']}")
                    
                    # 检查是否已存在相同URL的数据（避免重复）
                    existing_data = CollectedData.query.filter_by(
                        task_id=task.id,
                        url=extracted_data['url']
                    ).first()
                    
                    if not existing_data:
                        # 保存数据到数据库
                        collected_data = CollectedData(
                            task_id=task.id,
                            url=extracted_data['url'],
                            title=extracted_data['title'],
                            content=extracted_data['content'],
                            source='baidu_search',
                            status='collected'
                        )
                        db.session.add(collected_data)
                        results.append(collected_data)
                    else:
                        print(f"跳过重复数据: {extracted_data['url']}")
            
            # 提交数据库更改
            db.session.commit()
            
            # 更新任务状态
            task.status = 'completed'
            task.last_finish_time = datetime.utcnow()
            task.total_collected = CollectedData.query.filter_by(task_id=task_id).count()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'爬虫任务执行完成，共采集 {len(results)} 条数据',
                'data_count': len(results)
            }
        except Exception as e:
            print(f"crawler_service.run_crawler 异常: {str(e)}")
            print("错误堆栈:")
            traceback.print_exc()
            
            # 获取任务并更新状态为失败
            task = CollectionTask.query.get(task_id)
            if task:
                task.status = 'failed'
                task.error_message = str(e)
                db.session.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_crawler_status(self, task_id):
        """获取爬虫任务状态"""
        try:
            task = CollectionTask.query.get(task_id)
            if not task:
                return {'success': False, 'error': '任务不存在'}
            
            return {
                'success': True,
                'status': task.status,
                'last_run_time': task.last_run_time,
                'last_finish_time': task.last_finish_time,
                'total_collected': task.total_collected,
                'error_message': task.error_message
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# 创建爬虫服务实例
crawler_service = CrawlerService()