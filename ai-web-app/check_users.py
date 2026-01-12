from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print('现有用户:')
    for user in users:
        print(f'ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}')
    
    if not users:
        print('\n未找到用户，需要创建admin用户')
