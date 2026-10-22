# UserModel

> God node · 129 connections · `src/domain/models.py`

**Community:** [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md)

## Connections by Relation

### calls
- migrate_excel_to_db() `EXTRACTED`
- restore_from_vault() `EXTRACTED`
- migrate_excel_to_db() `EXTRACTED`
- cloud_merge() `EXTRACTED`
- cloud_seed() `EXTRACTED`
- test_api_purgatory_bulk_match() `EXTRACTED`
- .setUp() `EXTRACTED`

### contains
- models.py `EXTRACTED`

### imports
- purgatory.py `EXTRACTED`
- products.py `EXTRACTED`
- pipeline.py `EXTRACTED`
- admin.py `EXTRACTED`
- main.py `EXTRACTED`
- deps.py `EXTRACTED`
- dashboard.py `EXTRACTED`
- lore.py `EXTRACTED`
- users.py `EXTRACTED`
- auth.py `EXTRACTED`
- routers/collection.py `EXTRACTED`
- system.py `EXTRACTED`
- telegram_listener.py `EXTRACTED`
- phase0_migration.py `EXTRACTED`
- vault.py `EXTRACTED`
- restore_vault.py `EXTRACTED`
- phase0_vintage_migration.py `EXTRACTED`
- migrate_to_cloud.py `EXTRACTED`
- sync_excel_from_db.py `EXTRACTED`
- test_tcg_layouts_api.py `EXTRACTED`
- *…and 22 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Base `EXTRACTED`

### references
- .get_user_status() `EXTRACTED`

### uses
- TelegramListener `INFERRED`
- GuardianService `INFERRED`
- run_match_bulk_task() `INFERRED`
- run_match_task() `INFERRED`
- run_match_vintage_task() `INFERRED`
- is_admin() `INFERRED`
- scope_user_id() `INFERRED`
- relink_offer() `INFERRED`
- migrate_data() `INFERRED`
- check_and_send_multiuser_alerts() `INFERRED`
- harvest_missing_lore() `INFERRED`
- update_product_lore() `INFERRED`
- should_send_product_push() `INFERRED`
- save_tcg_layouts() `INFERRED`
- get_current_user() `INFERRED`
- backup_cloud_data() `INFERRED`
- TestPhase0Migration `INFERRED`
- login() `INFERRED`
- get_top_deals() `INFERRED`
- test_check_and_send_multiuser_alerts_price_alert() `INFERRED`
- *…and 57 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*