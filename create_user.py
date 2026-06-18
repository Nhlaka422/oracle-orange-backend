from app.core.database import SessionLocal, engine
from app.models.user import User
from app.services.auth_service import AuthService
from sqlalchemy import inspect

def create_test_user():
    # Check if table exists
    inspector = inspect(engine)
    if 'users' not in inspector.get_table_names():
        print("⚠️ Users table doesn't exist. Creating it now...")
        User.__table__.create(engine)
        print("✅ Users table created!")
    
    db = SessionLocal()
    try:
        user = AuthService.create_user(
            db=db,
            full_name="Admin User",
            email="admin@oracle.com",
            password="admin123",
            role="admin"
        )
        if user:
            print(f"✅ Created user: {user.email}")
            print(f"   Password: admin123")
        else:
            print("⚠️ User already exists")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()