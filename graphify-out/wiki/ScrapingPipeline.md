# ScrapingPipeline

> God node · 56 connections · `src/infrastructure/scrapers/pipeline.py`

**Community:** [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md)

## Connections by Relation

### calls
- run_daily_scan() `EXTRACTED`
- run_scraper_task() `EXTRACTED`
- .run_hunt() `EXTRACTED`
- run_scraper() `EXTRACTED`
- main() `EXTRACTED`
- execute_scraper() `EXTRACTED`
- test_sentinel() `EXTRACTED`
- main() `EXTRACTED`
- ingest_data() `EXTRACTED`
- .test_standardization() `EXTRACTED`
- test_pipeline() `EXTRACTED`
- main() `EXTRACTED`
- test_sync_availability_handles_timezone_aware_last_seen() `EXTRACTED`
- test_sync_availability_preserves_vintage_offers() `EXTRACTED`

### contains
- pipeline.py `EXTRACTED`

### imports
- daily_scan.py `EXTRACTED`
- scrapers.py `EXTRACTED`
- vinted_hunter_service.py `EXTRACTED`
- test_scraper_interface.py `EXTRACTED`
- wallapop_jobs.py `EXTRACTED`
- run_single.py `EXTRACTED`
- scrape_multi_via_cdp.py `EXTRACTED`
- wallapop_manual_importer.py `EXTRACTED`
- run_single_incursion.py `EXTRACTED`
- verify_sentinel.py `EXTRACTED`
- match_analysis.py `EXTRACTED`
- scrape_wallapop_via_cdp.py `EXTRACTED`
- repro_pipeline_v2.py `EXTRACTED`
- scrape_via_cdp.py `EXTRACTED`
- ingest_json.py `EXTRACTED`
- test_pipeline.py `EXTRACTED`
- repro_pipeline.py `EXTRACTED`

### method
- .update_database() `EXTRACTED`
- .run_product_search() `EXTRACTED`
- .sync_availability() `EXTRACTED`
- .__init__() `EXTRACTED`
- ._log() `EXTRACTED`
- .clean_product_name() `EXTRACTED`

### uses
- [ScrapedOffer](ScrapedOffer.md) `INFERRED`
- [OfferModel](OfferModel.md) `INFERRED`
- [PendingMatchModel](PendingMatchModel.md) `INFERRED`
- [BaseScraper](BaseScraper.md) `INFERRED`
- [LogisticsService](LogisticsService.md) `INFERRED`
- OfferHistoryModel `INFERRED`
- ProductRepository `INFERRED`
- BlackcludedItemModel `INFERRED`
- LogisticRuleModel `INFERRED`
- DealScorer `INFERRED`
- VintedHunterService `INFERRED`
- VintageMiscellaneousModel `INFERRED`
- SmartMatcher `INFERRED`
- SentinelService `INFERRED`
- BackupManager `INFERRED`
- AuditorService `INFERRED`
- submit_wallapop_job_results() `INFERRED`
- TestPipelineHardening `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*