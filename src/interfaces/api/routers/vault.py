import json
import os
import io
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.core.config import settings
from src.interfaces.api.deps import require_admin
from src.interfaces.api.schemas import StatusMessageOutput

router = APIRouter(tags=["vault"], dependencies=[Depends(require_admin)])

# Fase AAA-1.3: /api/vault/stage aceptaba un `file_path` arbitrario del cliente
# y lo abría directamente (path traversal / lectura de cualquier fichero legible
# por el proceso). Ahora solo admite un NOMBRE de fichero, resuelto siempre
# dentro de este directorio de cuarentena — nunca fuera de él.
_VAULT_STAGING_DIR = Path("backups/vaults").resolve()
_VAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_staged_file(filename: str) -> Path:
    """Resuelve `filename` dentro de _VAULT_STAGING_DIR, rechazando cualquier intento de escapar del directorio."""
    if not filename or "/" in filename or "\\" in filename or filename in (".", ".."):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")
    candidate = (_VAULT_STAGING_DIR / filename).resolve()
    if _VAULT_STAGING_DIR not in candidate.parents and candidate != _VAULT_STAGING_DIR:
        raise HTTPException(status_code=400, detail="Ruta fuera del directorio de cuarentena permitido.")
    if not candidate.exists():
        raise HTTPException(status_code=400, detail="Archivo no encontrado en cuarentena.")
    return candidate


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


@router.post("/api/vault/stage", response_model=StatusMessageOutput)
async def api_stage_vault(user_id: int = 2, filename: str = None):
    from src.application.services.vault_service import VaultService
    from src.domain.models import StagedImportModel

    staged_path = _resolve_staged_file(filename)

    vault_service = VaultService()
    try:
        vault_service.stage_vault_import(user_id, str(staged_path))
        with SessionCloud() as db:
            stage = StagedImportModel(
                user_id=user_id,
                import_type="VAULT",
                status="PENDING",
                data_payload=json.dumps({"source_file": str(staged_path)}),
                impact_summary="Importación de Bóveda SQLite detectada. Pendiente de auditoría del Arquitecto.",
            )
            db.add(stage)
            db.commit()
        return {"status": "success", "message": "Bóveda en Cuarentena. Un administrador debe validar la inyección."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Shield Protocol Bloqueó Infección: {str(e)}")


@router.post("/api/excel/sync", response_model=StatusMessageOutput)
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


@router.get("/api/vault/download-images/zip")
async def download_images_zip():
    cache_dir = Path(settings.IMAGE_CACHE_DIR)
    if not cache_dir.exists():
        raise HTTPException(status_code=404, detail="El directorio de caché de imágenes no existe.")
    
    image_files = []
    for ext in ("*.webp", "*.jpg", "*.jpeg", "*.png"):
        image_files.extend(cache_dir.glob(ext))
        
    if not image_files:
        raise HTTPException(status_code=404, detail="No hay imágenes en el caché local para descargar.")
        
    from src.domain.models import ProductModel
    product_map = {}
    with SessionCloud() as db:
        products = db.query(ProductModel.id, ProductModel.name, ProductModel.figure_id).all()
        for p_id, name, figure_id in products:
            product_map[p_id] = (name, figure_id)
            
    import re
    def slugify(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for img_path in image_files:
            try:
                p_id = int(img_path.stem)
            except ValueError:
                zip_file.write(img_path, img_path.name)
                continue
                
            if p_id in product_map:
                name, fig_id = product_map[p_id]
                slug_name = slugify(name)
                if not slug_name:
                    slug_name = "product"
                slug_id = fig_id if fig_id else str(p_id)
                new_name = f"{slug_name}-{slug_id}{img_path.suffix}"
            else:
                new_name = img_path.name
                
            zip_file.write(img_path, new_name)
            
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=motu_images.zip"}
    )

