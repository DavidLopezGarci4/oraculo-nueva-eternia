"""
Nexus Local Bridge (Fase 2 del plan docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md).

Cola de trabajos para resolver búsquedas de Wallapop desde una IP no vetada
(el PC del usuario) cuando el servidor (IP de datacenter) está bloqueado por
CloudFront incluso con la API v3 firmada (Fase 1.5).

Flujo:
  1. El panel de Configuración (o cualquier cliente) encola un trabajo:
     POST /api/wallapop/jobs {"query": "auto"}
  2. Un worker local (scripts/nexus_local_worker.py) hace polling:
     GET /api/wallapop/jobs/pending  -> reclama el job más antiguo (pending -> running)
  3. El worker ejecuta WallapopManualScraper().search(query) EN SU PROPIA MÁQUINA
     (IP residencial), y envía los resultados:
     POST /api/wallapop/jobs/{id}/results {"offers": [...], "blocked": false}
  4. El servidor persiste las ofertas en el Purgatorio vía ScrapingPipeline.update_database
     y marca el job como done/error.
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc

from src.domain.models import WallapopJobModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import (
    WallapopJobCreateRequest,
    WallapopJobResultsRequest,
    WallapopJobCreatedOutput,
    WallapopJobOutput,
    WallapopJobResultsOutput,
)

router = APIRouter(prefix="/api/wallapop/jobs", tags=["wallapop-nexus-bridge"])


@router.post("", response_model=WallapopJobCreatedOutput, dependencies=[Depends(verify_api_key)])
async def create_wallapop_job(request: WallapopJobCreateRequest):
    """Encola un nuevo trabajo de búsqueda para el Nexus Local Bridge (Admin Only)."""
    with SessionCloud() as db:
        job = WallapopJobModel(query=request.query or "auto", status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {
            "status": "success",
            "job_id": job.id,
            "message": f"Trabajo '{job.query}' encolado. Ejecuta el Nexus Local Bridge en tu PC para procesarlo.",
        }


@router.get("/pending", response_model=Optional[WallapopJobOutput], dependencies=[Depends(verify_api_key)])
async def claim_pending_wallapop_job(worker_id: str | None = None):
    """
    Reclama (y marca como 'running') el trabajo pendiente más antiguo, para que
    un worker local lo procese. Devuelve null si no hay trabajos pendientes.

    Nota: pensado para un único worker Nexus Bridge activo a la vez (uso local
    del usuario); no implementa locking distribuido para múltiples workers.
    """
    with SessionCloud() as db:
        job = (
            db.query(WallapopJobModel)
            .filter(WallapopJobModel.status == "pending")
            .order_by(WallapopJobModel.created_at.asc())
            .first()
        )
        if not job:
            return None

        job.status = "running"
        job.claimed_at = datetime.now(timezone.utc)
        if worker_id:
            job.worker_id = worker_id
        db.commit()
        db.refresh(job)
        return job


@router.post("/{job_id}/results", response_model=WallapopJobResultsOutput, dependencies=[Depends(verify_api_key)])
async def submit_wallapop_job_results(job_id: int, request: WallapopJobResultsRequest):
    """Recibe los resultados de un worker local y los enruta al Purgatorio (Admin Only)."""
    with SessionCloud() as db:
        job = db.query(WallapopJobModel).filter(WallapopJobModel.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Trabajo #{job_id} no encontrado.")

        if request.worker_id:
            job.worker_id = request.worker_id

        if request.error_message:
            job.status = "error"
            job.error_message = request.error_message
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            return {"status": "success", "job_status": job.status, "new_items": 0}

        offers_payload = [
            {
                "product_name": o.product_name,
                "price": o.price,
                "currency": o.currency,
                "url": o.url,
                "shop_name": "WallapopManual",
                "image_url": o.image_url,
                "source_type": o.source_type,
                "sale_type": o.sale_type,
            }
            for o in request.offers
        ]

        new_items = 0
        if offers_payload:
            from src.infrastructure.scrapers.pipeline import ScrapingPipeline

            pipeline = ScrapingPipeline([])
            new_items = pipeline.update_database(offers_payload, shop_names=["WallapopManual"]) or 0

        job.status = "error" if (request.blocked and not offers_payload) else "done"
        if job.status == "error" and not job.error_message:
            job.error_message = "Bloqueado por WAF desde la IP del worker local."
        job.result_count = len(offers_payload)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        return {"status": "success", "job_status": job.status, "new_items": new_items}


@router.get("", response_model=List[WallapopJobOutput], dependencies=[Depends(verify_api_key)])
async def list_wallapop_jobs(limit: int = 30):
    """Lista los trabajos más recientes del Nexus Local Bridge, para la UI de Configuración."""
    with SessionCloud() as db:
        return (
            db.query(WallapopJobModel)
            .order_by(desc(WallapopJobModel.created_at))
            .limit(limit)
            .all()
        )
