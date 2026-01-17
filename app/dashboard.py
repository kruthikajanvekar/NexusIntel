
import streamlit as st
import requests
import json
import os
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="NexusIntel | Intelligence Unit",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UI STYLING (Dark Bluish Chromo Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Background & Text */
    .stApp {
        background-color: #020617; /* Deepest Midnight */
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Inputs - FIXED HIGH-CONTRAST VISIBILITY */
    .stTextInput > label {
        color: #818cf8 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    /* Typed text and input box styling */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 2px solid #334155 !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        background-color: #0f172a !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
    }
    /* Placeholder text visibility */
    .stTextInput input::placeholder {
        color: #475569 !important;
        opacity: 1;
    }

    /* Report Header - Chrome Gradient */
    .report-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 1.25rem 1.25rem 0 0;
        border: 1px solid #312e81;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: -1px;
    }
    
    .status-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        padding: 0.4rem 0.8rem;
        border-radius: 2rem;
        font-size: 0.7rem;
        font-weight: 800;
        border: 1px solid rgba(99, 102, 241, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .report-body {
        background: #0f172a;
        padding: 2.5rem;
        border-radius: 0 0 1.25rem 1.25rem;
        border: 1px solid #1e293b;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    .label-caps {
        font-size: 0.7rem;
        font-weight: 800;
        color: #6366f1; /* Electric Blue Accent */
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .label-caps::after {
        content: "";
        flex-grow: 1;
        height: 1px;
        background: linear-gradient(to right, #1e293b, transparent);
    }

    /* Intelligence Values */
    .extraction-item {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
        border-left: 2px solid transparent;
        transition: all 0.2s;
    }
    .extraction-item:hover {
        border-left: 2px solid #6366f1;
        color: #f8fafc;
        background: rgba(99, 102, 241, 0.05);
    }

    .insight-panel {
        background: #020617;
        padding: 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid #1e293b;
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.7;
        font-style: italic;
    }

    /* Metadata Footer */
    .report-footer {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #334155;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #1e293b;
        display: flex;
        justify-content: space-between;
    }

    /* Styled Authenticate Button */
    .stButton>button {
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        box-shadow: 0 4px 12px -2px rgba(99, 102, 241, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 20px -4px rgba(99, 102, 241, 0.6);
        border: none !important;
    }
    
    /* Override for secondary buttons */
    [data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: 1px solid #1e293b !important;
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

if 'token' not in st.session_state: st.session_state.token = None
if 'operator' not in st.session_state: st.session_state.operator = None
if 'active_result' not in st.session_state: st.session_state.active_result = None

def check_backend():
    try: return requests.get(API_BASE_URL + "/", timeout=1).status_code == 200
    except: return False

def render_report_view(data, report_id=None, timestamp=None):
    """Renders the detailed intelligence report."""
    st.markdown(f"""
        <div class="report-header">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h1 style="margin:0; font-size: 2.8rem; color: #f8fafc; letter-spacing: -0.04em; font-weight:800;">{data['company_name']}</h1>
                    <p style="color: #818cf8; margin-top: 0.3rem; font-weight: 600; font-size: 1rem; letter-spacing: 0.05em;">{data.get('website', 'VERIFIED_DOMAIN').upper()}</p>
                </div>
                <div class="status-badge">Live Intelligence Scan</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.4); padding: 1.5rem; border-radius: 1rem; margin-top: 2rem; border: 1px solid rgba(255,255,255,0.05);">
                <p style="margin:0; font-style: italic; font-size: 1.1rem; line-height: 1.6; color: #cbd5e1;">"{data['summary']}"</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="report-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown('<p class="label-caps">Contact Matrix</p>', unsafe_allow_html=True)
            emails = data.get('emails', [])
            phones = data.get('phone_numbers', [])
            if emails:
                for e in emails: st.markdown(f'<div class="extraction-item">📧 <code>{e}</code></div>', unsafe_allow_html=True)
            if phones:
                for p in phones: st.markdown(f'<div class="extraction-item">📞 <code>{p}</code></div>', unsafe_allow_html=True)
            if not emails and not phones: st.caption("No communication routes found.")
            
        with c2:
            st.markdown('<p class="label-caps">Network Presence</p>', unsafe_allow_html=True)
            socials = data.get('socials', [])
            addrs = data.get('addresses', [])
            if socials:
                for s in socials: 
                    st.markdown(f'<div class="extraction-item">🌐 <b>{s["platform"]}</b>: <a href="{s["url"]}" style="color:#818cf8; text-decoration:none;">Link ↗</a></div>', unsafe_allow_html=True)
            if addrs:
                for a in addrs: st.markdown(f'<div class="extraction-item">📍 {a}</div>', unsafe_allow_html=True)
            if not socials and not addrs: st.caption("No digital/physical assets detected.")
            
        with c3:
            st.markdown('<p class="label-caps">Strategic Intelligence</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-panel">{data.get("notes", "No operational notes provided.")}</div>', unsafe_allow_html=True)
            
            st.markdown('<p class="label-caps" style="margin-top:2rem;">Intelligence Sources</p>', unsafe_allow_html=True)
            for src in data.get('sources', []):
                st.markdown(f'<p style="font-size:0.7rem; color: #475569; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">• {src}</p>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="report-footer">
                <span>UID: {report_id or str(uuid.uuid4())[:8].upper()}</span>
                <span>ISO_STAMP: {timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def login_screen():
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='height: 18vh'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align:center; margin-bottom: 3rem;'>
                <h1 style="color: #f8fafc; font-size: 3.5rem; font-weight: 900; letter-spacing: -0.05em; margin-bottom: 0;">NEXUS <span style="color:#6366f1;">INTEL</span></h1>
                <p style="color: #475569; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3em; margin-top: 0.5rem;">Intelligence Discovery Unit</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("nexus_login"):
            u = st.text_input("Email", placeholder="Email")
            p = st.text_input("Password", type="password", placeholder="Password")
            submit = st.form_submit_button("AUTHENTICATE", use_container_width=True)
            
            if submit:
                # Login logic: Robust check for non-empty input as requested
                if u and p:
                    try:
                        res = requests.post(f"{API_BASE_URL}/login", json={"email": u, "password": p})
                        if res.status_code == 200:
                            st.session_state.token = res.json()["access_token"]
                            st.session_state.operator = u.split('@')[0].upper() if '@' in u else u.upper()
                            st.rerun()
                        else:
                            st.error("ACCESS DENIED: Credentials Invalid.")
                    except Exception as e:
                        st.error("SYSTEM_FAULT: Backend node unreachable.")
                else:
                    st.warning("Please provide both email and password for authentication.")

def dashboard():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"""
            <div style="padding: 2rem 0;">
                <h1 style="color: #f8fafc; font-size: 1.8rem; display: flex; align-items: center; gap: 12px; font-weight: 900; margin: 0; letter-spacing: -0.04em;">
                    <span style="background: #6366f1; color:white; padding: 4px 10px; border-radius: 8px;">N</span> NEXUS
                </h1>
                <p style="color: #475569; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.2em; margin-top: 0.75rem;">Internal Portal</p>
            </div>
            <div style="margin-bottom: 2rem;"></div>
        """, unsafe_allow_html=True)
        
        nav_choice = st.radio("SELECT_MODULE", ["Discovery Console", "Archived Research"], label_visibility="collapsed")
        
        st.markdown("<div style='height: 40vh'></div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='padding: 1rem; background: #020617; border: 1px solid #1e293b; border-radius: 0.75rem; margin-bottom: 1rem;'>
                <p style='font-size:0.65rem; color:#475569; font-weight:800; text-transform:uppercase; margin-bottom:4px;'>Active Operator</p>
                <p style='font-family:JetBrains Mono; font-size:0.8rem; color:#818cf8; font-weight:700;'>{st.session_state.operator}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("TERMINATE SESSION", use_container_width=True):
            st.session_state.token = None
            st.session_state.operator = None
            st.session_state.active_result = None
            st.rerun()

    if nav_choice == "Discovery Console":
        st.title("Discovery Console")
        st.markdown("<p style='color: #475569; font-size: 1rem; margin-bottom: 2rem; font-weight: 500;'>Enter a company website to extract structured contact and business data.</p>", unsafe_allow_html=True)
        
        with st.container():
            c_url, c_btn = st.columns([4, 1.2])
            with c_url:
                target_url = st.text_input("Target Domain", placeholder="https://domain.com", label_visibility="collapsed")
            with c_btn:
                start_btn = st.button("SEARCH", use_container_width=True)

        if start_btn and target_url:
            # Replaced st.status with st.spinner to avoid the collapsible "Intelligence Extracted" box
            # This ensures the user sees the data immediately once loaded.
            with st.spinner("PROCESSING"):
                try:
                    res = requests.post(f"{API_BASE_URL}/analyze", json={"url": target_url}, headers=headers)
                    if res.status_code == 200:
                        st.session_state.active_result = res.json()
                        # Removed st.balloons() animation
                    else:
                        st.error("Protocol Failure: Domain unreachable or extraction timed out.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Persistent display of search results if they exist in state
        if st.session_state.active_result:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.75rem; font-weight:bold; color:#6366f1; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:1rem;'>Live Analysis Report</p>", unsafe_allow_html=True)
            render_report_view(st.session_state.active_result)

    else:
        st.title("Archived Research")
        st.markdown("<p style='color: #475569; font-size: 1rem; margin-bottom: 2rem;'>Retrieve historical records from the encrypted Nexus database.</p>", unsafe_allow_html=True)
        
        try:
            history = requests.get(f"{API_BASE_URL}/history", headers=headers).json()
            if not history:
                st.info("The intelligence archive is currently offline or empty.")
            else:
                list_col, view_col = st.columns([1, 2.5])
                
                with list_col:
                    st.markdown('<p class="label-caps">Historical Index</p>', unsafe_allow_html=True)
                    for rec in history:
                        d_str = datetime.strptime(rec['timestamp'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y.%m.%d')
                        if st.button(f"🏢 {rec['company_name']}\n[{d_str}]", key=rec['id'], use_container_width=True):
                            st.session_state.viewing_id = rec['id']
                
                with view_col:
                    v_id = st.session_state.get('viewing_id')
                    if v_id:
                        active_rec = next((x for x in history if x['id'] == v_id), None)
                        if active_rec:
                            mapped_data = {
                                "company_name": active_rec['company_name'],
                                "website": active_rec['website'],
                                "summary": active_rec['summary'],
                                "emails": json.loads(active_rec['emails']),
                                "phone_numbers": json.loads(active_rec['phone_numbers']),
                                "socials": json.loads(active_rec['socials']),
                                "addresses": json.loads(active_rec['addresses']),
                                "notes": active_rec['notes'],
                                "sources": json.loads(active_rec['sources'])
                            }
                            render_report_view(
                                mapped_data, 
                                report_id=f"REC_{str(active_rec['id']).zfill(4)}", 
                                timestamp=datetime.strptime(active_rec['timestamp'], '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y.%m.%d %H:%M:%S")
                            )
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("PURGE ARCHIVE ENTRY", type="secondary", use_container_width=True):
                                requests.delete(f"{API_BASE_URL}/history/{active_rec['id']}", headers=headers)
                                st.session_state.viewing_id = None
                                st.rerun()
                    else:
                        st.markdown("""
                            <div style="height:450px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#020617; border:2px dashed #1e293b; border-radius:1.5rem; color:#475569;">
                                <div style="font-size:4rem; margin-bottom:1rem; filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.2));">📁</div>
                                <p style="font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.2em;">Select Record for Decryption</p>
                            </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Archive Sync Error: {e}")

if not st.session_state.token:
    login_screen()
else:
    dashboard()
