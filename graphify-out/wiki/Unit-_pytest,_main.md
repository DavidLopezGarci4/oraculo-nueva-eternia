# Unit: pytest, main()

> 13 nodes

## Key Concepts

- **pytest** (31 connections)
- **main()** (10 connections) — `scripts/check_and_renew_ssl_gh_actions.py`
- **test_ssl_check_gh_actions.py** (9 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **run_ssh_renewal()** (8 connections) — `scripts/check_and_renew_ssl_gh_actions.py`
- **test_ssl_gh_actions_healthy_when_above_threshold()** (5 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **test_ssl_gh_actions_triggers_renewal_when_below_threshold()** (5 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **test_run_ssh_renewal_execution()** (3 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **asyncio** (2 connections)
- **Ejecuta la renovación remota de SSL en Oracle Cloud vía SSH.** (1 connections) — `scripts/check_and_renew_ssl_gh_actions.py`
- **Tests unitarios para el script de comprobación y renovación automática de SSL…** (1 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **Si el certificado tiene más de 14 días restantes, no debe intentar renovar y…** (1 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **Si el certificado tiene 14 días o menos, debe disparar la renovación vía SSH.** (1 connections) — `tests/unit/test_ssl_check_gh_actions.py`
- **Verifica que run_ssh_renewal invoca subprocess.run con los argumentos correctos.** (1 connections) — `tests/unit/test_ssl_check_gh_actions.py`

## Relationships

- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (5 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (3 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (3 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (2 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (2 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)
- [Unit: test_search_wallapop_v3_signed_smoke(), network](Unit-_test_search_wallapop_v3_signed_smoke,_network.md) (1 shared connections)
- [Unit: validate_motu_relevance(), test_api_motu_relevance.py](Unit-_validate_motu_relevance,_test_api_motu_relevance.py.md) (1 shared connections)

## Source Files

- `scripts/check_and_renew_ssl_gh_actions.py`
- `tests/unit/test_ssl_check_gh_actions.py`

## Audit Trail

- EXTRACTED: 57 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*