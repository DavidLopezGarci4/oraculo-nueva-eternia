
import pandas as pd
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel
from loguru import logger

def audit_catalogs():
    excel_path = 'C:/Users/dace8/OneDrive/Documentos/Antigravity/el-oraculo-de-eternia/data/MOTU/lista_MOTU.xlsx'
    logger.info(f"Auditing Excel: {excel_path}")
    
    # 1. Load Excel
    xl = pd.ExcelFile(excel_path)
    excel_data = []
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        # Apply the same logic as our migration script
        df = df.dropna(subset=['Figure ID'])
        for _, row in df.iterrows():
            raw_id = row['Figure ID']
            try:
                if isinstance(raw_id, float) and raw_id.is_integer():
                    f_id = str(int(raw_id))
                else:
                    f_id = str(raw_id).strip()
            except:
                f_id = str(raw_id).strip()
            
            # Sub-category logic
            sub_cat = sheet.replace('_Checklist', '').replace('_Checklis', '').replace('_', ' ').strip()
            if "Beasts_Vehicles_and_Pla" in sheet or "Beasts Vehicles" in sub_cat:
                sub_cat = "Beasts, Vehicles and Playsets"
            if "Origins Action" in sub_cat: sub_cat = "Origins"
            elif "Deluxe" in sub_cat: sub_cat = "Origins Deluxe"
            elif "Exclusives" in sub_cat: sub_cat = "Origins Exclusives"
            
            excel_data.append({
                'name': str(row['Name']).strip(),
                'figure_id': f_id,
                'sub_cat': sub_cat
            })

    # 2. Get Supabase data
    db = SessionCloud()
    cloud_products = db.query(ProductModel).all()
    cloud_map = {p.figure_id: p for p in cloud_products}
    db.close()

    # 3. Compare
    logger.info(f"Excel Items: {len(excel_data)}")
    logger.info(f"Cloud Items: {len(cloud_products)}")

    inconsistencies = []
    
    # A. Check Excel -> Cloud
    for item in excel_data:
        f_id = item['figure_id']
        if f_id not in cloud_map:
            inconsistencies.append(f"MISSING IN CLOUD: {item['name']} (ID: {f_id})")
        else:
            p = cloud_map[f_id]
            if p.name != item['name']:
                inconsistencies.append(f"NAME MISMATCH (ID {f_id}): Excel='{item['name']}' | Cloud='{p.name}'")
            if p.sub_category != item['sub_cat']:
                inconsistencies.append(f"CAT MISMATCH (ID {f_id}): Excel='{item['sub_cat']}' | Cloud='{p.sub_category}'")

    # B. Check Cloud -> Excel
    excel_ids = {i['figure_id'] for i in excel_data}
    for f_id in cloud_map:
        if f_id not in excel_ids:
            inconsistencies.append(f"GHOST IN CLOUD (Not in Excel): {cloud_map[f_id].name} (ID: {f_id})")

    # 4. Report
    if not inconsistencies:
        logger.success("✅ NO INCONSISTENCIES FOUND between clean Excel and Cloud.")
    else:
        logger.warning(f"Found {len(inconsistencies)} inconsistencies:")
        for inc in inconsistencies[:20]: # Show first 20
            print(inc)
        if len(inconsistencies) > 20:
            print(f"... and {len(inconsistencies)-20} more.")

if __name__ == "__main__":
    audit_catalogs()
