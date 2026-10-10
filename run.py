"""
AROHA - Application Launcher
Team: Syntax Society - SAS Hackathon Edition (7 October)
"Don't just prepare for today's jobs — prepare for tomorrow's skills."
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def open_browser(url: str):
    time.sleep(1.5)
    print(f"\n[AROHA] Opening web application in default browser: {url}")
    webbrowser.open(url)

def main():
    print("=" * 70)
    print("                 AROHA - AI SKILL INTELLIGENCE                 ")
    print("          Team: Syntax Society | SAS Hackathon Edition         ")
    print("    'Don't just prepare for today's jobs — prepare for tomorrow's skills.' ")
    print("=" * 70)

    # Check if user explicitly wants FastAPI backend
    if "--fastapi" in sys.argv:
        import uvicorn
        if "--no-browser" not in sys.argv:
            threading.Thread(target=open_browser, args=("http://127.0.0.1:8000",), daemon=True).start()
        print("\n[AROHA] Starting FastAPI backend server at http://127.0.0.1:8000")
        print("[AROHA] Interactive API documentation at http://127.0.0.1:8000/docs")
        uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
    else:
        # Default: Launch Streamlit application (SAS Hackathon primary interface)
        if "--no-browser" not in sys.argv:
            threading.Thread(target=open_browser, args=("http://localhost:8501",), daemon=True).start()
        print("\n[AROHA] Launching Streamlit decision-support application at http://localhost:8501 ...")
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"]
        try:
            subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        except KeyboardInterrupt:
            print("\n[AROHA] Gracefully shutting down application.")

if __name__ == "__main__":
    main()
