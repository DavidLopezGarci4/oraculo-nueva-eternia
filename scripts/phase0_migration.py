
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from datetime import datetime

logger = logging.getLogger("Migration")

# Add src to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import (
    Base, ProductModel, ProductAliasModel, CollectionItemModel, UserModel
)

def clean_price(val):
    """Limpia símbolos de moneda y convierte a float."""
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    # Quitar $14.99 -> 14.99, tildes, símbolos, etc.
    s = str(val).replace('$', '').replace('€', '').replace(',', '').strip()
    try:
        return float(s)
    except:
        return 0.0

def normalize_us_price(val_usd: float) -> float:
    """
    Normalizes a US Dollar value to Euro for comparison.
    Phase 10: Master Nexus baseline is 1 USD = 0.92 EUR (consistent with BBTS scraper).
    """
    if not val_usd or val_usd <= 0: return 0.0
    return round(val_usd * 0.92, 2)

def migrate_excel_to_db(excel_path: str, session):
    """
    Core migration logic.
    Reads all sheets, processes headers, and merges into the provided DB session.
    """
    logger.info(f"📂 Reading Excel: {excel_path}")
    
    try:
        # Load all sheets using a context manager to avoid file locks on Windows
        with pd.ExcelFile(excel_path) as xl:
            sheet_names = xl.sheet_names
            
            # Get default user for collection ownership
            # Get default user for collection ownership (Phase 42 Fix: David First)
            target_user = session.query(UserModel).filter_by(username="David").first()
            if not target_user:
                target_user = session.query(UserModel).filter_by(username="admin").first()
            
            if not target_user:
                # Fallback if no user exists (e.g. initial setup)
                target_user = UserModel(username="David", email="dace81@gmail.com", hashed_password="pw", role="admin")
                session.add(target_user)
                session.commit()

            total_imported = 0
            total_collected = 0

            for sheet in sheet_names:
                logger.info(f"📄 Processing sheet: {sheet}")
                
                # Read sheet starting from row 1 (headers)
                df = pd.read_excel(xl, sheet_name=sheet, header=1)
                
                # Clean columns (strip whitespace)
                df.columns = [str(c).strip() for c in df.columns]
                
                # Derive a clean sub_category (Line) from sheet name
                sub_category = sheet.replace('_Checklist', '').replace('_Checklis', '').replace('_', ' ').strip()
                
                # USER FEEDBACK: Standardize Beasts/Vehicles sub_category
                if "Beasts_Vehicles_and_Pla" in sheet or "Beasts Vehicles" in sub_category:
                    sub_category = "Beasts, Vehicles and Playsets"
                
                # Special cases for common sheet names
                if "Origins Action" in sub_category: sub_category = "Origins"
                elif "Deluxe" in sub_category: sub_category = "Origins Deluxe"
                elif "Exclusives" in sub_category: sub_category = "Origins Exclusives"
                
                # Validate required columns
                required = ['Name', 'Figure ID', 'Detail Link']
                if not all(col in df.columns for col in required):
                    logger.warning(f"⚠️ Missing required columns in sheet {sheet}. Skipping.")
                    continue

                for _, row in df.iterrows():
                    # 0. CLEAN FIGURE ID (Convert float to int string)
                    raw_id = row.get('Figure ID')
                    if pd.isna(raw_id) or str(raw_id).strip().lower() == 'nan':
                        continue # USER REQ: Remove/Skip NULL Figure IDs
                    
                    try:
                        # Convert 12.0 to "12", or keep "MC-01" as "MC-01"
                        if isinstance(raw_id, float) and raw_id.is_integer():
                            figure_id = str(int(raw_id))
                        else:
                            figure_id = str(raw_id).strip()
                    except Exception:
                        figure_id = str(raw_id).strip()

                    name = str(row['Name']).strip()
                    detail_link = str(row['Detail Link']).strip() if pd.notna(row['Detail Link']) else None
                    
                    if not name or name == "nan":
                        continue

                    # 1. FIND OR CREATE PRODUCT
                    product = None
                    if figure_id:
                        product = session.query(ProductModel).filter_by(figure_id=figure_id).first()
                    
                    if not product:
                        # Fallback to Name + Series if Figure ID missing or not found
                        product = session.query(ProductModel).filter_by(name=name, sub_category=sub_category, figure_id=None).first()

                    if not product:
                        # Create NEW
                        image_url = row.get('Image URL')
                        image_path = row.get('Image Path')
                        
                        # Phase 26: If we have a local path, we assume it's synced to Supabase
                        # The URL pattern for Supabase is predictable
                        if image_path and os.path.exists(image_path):
                            filename = os.path.basename(image_path)
                            # Fallback if image_url is missing or ActionFigure411 specific
                            from src.core.config import settings
                            supabase_url = getattr(settings, "SUPABASE_URL", "")
                            if supabase_url:
                                image_url = f"{supabase_url}/storage/v1/object/public/motu-catalog/{filename}"

                        # Phase 10 (Master Nexus): Segregated Benchmarks
                        currency = row.get('Currency', 'USD')
                        avg_raw = clean_price(row.get('Avg'))
                        
                        if currency == 'USD':
                             avg_us = normalize_us_price(avg_raw)
                        else:
                             avg_us = avg_raw # Already in EUR
                             
                        product = ProductModel(
                            name=name,
                            figure_id=figure_id,
                            image_url=image_url,
                            category="Masters of the Universe",
                            sub_category=sub_category,
                            variant_name=str(row.get('Wave', '')), # Using Wave as variant context
                            retail_price=clean_price(row.get('Retail')),
                            avg_market_price=avg_us, 
                            p25_price=clean_price(row.get('P25')),
                            # Phase 10 (Master Nexus): Segregated Benchmarks
                            avg_p2p_price_us=avg_us,
                            release_year=int(row.get('Year')) if pd.notna(row.get('Year')) and str(row.get('Year')).isdigit() else None,
                            
                            # Phase 50 Intelligence
                            popularity_score=int(row.get('Popularity', 0)) if pd.notna(row.get('Popularity')) else 0,
                            market_momentum=float(row.get('Momentum', 1.0)) if pd.notna(row.get('Momentum')) else 1.0,
                            asin=str(row.get('ASIN', '')).strip() if pd.notna(row.get('ASIN')) else None,
                            upc=str(row.get('UPC', '')).strip() if pd.notna(row.get('UPC')) else None
                        )
                        session.add(product)
                        session.flush() # Get ID
                        total_imported += 1
                    else:
                        # UPDATE existing if needed
                        if figure_id and not product.figure_id:
                            product.figure_id = figure_id
                        
                        # Ensure we have a cloud/valid image URL
                        image_path = row.get('Image Path')
                        if image_path and os.path.exists(image_path):
                            filename = os.path.basename(image_path)
                            from src.core.config import settings
                            supabase_url = getattr(settings, "SUPABASE_URL", "")
                            if supabase_url:
                                product.image_url = f"{supabase_url}/storage/v1/object/public/motu-catalog/{filename}"
                        elif not product.image_url:
                            product.image_url = row.get('Image URL')
                        
                        # Phase 18: Update intelligence fields even if product exists
                        product.retail_price = clean_price(row.get('Retail'))
                        product.avg_market_price = clean_price(row.get('Avg'))
                        # Phase 18 & 10 Updates
                        currency = row.get('Currency', 'USD')
                        avg_raw = clean_price(row.get('Avg'))
                        if currency == 'USD':
                            avg_us = normalize_us_price(avg_raw)
                        else:
                            avg_us = avg_raw
                            
                        product.avg_p2p_price_us = avg_us
                        
                        p25_raw = clean_price(row.get('P25'))
                        if currency == 'USD':
                            product.p25_p2p_price = normalize_us_price(p25_raw)
                        else:
                            product.p25_p2p_price = p25_raw
                        
                        if pd.notna(row.get('Year')) and str(row.get('Year')).isdigit():
                            product.release_year = int(row.get('Year'))

                        # Legacy sync
                        product.avg_market_price = product.avg_p2p_price_us
                        product.p25_price = product.p25_p2p_price

                        if pd.notna(row.get('Popularity')):
                            product.popularity_score = int(row.get('Popularity'))
                        if pd.notna(row.get('Momentum')):
                            product.market_momentum = float(row.get('Momentum'))
                        if pd.notna(row.get('ASIN')):
                            product.asin = str(row.get('ASIN')).strip()
                        if pd.notna(row.get('UPC')):
                            product.upc = str(row.get('UPC')).strip()

                    # 2. ALIAS LAYER
                    if detail_link:
                        alias = session.query(ProductAliasModel).filter_by(source_url=detail_link).first()
                        if not alias:
                            alias = ProductAliasModel(
                                product_id=product.id,
                                source_url=detail_link,
                                confirmed=True
                            )
                            session.add(alias)

                    # 3. COLLECTION (ADQUIRIDO)
                    adquirido = str(row.get('Adquirido', 'No')).strip().upper()
                    # Robust check: 'S' starts with S (can have non-ascii junk)
                    is_acquired = adquirido.startswith('S') or adquirido in ['YES', 'TRUE', '1', '1.0']
                    if is_acquired:
                        # Check if already in collection
                        exists = session.query(CollectionItemModel).filter_by(
                            product_id=product.id, 
                            owner_id=target_user.id
                        ).first()
                        
                        if not exists:
                            item = CollectionItemModel(
                                product_id=product.id,
                                owner_id=target_user.id,
                                acquired=True,
                                condition="New",
                                notes=f"Imported from Phase 0 Excel ({sheet})"
                            )
                            session.add(item)
                            total_collected += 1

                session.commit()
            
            logger.info(f"✅ Migration Summary: {total_imported} products imported, {total_collected} collected items added.")

    except Exception as e:
        logger.error(f"❌ Migration Error: {e}")
        session.rollback()
        raise

if __name__ == "__main__":
    # Setup for standalone run
    db_url = settings.DATABASE_URL
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Resolve relative to project root
    project_root = Path(__file__).resolve().parent.parent
    excel_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
    
    if not excel_path.exists():
        logger.error(f"Excel file not found at {excel_path}")
        sys.exit(1)
        
    migrate_excel_to_db(str(excel_path), session)
    session.close()
