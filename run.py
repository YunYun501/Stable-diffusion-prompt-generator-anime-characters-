#!/usr/bin/env python3
"""
Entry point for Random Character Prompt Generator.

Usage:
    python run.py

This will launch the Gradio web UI (auto-finds available port starting from 7865)
"""

import sys
import socket
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generator.app import create_app


def find_free_port(start_port=7865, end_port=7899):
    """Find a free port in the given range."""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def main():
    """Launch the web UI."""
    print("=" * 60)
    print("Random Character Prompt Generator for Stable Diffusion")
    print("=" * 60)
    print()
    
    # Find available port
    port = find_free_port()
    if port is None:
        print("ERROR: Could not find an available port in range 7865-7899")
        print("Please close some applications and try again.")
        sys.exit(1)
    
    print(f"Starting web UI on http://localhost:{port}")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    app = create_app()
    app.launch(
        server_name="127.0.0.1",  # Localhost only - avoids conflicts
        server_port=port,
        share=False,  # Set to True to create a public link
        inbrowser=True  # Auto-open browser
    )


if __name__ == "__main__":
    main()
