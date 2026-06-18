from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.user import User
from ..core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Create JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not user.check_password(password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, full_name: str, email: str, password: str, role: str = "user"):
        """Create new user"""
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return None
        
        user = User(full_name=full_name, email=email, role=role)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()