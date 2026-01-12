from app import create_app, db, bcrypt

app = create_app()

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    # 创建管理员用户
    from app.models import User
    
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
