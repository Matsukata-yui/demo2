from app import create_app, db
from app.models import CollectedData
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    # 检查CollectedData表是否存在deep_collected字段
    inspector = inspect(db.engine)
    columns = [column['name'] for column in inspector.get_columns('collected_data')]
    
    print(f"Current columns in collected_data: {columns}")
    
    # 使用SQLAlchemy 2.0+的语法执行SQL语句
    with db.engine.connect() as conn:
        # 如果deep_collected字段不存在，添加它
        if 'deep_collected' not in columns:
            print("Adding deep_collected column...")
            conn.execute(text('ALTER TABLE collected_data ADD COLUMN deep_collected BOOLEAN DEFAULT 0'))
            conn.commit()
        
        # 如果deep_collected_at字段不存在，添加它
        if 'deep_collected_at' not in columns:
            print("Adding deep_collected_at column...")
            conn.execute(text('ALTER TABLE collected_data ADD COLUMN deep_collected_at DATETIME'))
            conn.commit()
    
    print("Database schema updated successfully!")
