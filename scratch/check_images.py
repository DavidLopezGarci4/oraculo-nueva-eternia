import httpx
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel

db = SessionCloud()
products = db.query(ProductModel).all()

target_filenames = [
    "orko-200x-cartoon-collection",
    "panthor-flocked-2425",
    "panthor-standard-2414",
    "panthro-11289",
    "pig-head-4217",
    "prince-adam-200x-cartoon",
    "prince-adam-cringer-carto",
    "ram-man-200x-cartoon",
    "ram-man-deluxe-2417",
    "raphael-reptile-wars-8946"
]

print("=== AUDITORÍA DE IMÁGENES EN SUPABASE ===")
client = httpx.Client()

for target in target_filenames:
    # Find product containing target in image_url
    match = None
    for p in products:
        if p.image_url and target in p.image_url:
            match = p
            break
            
    if not match:
        print(f"\n❌ No se encontró ningún producto en la base de datos con el patrón: '{target}'")
        continue
        
    url = match.image_url
    print(f"\nFigura: {match.name} (ID: {match.id})")
    print(f"URL: {url}")
    
    try:
        resp = client.get(url, timeout=10.0)
        print(f"  - HTTP Status:   {resp.status_code}")
        print(f"  - Content-Type:  {resp.headers.get('content-type', 'N/A')}")
        print(f"  - Content-Length: {resp.headers.get('content-length', 'N/A')} bytes")
        # Check if it is a JSON error or HTML instead of image
        if "image" not in resp.headers.get('content-type', ''):
            print(f"  - ⚠️ AVISO: El contenido devuelto no es una imagen. Primeros 100 caracteres: {resp.text[:100]}")
    except Exception as e:
        print(f"  - ❌ Error al conectar: {e}")

db.close()
