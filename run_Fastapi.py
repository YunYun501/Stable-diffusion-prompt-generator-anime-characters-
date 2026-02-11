#!/usr/bin/env python3
"""
Entry point for the FastAPI web UI.

Usage:
    python run_Fastapi.py

Finds a free port, launches uvicorn, and opens the browser automatically.
"""

import sys
import socket
import webbrowser
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def find_free_port(start=8000, end=8099):
    """Find a free port in the given range."""
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return None


def open_browser(port):
    """Open the browser after a short delay to let the server start."""
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")


def main():
    print("=" * 60)
    print("Random Character Prompt Generator — FastAPI")
    print("=" * 60)
    print()

    port = find_free_port()
    if port is None:
        print("ERROR: No available port in range 8000-8099")
        sys.exit(1)

    print(f"Starting server on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop")
    print()

    # Open browser in background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    import uvicorn
    uvicorn.run("web.server:app", host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
