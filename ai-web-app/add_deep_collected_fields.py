"""
数据库迁移脚本：为CollectedData表添加深度采集标识字段
"""
from app import create_app, db
from app.models import CollectedData
from sqlalchemy import text

def add_deep_collected_fields():
    """添加深度采集标识字段"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('collected_data')]
            
            if 'deep_collected' not in columns:
                # 添加deep_collected字段
                db.session.execute(text("ALTER TABLE collected_data ADD COLUMN deep_collected BOOLEAN DEFAULT 0"))
                print("✓ 已添加 deep_collected 字段")
            else:
                print("✓ deep_collected 字段已存在")
            
            if 'deep_collected_at' not in columns:
                # 添加deep_collected_at字段
                db.session.execute(text("ALTER TABLE collected_data ADD COLUMN deep_collected_at DATETIME"))
                print("✓ 已添加 deep_collected_at 字段")
            else:
                print("✓ deep_collected_at 字段已存在")
            
            # 更新已有深度采集数据的标识
            # 查找所有有深度采集数据的源数据
            result = db.session.execute(text("""
                SELECT DISTINCT collected_data_id 
                FROM deep_collection_data
            """))
            
            collected_data_ids = [row[0] for row in result]
            
            if collected_data_ids:
                placeholders = ','.join(['?' for _ in collected_data_ids])
                db.session.execute(text(f"""
                    UPDATE collected_data 
                    SET deep_collected = 1 
                    WHERE id IN ({placeholders})
                """), collected_data_ids)
                print(f"✓ 已更新 {len(collected_data_ids)} 条源数据的深度采集标识")
            
            db.session.commit()
            print("✓ 数据库迁移完成")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 数据库迁移失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_deep_collected_fields()

