import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'), override=True)

async def test_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[ERROR] TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no estan configurados en el archivo .env")
        return
        
    print(f"[INFO] Intentando enviar mensaje de prueba a Telegram...")
    print(f"   Chat ID: {chat_id}")
    print(f"   Token (comienzo): {token[:10]}...")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "⚡ <b>Oráculo de Nueva Eternia</b>\n\n¡Esta es una prueba de conexión de Telegram exitosa desde tu entorno local! Tu bot está configurado correctamente.",
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[SUCCESS] Mensaje enviado con exito! Revisa tu aplicacion de Telegram.")
            else:
                print(f"[ERROR] Error de Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[ERROR] Ocurrio un error al enviar el mensaje: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
