import subprocess
import sys
import time
import os
import threading
import socket
import webbrowser

def kill_process_on_port(port):
    """Forcefully close any process using the specified port."""
    import os, signal
    try:
        if os.name == 'nt':  # Windows
            cmd = f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port}\') do taskkill /F /PID %a'
            subprocess.run(cmd, shell=True, capture_output=True)
        else: # Linux/Mac
            cmd = f'lsof -ti:{port} | xargs kill -9'
            subprocess.run(cmd, shell=True, capture_output=True)
    except:
        pass

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def stream_logs(pipe, prefix):
    try:
        for line in iter(pipe.readline, ''):
            if line:
                print(f"[{prefix}] {line.strip()}")
    except Exception:
        pass

def run_services():
    print("\n" + "="*60)
    print("🛡️  NEXUSINTEL - V3.0 SYSTEM REBOOT")
    print("="*60)
    
    # Force clean start
    print("🧹 Cleaning environment ports...")
    kill_process_on_port(8000)
    kill_process_on_port(8501)
    time.sleep(1)

    is_windows = os.name == 'nt'
    
    print("📡 Launching Backend (Port 8000)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.api:app", "--host", "127.0.0.1", "--port", "8000"]
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=is_windows
    )
    threading.Thread(target=stream_logs, args=(backend_process.stdout, "BACKEND"), daemon=True).start()
    threading.Thread(target=stream_logs, args=(backend_process.stderr, "BACKEND-LOG"), daemon=True).start()
    
    # Wait for backend to be ready
    for _ in range(10):
        if is_port_in_use(8000): break
        time.sleep(1)

    print("🖥️  Launching Dashboard (Port 8501)...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "app/dashboard.py", "--server.port", "8501", "--server.address", "127.0.0.1"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=is_windows
    )
    threading.Thread(target=stream_logs, args=(frontend_process.stdout, "DASHBOARD"), daemon=True).start()

    print("\n" + "—"*60)
    print("🚀 ALL SYSTEMS UPDATED AND ONLINE")
    print("🔗 URL: http://127.0.0.1:8501")
    print("—"*60 + "\n")

    webbrowser.open("http://127.0.0.1:8501")

    try:
        while True:
            time.sleep(2)
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n🛑 Closing services...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    run_services()
