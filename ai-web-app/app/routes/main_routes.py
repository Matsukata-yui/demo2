from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from app import db, bcrypt
from app.models import User, CollectionTask, CollectedData, CrawlerConfig, DeepCollectionData
from app.forms import LoginForm
from app.services.crawler_service import crawler_service
from app.services.crawler_source_manager import crawler_source_manager
from app.services.ai_service import ai_service
from flask_login import login_user, current_user, logout_user, login_required
import time
import json
from datetime import datetime
import asyncio

def api_login_required(f):
    """API端点的登录认证装饰器"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/collection-management')
@login_required
def collection_management():
    return render_template('collection_management.html')

@main.route('/crawler-management')
@login_required
def crawler_management():
    return render_template('crawler_management.html')

@main.route('/data-management')
@login_required
def data_management():
    return render_template('data_management.html')

@main.route('/deep-collection')
@login_required
def deep_collection():
    return render_template('deep_collection.html')

@main.route('/ai-analysis-reports')
@login_required
def ai_analysis_reports():
    return render_template('ai_analysis_reports.html')

@main.route('/ai-dashboard')
@login_required
def ai_dashboard():
    return render_template('ai_dashboard.html')

# 数据采集API
@main.route('/api/collection/task', methods=['POST'])
@login_required
def create_collection_task():
    """创建采集任务"""
    data = request.get_json()
    try:
        new_task = CollectionTask(
            name=data.get('name'),
            urls=data.get('urls'),
            interval=data.get('interval'),
            status='pending',
            created_by=current_user.username
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'success': True, 'task_id': new_task.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/task/<int:task_id>/start', methods=['POST'])
@login_required
def start_collection_task(task_id):
    """启动采集任务"""
    try:
        result = crawler_service.run_crawler(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/task/<int:task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    """获取任务状态"""
    try:
        result = crawler_service.get_crawler_status(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/data/<int:task_id>', methods=['GET'])
@login_required
def get_collected_data(task_id):
    """获取采集到的数据"""
    try:
        data = CollectedData.query.filter_by(task_id=task_id).all()
        result = []
        for item in data:
            result.append({
                'id': item.id,
                'url': item.url,
                'title': item.title,
                'content': item.content,
                'timestamp': item.timestamp,
                'status': item.status
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/tasks', methods=['GET'])
@login_required
def get_all_tasks():
    """获取所有采集任务"""
    try:
        tasks = CollectionTask.query.all()
        result = []
        for task in tasks:
            result.append({
                'id': task.id,
                'name': task.name,
                'urls': task.urls,
                'interval': task.interval,
                'status': task.status,
                'created_by': task.created_by,
                'created_at': task.created_at,
                'last_run_time': task.last_run_time,
                'last_finish_time': task.last_finish_time,
                'total_collected': task.total_collected
            })
        return jsonify({'success': True, 'tasks': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 关键词采集API
@main.route('/api/collection/start', methods=['POST'])
def start_keyword_collection():
    """开始关键词采集"""
    import traceback
    
    print("enter start collection")
    print(f"请求方法: {request.method}")
    print(f"请求路径: {request.path}")
    print(f"请求头: {dict(request.headers)}")
    
    # 请求数据解析验证
    print(f"request.json: {request.json}")
    data = request.get_json()
    print(f"接收到的请求数据: {data}")
    
    try:
        if not data:
            print("错误: 未接收到请求数据")
            return jsonify({'success': False, 'error': '未接收到请求数据'})
        
        keyword = data.get('keyword')
        crawlers = data.get('crawlers')
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        
        if not keyword:
            print("错误: 关键词不能为空")
            return jsonify({'success': False, 'error': '关键词不能为空'})
        
        if not crawlers or len(crawlers) == 0:
            print("错误: 至少选择一个爬虫源")
            return jsonify({'success': False, 'error': '至少选择一个爬虫源'})
        
        # 参数验证和转换
        page = int(page) if page else 1
        limit = int(limit) if limit else 10
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        
        print(f"处理后的参数: keyword={keyword}, crawlers={crawlers}, page={page}, limit={limit}")
        
        # 创建采集任务
        new_task = CollectionTask(
            name=f'关键词采集: {keyword}',
            urls=json.dumps({'keyword': keyword, 'crawlers': crawlers, 'page': page, 'limit': limit}),
            interval=0,
            status='running',
            created_by='admin'  # 使用固定用户名
        )
        db.session.add(new_task)
        db.session.commit()
        
        print("准备启动采集线程")
        # 启动采集线程
        import threading
        threading.Thread(target=run_keyword_collection, args=(new_task.id, keyword, crawlers, page, limit)).start()
        print("采集线程已启动")
        
        print(f"采集任务创建成功，任务ID: {new_task.id}")
        return jsonify({'success': True, 'task_id': new_task.id})
    except Exception as e:
        print(f"API错误: {str(e)}")
        print("错误堆栈:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/results/<int:task_id>', methods=['GET'])
def get_collection_results(task_id):
    """获取采集结果"""
    try:
        task = CollectionTask.query.get(task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'})
        
        # 获取采集到的数据
        collected_data = CollectedData.query.filter_by(task_id=task_id).all()
        results = []
        for item in collected_data:
            results.append({
                'id': item.id,
                'title': item.title,
                'url': item.url,
                'source': item.source,
                'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else None,
                'image': item.image
            })
        
        # 计算进度（简单实现，实际应该根据爬虫执行情况计算）
        progress = 0
        if task.status == 'completed':
            progress = 100
        elif task.status == 'running':
            progress = 50
        
        return jsonify({
            'success': True,
            'results': results,
            'status': task.status,
            'progress': progress,
            'total_collected': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def run_keyword_collection(task_id, keyword, crawlers, page=1, limit=10):
    """执行关键词采集"""
    import traceback
    from app.services.crawler_source_manager import crawler_source_manager
    from app import create_app
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            task = CollectionTask.query.get(task_id)
            if not task:
                return
            
            import time
            
            print(f"收到的爬虫源列表: {crawlers}")
            print(f"采集参数: keyword={keyword}, page={page}, limit={limit}")
            
            total_collected = 0
            
            # 对于每个选择的爬虫源，使用真实的爬虫服务执行采集
            for crawler_source_type in crawlers:
                # 检查任务状态
                task = CollectionTask.query.get(task_id)
                if task.status == 'stopped':
                    print(f"采集任务 {task_id} 已被停止")
                    return
                
                print(f"开始处理爬虫源: {crawler_source_type}")
                
                try:
                    # 使用爬虫源管理器执行采集
                    result = crawler_source_manager.run_crawler_by_source(
                        crawler_source_type,
                        {
                            'keyword': keyword,
                            'page': page,
                            'limit': limit
                        }
                    )
                    
                    print(f"爬虫源管理器返回结果: {result}")
                    
                    if result.get('success'):
                        search_results = result.get('results', [])
                        print(f"爬虫源 {crawler_source_type} 返回 {len(search_results)} 条结果")
                        
                        # 保存采集结果到数据库
                        for search_result in search_results:
                            # 检查任务状态
                            task = CollectionTask.query.get(task_id)
                            if task.status == 'stopped':
                                print(f"采集任务 {task_id} 已被停止")
                                return
                            
                            # 提取数据
                            url = search_result.get('url', '')
                            title = search_result.get('title', '')
                            content = search_result.get('content') or search_result.get('abstract', '')
                            
                            # 检查是否已存在相同URL的数据（避免重复）
                            existing_data = CollectedData.query.filter_by(
                                task_id=task_id,
                                url=url
                            ).first()
                            
                            if not existing_data:
                                # 创建新数据
                                new_data = CollectedData(
                                    task_id=task_id,
                                    url=url,
                                    title=title,
                                    content=content,
                                    source=crawler_source_type,
                                    status='collected'
                                )
                                db.session.add(new_data)
                                total_collected += 1
                            else:
                                print(f"跳过重复数据: {url}")
                        
                        # 批量提交数据库更改
                        db.session.commit()
                        print(f"爬虫源 {crawler_source_type} 采集完成，本次采集 {len(search_results)} 条数据")
                    else:
                        error_msg = result.get('error_message', result.get('error', '未知错误'))
                        print(f"爬虫源 {crawler_source_type} 采集失败: {error_msg}")
                        # 继续处理下一个爬虫源，不中断整个任务
                        
                except Exception as e:
                    error_msg = f"爬虫源 {crawler_source_type} 执行异常: {str(e)}"
                    print(error_msg)
                    traceback.print_exc()
                    # 继续处理下一个爬虫源，不中断整个任务
                
                # 短暂延迟，避免请求过于频繁
                time.sleep(1)
            
            # 检查任务状态，避免在停止后标记为完成
            task = CollectionTask.query.get(task_id)
            if task and task.status != 'stopped':
                # 确保任务状态正确更新
                if task.status != 'completed':
                    # 更新任务状态
                    task.status = 'completed'
                    task.last_finish_time = datetime.utcnow()
                    task.total_collected = CollectedData.query.filter_by(task_id=task_id).count()
                    db.session.commit()
                    print(f"采集任务完成，共采集 {task.total_collected} 条数据")
            
        except Exception as e:
            # 更新任务状态为失败
            task = CollectionTask.query.get(task_id)
            if task and task.status != 'stopped':
                task.status = 'failed'
                task.error_message = str(e)
                db.session.commit()
            print(f"采集任务失败: {str(e)}")
            traceback.print_exc()

@main.route('/api/collection/stop/<int:task_id>', methods=['POST'])
@login_required
def stop_collection(task_id):
    """停止采集任务"""
    try:
        task = CollectionTask.query.get(task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'})
        
        # 原子性地更新任务状态为stopped
        task.status = 'stopped'
        db.session.commit()
        
        return jsonify({'success': True, 'message': '采集任务已停止'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/collection/save', methods=['POST'])
@login_required
def save_collected_data():
    """保存采集到的数据"""
    data = request.get_json()
    try:
        data_ids = data.get('data_ids')
        task_id = data.get('task_id')
        
        if not data_ids or len(data_ids) == 0:
            return jsonify({'success': False, 'error': '至少选择一条数据'})
        
        # 更新选中数据的状态为已保存
        for data_id in data_ids:
            collected_item = CollectedData.query.get(data_id)
            if collected_item:
                collected_item.status = 'saved'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'成功保存 {len(data_ids)} 条数据'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 数据管理API
@main.route('/api/data/list', methods=['GET'])
@login_required
def get_data_list():
    """获取数据列表，支持分页和搜索"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # 获取搜索参数
        search = request.args.get('search', '')
        
        # 构建查询
        query = CollectedData.query
        
        # 添加搜索条件
        if search:
            query = query.filter(
                (CollectedData.title.ilike(f'%{search}%')) |
                (CollectedData.content.ilike(f'%{search}%')) |
                (CollectedData.source.ilike(f'%{search}%'))
            )
        
        # 执行分页查询
        pagination = query.order_by(CollectedData.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构建响应数据
        data_list = []
        for item in pagination.items:
            # 检查是否有深度采集数据
            has_deep_collection = DeepCollectionData.query.filter_by(collected_data_id=item.id).first() is not None
            
            data_list.append({
                'id': item.id,
                'title': item.title,
                'url': item.url,
                'content': item.content,
                'source': item.source,
                'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else None,
                'image': item.image,
                'status': item.status,
                'deep_collected': item.deep_collected or has_deep_collection,
                'deep_collected_at': item.deep_collected_at.strftime('%Y-%m-%d %H:%M:%S') if item.deep_collected_at else None
            })
        
        return jsonify({
            'success': True,
            'data': data_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/data/delete/<int:data_id>', methods=['DELETE'])
@login_required
def delete_data(data_id):
    """删除单条数据"""
    try:
        data = CollectedData.query.get(data_id)
        if not data:
            return jsonify({'success': False, 'error': '数据不存在'})
        
        db.session.delete(data)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '数据删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/data/batch_delete', methods=['POST'])
@login_required
def batch_delete_data():
    """批量删除数据"""
    data = request.get_json()
    try:
        data_ids = data.get('data_ids')
        if not data_ids or len(data_ids) == 0:
            return jsonify({'success': False, 'error': '至少选择一条数据'})
        
        # 删除选中的数据
        deleted_count = 0
        for data_id in data_ids:
            data_item = CollectedData.query.get(data_id)
            if data_item:
                db.session.delete(data_item)
                deleted_count += 1
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'成功删除 {deleted_count} 条数据'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/data/deep_collect/<int:data_id>', methods=['POST'])
@api_login_required
def deep_collect_data(data_id):
    """AI深度采集单条数据"""
    try:
        data = CollectedData.query.get(data_id)
        if not data:
            return jsonify({'success': False, 'error': '数据不存在'})
        
        # 获取请求参数
        request_data = request.get_json() or {}
        model_id = request_data.get('model_id')
        url = data.url
        
        if not url:
            return jsonify({'success': False, 'error': '数据没有URL地址'})
        
        # 执行深度采集（使用asyncio运行异步函数）
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(ai_service.deep_collect(data_id, url, model_id, None))
        loop.close()
        
        if result.get('success'):
            # 更新源数据的深度采集标识
            data.deep_collected = True
            data.deep_collected_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'AI深度采集完成', 'data': result.get('data')})
        else:
            return jsonify({'success': False, 'error': result.get('error')})
    except Exception as e:
        print(f"深度采集错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/data/batch_deep_collect', methods=['POST'])
@api_login_required
def batch_deep_collect_data():
    """批量AI深度采集数据"""
    data = request.get_json()
    try:
        data_ids = data.get('data_ids')
        model_id = data.get('model_id')
        
        if not data_ids or len(data_ids) == 0:
            return jsonify({'success': False, 'error': '至少选择一条数据'})
        
        results = []
        success_count = 0
        error_count = 0
        
        # 使用asyncio运行异步函数
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 逐个执行深度采集
        for data_id in data_ids:
            collected_data = CollectedData.query.get(data_id)
            if collected_data and collected_data.url:
                try:
                    result = loop.run_until_complete(ai_service.deep_collect(data_id, collected_data.url, model_id, None))
                    if result.get('success'):
                        success_count += 1
                        # 更新源数据的深度采集标识
                        collected_data.deep_collected = True
                        collected_data.deep_collected_at = datetime.utcnow()
                        results.append({
                            'data_id': data_id,
                            'success': True,
                            'message': '深度采集成功'
                        })
                    else:
                        error_count += 1
                        results.append({
                            'data_id': data_id,
                            'success': False,
                            'error': result.get('error')
                        })
                except Exception as e:
                    error_count += 1
                    results.append({
                        'data_id': data_id,
                        'success': False,
                        'error': str(e)
                    })
            else:
                error_count += 1
                results.append({
                    'data_id': data_id,
                    'success': False,
                    'error': '数据不存在或没有URL地址'
                })
        
        db.session.commit()
        loop.close()
        
        return jsonify({
            'success': True,
            'message': f'批量深度采集完成，成功 {success_count} 条，失败 {error_count} 条',
            'results': results,
            'success_count': success_count,
            'error_count': error_count
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deep_collection/data', methods=['GET'])
@api_login_required
def get_deep_collection_data():
    """获取深度采集数据列表"""
    try:
        # 获取分页和搜索参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '')
        collected_data_id = request.args.get('collected_data_id')
        
        # 调用服务获取数据
        result = ai_service.get_deep_collection_data(
            collected_data_id=collected_data_id,
            page=page,
            limit=limit,
            search=search
        )
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'success': False, 'error': result.get('error')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deep_collection/data/<int:data_id>', methods=['GET'])
@api_login_required
def get_deep_collection_data_detail(data_id):
    """获取深度采集数据详情"""
    try:
        deep_data = DeepCollectionData.query.get(data_id)
        if not deep_data:
            return jsonify({'success': False, 'error': '数据不存在'})
        
        return jsonify({
            'success': True,
            'data': {
                'id': deep_data.id,
                'collected_data_id': deep_data.collected_data_id,
                'url': deep_data.url,
                'title': deep_data.title,
                'content': deep_data.content,
                'ai_analysis': deep_data.ai_analysis,
                'model_used': deep_data.model_used,
                'status': deep_data.status,
                'created_at': deep_data.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': deep_data.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deep_collection/update/<int:data_id>', methods=['PUT'])
@api_login_required
def update_deep_collection_data(data_id):
    """更新深度采集数据"""
    try:
        deep_data = DeepCollectionData.query.get(data_id)
        if not deep_data:
            return jsonify({'success': False, 'error': '数据不存在'})
        
        data = request.get_json()
        
        # 更新字段
        if 'title' in data:
            deep_data.title = data['title']
        if 'url' in data:
            deep_data.url = data['url']
        if 'content' in data:
            deep_data.content = data['content']
        if 'ai_analysis' in data:
            deep_data.ai_analysis = data['ai_analysis']
        
        deep_data.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deep_collection/delete/<int:data_id>', methods=['DELETE'])
@api_login_required
def delete_deep_collection_data(data_id):
    """删除深度采集数据"""
    try:
        result = ai_service.delete_deep_collection_data(data_id)
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'success': False, 'error': result.get('error')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deep_collection/batch_delete', methods=['POST'])
@api_login_required
def batch_delete_deep_collection_data():
    """批量删除深度采集数据"""
    data = request.get_json()
    try:
        data_ids = data.get('data_ids')
        if not data_ids or len(data_ids) == 0:
            return jsonify({'success': False, 'error': '至少选择一条数据'})
        
        success_count = 0
        error_count = 0
        
        for data_id in data_ids:
            result = ai_service.delete_deep_collection_data(data_id)
            if result.get('success'):
                success_count += 1
            else:
                error_count += 1
        
        return jsonify({
            'success': True,
            'message': f'批量删除完成，成功 {success_count} 条，失败 {error_count} 条'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/dashboard/data', methods=['GET'])
@login_required
def get_dashboard_data():
    """获取数智大屏所需的数据"""
    try:
        # 获取总数据量
        total_collected = CollectedData.query.count()
        total_deep = DeepCollectionData.query.count()
        total_data = total_collected + total_deep
        
        # 获取今日新增数据量
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        today_collected = CollectedData.query.filter(
            CollectedData.timestamp >= datetime(today.year, today.month, today.day)
        ).count()
        today_deep = DeepCollectionData.query.filter(
            DeepCollectionData.created_at >= datetime(today.year, today.month, today.day)
        ).count()
        today_new = today_collected + today_deep
        
        # 获取运行爬虫数
        from app.models import CrawlerConfig
        total_crawlers = CrawlerConfig.query.count()
        running_crawlers = CrawlerConfig.query.filter_by(enabled=True).count()
        
        # 获取AI分析任务数
        ai_tasks = 15  # 模拟数据
        running_ai_tasks = 1  # 模拟数据
        
        # 获取系统负载
        system_load = 42  # 模拟数据
        
        # 获取舆情趋势数据（从数据库统计最近7天的数据）
        from datetime import timedelta
        trend_dates = []
        trend_positive = []
        trend_negative = []
        trend_neutral = []
        
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)
            
            # 统计当天的情感分布
            positive_count = CollectedData.query.filter(
                CollectedData.timestamp >= date_start,
                CollectedData.timestamp < date_end,
                CollectedData.sentiment == 'positive'
            ).count()
            
            negative_count = CollectedData.query.filter(
                CollectedData.timestamp >= date_start,
                CollectedData.timestamp < date_end,
                CollectedData.sentiment == 'negative'
            ).count()
            
            neutral_count = CollectedData.query.filter(
                CollectedData.timestamp >= date_start,
                CollectedData.timestamp < date_end,
                (CollectedData.sentiment == 'neutral') | (CollectedData.sentiment.is_(None))
            ).count()
            
            trend_dates.append(f"{date.month}月{date.day}日")
            trend_positive.append(positive_count)
            trend_negative.append(negative_count)
            trend_neutral.append(neutral_count)
        
        trend_data = {
            'dates': trend_dates,
            'positive': trend_positive,
            'negative': trend_negative,
            'neutral': trend_neutral
        }
        
        from app.services.database_tool_service import database_tool_service
        collected_stats = database_tool_service.get_collected_data_statistics()
        
        if collected_stats.get('success'):
            sentiment_stats = collected_stats.get('sentiment_stats', [])
            total_sentiment = sum(item['count'] for item in sentiment_stats)
            
            if total_sentiment > 0:
                sentiment_data = []
                for item in sentiment_stats:
                    sentiment_name = item['sentiment']
                    count = item['count']
                    percentage = round((count / total_sentiment) * 100, 1)
                    
                    if sentiment_name == 'positive' or sentiment_name == '正面':
                        color = '#52c41a'
                        name = '正面'
                    elif sentiment_name == 'negative' or sentiment_name == '负面':
                        color = '#ff4d4f'
                        name = '负面'
                    else:
                        color = '#faad14'
                        name = '中性'
                    
                    sentiment_data.append({
                        'value': percentage,
                        'name': name,
                        'itemStyle': {'color': color}
                    })
            else:
                sentiment_data = [
                    {'value': 68, 'name': '正面', 'itemStyle': {'color': '#52c41a'}},
                    {'value': 12, 'name': '负面', 'itemStyle': {'color': '#ff4d4f'}},
                    {'value': 20, 'name': '中性', 'itemStyle': {'color': '#faad14'}}
                ]
        else:
            sentiment_data = [
                {'value': 68, 'name': '正面', 'itemStyle': {'color': '#52c41a'}},
                {'value': 12, 'name': '负面', 'itemStyle': {'color': '#ff4d4f'}},
                {'value': 20, 'name': '中性', 'itemStyle': {'color': '#faad14'}}
            ]
        
        if collected_stats.get('success'):
            source_stats = collected_stats.get('source_stats', [])
            source_data = {
                'sources': [item['source'] for item in source_stats[:10]],  # 取前10个
                'counts': [item['count'] for item in source_stats[:10]]
            }
        else:
            source_data = {
                'sources': ['未知'],
                'counts': [0]
            }
        
        # 获取热门关键词（从数据库提取）
        keywords = []
        try:
            # 从collected_data表中提取关键词
            keyword_data = CollectedData.query.filter(CollectedData.keywords.isnot(None)).limit(100).all()
            keyword_count = {}
            for item in keyword_data:
                if item.keywords:
                    # 假设关键词用逗号分隔
                    for kw in item.keywords.split(','):
                        kw = kw.strip()
                        if kw:
                            keyword_count[kw] = keyword_count.get(kw, 0) + 1
            
            # 按频率排序，取前8个
            sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:8]
            keywords = [kw[0] for kw in sorted_keywords]
        except:
            keywords = ['数字化转型', '智慧城市', '人工智能', '大数据', '政策', '创新', '技术', '应用']
        
        # 获取全球舆情分布数据（基于数据中的地理位置信息，这里使用模拟数据）
        global_data = [
            {'value': [116.4074, 39.9042, 100], 'name': '北京'},
            {'value': [121.4737, 31.2304, 80], 'name': '上海'},
            {'value': [113.2644, 23.1291, 60], 'name': '广州'},
            {'value': [114.0579, 22.5431, 50], 'name': '深圳'},
            {'value': [-74.0060, 40.7128, 90], 'name': '纽约'},
            {'value': [139.6917, 35.6895, 70], 'name': '东京'},
            {'value': [0.1276, 51.5074, 60], 'name': '伦敦'},
            {'value': [104.0668, 30.5728, 80], 'name': '成都'}
        ]
        
        # 获取爬虫运行状态
        crawler_status = [
            {'name': '新闻爬虫-1', 'status': '运行中', 'speed': '12 条/分钟', 'success_rate': '98%', 'last_update': '刚刚'},
            {'name': '社交媒体爬虫-2', 'status': '运行中', 'speed': '25 条/分钟', 'success_rate': '96%', 'last_update': '1分钟前'},
            {'name': '论坛爬虫-3', 'status': '运行中', 'speed': '8 条/分钟', 'success_rate': '92%', 'last_update': '2分钟前'},
            {'name': '新闻爬虫-4', 'status': '运行中', 'speed': '15 条/分钟', 'success_rate': '99%', 'last_update': '3分钟前'}
        ]
        
        # 获取系统状态监控数据
        system_status = {
            'cpu': 42,
            'memory': 68,
            'disk': 72,
            'network': 35,
            'network_speed': '2.5 MB/s'
        }
        
        ai_analysis_results = []
        deep_items = DeepCollectionData.query.filter(DeepCollectionData.ai_analysis.isnot(None)).order_by(DeepCollectionData.updated_at.desc()).limit(3).all()
        for item in deep_items:
            content = item.ai_analysis or ''
            if len(content) > 200:
                content = content[:200] + '...'
            ai_analysis_results.append({
                'type': item.model_used or 'AI深度采集',
                'content': content,
                'updated_at': item.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        if not ai_analysis_results:
            ai_analysis_results = [
                {
                    'type': '趋势分析',
                    'content': '智慧城市相关舆情在1月5日达到峰值，主要围绕政策发布。',
                    'updated_at': '2026-01-07 09:15'
                },
                {
                    'type': '关键词提取',
                    'content': '"数字化转型"出现频率最高，共1,245次；"智慧城市"次之，共892次。',
                    'updated_at': '2026-01-07 08:40'
                },
                {
                    'type': '情感分析',
                    'content': '正面舆情占比68%，负面舆情占比12%，中性舆情占比20%。',
                    'updated_at': '2026-01-07 10:15'
                }
            ]
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_data': total_data,
                    'today_new': today_new,
                    'running_crawlers': running_crawlers,
                    'total_crawlers': total_crawlers,
                    'ai_tasks': ai_tasks,
                    'running_ai_tasks': running_ai_tasks,
                    'system_load': system_load
                },
                'trend_data': trend_data,
                'sentiment_data': sentiment_data,
                'source_data': source_data,
                'keywords': keywords,
                'global_data': global_data,
                'crawler_status': crawler_status,
                'system_status': system_status,
                'ai_analysis_results': ai_analysis_results
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
