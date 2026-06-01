import re

def normalize_url(url: str) -> str:
    """
    Normaliza de forma universal cualquier URL de ofertas (Wallapop, eBay, Vinted, Retail, etc.).
    - Elimina parámetros de consulta (?...)
    - Elimina fragmentos y anclas (#...)
    - Elimina barras diagonales opcionales al final (/)
    - Limpia espacios en blanco alrededor de la cadena.
    """
    if not url:
        return ""
        
    url = url.strip()
    
    # 1. Separar parámetros de consulta (?) y fragmentos (#)
    clean_url = url.split('?')[0].split('#')[0].strip()
    
    # 2. Eliminar barras diagonales finales
    if clean_url.endswith('/'):
        clean_url = clean_url[:-1]
        
    return clean_url
