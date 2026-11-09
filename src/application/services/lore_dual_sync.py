"""
Coordinador de persistencia dual del Grimorio MOTU (`SessionCloud` -> SQLite local).

Regla de arquitectura: todos los escritores de aplicacion usan `SessionCloud` (Supabase/PostgreSQL)
como fuente primaria. Este modulo replica de forma secuencial y *best-effort* hacia SQLite local
(`oraculo.db`) sin abortar nunca la operacion primaria. Es unidireccional: no existe replica
inversa `Local -> Cloud`.

Se inhibe automaticamente cuando:
  - la sesion primaria y la local apuntan al mismo motor, o
  - la sesion primaria es una base en memoria (tests), evitando contaminar `oraculo.db`.
"""
from typing import Iterable, Optional

from loguru import logger
from sqlalchemy.orm import Session

from src.domain.models import CharacterLoreModel, ProductLoreModel, ProductModel


def _row_to_dict(model, row) -> dict:
    return {c.name: getattr(row, c.name) for c in model.__table__.columns}


class LoreDualSync:
    @staticmethod
    def _open_secondary(primary_db: Session) -> Optional[Session]:
        """Devuelve una sesion SQLite local, o None si la replica debe omitirse."""
        try:
            from src.infrastructure.database import SessionLocal, engine as local_engine

            primary_url = primary_db.get_bind().url
            if "memory" in str(primary_url).lower():
                return None
            if primary_url == local_engine.url:
                return None
            return SessionLocal()
        except Exception as e:
            logger.warning(f"Lore dual sync :: sesion local no disponible, replica omitida: {e}")
            return None

    @classmethod
    def replicate_characters(cls, primary_db: Session, slugs: Iterable[str]) -> None:
        slugs = [s for s in set(slugs) if s]
        if not slugs:
            return
        local = cls._open_secondary(primary_db)
        if local is None:
            return
        try:
            rows = primary_db.query(CharacterLoreModel).filter(CharacterLoreModel.slug.in_(slugs)).all()
            for row in rows:
                local.merge(CharacterLoreModel(**_row_to_dict(CharacterLoreModel, row)))
            local.commit()
        except Exception as e:
            local.rollback()
            logger.warning(f"Lore dual sync :: character_lore no replicado: {e}")
        finally:
            local.close()

    @classmethod
    def replicate_product_lore(cls, primary_db: Session, product_ids: Iterable[int]) -> None:
        ids = [i for i in set(product_ids) if i is not None]
        if not ids:
            return
        local = cls._open_secondary(primary_db)
        if local is None:
            return
        try:
            local_ids = {r[0] for r in local.query(ProductModel.id).filter(ProductModel.id.in_(ids)).all()}
            rows = primary_db.query(ProductLoreModel).filter(ProductLoreModel.product_id.in_(ids)).all()
            for row in rows:
                # Evita violar la FK local si el producto homologo no existe en SQLite.
                if row.product_id in local_ids:
                    local.merge(ProductLoreModel(**_row_to_dict(ProductLoreModel, row)))
            local.commit()
        except Exception as e:
            local.rollback()
            logger.warning(f"Lore dual sync :: product_lore no replicado: {e}")
        finally:
            local.close()

    @classmethod
    def replicate_character_slugs(cls, primary_db: Session, product_ids: Optional[Iterable[int]] = None) -> None:
        """Replica `products.character_slug` (solo ese campo) hacia SQLite local."""
        local = cls._open_secondary(primary_db)
        if local is None:
            return
        try:
            query = primary_db.query(ProductModel.id, ProductModel.character_slug).filter(
                ProductModel.character_slug.isnot(None)
            )
            if product_ids is not None:
                ids = list(set(product_ids))
                if not ids:
                    return
                query = query.filter(ProductModel.id.in_(ids))
            wanted = {pid: slug for pid, slug in query.all()}
            if not wanted:
                return
            for prod in local.query(ProductModel).filter(ProductModel.id.in_(list(wanted))).all():
                if prod.character_slug != wanted[prod.id]:
                    prod.character_slug = wanted[prod.id]
            local.commit()
        except Exception as e:
            local.rollback()
            logger.warning(f"Lore dual sync :: character_slug no replicado: {e}")
        finally:
            local.close()

    @classmethod
    def delete_product_lore(cls, primary_db: Session, product_id: int) -> None:
        local = cls._open_secondary(primary_db)
        if local is None:
            return
        try:
            local.query(ProductLoreModel).filter(ProductLoreModel.product_id == product_id).delete()
            local.commit()
        except Exception as e:
            local.rollback()
            logger.warning(f"Lore dual sync :: borrado de product_lore no replicado: {e}")
        finally:
            local.close()

    @classmethod
    def replicate_all(cls, primary_db: Session) -> None:
        """Replica completa tras un sembrado masivo (character_lore, product_lore y slugs)."""
        if cls._probe(primary_db) is False:
            return
        cls.replicate_characters(primary_db, [r[0] for r in primary_db.query(CharacterLoreModel.slug).all()])
        cls.replicate_product_lore(primary_db, [r[0] for r in primary_db.query(ProductLoreModel.product_id).all()])
        cls.replicate_character_slugs(primary_db)

    @classmethod
    def _probe(cls, primary_db: Session) -> bool:
        session = cls._open_secondary(primary_db)
        if session is None:
            return False
        session.close()
        return True
