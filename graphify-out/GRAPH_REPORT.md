# Graph Report - oraculo-nueva-eternia  (2026-10-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3139 nodes · 9012 edges · 160 communities (84 shown, 76 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 854 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6b156fd8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 97
- Community 98
- Community 99
- Community 100
- Community 102
- Community 103
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 115
- Community 117
- Community 118
- Community 121
- Community 122
- Community 123
- Community 124
- Community 126

## God Nodes (most connected - your core abstractions)
1. `ProductModel` - 205 edges
2. `ScrapedOffer` - 144 edges
3. `OfferModel` - 136 edges
4. `UserModel` - 129 edges
5. `PendingMatchModel` - 97 edges
6. `CollectionItemModel` - 94 edges
7. `LogisticsService` - 62 edges
8. `BaseScraper` - 62 edges
9. `react` - 62 edges
10. `ScrapingPipeline` - 56 edges

## Surprising Connections (you probably didn't know these)
- `fix_ebay_tags()` --uses--> `OfferModel`  [INFERRED]
  scripts/fix_ebay_tags.py → src/domain/models.py
- `test_models_product_offer_alias()` --uses--> `OfferModel`  [INFERRED]
  tests/unit/test_scraper_interface.py → src/domain/models.py
- `get_urls()` --uses--> `PendingMatchModel`  [INFERRED]
  scripts/experimental/get_wallapop_urls.py → src/domain/models.py
- `get_link()` --uses--> `ProductAliasModel`  [INFERRED]
  scripts/experimental/get_af411_link.py → src/domain/models.py
- `test_scrape_multi_via_cdp_inner_imports()` --uses--> `ScrapedOffer`  [INFERRED]
  tests/unit/test_scraper_interface.py → src/infrastructure/scrapers/base.py

## Import Cycles
- None detected.

## Communities (160 total, 76 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (38): run_migrations_offline(), run_migrations_online(), analyze_dependencies(), main(), backup_cloud_data(), cloud_backup(), check_collection(), check_deals() (+30 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (56): check_p2p_stats(), run_cleanup(), delete_fictional_items(), verify_phase2(), fix_vintage_offers(), migrate_existing_vintage(), rollback_scrapers(), test_unlink() (+48 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (21): analyze_frikiverso(), brute_force(), get_engine_id(), test_tradeinn_playwright_refined(), test_tradeinn_robust(), audit_wallapop_search(), extract_patterns(), main() (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (11): test_enhanced_scrapers(), test_conversion(), main(), MockScraper, ScrapedOffer, DVDStoreSpainScraper, EbayScraper, test_scraper() (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (28): LoreHarvesterService, ProductLoreSeedService, CharacterLoreModel, ProductLoreModel, CharacterLoreListResponse, CharacterLoreOutput, CharacterLoreUpdateRequest, get_character_lore() (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (16): test_manual(), profile(), BixotoScraper, DeToyboysNLScraper, ElectropolisScraper, test_scraper(), FrikimazScraper, FrikiversoScraper (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (59): exportCollectionExcelVintage(), getPublicShowcase(), getScrapersLogs(), syncNexusVintage(), unlinkOffer(), updateProduct(), getCollection(), Product (+51 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (74): AuthorizedDeviceOutput, CardAiEnhanceInput, CardAiEnhanceOutput, CartBreakdownItemOutput, CartCalculationOutput, CartItem, CartRequest, CartShopBreakdownOutput (+66 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (30): verify_market_intelligence(), cloud_seed(), check_af411_data(), check_products(), bulk_sync(), verify_deal_scorer(), MaintenanceService, MarketIntelligenceService (+22 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (57): authorizeDevice(), deleteDevice(), deleteHero(), Device, downloadImagesZip(), exportCollectionExcel(), exportCollectionSqlite(), getDevices() (+49 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (51): Hero, isUserAdmin(), attachAuth(), clearSession(), getToken(), handleAuthError(), SESSION_KEYS, setToken() (+43 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (46): adminHeaders, createWallapopJob(), discardItem(), discardItemsBulk(), getPurgatory(), getWallapopJobs(), matchItemsBulk(), matchMiscellaneousItem() (+38 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (26): check_rules(), check_scoring(), repair_scores(), recover_and_normalize(), recover_and_normalize(), test_calc(), test_scenarios(), test_logistics() (+18 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (19): benchmark_v3(), main(), VintedHunterService, VintedSentinelService, SmartMatcher, SmartBridge, HunterAlertLogModel, _run_hunter_bg() (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.05
Nodes (21): diagnose_amazon(), diagnose_kidinn(), verify_tradeinn_final_specific(), verify_tradeinn_final(), verify_tradeinn_interactive(), verify_tradeinn_legitimized(), verify_tradeinn_two_phase(), main() (+13 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (11): check_cloud_data(), get_link(), get_urls(), fix_ebay_tags(), fix_users_table(), seed_vintage_items(), DealScorer, _add_column_if_missing_sqlite() (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.07
Nodes (21): get_cors_origins(), ensure_scrapers_registered(), get_current_user(), _is_service_key(), scope_user_id(), _user_from_token(), verify_api_key(), verify_device() (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (15): init_user_passwords(), rate_limit(), SecurityShield, EmailService, create_access_token(), is_admin(), require_admin(), forgot_password() (+7 more)

### Community 18 - "Community 18"
Cohesion: 0.07
Nodes (19): build_session(), clean_headers(), combine_sections(), download_image(), extract_detail_link(), extract_image_url(), find_sections(), generate_text_report() (+11 more)

### Community 19 - "Community 19"
Cohesion: 0.08
Nodes (43): getSystemTcgLayouts(), CardAiEnhancePayload, CardAiEnhanceResult, enhanceCardWithAI(), MotuArtStyle, CharacterLore, CharacterLoreListResponse, fetchCharacterLoreList() (+35 more)

### Community 20 - "Community 20"
Cohesion: 0.07
Nodes (18): MarketAnalyticsService, CollectionItemBase, CollectionItemCreate, CollectionItemSchema, ProductBase, ProductCreate, ProductSchema, BudgetOptimizeRequest (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.09
Nodes (21): check_users(), is_telegram_only_missing_enabled(), set_telegram_only_missing_enabled(), should_send_product_push(), AuthorizedDeviceModel, SystemConfigModel, UserModel, get_public_showcase() (+13 more)

### Community 22 - "Community 22"
Cohesion: 0.07
Nodes (11): run_final_sync(), trigger_nexus(), run_nuclear_sync(), CatalogRefreshService, NexusService, run_migration_task(), TelemetryHandler, run_migration_task() (+3 more)

### Community 23 - "Community 23"
Cohesion: 0.07
Nodes (21): exhaustive_search(), audit_catalogs(), audit_db(), find_diff(), clean_excel_nulls(), cleanup(), cloud_merge(), count_excel_ids() (+13 more)

### Community 24 - "Community 24"
Cohesion: 0.10
Nodes (16): build_session(), clean_headers(), download_image(), extract_detail_link(), extract_image_url(), find_sections(), generate_text_report(), get_project_paths() (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.07
Nodes (14): TestPipelineHardening, _harvest_tab(), main(), _normalize_price(), ingest_data(), ScraperPlugin, ScrapingPipeline, test_models_product_offer_alias() (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (7): main(), SmythsToysScraper, resolve(), test_smythstoys_default_masters_search_url(), test_smythstoys_parse_nuxt_data_devalue_and_vintage_guard(), test_smythstoys_search_rea_cdp_replay(), fake_fast_infiltration()

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (10): ExcelManager, VaultService, success(), StagedImportModel, api_generate_vault(), api_stage_vault(), api_sync_excel(), download_images_zip() (+2 more)

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (27): relinkOffer(), DashboardStats, FinancialHealth, getDashboardHistory(), getDashboardStats(), getHallOfFame(), getPeerToPeerOpportunities(), getTopDeals() (+19 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (15): test_amazon_extraction(), execute_scraper(), get_scraper_class(), main(), run_sequential_incursion(), AmazonScraper, test(), run_scraper() (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (9): SSLService, get_ssl_status(), _generate_test_cert_pem(), test_get_certificate_status_active(), test_get_certificate_status_expired(), test_get_certificate_status_expiring_soon(), test_get_certificate_status_fallback(), test_parse_x509_cert() (+1 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (10): WallapopIpLogModel, test(), WallapopScraper, _audit_ip_log(), _audit_ip_log(), search_wallapop_v3_signed(), SignedSearchResult, run() (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.07
Nodes (7): test_collection_non_admin_cannot_read_other_users(), test_collection_rejects_unauthenticated(), test_dashboard_stats_accepts_approved_device(), test_dashboard_stats_rejects_pending_device(), test_public_showcase_non_admin_cannot_target_other_user(), test_public_showcase_rejects_unauthenticated(), test_user_settings_non_admin_scoped_to_self()

### Community 33 - "Community 33"
Cohesion: 0.10
Nodes (13): debug_structure(), debug_siblings(), find_text(), check_actiontoys_api(), check_kidinn_search(), test_actiontoys(), test_kidinn(), test_logs() (+5 more)

### Community 34 - "Community 34"
Cohesion: 0.10
Nodes (20): calculateCart(), CartInvoice, CartInvoiceBreakdownItem, CartInvoiceShop, BudgetOptimizerModal(), BudgetOptimizerModalProps, OracleCart(), GrayskullRitualOverlay() (+12 more)

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (14): rename_scraper(), cleanup_shops(), cleanup_duplicates(), cleanup_specific_duplicates(), clean_harvester(), clean_idealo(), check_db(), initialize_scrapers() (+6 more)

### Community 36 - "Community 36"
Cohesion: 0.13
Nodes (10): sync_excel_from_db(), GuardianService, export_excel(), export_excel_vintage(), export_sqlite(), get_collection(), toggle_collection(), trigger_excel_sync_background() (+2 more)

### Community 37 - "Community 37"
Cohesion: 0.10
Nodes (23): name, private, type, version, autoprefixer, clsx, eslint, @eslint/js (+15 more)

### Community 38 - "Community 38"
Cohesion: 0.14
Nodes (6): GeminiCardService, enhance_card_with_ai(), test_enhance_card_alcala_texeira(), test_enhance_card_legacy_aliases(), test_enhance_card_obrero_norem(), test_enhance_card_with_mocked_multimodal_gemini()

### Community 40 - "Community 40"
Cohesion: 0.13
Nodes (18): authorize_device(), create_user(), delete_hero(), get_all_devices(), get_all_heroes(), get_duplicates(), renew_ssl(), reset_hero_password() (+10 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (6): GitHubQuotaService, export_execution_logs_csv(), get_github_quota_status(), test_generate_logs_csv(), test_quota_service_db_fallback(), test_quota_service_with_github_api()

### Community 42 - "Community 42"
Cohesion: 0.14
Nodes (12): build_section_headers(), build_section_params(), extract_image_url(), parse_section_items(), search_wallapop_section(), SectionSearchResult, test_build_section_headers(), test_build_section_params() (+4 more)

### Community 43 - "Community 43"
Cohesion: 0.09
Nodes (21): action, default_icon, default_popup, content_scripts, 128, 16, 24, 32 (+13 more)

### Community 44 - "Community 44"
Cohesion: 0.14
Nodes (4): test_manual(), test_reliability(), FantasiaScraper, analyze_matches()

### Community 45 - "Community 45"
Cohesion: 0.12
Nodes (8): test_logistics_integration(), admin_bearer(), admin_user(), authorized_device_headers(), bearer(), client(), test_user(), viewer_token()

### Community 46 - "Community 46"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.09
Nodes (7): test_admin_duplicates_devices_temporary_products_match_schema(), test_collection_toggle_and_update_match_schema(), test_logistics_cart_calculated_branch_matches_schema(), test_logistics_cart_pending_rules_branch_matches_schema(), test_scrapers_status_logs_ip_logs_match_schema(), test_vintage_miscellaneous_matches_schema(), test_wallapop_jobs_full_lifecycle_matches_schema()

### Community 48 - "Community 48"
Cohesion: 0.22
Nodes (20): Get-PythonExe(), Invoke-AssistedIncursion(), Invoke-BackupDual(), Invoke-ChromeDebug(), Invoke-CreateShortcuts(), Invoke-DeployCloud(), Invoke-DiagnosticDb(), Invoke-DockerStart() (+12 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (6): CompletenessValidator, PageAudit, render_markdown_report(), ScrapeRunReport, ScrapeRunReporter, StoreRun

### Community 50 - "Community 50"
Cohesion: 0.19
Nodes (3): OracleAssistantAI, test_telegram_oracle_ai_collection_query(), test_telegram_oracle_ai_deals_query()

### Community 51 - "Community 51"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+11 more)

### Community 52 - "Community 52"
Cohesion: 0.11
Nodes (8): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade()

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (9): _build_signed_headers(), WallapopSigner, test_parse_wallapop_json_objects_extracts_offer(), test_parse_wallapop_json_objects_filters_junk_keywords(), test_parse_wallapop_json_objects_skips_missing_price(), test_signature_changes_with_path(), test_signature_explicit_secret_still_wins_over_env(), test_signature_is_deterministic_for_fixed_timestamp() (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.13
Nodes (5): _build_product_index(), build_suggestion_context(), _ean_key(), _item(), _item()

### Community 55 - "Community 55"
Cohesion: 0.15
Nodes (3): SyncWorker, SyncQueueModel, SyncQueueRepository

### Community 56 - "Community 56"
Cohesion: 0.16
Nodes (5): ValuationService, get_dashboard_hall_of_fame(), get_dashboard_history(), get_dashboard_match_stats(), get_dashboard_stats()

### Community 57 - "Community 57"
Cohesion: 0.21
Nodes (7): parse_history_rows(), compute_suggestions(), _serialize_suggestion(), _suggestion_sort_key(), _item(), _row(), TestLinkMemory

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (6): claim_pending_job(), main_loop(), process_job(), submit_results(), _test(), WallapopManualScraper

### Community 60 - "Community 60"
Cohesion: 0.21
Nodes (7): evaluate_gate(), main(), run_gitleaks(), run_trufflehog(), ensure_chrome_debug_running(), find_chrome_executable(), is_chrome_debug_port_open()

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (13): downloadExecutionLogsCsv(), getGitHubQuotaStatus(), GitHubQuotaStatus, ScraperExecutionLog, CHART_COLORS, getParsedMetrics(), getStepperStatus(), StepperStatus (+5 more)

### Community 64 - "Community 64"
Cohesion: 0.12
Nodes (16): devDependencies, autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, postcss (+8 more)

### Community 65 - "Community 65"
Cohesion: 0.17
Nodes (10): ModernCalibratorModalProps, SwordCoords, VintageCalibratorModalProps, PowerSwordLoaderProps, LightningTheme, Point, ProceduralLightningCanvas(), ProceduralLightningCanvasProps (+2 more)

### Community 66 - "Community 66"
Cohesion: 0.21
Nodes (7): revert_vintage_to_purgatory(), PriceAlertModel, check_and_send_multiuser_alerts(), anyio_backend(), test_check_and_send_multiuser_alerts_price_alert(), test_check_and_send_multiuser_alerts_wishlist(), mock_query()

### Community 67 - "Community 67"
Cohesion: 0.13
Nodes (15): dependencies, axios, clsx, date-fns, framer-motion, html-to-image, lucide-react, react (+7 more)

### Community 68 - "Community 68"
Cohesion: 0.16
Nodes (3): _fuzzy_in(), PythonBrainEngine, split_catalog_name()

### Community 69 - "Community 69"
Cohesion: 0.20
Nodes (7): apply_learned_hits(), find_learned_hits(), jaccard(), learned_reason(), LearnedHit, LearnedLink, LinkMemory

### Community 70 - "Community 70"
Cohesion: 0.20
Nodes (6): WallapopJobModel, claim_pending_wallapop_job(), create_wallapop_job(), list_wallapop_jobs(), submit_wallapop_job_results(), WallapopJobResultsRequest

### Community 72 - "Community 72"
Cohesion: 0.21
Nodes (5): build_companion_lookup(), inject_vintage_sculpt_companions(), _norm_name(), _ascii_lower(), tokenize()

### Community 74 - "Community 74"
Cohesion: 0.25
Nodes (8): _fetch_and_cache_product_image(), _fake_source_image_bytes(), _FakeResponse, _make_test_session(), test_downloads_converts_and_caches_as_webp(), test_returns_none_and_does_not_crash_on_download_failure(), test_returns_none_for_nonexistent_product(), test_returns_none_when_product_has_no_image_url()

### Community 75 - "Community 75"
Cohesion: 0.24
Nodes (5): main(), run_ssh_renewal(), test_run_ssh_renewal_execution(), test_ssl_gh_actions_healthy_when_above_threshold(), test_ssl_gh_actions_triggers_renewal_when_below_threshold()

### Community 78 - "Community 78"
Cohesion: 0.20
Nodes (9): apiClient, AppArchitectureGraph(), ConnectedEdge, HealthStatus, hexToRgb(), ICON_MAP, Props, STATUS_COLORS (+1 more)

### Community 79 - "Community 79"
Cohesion: 0.18
Nodes (3): import_wallapop_manual_html(), run_scrapers(), stop_scrapers()

### Community 80 - "Community 80"
Cohesion: 0.24
Nodes (6): clean_price(), normalize_us_price(), test_currency_detection(), test_migration_logic(), clean_numeric(), extract_deep_intelligence()

### Community 83 - "Community 83"
Cohesion: 0.39
Nodes (3): test_v2(), test(), TradeinnScraper

### Community 84 - "Community 84"
Cohesion: 0.39
Nodes (4): apply_safe_zone_margin(), build_multi_res_ico(), main(), render_optical_lod()

### Community 86 - "Community 86"
Cohesion: 0.50
Nodes (7): createOracleButton(), extractProducts(), handleSendToOraculo(), init(), SELECTORS, showNotification(), updateCounter()

### Community 87 - "Community 87"
Cohesion: 0.32
Nodes (5): FAQ_CATEGORIES, FAQ_ITEMS, FaqCategory, FaqItem, CATEGORY_ICONS

### Community 90 - "Community 90"
Cohesion: 0.43
Nodes (6): validate_motu_relevance(), test_validate_motu_relevance_invalid_big_jim(), test_validate_motu_relevance_invalid_funko(), test_validate_motu_relevance_invalid_masterverse(), test_validate_motu_relevance_non_motu_vintage(), test_validate_motu_relevance_valid_cases()

### Community 92 - "Community 92"
Cohesion: 0.52
Nodes (5): importWallapopProducts(), parseWallapopText(), WallapopImportResult, WallapopProduct, WallapopImporter()

### Community 94 - "Community 94"
Cohesion: 0.52
Nodes (4): check_apify_token(), check_scraperapi_key(), run_diagnostics(), test_api_security()

### Community 100 - "Community 100"
Cohesion: 0.47
Nodes (3): populate_spanish_rules(), seed_logistics(), _execute()

### Community 107 - "Community 107"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 110 - "Community 110"
Cohesion: 0.50
Nodes (3): @tailwindcss/vite, vite, @vitejs/plugin-react

### Community 113 - "Community 113"
Cohesion: 0.67
Nodes (3): PATH, send_telegram_alert(), renew_ssl.sh script

## Knowledge Gaps
- **12 isolated node(s):** `PATH`, `oraculo-nueva-eternia`, `autoprefixer`, `clsx`, `postcss` (+7 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1024 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProductModel` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 25`, `Community 27`, `Community 35`, `Community 36`, `Community 39`, `Community 40`, `Community 47`, `Community 50`, `Community 56`, `Community 63`, `Community 66`, `Community 74`, `Community 102`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 82 inferred relationships involving `ProductModel` (e.g. with `audit_catalogs()` and `verify_market_intelligence()`) actually correct?**
  _`ProductModel` has 82 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PATH`, `oraculo-nueva-eternia`, `autoprefixer` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.04253968253968254 - nodes in this community are weakly interconnected._
- **Why does `ScrapedOffer` connect `Community 3` to `Community 2`, `Community 98`, `Community 5`, `Community 42`, `Community 44`, `Community 13`, `Community 15`, `Community 83`, `Community 53`, `Community 25`, `Community 26`, `Community 59`, `Community 29`, `Community 31`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `ScrapedOffer` (e.g. with `TestPipelineHardening` and `MockScraper`) actually correct?**
  _`ScrapedOffer` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05396825396825397 - nodes in this community are weakly interconnected._