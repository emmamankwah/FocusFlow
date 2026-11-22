import subprocess
import sys
import time
import json
import urllib.request
from pathlib import Path

# Paths (adjust if your project layout differs)
PROJECT_ROOT = Path(r'C:\Users\emman\Desktop\FocusFlow')
FRONTEND_DIR = PROJECT_ROOT / 'Frontend'
NGROK_EXEC = 'ngrok'  # assume ngrok is on PATH

def start_vite():
    """Start the Vite dev server in the frontend directory.
    It runs with `npm install` (if needed) and `npm run dev`.
    Returns the subprocess.Popen object.
    """
    # Ensure dependencies are installed (ignore errors if already installed)
    subprocess.run([r'C:\Program Files\nodejs\npm.cmd', 'install'], cwd=FRONTEND_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Start the dev server (hot‑module replacement will keep it alive)
    proc = subprocess.Popen([r'C:\Program Files\nodejs\npm.cmd', 'run', 'dev'], cwd=FRONTEND_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # Give it a moment to start
    time.sleep(3)
    return proc

def start_ngrok(port: int = 5173):
    # Attempt to start ngrok; if not found, just return None and we'll use localhost.
    try:
        proc = subprocess.Popen([NGROK_EXEC, 'http', str(port), '--log', 'stdout'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time.sleep(2)
        return proc
    except FileNotFoundError:
        print('[live-preview] ngrok not found – using localhost URL.', file=sys.stderr)
        return None
    """Launch ngrok to expose the given local port.
    Returns the subprocess.Popen object.
    """
    proc = subprocess.Popen([NGROK_EXEC, 'http', str(port), '--log', 'stdout'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # Wait a bit for ngrok to initialise
    time.sleep(2)
    return proc

def get_public_url():
    """Query ngrok's local API for the public URL of the tunnel.
    Returns a string like "https://abcd1234.ngrok.io".
    """
    try:
        with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels') as resp:
            data = json.load(resp)
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
            # fallback to http tunnel
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'http':
                    return tunnel.get('public_url')
    except Exception as e:
        print(f'[live-preview] Failed to get public URL: {e}', file=sys.stderr)
    return None

def main():
    print('[live-preview] Starting Vite dev server...')
    vite_proc = start_vite()
    print('[live-preview] Launching ngrok tunnel (if available)...')
    ngrok_proc = start_ngrok()

    # Determine which URL to show
    if ngrok_proc is not None:
        # Poll until we have a public URL from ngrok
        public_url = None
        for _ in range(30):
            public_url = get_public_url()
            if public_url:
                break
            time.sleep(1)
        if not public_url:
            print('[live-preview] Could not obtain ngrok URL. Falling back to localhost.', file=sys.stderr)
            public_url = f'http://127.0.0.1:{5173}'
    else:
        public_url = f'http://127.0.0.1:{5173}'

    print(f'[live-preview] URL: {public_url}')
    print('[live-preview] Open this URL in a browser to see live updates.')
    print('[live-preview] Press Ctrl+C to stop.')

    try:
        # Keep the script alive while both child processes run
        while True:
            if vite_proc.poll() is not None:
                print('[live-preview] Vite process exited unexpectedly.', file=sys.stderr)
                break
            if ngrok_proc is not None and ngrok_proc.poll() is not None:
                print('[live-preview] Ngrok process exited unexpectedly.', file=sys.stderr)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n[live-preview] Shutting down...')
    finally:
        if ngrok_proc is not None:
            ngrok_proc.terminate()
            ngrok_proc.wait()
        vite_proc.terminate()
        vite_proc.wait()
        print('[live-preview] All processes terminated.')


if __name__ == '__main__':
    main()
