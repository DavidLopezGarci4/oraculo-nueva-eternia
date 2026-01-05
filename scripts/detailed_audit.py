
import pandas as pd
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel
from loguru import logger

def detailed_audit():
    excel_path = 'C:/Users/dace8/OneDrive/Documentos/Antigravity/el-oraculo-de-eternia/data/MOTU/lista_MOTU.xlsx'
    xl = pd.ExcelFile(excel_path)
    
    logger.info("--- [AUDIT] EXCEL COMPREHENSIVE BREAKDOWN ---")
    total_found = 0
    all_items = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        # Drop rows where Name is null
        df = df[df['Name'].notna()]
        
        for _, row in df.iterrows():
            raw_id = row.get('Figure ID')
            if pd.isna(raw_id):
                continue
            
            total_found += 1
            all_items.append({
                'sheet': sheet,
                'name': str(row['Name']).strip(),
                'figure_id': str(raw_id)
            })

    logger.info(f"Total Rows with any Figure ID: {total_found}")
    
    # Analyze IDs
    numeric_ids = 0
    float_ids = 0
    text_ids = 0
    for item in all_items:
        fid = item['figure_id']
        if fid.replace('.0','').isdigit():
            numeric_ids += 1
            if '.0' in fid: float_ids += 1
        else:
            text_ids += 1
            
    logger.info(f"Numeric/Int IDs: {numeric_ids}")
    logger.info(f"Float IDs (.0): {float_ids}")
    logger.info(f"Text/Mix IDs: {text_ids}")

    # Check for duplicates across sheets
    id_counts = {}
    for item in all_items:
        fid = item['figure_id']
        id_counts[fid] = id_counts.get(fid, 0) + 1
    
    dupes = {fid: count for fid, count in id_counts.items() if count > 1}
    if dupes:
        logger.warning(f"Found {len(dupes)} IDs duplicated across sheets!")
        # for fid, count in dupes.items():
        #     logger.info(f"ID {fid} appears {count} times")

    # Supabase check
    db = SessionCloud()
    cloud_count = db.query(ProductModel).count()
    db.close()
    logger.info(f"Supabase Total: {cloud_count}")

if __name__ == "__main__":
    detailed_audit()
