from app.core.database import engine
from app.models.user import User
from sqlalchemy import inspect

def create_users_table():
    """Create the users table if it doesn't exist"""
    inspector = inspect(engine)
    
    if 'users' not in inspector.get_table_names():
        print("📦 Creating users table...")
        User.__table__.create(engine)
        print("✅ Users table created successfully!")
    else:
        print("✅ Users table already exists!")

if __name__ == "__main__":
    create_users_table()