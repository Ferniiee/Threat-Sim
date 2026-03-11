from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import User, AuditLog
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import os

router = APIRouter(prefix="/auth", tags=["auth"])

# This handles password hashing - NEVER store plain text passwords
# bcrypt is the industry standard hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"  # the algorithm used to sign JWT tokens
TOKEN_EXPIRE_HOURS = 24

# --- HELPER FUNCTIONS ---

def hash_password(password: str) -> str:
    # turns "mypassword123" into "$2b$12$..." (unreadable hash)
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # checks if a plain password matches a stored hash
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int, role: str) -> str:
    # JWT = JSON Web Token
    # It's a signed string that proves who you are without hitting the DB every request
    payload = {
        "sub": str(user_id),     # "sub" = subject (who this token is for)
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)  # expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# --- REQUEST BODY SHAPES ---

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "admin"

class LoginRequest(BaseModel):
    email: str
    password: str

# --- ENDPOINTS ---

@router.post("/register")
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    # Check if email already exists
    existing = session.exec(select(User).where(User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with hashed password
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        role=req.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Log this action to audit log (SOC2 pattern)
    log = AuditLog(
        user_id=user.id,
        action="user_registered",
        detail=f"New user registered: {user.email} with role {user.role}"
    )
    session.add(log)
    session.commit()

    return {"message": "User created successfully", "user_id": user.id}

@router.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_session)):
    # Find user by email
    user = session.exec(select(User).where(User.email == req.email)).first()
    
    # Check user exists AND password is correct
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT token
    token = create_token(user.id, user.role)

    # Log login to audit log
    log = AuditLog(
        user_id=user.id,
        action="user_login",
        detail=f"User logged in: {user.email}"
    )
    session.add(log)
    session.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }