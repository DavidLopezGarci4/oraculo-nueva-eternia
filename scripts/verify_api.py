import requests
import json

def verify_api():
    print("--- VERIFICANDO API (TOP DEALS) ---")
    url = "http://127.0.0.1:8000/api/dashboard/top-deals"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            deals = response.json()
            print(f"Top Deals encontrados: {len(deals)}")
            if deals:
                print("Muestra del primero:")
                print(json.dumps(deals[0], indent=2))
        else:
            print(f"Error API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"No se pudo conectar a la API local: {e}")

if __name__ == "__main__":
    verify_api()
