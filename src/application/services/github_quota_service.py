import math
import io
import csv
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import httpx
from loguru import logger

from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperExecutionLogModel

class GitHubQuotaService:
    """
    Servicio de Telemetría FinOps y Sincronización en Vivo con GitHub Actions.
    Calcula minutos facturables reales, minutos restantes sobre la cuota mensual de 2.000 min,
    cuenta atrás de reposición del ciclo y exportación de logs a CSV.
    """

    TOTAL_MONTHLY_QUOTA_MINUTES = 2000

    @classmethod
    async def get_quota_status(cls) -> Dict[str, Any]:
        """Obtiene el estado de la cuota mensual combinando GitHub API en vivo y base de datos local."""
        now = datetime.now(timezone.utc)
        
        # 1. Calcular rango del mes actual (del día 1 a las 00:00 UTC al fin de mes)
        month_start = datetime(now.year, now.month, 1, 0, 0, tzinfo=timezone.utc)
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1, 0, 0, tzinfo=timezone.utc)
            
        days_until_reset = max(1, (next_month_start - now).days)
        total_days_in_month = (next_month_start - month_start).days
        days_elapsed = max(1, (now - month_start).days)

        # 2. Intentar consultar ejecuciones en vivo desde la API de GitHub Actions
        gh_runs_data = await cls._fetch_github_runs_this_month(month_start)
        
        if gh_runs_data is not None:
            # Sincronización en vivo con GitHub
            billed_minutes = gh_runs_data["total_billed_minutes"]
            total_runs = gh_runs_data["total_runs"]
            breakdown = gh_runs_data["breakdown"]
            source = "github_api_live"
        else:
            # Fallback a registros de la base de datos local
            db_data = cls._fetch_db_logs_this_month(month_start)
            billed_minutes = db_data["total_billed_minutes"]
            total_runs = db_data["total_runs"]
            breakdown = db_data["breakdown"]
            source = "database_fallback"

        # 3. Métricas de cuota y porcentajes
        remaining_minutes = max(0, cls.TOTAL_MONTHLY_QUOTA_MINUTES - billed_minutes)
        percentage_used = round((billed_minutes / cls.TOTAL_MONTHLY_QUOTA_MINUTES) * 100, 1)

        # 4. Proyección de fin de mes y recomendación de cadencia
        daily_average_minutes = round(billed_minutes / days_elapsed, 1)
        projected_month_end_minutes = int(daily_average_minutes * total_days_in_month)
        
        if projected_month_end_minutes <= 1400:
            cadence_status = "optimal"
            cadence_message = (
                f"🟢 Cadencia actual (50-75 min) óptima: proyección de {projected_month_end_minutes} min/mes "
                f"({round((projected_month_end_minutes / cls.TOTAL_MONTHLY_QUOTA_MINUTES) * 100, 1)}% del cupo). "
                f"Margen seguro: {cls.TOTAL_MONTHLY_QUOTA_MINUTES - projected_month_end_minutes} min libres."
            )
        elif projected_month_end_minutes <= 1850:
            cadence_status = "warning"
            cadence_message = (
                f"🟡 Consumo moderado: proyección de {projected_month_end_minutes} min/mes. "
                f"Se recomienda mantener la cadencia actual y no reducir los intervalos a menos de 50 min."
            )
        else:
            cadence_status = "critical"
            cadence_message = (
                f"🔴 Alerta de Cuota: proyección de {projected_month_end_minutes} min/mes "
                f"supera el límite gratuito. Se aconseja espaciar los centinelas a 90-120 min."
            )

        return {
            "source": source,
            "total_quota_minutes": cls.TOTAL_MONTHLY_QUOTA_MINUTES,
            "used_minutes": billed_minutes,
            "remaining_minutes": remaining_minutes,
            "percentage_used": percentage_used,
            "reset_date": next_month_start.strftime("%d/%m/%Y 00:00 UTC"),
            "days_until_reset": days_until_reset,
            "total_runs_this_month": total_runs,
            "daily_average_minutes": daily_average_minutes,
            "projected_month_end_minutes": projected_month_end_minutes,
            "cadence_status": cadence_status,
            "cadence_recommendation": cadence_message,
            "breakdown": breakdown
        }

    @classmethod
    async def _fetch_github_runs_this_month(cls, month_start: datetime) -> Optional[Dict[str, Any]]:
        """Consulta la API de GitHub Actions para el repositorio y mes actual."""
        if not settings.GITHUB_TOKEN or not settings.GITHUB_REPOSITORY:
            return None

        url = f"https://api.github.com/repos/{settings.GITHUB_REPOSITORY}/actions/runs"
        headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        params = {
            "created": f">={month_start.strftime('%Y-%m-%d')}",
            "per_page": 100
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    logger.warning(f"GitHub API returned {resp.status_code}: {resp.text}")
                    return None

                data = resp.json()
                runs = data.get("workflow_runs", [])
                
                total_billed = 0
                breakdown = {
                    "daily_scan": {"minutes": 0, "runs": 0},
                    "vinted_sentinel": {"minutes": 0, "runs": 0},
                    "ci_tests": {"minutes": 0, "runs": 0},
                    "others": {"minutes": 0, "runs": 0}
                }

                for r in runs:
                    started_str = r.get("run_started_at") or r.get("created_at")
                    updated_str = r.get("updated_at")
                    
                    # Calcular duración en segundos
                    duration_s = 60 # Default fallback
                    if started_str and updated_str:
                        try:
                            st = datetime.fromisoformat(started_str.replace("Z", "+00:00"))
                            ut = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                            duration_s = max(1, (ut - st).total_seconds())
                        except Exception:
                            duration_s = 60

                    # Facturación GitHub: Redondeo hacia arriba al minuto completo
                    billed_m = max(1, math.ceil(duration_s / 60))
                    total_billed += billed_m

                    name = (r.get("name") or "").lower()
                    if "scraper" in name or "daily" in name:
                        breakdown["daily_scan"]["minutes"] += billed_m
                        breakdown["daily_scan"]["runs"] += 1
                    elif "vinted" in name or "hunter" in name or "caza" in name:
                        breakdown["vinted_sentinel"]["minutes"] += billed_m
                        breakdown["vinted_sentinel"]["runs"] += 1
                    elif "ci" in name or "test" in name:
                        breakdown["ci_tests"]["minutes"] += billed_m
                        breakdown["ci_tests"]["runs"] += 1
                    else:
                        breakdown["others"]["minutes"] += billed_m
                        breakdown["others"]["runs"] += 1

                return {
                    "total_billed_minutes": total_billed,
                    "total_runs": len(runs),
                    "breakdown": breakdown
                }
        except Exception as ex:
            logger.error(f"Error fetching GitHub runs: {ex}")
            return None

    @classmethod
    def _fetch_db_logs_this_month(cls, month_start: datetime) -> Dict[str, Any]:
        """Consulta los registros de ScraperExecutionLogModel en base de datos como fallback."""
        with SessionCloud() as db:
            logs = db.query(ScraperExecutionLogModel).filter(
                ScraperExecutionLogModel.start_time >= month_start.replace(tzinfo=None)
            ).all()

            total_billed = 0
            breakdown = {
                "daily_scan": {"minutes": 0, "runs": 0},
                "vinted_sentinel": {"minutes": 0, "runs": 0},
                "ci_tests": {"minutes": 0, "runs": 0},
                "others": {"minutes": 0, "runs": 0}
            }

            for l in logs:
                if l.end_time and l.start_time:
                    dur_s = max(1, (l.end_time - l.start_time).total_seconds())
                else:
                    dur_s = 60
                
                billed_m = max(1, math.ceil(dur_s / 60))
                total_billed += billed_m

                name = (l.spider_name or "").lower()
                if "daily" in name or "scrapers" in name:
                    breakdown["daily_scan"]["minutes"] += billed_m
                    breakdown["daily_scan"]["runs"] += 1
                elif "vinted" in name or "hunter" in name or "sentinel" in name:
                    breakdown["vinted_sentinel"]["minutes"] += billed_m
                    breakdown["vinted_sentinel"]["runs"] += 1
                elif "ci" in name:
                    breakdown["ci_tests"]["minutes"] += billed_m
                    breakdown["ci_tests"]["runs"] += 1
                else:
                    breakdown["others"]["minutes"] += billed_m
                    breakdown["others"]["runs"] += 1

            return {
                "total_billed_minutes": total_billed,
                "total_runs": len(logs),
                "breakdown": breakdown
            }

    @classmethod
    def generate_logs_csv(cls, db_session=None) -> str:
        """Genera el contenido en formato CSV de todo el historial de ejecuciones."""
        if db_session is not None:
            return cls._render_csv(db_session)
        with SessionCloud() as db:
            return cls._render_csv(db)

    @classmethod
    def _render_csv(cls, db) -> str:
        logs = db.query(ScraperExecutionLogModel).order_by(
            ScraperExecutionLogModel.start_time.desc()
        ).limit(500).all()

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        
        # Cabeceras
        writer.writerow([
            "ID",
            "Proceso / Spider",
            "Estado",
            "Disparador",
            "Fecha Inicio (UTC)",
            "Fecha Fin (UTC)",
            "Duracion (Segundos)",
            "Minutos Facturables GitHub",
            "Ofertas Procesadas",
            "Nuevas / Gangas",
            "Errores",
            "Mensaje de Error"
        ])

        for l in logs:
            dur_s = int((l.end_time - l.start_time).total_seconds()) if l.end_time and l.start_time else 0
            billable_m = max(1, math.ceil(dur_s / 60)) if dur_s > 0 else 0
            
            writer.writerow([
                l.id,
                l.spider_name or "Desconocido",
                l.status or "unspecified",
                l.trigger_type or "manual",
                l.start_time.strftime("%Y-%m-%d %H:%M:%S") if l.start_time else "",
                l.end_time.strftime("%Y-%m-%d %H:%M:%S") if l.end_time else "",
                dur_s,
                billable_m,
                l.items_found or 0,
                l.new_items or 0,
                l.errors or 0,
                (l.error_message or "").replace(";", " ")
            ])

        return output.getvalue()
