from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_tables
from contextlib import asynccontextmanager
from routers import auth, campaigns, targets, tracking, analytics  # ← added analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    print("✅ Database tables created")
    yield
    print("Server shutting down")

app = FastAPI(
    title="ThreatSim API",
    description="Phishing simulation and security awareness platform",
    version="0.1.0",
    lifespan=lifespan
)

# Update allow_origins with your deployed frontend URL when ready
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # "https://your-frontend.vercel.app",  # ← add after deploy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(targets.router)
app.include_router(tracking.router)
app.include_router(analytics.router)   # ← added

@app.get("/")
def root():
    return {"message": "ThreatSim API is running"}

from fastapi.security import OAuth2PasswordBearer
from fastapi import Security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user