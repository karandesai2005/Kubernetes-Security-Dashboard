"""
Seed the local database with mock Falco events, Trivy findings,
and RBAC anomalies for UI development without a live cluster.

Usage: python scripts/seed-mock-data.py
(or `make seed`)
"""
import json
import os
import urllib.request
import urllib.error

API = os.getenv("API_URL", "http://localhost:8000")

def seed():
    url = f"{API}/api/v1/seed"
    print(f"[seed] Seeding via {url} ...")
    try:
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode())
            print("[seed] Response:", data)
            print("[seed] Done. Visit http://localhost:3000")
    except urllib.error.URLError as exc:
        print("[seed] Failed to reach backend:", exc)
        print("       Make sure the stack is running: make dev (or docker compose up)")
    except Exception as exc:
        print("[seed] Error:", exc)

if __name__ == "__main__":
    seed()
