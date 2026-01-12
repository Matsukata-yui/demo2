from app import create_app, bcrypt
from app.models import User

app = create_app()
with app.app_context():
    # 获取admin用户
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f'找到用户: {user.username}')
        print(f'存储的密码哈希: {user.password}')
        
        # 测试密码验证
        test_passwords = ['admin123', 'wrongpassword']
        for password in test_passwords:
            is_valid = bcrypt.check_password_hash(user.password, password)
            print(f'密码 "{password}" 验证: {is_valid}')
    else:
        print('未找到admin用户')
