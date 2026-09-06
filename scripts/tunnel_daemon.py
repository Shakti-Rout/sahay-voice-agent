"""
Localtunnel Persistent Daemon with Automatic Reconnection.
Ensures https://nhaa-vortex-helpline.loca.lt stays alive permanently.
"""

import subprocess
import time
import sys

SUBDOMAIN = "nhaa-vortex-helpline"
PORT = "8000"

def run_tunnel():
    print(f"[TunnelDaemon] Starting localtunnel for port {PORT} with subdomain {SUBDOMAIN}...")
    while True:
        try:
            cmd = ["cmd.exe", "/c", "npx", "-y", "localtunnel", "--port", PORT, "--subdomain", SUBDOMAIN]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
            proc.wait()
            print(f"[TunnelDaemon] Localtunnel process exited with code {proc.returncode}. Reconnecting in 2s...")
        except Exception as e:
            print(f"[TunnelDaemon] Exception: {e}. Reconnecting in 3s...")
            time.sleep(3)
        time.sleep(2)

if __name__ == "__main__":
    run_tunnel()
