import json
import os
import threading
import httpx
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.core.config import settings

router = APIRouter(tags=["vault"])

# Estado de la descarga de imágenes en caché
_image_download_status = {
    "active": False,
    "total": 0,
    "current": 0,
    "errors": 0,
    "last_error": None
}
_image_download_lock = threading.Lock()


async def download_all_images_task(user_id: int = 2, client_type: str = "pc"):
    global _image_download_status
    
    from src.domain.models import ProductModel, UserModel
    
    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
    image_cache_dir = settings.IMAGE_CACHE_DIR
    if user:
        custom_path = user.mobile_image_path if client_type == "mobile" else user.pc_image_path
        if custom_path:
            try:
                os.makedirs(custom_path, exist_ok=True)
                image_cache_dir = custom_path
            except Exception as e:
                logger.warning(f"No se pudo crear la ruta personalizada {custom_path}: {e}")
                
    os.makedirs(image_cache_dir, exist_ok=True)
    
    with _image_download_lock:
        _image_download_status["active"] = True
        _image_download_status["total"] = len(products)
        _image_download_status["current"] = 0
        _image_download_status["errors"] = 0
        _image_download_status["last_error"] = None
        
    async with httpx.AsyncClient(timeout=10) as client:
        for p in products:
            # Control de cancelación
            with _image_download_lock:
                if not _image_download_status["active"]:
                    break
                
            if not p.image_url:
                with _image_download_lock:
                    _image_download_status["current"] += 1
                continue
                
            file_path = os.path.join(image_cache_dir, f"{p.id}.webp")
            
            # Si ya está en disco y pesa algo, saltar
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with _image_download_lock:
                    _image_download_status["current"] += 1
                continue
                
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = await client.get(p.image_url, headers=headers)
                if response.status_code == 200:
                    from PIL import Image
                    import io
                    # Convert to WebP
                    img = Image.open(io.BytesIO(response.content))
                    # Handle transparency
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.save(file_path, "WEBP", quality=85)
                else:
                    raise Exception(f"HTTP Status {response.status_code}")
            except Exception as e:
                logger.warning(f"Error descargando imagen para producto {p.id} ({p.name}): {e}")
                with _image_download_lock:
                    _image_download_status["errors"] += 1
                    _image_download_status["last_error"] = str(e)
            finally:
                with _image_download_lock:
                    _image_download_status["current"] += 1
                    
    with _image_download_lock:
        _image_download_status["active"] = False
        logger.info("Background product image cache download finished.")


@router.get("/api/vault/generate")
async def api_generate_vault(user_id: int = 2):
    from src.application.services.vault_service import VaultService

    vault_service = VaultService()
    with SessionCloud() as db:
        try:
            vault_path = vault_service.generate_user_vault(user_id, db)
            return FileResponse(
                path=vault_path,
                filename=os.path.basename(vault_path),
                media_type="application/x-sqlite3",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/vault/stage")
async def api_stage_vault(user_id: int = 2, file_path: str = None):
    from src.application.services.vault_service import VaultService
    from src.domain.models import StagedImportModel

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Archivo no encontrado.")

    vault_service = VaultService()
    try:
        vault_service.stage_vault_import(user_id, file_path)
        with SessionCloud() as db:
            stage = StagedImportModel(
                user_id=user_id,
                import_type="VAULT",
                status="PENDING",
                data_payload=json.dumps({"source_file": file_path}),
                impact_summary="Importación de Bóveda SQLite detectada. Pendiente de auditoría del Arquitecto.",
            )
            db.add(stage)
            db.commit()
        return {"status": "success", "message": "Bóveda en Cuarentena. Un administrador debe validar la inyección."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Shield Protocol Bloqueó Infección: {str(e)}")


@router.post("/api/excel/sync")
async def api_sync_excel(user_id: int = 2):
    from src.application.services.excel_manager import ExcelManager
    from src.domain.models import UserModel
    from src.infrastructure.database_cloud import SessionCloud
    import shutil

    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        is_admin = user.role == 'admin' or user.username == 'David'
        username = user.username

    project_root = Path(__file__).resolve().parents[4]
    
    if is_admin:
        excel_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
    else:
        # User-specific excel file path
        excel_path = project_root / "data" / "MOTU" / f"lista_MOTU_{username}.xlsx"
        # Copy template if it doesn't exist yet
        if not excel_path.exists():
            template_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
            if not template_path.exists():
                raise HTTPException(status_code=500, detail="Plantilla de Excel lista_MOTU.xlsx no encontrada.")
            # Ensure directories exist
            excel_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_path, excel_path)

    manager = ExcelManager(str(excel_path))
    success = manager.sync_acquisitions_from_db(user_id)

    if success:
        return {"status": "success", "message": f"Excel Bridge de {username if not is_admin else 'David'} sincronizado con éxito."}
    raise HTTPException(
        status_code=500,
        detail="Fallo en la sincronización del Excel. Verifique la ruta y el formato.",
    )


@router.post("/api/vault/download-images")
async def trigger_image_download(background_tasks: BackgroundTasks):
    global _image_download_status
    with _image_download_lock:
        if _image_download_status["active"]:
            return {"status": "running", "message": "Descarga de imágenes ya en curso."}
            
    background_tasks.add_task(download_all_images_task)
    return {"status": "started", "message": "Descarga de imágenes iniciada en segundo plano."}


@router.get("/api/vault/download-images/status")
async def get_image_download_status():
    global _image_download_status
    with _image_download_lock:
        return _image_download_status


@router.post("/api/vault/download-images/cancel")
async def cancel_image_download():
    global _image_download_status
    with _image_download_lock:
        if _image_download_status["active"]:
            _image_download_status["active"] = False
            return {"status": "cancelled", "message": "Descarga cancelada."}
        return {"status": "inactive", "message": "No hay descargas activas."}
