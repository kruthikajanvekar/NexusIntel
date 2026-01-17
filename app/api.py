import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from dotenv import load_dotenv

from src.database.manager import DatabaseManager
from src.llm.research_agent import ResearchAgent

load_dotenv()

app = FastAPI(title="NexusIntel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

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

# Lazy init to avoid startup failures on Render
db_manager = None
research_agent = None

def get_db():
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_agent():
    global research_agent
    if research_agent is None:
        research_agent = ResearchAgent()
    return research_agent

SECRET_KEY = os.getenv("SECRET_KEY", "nexus_internal_secure_key_2025")
ALGORITHM = "HS256"

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/")
async def health():
    return {"status": "online", "service": "nexus-intel-api"}

@app.post("/login")
async def login(req: LoginRequest, db=Depends(get_db)):
    db.log_user(req.email, req.password)
    token = jwt.encode({"sub": req.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/analyze", response_model=DiscoveryResult)
async def analyze(req: AnalysisRequest, current_user: dict = Depends(get_current_user), agent=Depends(get_agent), db=Depends(get_db)):
    result = agent.perform_discovery(req.url)
    db.save_record(result)
    return result

@app.get("/history")
async def fetch_history(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    return db.get_all_records()

@app.delete("/history/{record_id}")
async def remove_record(record_id: int, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    db.delete_record(record_id)
    return {"status": "deleted"}
