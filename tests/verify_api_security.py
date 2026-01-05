
import httpx
import subprocess
import time
import sys
import os

# Asegurar que el path incluya la raíz del proyecto para importar settings
sys.path.append(os.getcwd())
from src.core.config import settings

def test_api_security():
    print("--- [VERIFY] API Security Handshake (HTTTPX) ---")
    
    # 1. Start API Server in background
    cmd = ["python", "src/interfaces/api/main.py"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("Waiting for API Broker to start...")
    time.sleep(3)
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        with httpx.Client() as client:
            # TEST A: Unprotected Health Check
            print("Test A: Checking /health (Public)...", end=" ")
            res = client.get(f"{base_url}/health")
            if res.status_code == 200:
                print("OK")
            else:
                print(f"FAILED (Status {res.status_code})")
                
            # TEST B: Sync Batch without Key (Should fail)
            print("Test B: Posting to /sync/batch WITHOUT X-API-KEY...", end=" ")
            res = client.post(f"{base_url}/sync/batch", json=[])
            if res.status_code in [403, 422]: 
                print("REJECTED (Correct)")
            else:
                print(f"FAILED (Expected block, got {res.status_code})")
                
            # TEST C: Sync Batch with WRONG Key (Should fail)
            print("Test C: Posting to /sync/batch with WRONG X-API-KEY...", end=" ")
            headers = {"X-API-KEY": "wrong-key"}
            res = client.post(f"{base_url}/sync/batch", json=[], headers=headers)
            if res.status_code == 403:
                print("REJECTED (Correct)")
            else:
                print(f"FAILED (Expected 403, got {res.status_code})")
                
            # TEST D: Sync Batch with CORRECT Key (Should succeed)
            print("Test D: Posting to /sync/batch with CORRECT X-API-KEY...", end=" ")
            headers = {"X-API-KEY": settings.ORACULO_API_KEY}
            res = client.post(f"{base_url}/sync/batch", json=[], headers=headers)
            if res.status_code == 200:
                print("GRANTED (Success!)")
            else:
                print(f"FAILED (Expected 200, got {res.status_code})")
                print(f"Response: {res.text}")

    except Exception as e:
        print(f"\nERROR: Connection failed: {e}")
    finally:
        print("\nStopping API Broker...")
        proc.terminate()

if __name__ == "__main__":
    test_api_security()
