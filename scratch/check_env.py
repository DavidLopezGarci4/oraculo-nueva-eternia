import os
from src.core.config import settings

print("SUPABASE_DATABASE_URL en settings:", settings.SUPABASE_DATABASE_URL)
print("DATABASE_URL en settings:", settings.DATABASE_URL)
print("SUPABASE_URL en settings:", settings.SUPABASE_URL)
print("Entorno completo:")
for k, v in os.environ.items():
    if any(x in k.lower() for x in ['supabase', 'database', 'url', 'oraculo', 'connection']):
        print(f"{k}: {v}")
