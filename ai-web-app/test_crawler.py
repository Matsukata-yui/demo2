from app import create_app, db
from app.models import CollectionTask
from app.services.crawler_service import crawler_service
import time

# 创建应用实例
app = create_app()

with app.app_context():
    # 创建一个测试任务
    task = CollectionTask(
        name='测试任务',
        urls='https://www.baidu.com,https://www.sina.com.cn',
        interval=3600,
        created_by='admin'
    )
    db.session.add(task)
    db.session.commit()
    
    print(f'创建测试任务成功，任务ID：{task.id}')
    print(f'任务状态：{task.status}')
    
    # 运行爬虫任务
    result = crawler_service.run_crawler(task.id)
    print(f'爬虫任务执行结果：{result}')
    
    # 等待爬虫完成
    time.sleep(10)
    
    # 检查任务状态
    status = crawler_service.get_crawler_status(task.id)
    print(f'爬虫任务最终状态：{status}')
    
    # 清理测试数据
    db.session.delete(task)
    db.session.commit()
    print('测试数据已清理')