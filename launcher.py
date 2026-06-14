import os
import sys
import time
import threading

import requests
import webview
import streamlit.web.cli as stcli


PORT = 8501


def run_streamlit():
    if getattr(sys, "frozen", False):
        app_path = os.path.join(sys._MEIPASS, "streamlit_app.py")
    else:
        app_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "streamlit_app.py"
        )

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        f"--server.port={PORT}",
        "--global.developmentMode=false",
        "--server.headless=true",
    ]

    stcli.main()


def wait_for_streamlit():
    url = f"http://127.0.0.1:{PORT}"

    while True:
        try:
            requests.get(url, timeout=1)
            return
        except Exception:
            time.sleep(0.5)


if __name__ == "__main__":
    # Start Streamlit in background
    threading.Thread(
        target=run_streamlit,
        daemon=True,
    ).start()

    # Wait until Streamlit is reachable
    wait_for_streamlit()

    # Create native window
    webview.create_window(
        title="Rip Tags",
        url=f"http://127.0.0.1:{PORT}",
        width=1400,
        height=900,
        resizable=True,
    )

    webview.start()