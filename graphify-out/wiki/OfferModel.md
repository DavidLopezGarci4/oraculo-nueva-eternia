# OfferModel

> God node · 136 connections · `src/domain/models.py`

**Community:** [Routers: OfferModel, json](Routers-_OfferModel,_json.md)

## Connections by Relation

### calls
- test_atomic_undo() `EXTRACTED`
- test_budget_optimizer_greedy_selection() `EXTRACTED`
- .test_dynamic_periods_and_monthly_compacted_reuse_without_synthetic_sine() `EXTRACTED`
- test_budget_optimizer_bundles_same_store_shipping() `EXTRACTED`
- test_retail_scarcity_alerts_detects_single_retail_store() `EXTRACTED`
- test_products_offers_analytics_history_vintage_match_schema() `EXTRACTED`
- .test_compactation_6_months_and_active_links_preservation() `EXTRACTED`
- test_p2p_liquidity_pulse_classifies_velocity_and_stagnant_bargains() `EXTRACTED`
- test_get_products_pagination_no_truncation_with_multiple_p2p_offers() `EXTRACTED`

### contains
- models.py `EXTRACTED`

### imports
- purgatory.py `EXTRACTED`
- products.py `EXTRACTED`
- scrapers.py `EXTRACTED`
- pipeline.py `EXTRACTED`
- admin.py `EXTRACTED`
- main.py `EXTRACTED`
- dashboard.py `EXTRACTED`
- users.py `EXTRACTED`
- routers/collection.py `EXTRACTED`
- system.py `EXTRACTED`
- nexus_service.py `EXTRACTED`
- telegram_listener.py `EXTRACTED`
- test_api_response_schemas.py `EXTRACTED`
- nexus_vintage_service.py `EXTRACTED`
- test_scraper_interface.py `EXTRACTED`
- restore_vault.py `EXTRACTED`
- migrate_purgatory_vintage.py `EXTRACTED`
- product.py `EXTRACTED`
- market_analytics_service.py `EXTRACTED`
- test_revert_logistics.py `EXTRACTED`
- *…and 38 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Base `EXTRACTED`

### references
- .add_offer() `EXTRACTED`
- .get_offer_by_url() `EXTRACTED`

### uses
- [ScrapingPipeline](ScrapingPipeline.md) `INFERRED`
- TelegramListener `INFERRED`
- ProductRepository `INFERRED`
- MarketAnalyticsService `INFERRED`
- NexusService `INFERRED`
- OracleAssistantAI `INFERRED`
- ValuationService `INFERRED`
- run_match_bulk_task() `INFERRED`
- BudgetOptimizerService `INFERRED`
- MaintenanceService `INFERRED`
- NexusVintageService `INFERRED`
- MarketIntelligenceService `INFERRED`
- clean_purgatory_globally() `INFERRED`
- revert_action() `INFERRED`
- import_wallapop_products() `INFERRED`
- restore_from_vault() `INFERRED`
- relink_offer() `INFERRED`
- migrate_data() `INFERRED`
- _fetch_and_cache_product_image() `INFERRED`
- delete_product() `INFERRED`
- *…and 45 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*