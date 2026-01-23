-- Migration: spider_name -> scraper_name
-- Target: PostgreSQL (Supabase / Docker)

-- 1. Scraper Status Table
ALTER TABLE scraper_status RENAME COLUMN spider_name TO scraper_name;

-- 2. Scraper Execution Logs Table
ALTER TABLE scraper_execution_logs RENAME COLUMN spider_name TO scraper_name;

-- 3. Kaizen Insights Table
ALTER TABLE kaizen_insights RENAME COLUMN spider_name TO scraper_name;

-- Verify (optional)
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'scraper_status';
