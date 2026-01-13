import requests
import json

def test_hall_of_fame():
    try:
        response = requests.get("http://localhost:8000/api/dashboard/hall-of-fame")
        if response.status_code == 200:
            data = response.json()
            print("\n[OK] Endpoint /api/dashboard/hall-of-fame reachable")
            
            print("\n[TOP VALUE] (Griales del Reino):")
            for item in data.get("top_value", []):
                print(f"- {item['name']}: {item['market_value']} EUR (Inv: {item['invested_value']} EUR)")
                
            print("\n[TOP ROI] (Potencial Oculto):")
            for item in data.get("top_roi", []):
                print(f"- {item['name']}: +{item['roi_percentage']}% (Inv: {item['invested_value']} EUR -> Mkt: {item['market_value']} EUR)")
                
            if not data.get("top_value") and not data.get("top_roi"):
                print("\n[WARN] No data returned (Empty collections/market?). This might be normal if DB is empty.")
            
        else:
            print(f"[ERROR] Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")

if __name__ == "__main__":
    test_hall_of_fame()
