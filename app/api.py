import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# additional dependency for the proxy
import httpx
from pydantic import BaseModel
from jose import jwt, JWTError
from dotenv import load_dotenv

from src.database.manager import DatabaseManager
from src.llm.research_agent import ResearchAgent

load_dotenv()

# `api` contains all of our JSON endpoints. We'll mount it later under
# `/api` so that we can run a small proxy that forwards everything else to the
# Streamlit dashboard (which listens on localhost:8501).
api = FastAPI(title="NexusIntel API")

# outer application used by Uvicorn. requests to `/api/*` are handled by the
# `api` instance; all other paths are proxied to Streamlit.
app = FastAPI()
app.mount("/api", api)

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

# using init to avoid startup failures on Render
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


# ----- proxy middleware ---------------------------------------------------
# when the application is deployed the Streamlit dashboard will be started
# concurrently (on the same container) at port 8501.  Because Railway only
# exposes a single public port ($PORT) we need to funnel all non-API traffic
# through this FastAPI process and forward it to Streamlit.  This lets the
# backend and dashboard share the same URL/domain; the dashboard is reachable
# at the root path while the JSON API remains under "/api".

@app.middleware("http")
async def proxy_to_streamlit(request: Request, call_next):
    # only proxy when request is not targeting our mounted `/api` application
    if not request.url.path.startswith("/api"):
        # build new url pointing to the local Streamlit instance
        upstream = httpx.URL(f"http://127.0.0.1:8501{request.url.path}")
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                request.method,
                upstream,
                headers={k: v for k, v in request.headers.items()},
                content=await request.body(),
                params=request.query_params,
                timeout=None,
                follow_redirects=True,
            )
            return fastapi.Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=resp.headers,
            )
    return await call_next(request)
