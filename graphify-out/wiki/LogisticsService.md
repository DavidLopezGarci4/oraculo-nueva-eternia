# LogisticsService

> God node · 62 connections · `src/application/services/logistics_service.py`

**Community:** [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md)

## Connections by Relation

### contains
- logistics_service.py `EXTRACTED`

### imports
- daily_scan.py `EXTRACTED`
- purgatory.py `EXTRACTED`
- products.py `EXTRACTED`
- pipeline.py `EXTRACTED`
- dashboard.py `EXTRACTED`
- users.py `EXTRACTED`
- vinted_hunter_service.py `EXTRACTED`
- migrate_purgatory_vintage.py `EXTRACTED`
- market_analytics_service.py `EXTRACTED`
- test_logistics_and_pricing.py `EXTRACTED`
- telegram_oracle_ai.py `EXTRACTED`
- budget_optimizer_service.py `EXTRACTED`
- logistics.py `EXTRACTED`
- restore_intelligence.py `EXTRACTED`
- restore_cloud.py `EXTRACTED`
- repair_opportunity_scores.py `EXTRACTED`
- valuation_service.py `EXTRACTED`
- check_scoring.py `EXTRACTED`
- test_cart_api.py `EXTRACTED`
- verify_logistics.py `EXTRACTED`
- *…and 2 more `imports` connection(s) not listed (lowest-degree first to go)*

### method
- .get_landing_price() `EXTRACTED`
- .optimized_get_landing_price() `EXTRACTED`
- .calculate_cart() `EXTRACTED`
- .normalize_shop_name() `EXTRACTED`
- ._resolve_rule() `EXTRACTED`
- ._apply_rule() `EXTRACTED`
- .get_rules_by_shop() `EXTRACTED`
- .calculate_roi() `EXTRACTED`

### rationale_for
- Oráculo Logístico (Phase 15/18/42): Servicio centralizado para el cálculo de… `EXTRACTED`

### uses
- [ScrapingPipeline](ScrapingPipeline.md) `INFERRED`
- LogisticRuleModel `INFERRED`
- MarketAnalyticsService `INFERRED`
- VintedHunterService `INFERRED`
- ValuationService `INFERRED`
- run_match_bulk_task() `INFERRED`
- BudgetOptimizerService `INFERRED`
- run_match_task() `INFERRED`
- migrate_existing_vintage() `INFERRED`
- run_match_vintage_task() `INFERRED`
- relink_offer() `INFERRED`
- CurrencyService `INFERRED`
- get_top_deals() `INFERRED`
- recover_and_normalize() `INFERRED`
- get_product_offers() `INFERRED`
- get_p2p_opportunities() `INFERRED`
- check_scoring() `INFERRED`
- repair_scores() `INFERRED`
- recover_and_normalize() `INFERRED`
- api_calculate_cart() `INFERRED`
- *…and 10 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*