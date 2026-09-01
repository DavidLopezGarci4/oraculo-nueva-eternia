import os
import re
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin
from datetime import datetime, timezone

from PIL import Image
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.domain.models import ProductModel
from src.application.services.storage_service import StorageService

logger = logging.getLogger('oraculo.catalog_refresh')

class CatalogRefreshService:
    CHECKLIST_URLS = [
        'https://www.actionfigure411.com/masters-of-the-universe/origins-checklist.php',
        'https://www.actionfigure411.com/masters-of-the-universe/original-checklist.php',
        'https://www.actionfigure411.com/masters-of-the-universe/masterverse-checklist.php',
        'https://www.actionfigure411.com/masters-of-the-universe/turtles-of-grayskull-checklist.php'
    ]

    @classmethod
    def find_af411_detail_url(cls, figure_id: str) -> Optional[str]:
        clean_id = str(figure_id).strip()
        for chk_url in cls.CHECKLIST_URLS:
            try:
                res = cffi_requests.get(chk_url, impersonate='chrome120', timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    link = soup.find('a', href=lambda h: h and clean_id in h)
                    if link and link.get('href'):
                        return urljoin('https://www.actionfigure411.com/masters-of-the-universe/', link.get('href'))
            except Exception as e:
                logger.warning(f'Error consultando checklist {chk_url}: {e}')
        return None

    @classmethod
    def refresh_figure_image(cls, db: Session, figure_id_or_product_id: str) -> Dict[str, Any]:
        query_val = str(figure_id_or_product_id).strip()
        product = None
        if query_val.isdigit():
            product = db.query(ProductModel).filter(
                (ProductModel.id == int(query_val)) | (ProductModel.figure_id == query_val)
            ).first()
        else:
            product = db.query(ProductModel).filter(ProductModel.figure_id == query_val).first()

        if not product:
            return {'success': False, 'error': f'No se encontro la figura con ID {query_val}'}

        effective_fig_id = product.figure_id or query_val
        detail_url = cls.find_af411_detail_url(effective_fig_id)
        if not detail_url:
            return {'success': False, 'error': f'No se encontro URL en AF411 para {effective_fig_id}'}

        try:
            d_res = cffi_requests.get(detail_url, impersonate='chrome120', timeout=10)
            if d_res.status_code != 200:
                return {'success': False, 'error': f'Error en {detail_url} HTTP {d_res.status_code}'}
            
            d_soup = BeautifulSoup(d_res.text, 'html.parser')
            a_fancy = d_soup.select_one('a[data-fancybox][href]')
            if not a_fancy or not a_fancy.get('href'):
                return {'success': False, 'error': 'No se encontro enlace fancybox'}

            remote_img_url = urljoin('https://www.actionfigure411.com/', a_fancy.get('href'))
            img_res = cffi_requests.get(remote_img_url, impersonate='chrome120', timeout=15)
            if img_res.status_code != 200:
                return {'success': False, 'error': f'Error descargando imagen HTTP {img_res.status_code}'}

            temp_dir = Path('data/temp_images')
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            slug_name = re.sub(r'[^a-zA-Z0-9]', '-', product.name.lower()).strip('-')
            webp_filename = f'{slug_name}-{effective_fig_id}.webp'
            webp_path = temp_dir / webp_filename

            import io
            with Image.open(io.BytesIO(img_res.content)) as im:
                if im.mode in ('RGBA', 'LA'):
                    bg = Image.new('RGB', im.size, (255, 255, 255))
                    bg.paste(im, mask=im.split()[3])
                    im = bg
                elif im.mode != 'RGB':
                    im = im.convert('RGB')
                im.save(str(webp_path), 'WEBP', quality=90)

            with open(webp_path, 'rb') as f:
                img_hash = hashlib.md5(f.read()).hexdigest()

            folder = 'vintage' if product.is_vintage else ''
            storage = StorageService()
            new_public_url = storage.upload_image(str(webp_path), folder=folder)

            if not new_public_url:
                bucket_prefix = 'https://stxjzolhpcinrbkltehy.supabase.co/storage/v1/object/public/motu-catalog/'
                subpath = f'vintage/{webp_filename}' if product.is_vintage else webp_filename
                new_public_url = f'{bucket_prefix}{subpath}'

            old_image_url = product.image_url
            product.image_url = new_public_url
            product.master_image_hash = img_hash
            product.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(product)

            return {
                'success': True,
                'product_id': product.id,
                'figure_id': effective_fig_id,
                'name': product.name,
                'old_image_url': old_image_url,
                'new_image_url': new_public_url,
                'image_hash': img_hash,
                'af411_source': remote_img_url
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
