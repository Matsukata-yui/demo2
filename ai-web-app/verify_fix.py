from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = [column['name'] for column in inspector.get_columns('collected_data')]
    print('Updated columns in collected_data:', columns)
    
    # 检查是否包含新添加的字段
    if 'deep_collected' in columns and 'deep_collected_at' in columns:
        print("✅ Fix successful! Both deep_collected and deep_collected_at fields are present.")
    else:
        print("❌ Fix failed! Some fields are missing.")
