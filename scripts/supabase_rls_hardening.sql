-- =============================================================================
-- 🛡️ SUPABASE ZERO-TRUST SECURITY HARDENING (RLS + REVOKE + EVENT TRIGGER)
-- Proyecto: Oráculo de Nueva Eternia
-- Propósito: Blindar el esquema `public` contra accesos no autorizados vía Data API
--            (PostgREST / GraphQL), incluyendo tablas futuras y `alembic_version`.
-- =============================================================================

-- 1. Revocar privilegios presentes y futuros en `public` para roles de API pública
REVOKE USAGE ON SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON ROUTINES FROM anon, authenticated;

-- 2. Activar RLS dinámicamente en todas las tablas propias de `public`
--    (Incluye `alembic_version` y excluye objetos pertenecientes a extensiones)
DO $$
DECLARE
    r RECORD;
    v_count INTEGER := 0;
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
        v_count := v_count + 1;
        RAISE NOTICE 'RLS activado en public.%', r.tablename;
    END LOOP;

    RAISE NOTICE 'Barrido RLS completado (% tablas actualizadas).', v_count;
END $$;

-- 3. Auto-blindaje atómico (0 ms de exposición) para cualquier tabla futura en `public`
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

REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon, authenticated;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_event_trigger WHERE evtname = 'ensure_rls_on_public') THEN
        CREATE EVENT TRIGGER ensure_rls_on_public
        ON ddl_command_end
        WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
        EXECUTE FUNCTION public.rls_auto_enable();
        RAISE NOTICE 'Event Trigger ensure_rls_on_public instalado correctamente.';
    END IF;
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE WARNING 'El rol actual no posee permisos para CREATE EVENT TRIGGER; RLS y REVOKE ya quedaron aplicados.';
END $$;

-- 4. Consulta de verificación (debe devolver 0 filas con rowsecurity = false)
SELECT c.relname AS tablename, c.relrowsecurity AS rowsecurity
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p')
  AND NOT EXISTS (
      SELECT 1 FROM pg_depend d
      WHERE d.objid = c.oid AND d.deptype = 'e'
  )
ORDER BY c.relrowsecurity ASC, c.relname ASC;
