import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger("CurrencyService")

class CurrencyService:
    """
    Servicio de Cambio de Divisas (Phase 56).
    Obtiene el cambio USD/EUR de XE.com con caché persistente de 24h.
    """
    _cache = {
        "rate": 0.92, # Fallback prudente
        "expiry": datetime.min
    }

    @classmethod
    def get_usd_to_eur_rate(cls) -> float:
        """
        Retorna el ratio de cambio USD -> EUR.
        Cacheado durante 24 horas para evitar fatiga de red.
        """
        if datetime.now() < cls._cache["expiry"]:
            return cls._cache["rate"]

        try:
            logger.info("Currency: Fetching real-time USD/EUR rate from XE.com...")
            url = "https://www.xe.com/es-es/currencyconverter/convert/?Amount=1&From=USD&To=EUR"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selector basado en el feedback del usuario: p.text-lg.font-semibold
            # O buscando el texto "1.00 USD ="
            rate_text = ""
            p_tag = soup.find("p", class_=re.compile(r"text-lg.*font-semibold"))
            if p_tag:
                rate_text = p_tag.get_text(strip=True)
            else:
                # Fallback: buscar cualquier tag que contenga "1.00 USD ="
                candidate = soup.find(string=re.compile(r"1\.00\s*USD\s*="))
                if candidate:
                    rate_text = candidate.parent.get_text(strip=True)

            if rate_text:
                # Extraer el número: "1.00 USD = 0,921234 EUR" -> 0.921234
                match = re.search(r"=\s*(\d+[,.]\d+)", rate_text)
                if match:
                    val_str = match.group(1).replace(",", ".")
                    rate = float(val_str)
                    
                    # Update Cache
                    cls._cache["rate"] = rate
                    cls._cache["expiry"] = datetime.now() + timedelta(hours=24)
                    logger.info(f"Currency: Rate updated to {rate} EUR per USD.")
                    return rate

            logger.warning("Currency: Could not parse rate from XE.com. Using fallback.")
        except Exception as e:
            logger.error(f"Currency: Error fetching rate: {e}")

        return cls._cache["rate"]

if __name__ == "__main__":
    # Test simple
    rate = CurrencyService.get_usd_to_eur_rate()
    print(f"Current Rate: 1 USD = {rate} EUR")
