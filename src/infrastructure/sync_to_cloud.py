
import sqlite3
from sqlalchemy import create_engine, text, inspect, Boolean
from src.core.config import settings
from src.domain.models import Base
import os

def sync():
    """
    Migra los datos de oraculo.db (SQLite) a Supabase (Postgres).
    Version 'Genius': 
    1. Detecta tipos booleanos automaticamente usando los modelos de SQLAlchemy.
    2. Convierte 0/1 a False/True para Postgres.
    """
    print("--- INICIANDO MIGRACION INTELIGENTE A SUPABASE ---")
    
    db_path = "oraculo.db"
    if not os.path.exists(db_path):
        print(f"Error: No se encuentra el archivo {db_path} en la raiz.")
        return

    # 1. Conexiones
    local_conn = sqlite3.connect(db_path)
    local_conn.row_factory = sqlite3.Row
    
    cloud_url = settings.SUPABASE_DATABASE_URL
    if not cloud_url:
        print("Error: SUPABASE_DATABASE_URL no encontrada en .env")
        return

    cloud_engine = create_engine(cloud_url)
    
    # 2. Detectar tablas reales en el archivo SQLite
    cursor = local_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tablas detectadas: {', '.join(tables)}")

    # 3. Asegurar Esquema en Cloud
    print("Verificando tablas en la nube...")
    Base.metadata.create_all(bind=cloud_engine)
    
    # 4. Mapeo de tipos booleanos por tabla
    bool_columns_map = {}
    for table_name, table_obj in Base.metadata.tables.items():
        bool_cols = [col.name for col in table_obj.columns if isinstance(col.type, Boolean)]
        if bool_cols:
            bool_columns_map[table_name] = bool_cols

    try:
        with cloud_engine.begin() as cloud_conn:
            for table in tables:
                print(f"Migrando {table}...")
                
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if not rows:
                    print(f"  -> Tabla {table} esta vacia. Saltando.")
                    continue

                columns = rows[0].keys()
                col_names = ", ".join([f'"{c}"' for c in columns])
                placeholders = ", ".join([f":{c}" for c in columns])
                
                insert_stmt = text(f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING')
                
                # Obtener columnas booleanas para esta tabla
                bool_cols = bool_columns_map.get(table, [])
                
                count = 0
                for row in rows:
                    data = dict(row)
                    # Conversion automatica de tipos para Postgres
                    for col in bool_cols:
                        if col in data and isinstance(data[col], int):
                            data[col] = bool(data[col])
                    
                    cloud_conn.execute(insert_stmt, data)
                    count += 1
                
                print(f"  -> Exito: {count} registros sincronizados.")

        print("\n--- ¡MIGRACION FINALIZADA CON EXITO! ---")

    except Exception as e:
        print(f"\nError critico: {e}")
    finally:
        local_conn.close()

if __name__ == "__main__":
    sync()
