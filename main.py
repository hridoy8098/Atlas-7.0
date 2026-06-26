"""Atlas 7.0 — Desktop entry point"""
import threading
import time
import webbrowser
import sys
import os

# Make sure the app's root dir is on PATH so PyInstaller can find data
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

def open_browser():
    time.sleep(6)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  ATLAS 7.0 — Personal AI Assistant")
    print("=" * 60)
    print("  Starting server...")

    threading.Thread(target=open_browser, daemon=True).start()

    from server import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
