# Services: SSLService, test_ssl_service.py

> 31 nodes

## Key Concepts

- **SSLService** (23 connections) — `src/application/services/ssl_service.py`
- **test_ssl_service.py** (16 connections) — `tests/unit/test_ssl_service.py`
- **.get_certificate_status()** (13 connections) — `src/application/services/ssl_service.py`
- **.renew_ssl_certificate()** (9 connections) — `src/application/services/ssl_service.py`
- **_generate_test_cert_pem()** (7 connections) — `tests/unit/test_ssl_service.py`
- **._parse_x509_cert()** (5 connections) — `src/application/services/ssl_service.py`
- **get_ssl_status()** (5 connections) — `src/interfaces/api/routers/admin.py`
- **._fetch_live_tls_cert()** (4 connections) — `src/application/services/ssl_service.py`
- **._find_cert_path()** (4 connections) — `src/application/services/ssl_service.py`
- **test_get_certificate_status_active()** (4 connections) — `tests/unit/test_ssl_service.py`
- **test_get_certificate_status_expired()** (4 connections) — `tests/unit/test_ssl_service.py`
- **test_get_certificate_status_expiring_soon()** (4 connections) — `tests/unit/test_ssl_service.py`
- **test_parse_x509_cert()** (4 connections) — `tests/unit/test_ssl_service.py`
- **test_renew_ssl_certificate()** (4 connections) — `tests/unit/test_ssl_service.py`
- **test_get_certificate_status_fallback()** (3 connections) — `tests/unit/test_ssl_service.py`
- **datetime** (2 connections)
- **_run_sub()** (1 connections) — `src/application/services/ssl_service.py`
- **Path** (1 connections)
- **asyncio** (1 connections)
- **Servicio integral de diagnóstico, observabilidad y renovación de certificados…** (1 connections) — `src/application/services/ssl_service.py`
- **Ejecuta la renovación del certificado SSL de forma no bloqueante. - Invoca el…** (1 connections) — `src/application/services/ssl_service.py`
- **Busca el archivo de certificado en las ubicaciones estándar.** (1 connections) — `src/application/services/ssl_service.py`
- **Parsea un certificado PEM X.509 utilizando cryptography.** (1 connections) — `src/application/services/ssl_service.py`
- **Consulta el certificado SSL directamente desde el socket TLS del servidor en…** (1 connections) — `src/application/services/ssl_service.py`
- **Obtiene el estado completo del certificado SSL. Prioridad: 1. Archivo en disco…** (1 connections) — `src/application/services/ssl_service.py`
- *... and 6 more nodes in this community*

## Relationships

- [Routers: admin.py, post](Routers-_admin.py,_post.md) (4 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (3 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (2 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (2 shared connections)
- [Services: .process_callback_query(), .get_user_status()](Services-_.process_callback_query,_.get_user_status.md) (2 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (1 shared connections)

## Source Files

- `src/application/services/ssl_service.py`
- `src/interfaces/api/routers/admin.py`
- `tests/unit/test_ssl_service.py`

## Audit Trail

- EXTRACTED: 60 (82%)
- INFERRED: 13 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*