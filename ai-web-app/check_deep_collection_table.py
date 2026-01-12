from app import create_app, db
from app.models import DeepCollectionData

app = create_app()

with app.app_context():
    # 检查所有表
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('All tables:', tables)
    
    # 检查DeepCollectionData表是否存在
    table_exists = 'deep_collection_data' in tables
    print('DeepCollectionData table exists:', table_exists)
    
    # 如果表不存在，创建它
    if not table_exists:
        print('Creating DeepCollectionData table...')
        db.create_all()
        print('DeepCollectionData table created successfully!')
    
    # 再次检查所有表
    tables_after = inspector.get_table_names()
    print('All tables after:', tables_after)
