import os
import sys
import httpx
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

def check_apify_token(token_name: str, token_val: str | None) -> dict:
    if not token_val:
        return {
            "name": token_name,
            "configured": False,
            "status": "MISSING",
            "message": "No configurado en .env"
        }
    
    try:
        # Endpoint de metadatos de usuario (Cero gasto de créditos)
        url = f"https://api.apify.com/v2/users/me?token={token_val.strip()}"
        res = httpx.get(url, timeout=10.0)
        
        if res.status_code == 200:
            data = res.json().get("data", {})
            username = data.get("username", "Desconocido")
            plan = data.get("plan", {}).get("name", "Free")
            return {
                "name": token_name,
                "configured": True,
                "status": "ACTIVE",
                "username": username,
                "plan": plan,
                "message": f"Operativo (Usuario: {username}, Plan: {plan})"
            }
        elif res.status_code in [401, 403]:
            return {
                "name": token_name,
                "configured": True,
                "status": "INVALID",
                "message": "Token inválido o expirado (HTTP 401/403)"
            }
        else:
            return {
                "name": token_name,
                "configured": True,
                "status": "ERROR",
                "message": f"Error al validar (HTTP {res.status_code})"
            }
    except Exception as e:
        return {
            "name": token_name,
            "configured": True,
            "status": "CONN_ERROR",
            "message": f"Error de conexión: {e}"
        }

def check_scraperapi_key(key_val: str | None) -> dict:
    if not key_val:
        return {
            "name": "SCRAPERAPI_KEY",
            "configured": False,
            "status": "MISSING",
            "message": "No configurado en .env"
        }
        
    try:
        # Endpoint de cuenta ScraperAPI (Cero gasto de créditos)
        url = f"https://api.scraperapi.com/account?api_key={key_val.strip()}"
        res = httpx.get(url, timeout=10.0)
        
        if res.status_code == 200:
            data = res.json()
            req_count = data.get("requestCount", 0)
            req_limit = data.get("requestLimit", 0)
            concurrency = data.get("concurrencyLimit", 0)
            return {
                "name": "SCRAPERAPI_KEY",
                "configured": True,
                "status": "ACTIVE",
                "req_count": req_count,
                "req_limit": req_limit,
                "message": f"Operativo ({req_count}/{req_limit} peticiones usadas, concurrencia: {concurrency})"
            }
        elif res.status_code in [401, 403]:
            return {
                "name": "SCRAPERAPI_KEY",
                "configured": True,
                "status": "INVALID",
                "message": "API Key inválida o suspendida (HTTP 401/403)"
            }
        else:
            return {
                "name": "SCRAPERAPI_KEY",
                "configured": True,
                "status": "ERROR",
                "message": f"Error al validar (HTTP {res.status_code})"
            }
    except Exception as e:
        return {
            "name": "SCRAPERAPI_KEY",
            "configured": True,
            "status": "CONN_ERROR",
            "message": f"Error de conexión: {e}"
        }

def run_diagnostics():
    print("\n" + "=" * 60)
    print(" 🛡️  EL ORÁCULO DE ETERNIA: DIAGNÓSTICO DE TOKENS DE SCRAPING")
    print("     (Comprobación segura de metadatos: Gasto de 0 créditos)")
    print("=" * 60 + "\n")
    
    t1 = os.environ.get("APIFY_TOKEN")
    t2 = os.environ.get("APIFY_TOKEN2") or os.environ.get("APYFY_TOKEN2")
    t3 = os.environ.get("APIFY_TOKEN3")
    s_key = os.environ.get("SCRAPERAPI_KEY")
    
    results = [
        check_apify_token("APIFY_TOKEN (Cuenta 1)", t1),
        check_apify_token("APIFY_TOKEN2 (Cuenta 2)", t2),
        check_apify_token("APIFY_TOKEN3 (Cuenta 3)", t3),
        check_scraperapi_key(s_key)
    ]
    
    for r in results:
        status_icon = "🟢" if r["status"] == "ACTIVE" else "🟡" if r["status"] == "MISSING" else "🔴"
        print(f" {status_icon} [{r['name']}]: {r['message']}")
        
    print("\n" + "=" * 60)
    print(" Diagnóstico finalizado con éxito.\n")

if __name__ == "__main__":
    run_diagnostics()
