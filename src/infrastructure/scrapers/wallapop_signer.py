import hashlib
import hmac
import base64
import time
from urllib.parse import urlparse

class WallapopSigner:
    """
    Generador de firmas X-Signature para la API v3 de Wallapop.
    Basado en ingenieria inversa del cliente web React.
    """
    
    # Esta clave suele ser estática en el bundle JS de Wallapop
    # Nota: Si cambia, hay que extraerla del bundle JS (mangling logic)
    DEFAULT_SECRET = "Tm93IHRoYXQgeW91J3ZlIGZvdW5kIHRoaXMsIGFyZSB5b3UcmVhZHkgdG8gam9pbiB1cz8gam9ic0B3YWxsYXBvcC5jb20==" # Updated React secret
    
    @staticmethod
    def generate_signature(method: str, path: str, timestamp: int = None, secret: str = DEFAULT_SECRET) -> str:
        """
        Genera la firma X-Signature.
        Payload: method|path|timestamp
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)
            
        # El path debe ser solo la parte del endpoint (ej: /api/v3/general/search)
        # O el path completo con params si se desea (según versión de la API)
        normalized_path = path if '?' in path else urlparse(path).path
        
        payload = f"{method}|{normalized_path}|{timestamp}".encode('utf-8')
        
        # En Wallapop React, a veces el secret se decodifica de Base64 si asi viene en el bundle
        try:
            key = base64.b64decode(secret)
        except:
            key = secret.encode('utf-8')
            
        signature = hmac.new(key, payload, hashlib.sha256).digest()
        encoded_sig = base64.b64encode(signature).decode('utf-8')
        
        return encoded_sig, timestamp

if __name__ == "__main__":
    # Test simple
    signer = WallapopSigner()
    sig, ts = signer.generate_signature("GET", "/api/v3/general/search")
    print(f"Timestamp: {ts}")
    print(f"X-Signature: {sig}")
