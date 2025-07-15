from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import uvicorn
from main import BinarybrainedSystem
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

# Mock user database (replace with real DB in production)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.system = BinarybrainedSystem()
    await app.state.system.initialize()
    logging.info("Binarybrained system initialized and ready")
    yield
    # Shutdown
    # Add any cleanup code here

app = FastAPI(title="Binarybrained AI API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: dict):
    # In a real app, you would:
    # 1. Validate input
    # 2. Hash password
    # 3. Store in database
    return {"message": "User registered successfully", "user": user_data}

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/api/auth/check-auth")
async def check_auth(current_user: User = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user}

@app.post("/api/auth/logout")
async def logout():
    return {"message": "Successfully logged out"}

# Existing endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Binarybrained AI is running"}

@app.get("/api/chat/status")
async def get_system_status():
    status = app.state.system.get_system_status()
    return JSONResponse(status)

@app.post("/api/chat")
async def process_chat_message(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get actual response from your AI system
        result = await app.state.system.process_request(user_input)
        
        # Format the response properly
        return {
            "response": result["response"],
            "metadata": {
                "agents_used": result.get("metadata", {}).get("agents", []),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Binarybrained AI API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")