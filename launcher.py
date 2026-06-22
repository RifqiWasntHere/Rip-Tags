import subprocess
import socket
import sys
import time
import webview

PORT = 8501

streamlit_proc = subprocess.Popen([
    sys.executable, "-m", "streamlit",
    "run",
    "streamlit_app.py",
    f"--server.port={PORT}",
    "--server.headless=true",
])


def on_closed():
    print("Closing Streamlit...")

    if streamlit_proc.poll() is None:
        streamlit_proc.terminate()

        try:
            streamlit_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_proc.kill()


# Wait until Streamlit is ready
for _ in range(50):
    try:
        with socket.create_connection(("localhost", PORT), timeout=1):
            break
    except OSError:
        time.sleep(0.2)

window = webview.create_window(
    "Rip Tags",
    f"http://localhost:{PORT}",
    width=1200,
    height=800,
)

window.events.closed += on_closed

webview.start()