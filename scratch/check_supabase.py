import sys
import os
sys.path.append(os.path.abspath('.'))

try:
    from src.core.config import settings
    print("SUPABASE_DATABASE_URL:", "Configurada" if settings.SUPABASE_DATABASE_URL else "No configurada")
    print("SUPABASE_URL:", "Configurada" if settings.SUPABASE_URL else "No configurada")
    
    if settings.SUPABASE_DATABASE_URL:
        # Intentar conectarse y obtener las últimas fechas
        import sqlalchemy
        engine = sqlalchemy.create_engine(settings.SUPABASE_DATABASE_URL)
        with engine.connect() as conn:
            # Obtener tablas
            meta = sqlalchemy.MetaData()
            meta.reflect(bind=engine)
            print("Tablas en Supabase:", list(meta.tables.keys()))
            
            # Buscar últimas ofertas
            if 'offers' in meta.tables:
                max_seen = conn.execute(sqlalchemy.text("SELECT max(last_seen) FROM offers")).fetchone()[0]
                print("Última oferta vista en Supabase (last_seen):", max_seen)
            if 'products' in meta.tables:
                max_updated = conn.execute(sqlalchemy.text("SELECT max(updated_at) FROM products")).fetchone()[0]
                print("Último producto actualizado en Supabase (updated_at):", max_updated)
            if 'scraper_execution_logs' in meta.tables:
                max_log = conn.execute(sqlalchemy.text("SELECT max(start_time) FROM scraper_execution_logs")).fetchone()[0]
                print("Último log de scraper en Supabase (start_time):", max_log)
            if 'pending_matches' in meta.tables:
                max_pm = conn.execute(sqlalchemy.text("SELECT max(found_at) FROM pending_matches")).fetchone()[0]
                print("Último pending_match en Supabase (found_at):", max_pm)
except Exception as e:
    print("Error:", e)
