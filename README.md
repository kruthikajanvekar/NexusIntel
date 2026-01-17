# 🏢 NexusIntel - Internal Website Intelligence & Contact Discovery

**NexusIntel** is a high-performance, internal research engine designed for sales teams, analysts, and lead generation specialists. It automates the extraction of business intelligence and verified contact information directly from the web using state-of-the-art AI.

---

## 📋 Problem Statement
In the modern B2B landscape, manual company research is a massive bottleneck. Research analysts often spend **40-60% of their day** performing repetitive tasks:
- Manually browsing corporate websites to find core business descriptions.
- Searching for "Contact Us" or "About" pages to hunt for emails and phone numbers.
- Navigating footers to find social media links and physical office addresses.
- Cross-referencing data points to ensure accuracy.

This manual process is **slow**, **unscalable**, and **highly prone to human error**, leading to stale leads and wasted outreach efforts.

## 💡 The Solution
**NexusIntel** acts as an autonomous "Intelligence Unit" that bridges the gap between raw web data and structured CRM-ready records. 

By simply providing a domain URL, the system:
1.  **Autonomous Web Scanning**: Uses Gemini 3's real-time Google Search grounding to scan the entire internet for mentions of the target company.
2.  **Intelligent Data Structuring**: Leverages LLMs to understand unstructured web content and extract specific entities (Emails, Phone numbers, Addresses) with high confidence.
3.  **Centralized Repository**: Automatically archives every discovery into a secure local database for internal cross-referencing and auditing.

---

## 🛠️ Tech Stack

### **Frontend & Interface**
- **Streamlit**: Powers the interactive dashboard. Chosen for its rapid development cycle and specialized support for data-heavy internal tools.
- **Custom CSS (Tailwind-inspired)**: Custom-built "Obsidian Dark" theme for a professional, high-focus user experience.

### **Backend Engine**
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.9+ based on standard Python type hints.
- **Uvicorn**: Lightning-fast ASGI server implementation for the API layer.
- **Python-Jose (JWT)**: Secure authentication system using JSON Web Tokens for session-based access control.

### **Artificial Intelligence (The Brain)**
- **Google GenAI SDK**: Integrates the latest **Gemini 3** series models.
- **Google Search Grounding**: Direct integration with Google's search engine to prevent "AI Hallucinations" and provide up-to-the-minute data.
- **JSON Schema Enforcement**: Ensures the AI output is always valid and can be parsed by our backend.

### **Data & Persistence**
- **SQLite**: A lightweight, serverless relational database engine used for local data sovereignty.
- **SQLAlchemy ORM**: Object-Relational Mapper that allows for easy migration to enterprise databases (PostgreSQL/SQL Server) if needed.

---

## 🚀 Technical Architecture

1.  **Dashboard (Streamlit)**: Captures user input (URLs) and displays historical research.
2.  **API Gateway (FastAPI)**: Validates authentication and routes requests to the intelligence engine.
3.  **Research Agent (Gemini 3)**: Performs the live web crawl and intelligence extraction.
4.  **Database (SQLAlchemy)**: Permanently stores every successful discovery.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+ installed.
- A valid Google Gemini API Key.

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd nexus-intel

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Execution
The project includes a master orchestrator that handles everything (API + Dashboard + Browser).
```bash
python main.py
```

---

## 🛡️ Internal Access Credentials
- **Username**: Any email format (e.g., `admin@nexus.io`)
- **Password**: Any non-empty string.
*(Note: As an internal tool, login is designed for convenience while still logging session data.)*
