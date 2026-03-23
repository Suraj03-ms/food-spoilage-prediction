"""
run.py — starts Flask API (port 5000) and Gradio UI (port 7860) together.
Usage:  python run.py
"""

import threading
import subprocess
import sys
import time
import webbrowser


def run_flask():
    subprocess.run([sys.executable, "app.py"])


def run_gradio():
    time.sleep(2)   # wait for Flask to be ready first
    subprocess.run([sys.executable, "gradio_app.py"])


if __name__ == "__main__":
    print("🚀 Starting Flask API on http://localhost:5000 ...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print("🎨 Starting Gradio UI on http://localhost:7860 ...")
    time.sleep(2)

    gradio_thread = threading.Thread(target=run_gradio, daemon=True)
    gradio_thread.start()

    time.sleep(4)
    print("\n✅ Both services running!")
    print("   Flask API  → http://localhost:5000")
    print("   Gradio UI  → http://localhost:7860")
    print("\nPress Ctrl+C to stop.\n")
    webbrowser.open("http://localhost:7860")

    try:
        flask_thread.join()
        gradio_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")