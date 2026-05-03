import subprocess
import sys
import time

def main():
    print("Starting FastAPI backend...")
    # Start FastAPI server
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
    )
    
    # Give FastAPI a moment to start before launching Streamlit
    time.sleep(3)
    
    print("Starting Streamlit frontend...")
    # Start Streamlit app
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"]
    )
    
    try:
        # Wait for both processes to complete (they usually run indefinitely)
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down both servers...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.wait()
        streamlit_process.wait()
        print("Servers stopped successfully.")

if __name__ == "__main__":
    main()
