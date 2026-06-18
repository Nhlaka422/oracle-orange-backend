from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta, datetime
from ..core.database import get_db
from ..services.auth_service import AuthService
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Pydantic models
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

# Forgot Password Models
class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user = AuthService.create_user(
        db=db,
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user

@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = AuthService.authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user info"""
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    email = payload.get("sub")
    user = AuthService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to get current user for other routes"""
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    email = payload.get("sub")
    user = AuthService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ===== FORGOT PASSWORD ENDPOINTS =====

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset - sends reset link to email"""
    user = AuthService.get_user_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists for security reasons
        return {
            "message": "If your email exists, you will receive a reset link",
            "reset_token": None
        }
    
    # Generate reset token
    token = user.generate_reset_token()
    db.commit()
    
    # In production, send email with reset link
    # For demo, return the token in response
    return {
        "message": "Password reset link sent to your email",
        "reset_token": token,  # Remove this in production, only for demo
        "reset_link": f"http://localhost:3000/reset-password?token={token}"
    }

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    # Find user with this token
    user = db.query(User).filter(User.reset_token == request.token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if not user.verify_reset_token(request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired. Please request a new one."
        )
    //tfrtyrfyt
    # Update password
    user.set_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully! Please login with your new password."}

@router.post("/validate-reset-token")
def validate_reset_token(request: dict, db: Session = Depends(get_db)):
    """Validate if a reset token is valid"""
    token = request.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        return {"valid": False, "message": "Invalid token"}
    
    if not user.verify_reset_token(token):
        return {"valid": False, "message": "Token has expired"}
    
    return {"valid": True, "message": "Token is valid", "email": user.email}