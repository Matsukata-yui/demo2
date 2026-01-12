from app.models import CrawlerConfig
from app import db
import json
import time
import sys
import os

# Add the dist directory to the path so we can import the Baidu spider
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dist')))

# Import the Baidu search spider
from baidusearch.baidu_spider import BaiduSearchSpider

class CrawlerSourceManager:
    """爬虫源管理器，负责动态加载和管理爬虫源配置"""
    
    def __init__(self):
        self.config_cache = {}
        self.last_update_time = 0
        self.cache_expiry = 5  # 缓存过期时间（秒）
    
    def get_all_crawler_configs(self, refresh=False):
        """获取所有爬虫源配置
        
        Args:
            refresh: 是否强制刷新缓存
            
        Returns:
            dict: 所有启用的爬虫源配置，格式为 {config_id: config_data}
        """
        # 检查缓存是否过期
        current_time = time.time()
        if refresh or current_time - self.last_update_time > self.cache_expiry:
            self._refresh_cache()
        
        return self.config_cache
    
    def get_crawler_config(self, config_id):
        """获取指定的爬虫源配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            dict: 爬虫源配置数据
        """
        # 确保缓存是最新的
        self._ensure_cache_fresh()
        
        return self.config_cache.get(config_id)
    
    def run_crawler_by_config(self, config_id, params=None):
        """根据配置运行爬虫

        Args:
            config_id: 配置ID
            params: 额外参数

        Returns:
            dict: 爬虫运行结果
        """
        try:
            # 获取配置
            config = self.get_crawler_config(config_id)
            if not config:
                return {"success": False, "error_code": "CONFIG_NOT_FOUND", "error_message": f"配置ID {config_id} 不存在或未启用"}
            
            # 标准化参数处理
            if params is None:
                params = {}
            
            # 参数验证
            try:
                self._validate_params(params)
            except ValueError as e:
                return {"success": False, "error_code": "PARAM_ERROR", "error_message": str(e)}
            
            # 解析配置
            try:
                request_params = json.loads(config.get('request_params', '{}'))
                headers = json.loads(config.get('headers', '{}'))
            except json.JSONDecodeError as e:
                return {"success": False, "error_code": "JSON_PARSE_ERROR", "error_message": f"配置解析失败: {str(e)}"}
            
            # 合并额外参数
            request_params.update(params)
            
            # 运行爬虫
            results = []
            
            # 检查是否为百度搜索配置
            if config.get('source_type') == 'baidu_search':
                # 使用真实的百度搜索爬虫
                try:
                    # 统一参数获取方式
                    keyword = request_params.get('wd', request_params.get('keyword', 'Python'))
                    page = int(request_params.get('pn', (request_params.get('page', 1) - 1) * 10)) // 10 + 1
                    limit = int(request_params.get('limit', 10))
                    
                    print(f"运行百度爬虫: 关键词='{keyword}', 页码={page}, 限制={limit}")
                    
                    spider = BaiduSearchSpider()
                    # 调用统一的run方法
                    real_results = spider.run(request_params)
                    
                    # 转换结果格式
                    for result in real_results:
                        results.append({
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("abstract", result.get("content", "")),
                            "timestamp": time.time()
                        })
                    
                    print(f"百度爬虫返回 {len(results)} 条结果")
                except Exception as e:
                    error_msg = f"百度爬虫运行失败: {str(e)}"
                    print(error_msg)
                    return {
                        "success": False, 
                        "error_code": "CRAWLER_ERROR", 
                        "error_message": error_msg,
                        "config": config
                    }
            else:
                # 对于其他配置，生成模拟结果
                try:
                    # 模拟其他爬虫的run方法
                    limit = int(request_params.get('limit', 3))
                    for i in range(limit):
                        results.append({
                            "url": f"{config['url']}/page/{i+1}",
                            "title": f"模拟结果 #{i+1}",
                            "content": f"这是模拟的爬虫结果内容 #{i+1}",
                            "timestamp": time.time()
                        })
                except Exception as e:
                    error_msg = f"爬虫运行失败: {str(e)}"
                    print(error_msg)
                    return {
                        "success": False, 
                        "error_code": "CRAWLER_ERROR", 
                        "error_message": error_msg,
                        "config": config
                    }
            
            # 检查结果是否为空
            if not results:
                return {
                    "success": False, 
                    "error_code": "NO_RESULTS", 
                    "error_message": "未找到匹配的数据",
                    "config": config
                }
            
            return {
                "success": True,
                "results": results,
                "config": config,
                "message": f"使用配置 {config['name']} 运行爬虫成功",
                "total_results": len(results)
            }
            
        except Exception as e:
            error_msg = f"内部错误: {str(e)}"
            print(error_msg)
            return {"success": False, "error_code": "INTERNAL_ERROR", "error_message": error_msg}
    
    def _validate_params(self, params):
        """验证参数

        Args:
            params: 要验证的参数字典

        Raises:
            ValueError: 如果参数验证失败
        """
        # 这里可以添加具体的参数验证逻辑
        # 例如：检查关键词长度、页码范围等
        if 'keyword' in params:
            keyword = params['keyword']
            if not isinstance(keyword, str):
                raise ValueError("关键词必须是字符串类型")
            if len(keyword.strip()) == 0:
                raise ValueError("关键词不能为空")
        
        if 'page' in params:
            page = params['page']
            if not isinstance(page, (int, float)):
                raise ValueError("页码必须是数字类型")
            if page < 1:
                raise ValueError("页码必须大于等于1")
        
        if 'limit' in params:
            limit = params['limit']
            if not isinstance(limit, (int, float)):
                raise ValueError("限制数量必须是数字类型")
            if limit < 1 or limit > 100:
                raise ValueError("限制数量必须在1-100之间")

    def run_crawler_by_source(self, source_name, params=None):
        """根据数据源类型运行爬虫

        Args:
            source_name: 数据源类型
            params: 额外参数

        Returns:
            dict: 爬虫运行结果
        """
        try:
            # 获取所有配置
            configs = self.get_all_crawler_configs()
            
            # 查找匹配的配置
            matched_configs = []
            for config_id, config in configs.items():
                if config.get('source_type') == source_name:
                    matched_configs.append(config)
            
            if not matched_configs:
                return {"success": False, "error_code": "SOURCE_NOT_FOUND", "error_message": f"未找到数据源类型为 {source_name} 的爬虫配置"}
            
            # 使用第一个匹配的配置
            config = matched_configs[0]
            
            # 标准化参数处理
            if params is None:
                params = {}
            
            # 解析配置
            try:
                request_params = json.loads(config.get('request_params', '{}'))
                headers = json.loads(config.get('headers', '{}'))
            except json.JSONDecodeError as e:
                return {"success": False, "error_code": "JSON_PARSE_ERROR", "error_message": f"配置解析失败: {str(e)}"}
            
            # 合并额外参数（额外参数优先级更高）
            request_params.update(params)
            
            # 参数验证
            try:
                self._validate_params(request_params)
            except ValueError as e:
                return {"success": False, "error_code": "PARAM_ERROR", "error_message": str(e)}
            
            # 运行爬虫
            results = []
            
            # 根据不同的数据源类型生成不同的结果
            if source_name == "baidu_search":
                try:
                    # 统一参数处理
                    keyword = request_params.get('wd', request_params.get('keyword', 'Python'))
                    page = int(request_params.get('pn', (request_params.get('page', 1) - 1) * 10)) // 10 + 1
                    limit = int(request_params.get('limit', 10))
                    
                    print(f"运行百度爬虫(按数据源): 关键词='{keyword}', 页码={page}, 限制={limit}")
                    print(f"使用配置: {config['name']}")
                    print(f"合并后的参数: {request_params}")
                    
                    # 使用真实的百度搜索爬虫
                    spider = BaiduSearchSpider()
                    # 调用统一的run方法
                    real_results = spider.run(request_params)
                    
                    # 转换结果格式
                    for result in real_results:
                        results.append({
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("abstract", ""),
                            "abstract": result.get("abstract", ""),
                            "timestamp": time.time()
                        })
                    
                    print(f"百度爬虫(按数据源)返回 {len(results)} 条结果")
                except Exception as e:
                    error_msg = f"百度爬虫运行失败: {str(e)}"
                    print(error_msg)
                    return {
                        "success": False, 
                        "error_code": "CRAWLER_ERROR", 
                        "error_message": error_msg,
                        "config": config
                    }
            else:
                # 默认模拟结果
                try:
                    limit = int(request_params.get("limit", 5))
                    for i in range(limit):
                        results.append({
                            "url": f"{config['url']}/item/{i+1}",
                            "title": f"{source_name} 结果 #{i+1}",
                            "content": f"这是 {source_name} 数据源的模拟结果 #{i+1}"
                        })
                except Exception as e:
                    error_msg = f"爬虫运行失败: {str(e)}"
                    print(error_msg)
                    return {
                        "success": False, 
                        "error_code": "CRAWLER_ERROR", 
                        "error_message": error_msg,
                        "config": config
                    }
            
            # 检查结果是否为空
            if not results:
                return {
                    "success": False, 
                    "error_code": "NO_RESULTS", 
                    "error_message": "未找到匹配的数据",
                    "config": config
                }
            
            return {
                "success": True,
                "results": results,
                "config": config,
                "message": f"使用 {source_name} 数据源运行爬虫成功",
                "total_results": len(results)
            }
            
        except ValueError as e:
            return {"success": False, "error_code": "PARAM_ERROR", "error_message": str(e)}
        except Exception as e:
            error_msg = f"内部错误: {str(e)}"
            print(error_msg)
            return {"success": False, "error_code": "INTERNAL_ERROR", "error_message": error_msg}
    
    def _refresh_cache(self):
        """刷新配置缓存"""
        try:
            # 查询所有启用的爬虫源配置
            configs = CrawlerConfig.query.filter_by(enabled=True).all()
            
            # 构建缓存
            new_cache = {}
            for config in configs:
                config_data = {
                    'id': config.id,
                    'name': config.name,
                    'url': config.url,
                    'request_method': config.request_method,
                    'headers': config.headers,
                    'request_params': config.request_params,
                    'source_type': config.source_type,
                    'crawl_interval': config.crawl_interval,
                    'timeout': config.timeout,
                    'retry_count': config.retry_count
                }
                new_cache[config.id] = config_data
            
            # 更新缓存
            self.config_cache = new_cache
            self.last_update_time = time.time()
            
        except Exception as e:
            # 缓存刷新失败时，使用旧缓存
            print(f"刷新爬虫源配置缓存失败: {e}")
    
    def _ensure_cache_fresh(self):
        """确保缓存是最新的"""
        current_time = time.time()
        if current_time - self.last_update_time > self.cache_expiry:
            self._refresh_cache()
    
    def create_crawler_config(self, name, url, source_type='website', crawl_interval=3600, 
                             enabled=True, headers=None, request_params=None, 
                             request_method='GET', parse_rules=None, 
                             timeout=10, retry_count=3, proxy=None):
        """创建爬虫配置
        
        Args:
            name: 爬虫源名称
            url: 目标网站URL
            source_type: 数据源类型
            crawl_interval: 爬取间隔
            enabled: 是否启用
            headers: 请求头
            request_params: 请求参数
            request_method: 请求方法
            parse_rules: 解析规则
            timeout: 超时时间
            retry_count: 重试次数
            proxy: 代理配置
            
        Returns:
            dict: 创建结果
        """
        try:
            # 检查名称是否已存在
            existing_config = CrawlerConfig.query.filter_by(name=name).first()
            if existing_config:
                return {'success': False, 'message': '爬虫源名称已存在'}
            
            # 创建新配置
            new_config = CrawlerConfig(
                name=name,
                url=url,
                source_type=source_type,
                crawl_interval=crawl_interval,
                enabled=enabled,
                headers=headers or '{}',
                request_params=request_params or '{}',
                request_method=request_method,
                parse_rules=parse_rules or '{}',
                timeout=timeout,
                retry_count=retry_count,
                proxy=proxy or '{}'
            )
            
            db.session.add(new_config)
            db.session.commit()
            
            # 刷新缓存
            self._refresh_cache()
            
            return {'success': True, 'message': '配置创建成功', 'config_id': new_config.id}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    def update_crawler_config(self, config_id, name=None, url=None, source_type=None, 
                             crawl_interval=None, enabled=None, headers=None, 
                             request_params=None, request_method=None, 
                             parse_rules=None, timeout=None, retry_count=None, 
                             proxy=None):
        """更新爬虫配置
        
        Args:
            config_id: 配置ID
            name: 爬虫源名称
            url: 目标网站URL
            source_type: 数据源类型
            crawl_interval: 爬取间隔
            enabled: 是否启用
            headers: 请求头
            request_params: 请求参数
            request_method: 请求方法
            parse_rules: 解析规则
            timeout: 超时时间
            retry_count: 重试次数
            proxy: 代理配置
            
        Returns:
            dict: 更新结果
        """
        try:
            # 获取配置
            config = CrawlerConfig.query.get(config_id)
            if not config:
                return {'success': False, 'message': '配置不存在'}
            
            # 检查名称是否已存在（如果更新名称）
            if name and name != config.name:
                existing_config = CrawlerConfig.query.filter_by(name=name).first()
                if existing_config:
                    return {'success': False, 'message': '爬虫源名称已存在'}
                config.name = name
            
            # 更新其他字段
            if url is not None:
                config.url = url
            if source_type is not None:
                config.source_type = source_type
            if crawl_interval is not None:
                config.crawl_interval = crawl_interval
            if enabled is not None:
                config.enabled = enabled
            if headers is not None:
                config.headers = headers
            if request_params is not None:
                config.request_params = request_params
            if request_method is not None:
                config.request_method = request_method
            if parse_rules is not None:
                config.parse_rules = parse_rules
            if timeout is not None:
                config.timeout = timeout
            if retry_count is not None:
                config.retry_count = retry_count
            if proxy is not None:
                config.proxy = proxy
            
            db.session.commit()
            
            # 刷新缓存
            self._refresh_cache()
            
            return {'success': True, 'message': '配置更新成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    def delete_crawler_config(self, config_id):
        """删除爬虫配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            dict: 删除结果
        """
        try:
            # 获取配置
            config = CrawlerConfig.query.get(config_id)
            if not config:
                return {'success': False, 'message': '配置不存在'}
            
            # 删除配置
            db.session.delete(config)
            db.session.commit()
            
            # 刷新缓存
            self._refresh_cache()
            
            return {'success': True, 'message': '配置删除成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}

# 创建全局爬虫源管理器实例
crawler_source_manager = CrawlerSourceManager()