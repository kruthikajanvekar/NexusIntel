# start both dashboard and API; $PORT comes from the environment
web: bash -lc "streamlit run app/dashboard.py --server.port 8501 --server.address 127.0.0.1 & uvicorn app.api:app --host 0.0.0.0 --port $PORT"
