# ProductModel

> God node · 205 connections · `src/domain/models.py`

**Community:** [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md)

## Connections by Relation

### calls
- migrate_excel_to_db() `EXTRACTED`
- migrate_existing_vintage() `EXTRACTED`
- run_match_vintage_task() `EXTRACTED`
- restore_from_vault() `EXTRACTED`
- migrate_excel_to_db() `EXTRACTED`
- test_sentinel() `EXTRACTED`
- test_budget_optimizer_greedy_selection() `EXTRACTED`
- _make_test_session() `EXTRACTED`
- .test_dynamic_periods_and_monthly_compacted_reuse_without_synthetic_sine() `EXTRACTED`
- test_budget_optimizer_bundles_same_store_shipping() `EXTRACTED`
- test_retail_scarcity_alerts_detects_single_retail_store() `EXTRACTED`
- cloud_seed() `EXTRACTED`
- verify_deal_scorer() `EXTRACTED`
- test_returns_none_when_product_has_no_image_url() `EXTRACTED`
- test_api_purgatory_bulk_match() `EXTRACTED`
- test_products_offers_analytics_history_vintage_match_schema() `EXTRACTED`
- .test_compactation_6_months_and_active_links_preservation() `EXTRACTED`
- test_delta_updates_catalog() `EXTRACTED`
- test_market_index_calculation() `EXTRACTED`
- test_p2p_liquidity_pulse_classifies_velocity_and_stagnant_bargains() `EXTRACTED`
- *…and 6 more `calls` connection(s) not listed (lowest-degree first to go)*

### contains
- models.py `EXTRACTED`

### imports
- daily_scan.py `EXTRACTED`
- purgatory.py `EXTRACTED`
- products.py `EXTRACTED`
- pipeline.py `EXTRACTED`
- admin.py `EXTRACTED`
- main.py `EXTRACTED`
- dashboard.py `EXTRACTED`
- lore.py `EXTRACTED`
- users.py `EXTRACTED`
- routers/collection.py `EXTRACTED`
- system.py `EXTRACTED`
- nexus_service.py `EXTRACTED`
- telegram_listener.py `EXTRACTED`
- test_api_response_schemas.py `EXTRACTED`
- nexus_vintage_service.py `EXTRACTED`
- phase0_migration.py `EXTRACTED`
- vinted_hunter_service.py `EXTRACTED`
- vault.py `EXTRACTED`
- test_scraper_interface.py `EXTRACTED`
- restore_vault.py `EXTRACTED`
- *…and 65 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Base `EXTRACTED`

### references
- .calculate_score() `EXTRACTED`
- .generate_default_lore_for_product() `EXTRACTED`
- .add_offer() `EXTRACTED`
- .is_mandatory_buy() `EXTRACTED`
- .get_consolidated_value() `EXTRACTED`
- .get_pure_landed_value() `EXTRACTED`
- .get_by_name() `EXTRACTED`
- .validate_cross_reference() `EXTRACTED`
- .get_by_figure_id() `EXTRACTED`
- .get_by_series() `EXTRACTED`

### uses
- TelegramListener `INFERRED`
- run_daily_scan() `INFERRED`
- ProductRepository `INFERRED`
- LoreHarvesterService `INFERRED`
- MarketAnalyticsService `INFERRED`
- DealScorer `INFERRED`
- NexusService `INFERRED`
- VintedHunterService `INFERRED`
- OracleAssistantAI `INFERRED`
- GuardianService `INFERRED`
- ValuationService `INFERRED`
- run_match_bulk_task() `INFERRED`
- BudgetOptimizerService `INFERRED`
- MaintenanceService `INFERRED`
- NexusVintageService `INFERRED`
- run_match_task() `INFERRED`
- MarketIntelligenceService `INFERRED`
- revert_action() `INFERRED`
- ProductLoreSeedService `INFERRED`
- SentinelService `INFERRED`
- *…and 62 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*