import asyncio
from curl_cffi.requests import AsyncSession
import sys
import os
import io

# [3OX] Unicode Resilience Shield
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

async def diagnose_amazon():
    # Test different impersonation profiles
    profiles = ["chrome101", "chrome110", "chrome120", "safari15_5", "edge101"]
    url = "https://www.amazon.es/s?k=masters+of+the+universe+origins"
    
    print(f"🚀 Iniciando diagnóstico de Amazon para: {url}\n")
    
    for profile in profiles:
        print(f"--- Probando perfil: {profile} ---")
        try:
            async with AsyncSession(impersonate=profile) as s:
                # Add some standard headers that might be missing
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                    "Cache-Control": "max-age=0",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                }
                
                resp = await s.get(url, headers=headers, timeout=15)
                print(f"Status: {resp.status_code}")
                print(f"Server: {resp.headers.get('Server', 'Unknown')}")
                
                if resp.status_code == 200:
                    title = "No Title"
                    if "<title>" in resp.text:
                        title = resp.text.split("<title>")[1].split("</title>")[0]
                    print(f"✅ Éxito! Título: {title}")
                    if "captcha" in resp.text.lower() or "robot" in resp.text.lower():
                        print("⚠️ Detectado CAPTCHA/ROBOT.")
                    else:
                        print("🎉 PARECE CONTENIDO REAL!")
                elif resp.status_code == 503:
                    print("❌ Bloqueado con 503")
                else:
                    print(f"❌ Error: {resp.status_code}")
                
        except Exception as e:
            print(f"💥 Excepción: {e}")
        
        print("\n")
        await asyncio.sleep(2) # Be kind

if __name__ == "__main__":
    asyncio.run(diagnose_amazon())
