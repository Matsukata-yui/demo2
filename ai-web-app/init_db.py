from app import create_app, db

app = create_app()

with app.app_context():
    print('Initializing database...')
    
    # 删除所有表（如果存在）
    db.drop_all()
    print('Dropped all existing tables')
    
    # 创建所有表
    db.create_all()
    print('Created all tables')
    
    # 创建管理员用户
    from app.models import User
    from app import bcrypt
    
    # 检查是否已经存在管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # 创建新的管理员用户
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', email='admin@example.com', password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully!')
    else:
        print('Admin user already exists!')
    
    # 检查CollectedData表结构
    from app.models import CollectedData
    print('\nChecking CollectedData table structure...')
    
    # 使用sqlite3检查表结构
    import sqlite3
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(collected_data);")
    columns = [row[1] for row in cursor.fetchall()]
    print('Columns:', columns)
    print('Has source column:', 'source' in columns)
    print('Has image column:', 'image' in columns)
    
    conn.close()
    
    print('\nDatabase initialization completed!')
