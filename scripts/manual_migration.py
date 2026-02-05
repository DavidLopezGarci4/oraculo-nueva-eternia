
import os
import sys
from pathlib import Path
import logging

# Add src to path
root_dir = Path(".").absolute()
sys.path.append(str(root_dir))

from scripts.phase0_migration import migrate_excel_to_db
from src.infrastructure.database_cloud import SessionCloud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ManualMigration")

def run_manual_migration():
    excel_path = root_dir / "data" / "MOTU" / "lista_MOTU.xlsx"
    print(f"STARTING STANDALONE MIGRATION FROM: {excel_path}")
    
    if not excel_path.exists():
        print(f"ERROR: Excel file not found at {excel_path}")
        return

    try:
        with SessionCloud() as session:
            migrate_excel_to_db(str(excel_path), session)
            session.commit()
        print("SUCCESS: MANAUL MIGRATION COMPLETED SUCCESSFULLY!")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_manual_migration()
