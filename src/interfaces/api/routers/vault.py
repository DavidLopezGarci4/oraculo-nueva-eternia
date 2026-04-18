import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud

router = APIRouter(tags=["vault"])


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

    project_root = Path(__file__).resolve().parents[4]
    david_excel = str(project_root / "data" / "MOTU" / "lista_MOTU.xlsx")

    manager = ExcelManager(david_excel)
    success = manager.sync_acquisitions_from_db(user_id)

    if success:
        return {"status": "success", "message": "Excel Bridge sincronizado con éxito."}
    raise HTTPException(
        status_code=500,
        detail="Fallo en la sincronización del Excel. Verifique la ruta y el formato.",
    )
