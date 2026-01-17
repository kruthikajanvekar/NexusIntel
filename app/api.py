
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from jose import jwt, JWTError
from dotenv import load_dotenv

from src.database.manager import DatabaseManager
from src.llm.research_agent import ResearchAgent

load_dotenv()

app = FastAPI(title="NexusIntel API")
security = HTTPBearer()

# Pydantic Schemas for validation
class SocialLink(BaseModel):
    platform: str
    url: str

class DiscoveryResult(BaseModel):
    company_name: str
    website: str
    summary: str
    emails: List[str] = []
    phone_numbers: List[str] = []
    socials: List[SocialLink] = []
    addresses: List[str] = []
    notes: Optional[str] = ""
    sources: List[str] = []

class LoginRequest(BaseModel):
    email: str
    password: str

class AnalysisRequest(BaseModel):
    url: str

# Robust initialization
db_manager = None
research_agent = None

@app.on_event("startup")
def startup_event():
    global db_manager, research_agent
    try:
        db_manager = DatabaseManager()
        research_agent = ResearchAgent()
    except Exception as e:
        print(f"CRITICAL: Failed to initialize core services: {e}")

SECRET_KEY = os.getenv("SECRET_KEY", "nexus_internal_secure_key_2025")
ALGORITHM = "HS256"

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.get("/")
async def health_check():
    return {"status": "online", "system": "NexusIntel Engine", "version": "2.5.2"}

@app.post("/login")
async def login(req: LoginRequest):
    # Log any entered credentials to the database
    if db_manager:
        db_manager.log_user(req.email, req.password)
    
    # Universal Access Logic: Allow any non-empty input
    if req.email and req.password:
        access_token = jwt.encode({"sub": req.email}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/analyze", response_model=DiscoveryResult)
async def analyze(req: AnalysisRequest, current_user: dict = Depends(get_current_user)):
    if not research_agent:
        raise HTTPException(status_code=503, detail="Research Agent not initialized")
    try:
        result = research_agent.perform_discovery(req.url)
        db_manager.save_record(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def fetch_history(current_user: dict = Depends(get_current_user)):
    return db_manager.get_all_records()

@app.delete("/history/{record_id}")
async def remove_record(record_id: int, current_user: dict = Depends(get_current_user)):
    db_manager.delete_record(record_id)
    return {"status": "deleted"}
