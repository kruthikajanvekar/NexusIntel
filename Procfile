# start Streamlit locally and then launch the FastAPI proxy/backend
env PORT=${PORT:-8000}
web: bash -lc "streamlit run app/dashboard.py --server.port 8501 --server.address 127.0.0.1 & uvicorn app.api:app --host 0.0.0.0 --port $PORT"
