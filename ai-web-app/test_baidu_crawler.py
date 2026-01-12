from app import create_app, db
from app.models import CollectionTask
from app.services.crawler_service import crawler_service
import time

# 创建应用实例
app = create_app()

with app.app_context():
    # 创建一个百度搜索测试任务
    task = CollectionTask(
        name='百度搜索测试任务',
        urls='baidu_search:四川美食:1:5',  # 百度搜索格式：baidu_search:关键词:页码:数量
        interval=3600,
        created_by='admin'
    )
    db.session.add(task)
    db.session.commit()
    
    print(f'创建百度搜索测试任务成功，任务ID：{task.id}')
    print(f'任务状态：{task.status}')
    
    # 运行百度搜索爬虫任务
    result = crawler_service.run_crawler(task.id)
    print(f'百度搜索爬虫任务执行结果：{result}')
    
    # 等待爬虫完成
    time.sleep(10)
    
    # 检查任务状态
    status = crawler_service.get_crawler_status(task.id)
    print(f'百度搜索爬虫任务最终状态：{status}')
    
    # 查询采集到的数据
    from app.models import CollectedData
    collected_data = CollectedData.query.filter_by(task_id=task.id).all()
    print(f'共采集到 {len(collected_data)} 条数据：')
    for i, data in enumerate(collected_data, 1):
        print(f'\n数据 {i}:')
        print(f'标题: {data.title}')
        print(f'URL: {data.url}')
        print(f'内容摘要: {data.content[:100]}...')
    
    # 清理测试数据
    db.session.delete(task)
    db.session.commit()
    print('\n测试数据已清理')
