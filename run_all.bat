@echo off
REM ==============================
REM Activate virtual environment
REM ==============================
call venv\Scripts\activate

REM ==============================
REM Start FastAPI in new CMD window
REM ==============================
start cmd /k "uvicorn server:app --host 0.0.0.0 --port 8001"

REM ==============================
REM Start Streamlit in current window
REM ==============================
streamlit run main.py --server.address 0.0.0.0 --server.port 8501
