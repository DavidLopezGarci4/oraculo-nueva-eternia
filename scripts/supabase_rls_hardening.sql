-- ==========================================
-- 🛡️ SUPABASE SECURITY HARDENING (RLS)
-- Proyecto: Oráculo de Nueva Eternia
-- Propósito: Protege las tablas contra accesos no autorizados vía API pública.
-- ==========================================

-- 1. Habilitar RLS en todas las tablas identificadas
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collection_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pending_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.offer_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scraper_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blackcluded_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scraper_execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kaizen_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_aliases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.logistic_rules ENABLE ROW LEVEL SECURITY;

-- 2. Crear Políticas de Denegación por Defecto (Opcional pero recomendado)
-- Por defecto, al activar RLS, Supabase deniega todo. 
-- No creamos políticas SELECT/INSERT/UPDATE para 'anon' para que la API pública quede cerrada.
-- Nuestra conexión directa (FastAPI) usa credenciales que saltan el RLS por configuración de conexión.

-- 3. Verificación
-- Una vez ejecutado, los errores en "Security Advisor" deberían desaparecer.
-- Las tablas solo serán accesibles mediante el Service Role Key o conexión Postgres directa.

RAISE NOTICE 'RLS habilitado con éxito en 15 tablas.';
