#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from datetime import datetime

logger = logging.getLogger("VintageMigration")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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
    s = str(val).replace('$', '').replace('€', '').replace(',', '').strip()
    try:
        return float(s)
    except:
        return 0.0

def normalize_us_price(val_usd: float) -> float:
    """
    Normalizes a US Dollar value to Euro for comparison.
    Vintage baseline: 1 USD = 0.92 EUR.
    """
    if not val_usd or val_usd <= 0: return 0.0
    return round(val_usd * 0.92, 2)

def download_missing_image(url: str, local_path: str) -> bool:
    import requests
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"⬇️ Downloaded missing image from web: {url} -> {local_path}")
            return True
        else:
            logger.warning(f"⚠️ Failed to download image from web (status {r.status_code}): {url}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error downloading image from web {url}: {e}")
        return False

def resolve_local_image_path(image_path_str: str, image_url: str = None) -> str | None:
    if not image_path_str:
        return None
    
    # Normalize paths
    path_str = image_path_str.replace('\\', '/')
    if path_str.startswith('/app/'):
        path_str = path_str.replace('/app/', '', 1)
        
    project_root = Path(__file__).resolve().parent.parent
    local_path = project_root / path_str
    
    if local_path.exists():
        return str(local_path)
        
    # Try direct path
    direct_path = Path(image_path_str)
    if direct_path.exists():
        return str(direct_path)
        
    # If file doesn't exist but we have a web URL, download it!
    if image_url and image_url.startswith('http'):
        if "supabase.co" not in image_url:
            success = download_missing_image(image_url, str(local_path))
            if success:
                return str(local_path)
                
    return None

def cache_image_locally(src_path: str, product_id: int, session):
    if os.getenv("GITHUB_ACTIONS") == "true":
        return
        
    try:
        from PIL import Image
        cache_dir = settings.IMAGE_CACHE_DIR
        os.makedirs(cache_dir, exist_ok=True)
        dest_path = os.path.join(cache_dir, f"{product_id}.webp")
        
        # 1. Convert to WebP and save in server cache if not exists
        if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
            with Image.open(src_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(dest_path, "WEBP", quality=85)
                logger.info(f"📸 Cached image locally: {dest_path}")
        
        # 2. Copy to user's configured custom paths (pc_image_path / mobile_image_path)
        from src.domain.models import UserModel
        users = session.query(UserModel).filter(
            (UserModel.pc_image_path != None) | (UserModel.mobile_image_path != None)
        ).all()
        
        import shutil
        for user in users:
            for path_attr in ['pc_image_path', 'mobile_image_path']:
                custom_dir = getattr(user, path_attr)
                if custom_dir:
                    try:
                        os.makedirs(custom_dir, exist_ok=True)
                        user_dest = os.path.join(custom_dir, f"{product_id}.webp")
                        if not os.path.exists(user_dest) or os.path.getsize(user_dest) == 0:
                            shutil.copy2(dest_path, user_dest)
                            logger.info(f"📂 Copied WebP to user custom {path_attr}: {user_dest}")
                    except Exception as ce:
                        logger.warning(f"⚠️ Failed to copy WebP to custom folder {custom_dir}: {ce}")
    except Exception as e:
        logger.warning(f"⚠️ Error caching image {src_path} for product {product_id}: {e}")

def migrate_excel_to_db(excel_path: str, session):
    """
    Core migration logic for Vintage figures.
    Reads all sheets, processes headers, and merges into the provided DB session.
    Forces is_vintage = True.
    """
    logger.info(f"📂 Reading Vintage Excel: {excel_path}")
    
    try:
        with pd.ExcelFile(excel_path) as xl:
            sheet_names = xl.sheet_names
            
            # Get default user for collection ownership (David First)
            target_user = session.query(UserModel).filter_by(username="David").first()
            if not target_user:
                target_user = session.query(UserModel).filter_by(username="admin").first()
            
            if not target_user:
                target_user = UserModel(username="David", email="dace81@gmail.com", hashed_password="pw", role="admin")
                session.add(target_user)
                session.commit()

            total_imported = 0
            total_collected = 0

            for sheet in sheet_names:
                logger.info(f"📄 Processing Vintage sheet: {sheet}")
                
                df = pd.read_excel(xl, sheet_name=sheet, header=1)
                df.columns = [str(c).strip() for c in df.columns]
                
                # Derive a clean sub_category (Line) from sheet name
                raw_sub = sheet.replace('_Checklist', '').replace('_Checklis', '').replace('_', ' ').strip()
                # e.g., "1982" -> "Vintage 1982"
                if not raw_sub.startswith("Vintage"):
                    sub_category = f"Vintage {raw_sub}"
                else:
                    sub_category = raw_sub
                
                required = ['Name', 'Figure ID', 'Detail Link']
                if not all(col in df.columns for col in required):
                    logger.warning(f"⚠️ Missing required columns in sheet {sheet}. Skipping.")
                    continue

                for _, row in df.iterrows():
                    raw_id = row.get('Figure ID')
                    if pd.isna(raw_id) or str(raw_id).strip().lower() == 'nan':
                        continue
                    
                    try:
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

                    # Find product (specifically a Vintage product)
                    product = session.query(ProductModel).filter_by(figure_id=figure_id, is_vintage=True).first()
                    if not product:
                        product = session.query(ProductModel).filter_by(name=name, sub_category=sub_category, is_vintage=True).first()

                    # Supabase Image Path mapping in the dedicated "/vintage/" subdirectory
                    image_url_raw = row.get('Image URL')
                    image_url = image_url_raw
                    image_path = row.get('Image Path')
                    
                    resolved_path = resolve_local_image_path(image_path, image_url_raw)
                    if resolved_path:
                        filename = os.path.basename(resolved_path)
                        filename_webp = os.path.splitext(filename)[0] + ".webp"
                        supabase_url = getattr(settings, "SUPABASE_URL", "")
                        if supabase_url:
                            image_url = f"{supabase_url}/storage/v1/object/public/motu-catalog/vintage/{filename_webp}"

                    currency = row.get('Currency', 'USD')
                    avg_raw = clean_price(row.get('Avg'))
                    
                    if currency == 'USD':
                         avg_us = normalize_us_price(avg_raw)
                    else:
                         avg_us = avg_raw

                    if not product:
                        # Create NEW Vintage Product
                        product = ProductModel(
                            name=name,
                            figure_id=figure_id,
                            image_url=image_url,
                            category="Masters of the Universe",
                            sub_category=sub_category,
                            variant_name=str(row.get('Wave', '')),
                            retail_price=clean_price(row.get('Retail')),
                            avg_market_price=avg_us,
                            p25_price=clean_price(row.get('P25')),
                            avg_p2p_price_us=avg_us,
                            release_year=int(row.get('Year')) if pd.notna(row.get('Year')) and str(row.get('Year')).isdigit() else None,
                            popularity_score=int(row.get('Popularity', 0)) if pd.notna(row.get('Popularity')) else 0,
                            market_momentum=float(row.get('Momentum', 1.0)) if pd.notna(row.get('Momentum')) else 1.0,
                            asin=str(row.get('ASIN', '')).strip() if pd.notna(row.get('ASIN')) else None,
                            upc=str(row.get('UPC', '')).strip() if pd.notna(row.get('UPC')) else None,
                            is_vintage=True # global mark for parallel line
                        )
                        session.add(product)
                        session.flush()
                        total_imported += 1
                        if resolved_path:
                            cache_image_locally(resolved_path, product.id, session)
                    else:
                        # Update Existing Vintage Product
                        if figure_id and not product.figure_id:
                            product.figure_id = figure_id
                        
                        if image_url:
                            product.image_url = image_url
                            
                        if resolved_path:
                            cache_image_locally(resolved_path, product.id, session)
                        
                        product.retail_price = clean_price(row.get('Retail'))
                        product.avg_p2p_price_us = avg_us
                        
                        p25_raw = clean_price(row.get('P25'))
                        if currency == 'USD':
                            product.p25_p2p_price = normalize_us_price(p25_raw)
                        else:
                            product.p25_p2p_price = p25_raw
                        
                        if pd.notna(row.get('Year')) and str(row.get('Year')).isdigit():
                            product.release_year = int(row.get('Year'))

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
                            
                        # Make sure it's strictly marked as vintage
                        product.is_vintage = True

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

                    # 3. COLLECTION SYNC (ADQUIRIDO)
                    adquirido = str(row.get('Adquirido', 'No')).strip().upper()
                    is_acquired = adquirido.startswith('S') or adquirido in ['YES', 'TRUE', '1', '1.0']
                    if is_acquired:
                        exists = session.query(CollectionItemModel).filter_by(
                            product_id=product.id, 
                            owner_id=target_user.id
                        ).first()
                        
                        if not exists:
                            item = CollectionItemModel(
                                product_id=product.id,
                                owner_id=target_user.id,
                                acquired=True,
                                condition="MOC" if target_user.username == "David" else "New",
                                notes=f"Imported from Vintage Checklist ({sheet})"
                            )
                            session.add(item)
                            total_collected += 1

                session.commit()
            
            logger.info(f"✅ Vintage Migration Summary: {total_imported} vintage products imported, {total_collected} collected items added.")

    except Exception as e:
        logger.error(f"❌ Vintage Migration Error: {e}")
        session.rollback()
        raise

if __name__ == "__main__":
    db_url = settings.DATABASE_URL
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    project_root = Path(__file__).resolve().parent.parent
    excel_path = project_root / "data" / "MOTU" / "lista_vintage.xlsx"
    
    if not excel_path.exists():
        logger.error(f"Excel file not found at {excel_path}")
        sys.exit(1)
        
    migrate_excel_to_db(str(excel_path), session)
    session.close()
