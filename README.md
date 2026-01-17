# 🏢 NexusIntel - Internal Website Intelligence & Contact Discovery

NexusIntel is an enterprise-grade internal research platform designed to automate the process of company discovery and contact extraction.

---

## 📋 Problem Statement
In B2B sales, market research, and lead generation, analysts spend hours manually scouring websites to find:
- **Verified contact information** (Emails, Phone numbers).
- **Core business summaries**.
- **Physical office locations** and social media presence.

This manual process is slow, prone to human error, and the data is often lost in spreadsheets or disparate notes.

## 💡 The Solution
**NexusIntel** provides a centralized, AI-powered "Intelligence Unit." By simply entering a company URL, the system's autonomous Research Agent:
1.  **Scans the Web**: Uses Gemini 3 Pro with real-time Google Search grounding.
2.  **Extracts Intelligence**: Intelligently identifies and structures unstructured web data.
3.  **Archives Records**: Saves everything into a local database for future reference and internal sharing.

---

## 🚀 Technical Architecture

### 1. Backend (FastAPI Engine)
- **Security**: Implements JWT (JSON Web Tokens) for secure, session-based access.
- **API Performance**: Asynchronous endpoints for fast data retrieval and deletion.
- **Persistence**: SQLite database with SQLAlchemy ORM to manage intelligence records locally.

### 2. Frontend (Streamlit Dashboard)
- **Console**: A high-performance research interface for running new scans.
- **Archive**: A historical repository of all past discoveries.
- **UX**: A "Dark Mode" specialized theme designed for focus and productivity.

### 3. AI Core (Research Agent)
- **Model**: Gemini 3 Pro (`gemini-3-pro-preview`).
- **Tooling**: Integrated `google_search` for high-accuracy real-time grounding.
- **Reliability**: Built-in "Safe Mode" that gracefully handles API quota limits.

---

## ⚙️ Setup & Local Execution

### 1. Prerequisites
Ensure you have **Python 3.9 or higher** installed on your system.

### 2. Installation
```bash
# Clone the repository and enter the directory
git clone <your-repo-url>
cd nexus-intel

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install all necessary libraries
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root folder with the following:
```env
API_KEY=YOUR_GEMINI_API_KEY_HERE
SECRET_KEY=any_random_secure_string_2025
```

### 4. Running the Project
Simply run the master orchestrator script:
```bash
python main.py
```
This script handles the cleanup of ports, starts the FastAPI server, launches the Streamlit UI, and opens your browser automatically.

---

## 🛡️ Internal Access Credentials
- **Username**: `admin@nexus.io` (or any valid email format)
- **Password**: `password` (any non-empty string)

## 📂 Design Assumptions
- **Security**: Since this is an internal tool, the login logic is permissive (logs credentials to DB but grants access to any valid format) for ease of internal use.
- **Data Privacy**: All research results are stored locally in `nexus_intel.db` to ensure data sovereignty.
- **Scalability**: The architecture allows for swapping SQLite with PostgreSQL in a production cloud environment with minimal code changes.
