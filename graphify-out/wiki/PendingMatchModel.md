# PendingMatchModel

> God node · 97 connections · `src/domain/models.py`

**Community:** [Routers: OfferModel, json](Routers-_OfferModel,_json.md)

## Connections by Relation

### calls
- .update_database() `EXTRACTED`
- revert_vintage_to_purgatory() `EXTRACTED`
- verify_phase2() `EXTRACTED`
- test_atomic_undo() `EXTRACTED`
- rollback_shops_to_purgatory() `EXTRACTED`
- rollback_scrapers() `EXTRACTED`
- test_unlink() `EXTRACTED`
- recover_to_purgatory() `EXTRACTED`
- .cmd_import_wallapop() `EXTRACTED`
- ._save_to_purgatory() `EXTRACTED`
- test_api_purgatory_bulk_match() `EXTRACTED`
- run_cleanup() `EXTRACTED`
- test_purgatory_list_matches_schema() `EXTRACTED`
- seed_vintage_items() `EXTRACTED`

### contains
- models.py `EXTRACTED`

### imports
- daily_scan.py `EXTRACTED`
- purgatory.py `EXTRACTED`
- products.py `EXTRACTED`
- scrapers.py `EXTRACTED`
- pipeline.py `EXTRACTED`
- admin.py `EXTRACTED`
- dashboard.py `EXTRACTED`
- users.py `EXTRACTED`
- telegram_listener.py `EXTRACTED`
- test_api_response_schemas.py `EXTRACTED`
- vinted_hunter_service.py `EXTRACTED`
- restore_vault.py `EXTRACTED`
- migrate_purgatory_vintage.py `EXTRACTED`
- product.py `EXTRACTED`
- test_revert_logistics.py `EXTRACTED`
- migrate_to_cloud.py `EXTRACTED`
- test_vinted_hunter.py `EXTRACTED`
- wallapop_manual_importer.py `EXTRACTED`
- smoke_test.py `EXTRACTED`
- telegram_oracle_ai.py `EXTRACTED`
- *…and 18 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Base `EXTRACTED`

### rationale_for
- Stores scraped items that weren't confidently matched to a Product. These sit… `EXTRACTED`

### references
- .get_pending_matches() `EXTRACTED`

### uses
- [ScrapingPipeline](ScrapingPipeline.md) `INFERRED`
- TelegramListener `INFERRED`
- run_daily_scan() `INFERRED`
- ProductRepository `INFERRED`
- VintedHunterService `INFERRED`
- OracleAssistantAI `INFERRED`
- run_match_bulk_task() `INFERRED`
- BudgetOptimizerService `INFERRED`
- run_match_task() `INFERRED`
- migrate_existing_vintage() `INFERRED`
- clean_purgatory_globally() `INFERRED`
- revert_action() `INFERRED`
- run_match_vintage_task() `INFERRED`
- import_wallapop_products() `INFERRED`
- restore_from_vault() `INFERRED`
- MatchService `INFERRED`
- migrate_data() `INFERRED`
- WallapopManualImporter `INFERRED`
- delete_product() `INFERRED`
- test_revert_linked_vintage_returns_to_purgatory_and_survives_cleanup() `INFERRED`
- *…and 21 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*