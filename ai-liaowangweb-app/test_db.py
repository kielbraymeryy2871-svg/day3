from app import app, db
from app.models.collect_data import CollectData
from datetime import datetime

with app.app_context():
    print("Testing database connection...")
    try:
        # 创建表结构
        db.create_all()
        print("Tables created successfully")
        
        # 测试插入数据
        test_data = CollectData(
            title="Test Title",
            url="https://test.com",
            abstract="Test abstract",
            source="Test Source",
            keyword="test",
            cover_image="https://test.com/image.jpg"
        )
        db.session.add(test_data)
        db.session.commit()
        print("Data inserted successfully")
        
        # 查询测试
        found = CollectData.query.filter_by(url="https://test.com").first()
        print(f"Data found: {found.title}")
        
        # 更新测试
        found.title = "Updated Title"
        db.session.commit()
        print("Data updated successfully")
        
        # 删除测试
        db.session.delete(found)
        db.session.commit()
        print("Data deleted successfully")
        
        # 测试upsert逻辑
        upsert_data = CollectData(
            title="Upsert Test",
            url="https://upsert.com",
            abstract="Upsert test abstract",
            source="Test Source",
            keyword="test",
            cover_image="https://test.com/image.jpg"
        )
        
        # 检查是否存在
        existing = CollectData.query.filter_by(url="https://upsert.com").first()
        if existing:
            existing.title = "Updated Upsert Test"
            print("Upsert: Updated existing record")
        else:
            db.session.add(upsert_data)
            print("Upsert: Created new record")
        db.session.commit()
        
        # 再次检查
        check = CollectData.query.filter_by(url="https://upsert.com").first()
        print(f"Upsert result: {check.title}")
        
        print("Database test completed successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()