
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Restorer")

def clean_acquired(val):
    if pd.isna(val): return "No"
    s = str(val).strip().upper()
    # Handle "SÍ", "SI", "YES", "S", "TRUE", "1"
    if s.startswith('S') or s in ['YES', 'TRUE', '1', '1.0']:
        return "SÍ"
    return "No"

def restore_acquired_status():
    project_root = Path("data/MOTU")
    backup_path = project_root / "lista_MOTU_backup.xlsx"
    current_path = project_root / "lista_MOTU.xlsx"
    
    if not backup_path.exists():
        logger.error(f"Backup file not found at {backup_path}")
        return
    if not current_path.exists():
        logger.error(f"Current file not found at {current_path}")
        return
    
    logger.info(f"Reading backup: {backup_path}")
    logger.info(f"Reading current: {current_path}")
    
    with pd.ExcelFile(backup_path) as xl_old, pd.ExcelFile(current_path) as xl_new:
        old_sheets = {s: pd.read_excel(xl_old, sheet_name=s, header=1) for s in xl_old.sheet_names}
        new_sheets = {s: pd.read_excel(xl_new, sheet_name=s, header=1) for s in xl_new.sheet_names}
    
    # Create mappings
    acquired_by_id = {}
    acquired_by_name_year = {}
    
    for sheet_name, df in old_sheets.items():
        if 'Adquirido' not in df.columns: continue
        for _, row in df.iterrows():
            status = clean_acquired(row.get('Adquirido'))
            if status != "SÍ": continue
            
            fig_id = str(row.get('Figure ID', '')).strip()
            name = str(row.get('Name', '')).strip()
            year = str(row.get('Year', '')).strip()
            
            if fig_id and fig_id != 'nan' and fig_id != '0':
                # Convert 2394.0 -> 2394
                if fig_id.endswith('.0'): fig_id = fig_id[:-2]
                acquired_by_id[fig_id] = "SÍ"
            
            key = f"{name}|{year}"
            acquired_by_name_year[key] = "SÍ"

    logger.info(f"Mapped {len(acquired_by_id)} items by Figure ID and {len(acquired_by_name_year)} by Name|Year.")
    
    updated_sections = []
    total_restored = 0
    for sheet_name, df_new in new_sheets.items():
        logger.info(f"Restoring 'Adquirido' for sheet: {sheet_name}")
        df_new['Adquirido'] = 'No' # Default
        for i, row in df_new.iterrows():
            fig_id = str(row.get('Figure ID', '')).strip()
            if fig_id.endswith('.0'): fig_id = fig_id[:-2]
            
            name = str(row.get('Name', '')).strip()
            year = str(row.get('Year', '')).strip()
            key = f"{name}|{year}"
            
            found = False
            if fig_id in acquired_by_id:
                df_new.at[i, 'Adquirido'] = "SÍ"
                found = True
            elif key in acquired_by_name_year:
                df_new.at[i, 'Adquirido'] = "SÍ"
                found = True
            
            if found:
                total_restored += 1
        
        updated_sections.append((sheet_name, df_new))

    logger.info(f"Total items restored as 'SÍ': {total_restored}")

    with pd.ExcelWriter(current_path, engine='xlsxwriter') as writer:
        for name, df in updated_sections:
            df.to_excel(writer, sheet_name=name[:31], index=False, startrow=1)
            ws = writer.sheets[name[:31]]
            ws.write(0, 0, name)

    logger.info("Successfully restored 'Adquirido' status to fresh Excel.")

if __name__ == "__main__":
    restore_acquired_status()
