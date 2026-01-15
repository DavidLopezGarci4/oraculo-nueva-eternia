import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.services.telegram_service import telegram_service

async def test_telegram():
    print("="*60)
    print("[*] TEST DE TELEGRAM: EL OJO DE SAURON")
    print("="*60)
    
    if not telegram_service.enabled:
        print("\n[!] ATENCION: Telegram no esta configurado.")
        print("    Para que este test sea real, añade esto a tu .env:")
        print("    TELEGRAM_BOT_TOKEN=tu_token")
        print("    TELEGRAM_CHAT_ID=tu_chat_id")
        print("\n    Simulando llamada al servicio...")
    
    # Intento de envío (fallara silenciosamente o logeara error si no hay keys)
    print("\n[+] Enviando alerta de prueba para: 'He-Man Origins (Test)'...")
    try:
        # Usamos un try/except para capturar si httpx falla por falta de red o config
        result = await telegram_service.send_deal_alert(
            product_name="He-Man Origins (Test)",
            price=14.99,
            shop_name="Eternia Shop",
            url="https://example.com/he-man"
        )
        
        if result:
            print("[OK] Exito: Mensaje enviado correctamente.")
        else:
            print("[X] El mensaje no se envio (Configuracion faltante o Error).")
            
    except Exception as e:
        print(f"[ERROR] Error durante el test: {e}")

    print("\n" + "="*60)
    print("FIN DEL TEST")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_telegram())
