"""enforce_supabase_rls_and_event_trigger

Revision ID: 9b4c7d8e1f2a
Revises: 8f1e2d3c4b5a
Create Date: 2026-11-03 21:00:00.000000

Blindaje Zero-Trust definitivo contra `rls_disabled_in_public` en Supabase:
1. Revoca privilegios presentes y futuros (`DEFAULT PRIVILEGES`) para `anon` y `authenticated` en `public`.
2. Habilita RLS dinámicamente en todas las tablas propias de `public` (incluida `alembic_version`,
   excluyendo objetos dependientes de extensiones).
3. Instala el Event Trigger `ensure_rls_on_public` (`ON ddl_command_end`) para auto-blindar en 0 ms
   cualquier tabla futura creada en `public`.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9b4c7d8e1f2a"
down_revision: Union[str, Sequence[str], None] = "8f1e2d3c4b5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enforce RLS, privilege revocation, and automatic DDL event trigger on PostgreSQL."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # 1. Revocar permisos presentes y futuros en public para anon y authenticated
    op.execute("REVOKE USAGE ON SCHEMA public FROM anon, authenticated;")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;")
    op.execute("REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;")
    op.execute("REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated;")

    op.execute(
        "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
        "REVOKE ALL ON TABLES FROM anon, authenticated;"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
        "REVOKE ALL ON SEQUENCES FROM anon, authenticated;"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
        "REVOKE ALL ON ROUTINES FROM anon, authenticated;"
    )

    # 2. Barrido dinámico de RLS en todas las tablas propias de public (incluye alembic_version)
    op.execute(
        """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN
                SELECT c.relname AS tablename
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public'
                  AND c.relkind IN ('r', 'p')
                  AND c.relrowsecurity = false
                  AND pg_get_userbyid(c.relowner) = current_user
                  AND NOT EXISTS (
                      SELECT 1 FROM pg_depend d
                      WHERE d.objid = c.oid AND d.deptype = 'e'
                  )
            LOOP
                EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', r.tablename);
            END LOOP;
        END $$;
        """
    )

    # 3. Función y Event Trigger para blindaje automático de futuras tablas
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.rls_auto_enable()
        RETURNS event_trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $$
        DECLARE
            cmd RECORD;
        BEGIN
            FOR cmd IN SELECT * FROM pg_event_trigger_ddl_commands()
            LOOP
                IF cmd.object_type IN ('table', 'partitioned table') AND cmd.schema_name = 'public' THEN
                    EXECUTE format('ALTER TABLE %s ENABLE ROW LEVEL SECURITY;', cmd.object_identity);
                    EXECUTE format('REVOKE ALL ON TABLE %s FROM anon, authenticated;', cmd.object_identity);
                END IF;
            END LOOP;
        END;
        $$;
        """
    )
    op.execute("REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon, authenticated;")

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_event_trigger WHERE evtname = 'ensure_rls_on_public') THEN
                CREATE EVENT TRIGGER ensure_rls_on_public
                ON ddl_command_end
                WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
                EXECUTE FUNCTION public.rls_auto_enable();
            END IF;
        EXCEPTION
            WHEN insufficient_privilege THEN
                RAISE WARNING 'Rol actual sin permiso CREATE EVENT TRIGGER; RLS y REVOKE ya quedaron aplicados.';
        END $$;
        """
    )


def downgrade() -> None:
    """
    Por invariante de seguridad, un downgrade NUNCA desactiva RLS ni reabre privilegios públicos.
    Únicamente retira el Event Trigger si se revierte la revisión.
    """
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_event_trigger WHERE evtname = 'ensure_rls_on_public') THEN
                DROP EVENT TRIGGER ensure_rls_on_public;
            END IF;
        EXCEPTION
            WHEN insufficient_privilege THEN
                NULL;
        END $$;
        """
    )
