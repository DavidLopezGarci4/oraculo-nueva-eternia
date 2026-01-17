"""
Script para corregir la secuencia de IDs de collection_items en PostgreSQL.
Este problema ocurre cuando se migran datos con IDs específicos sin actualizar la secuencia.
"""
from src.infrastructure.database_cloud import SessionCloud
from sqlalchemy import text

def fix_sequence():
    with SessionCloud() as db:
        # Get max ID
        result = db.execute(text("SELECT MAX(id) FROM collection_items"))
        max_id = result.scalar() or 0
        print(f"Current max ID in collection_items: {max_id}")
        
        # Get current sequence value
        result = db.execute(text("SELECT last_value FROM collection_items_id_seq"))
        seq_val = result.scalar()
        print(f"Current sequence value: {seq_val}")
        
        # Fix the sequence
        new_val = max_id + 1
        db.execute(text(f"ALTER SEQUENCE collection_items_id_seq RESTART WITH {new_val}"))
        db.commit()
        
        print(f"[OK] Sequence reset to: {new_val}")
        
        # Verify
        result = db.execute(text("SELECT last_value FROM collection_items_id_seq"))
        print(f"New sequence value: {result.scalar()}")

if __name__ == "__main__":
    fix_sequence()
