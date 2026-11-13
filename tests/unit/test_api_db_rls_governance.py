import ast
import re
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text

REPO_ROOT = Path(__file__).resolve().parents[2]

LEGACY_PRE_GOVERNANCE_REVISIONS = {
    "66c2ec769424",
    "e905ab7993c4",
    "f48b00d4a369",
    "d4283e0fbed1",
    "feac3ac24f77",
    "8f1e2d3c4b5a",
}


def _strip_dollar_quoted_blocks(sql_text: str) -> str:
    """Elimina bloques PL/pgSQL delimitados por $$ ... $$ para auditar SQL de nivel raíz."""
    return re.sub(r"\$\$.*?\$\$", "", sql_text, flags=re.DOTALL)


def test_supabase_rls_hardening_sql_is_valid_and_complete():
    sql_path = REPO_ROOT / "scripts" / "supabase_rls_hardening.sql"
    assert sql_path.exists(), "Debe existir scripts/supabase_rls_hardening.sql"

    sql = sql_path.read_text(encoding="utf-8")
    top_level_sql = _strip_dollar_quoted_blocks(sql)

    # 1. Prohibido RAISE NOTICE a nivel raíz fuera de bloques PL/pgSQL (error 42601)
    assert not re.search(
        r"\bRAISE\s+(NOTICE|WARNING|EXCEPTION|LOG)\b", top_level_sql, flags=re.IGNORECASE
    ), "RAISE fuera de un bloque $$ ... $$ provoca error de sintaxis 42601 en PostgreSQL."

    # 2. Revocación explícita de privilegios presentes y futuros para anon y authenticated
    assert "REVOKE USAGE ON SCHEMA public FROM anon, authenticated;" in sql
    assert "REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;" in sql
    assert (
        "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;"
        in sql
    )

    # 3. Barrido dinámico seguro excluyendo tablas de extensiones (deptype = 'e') y verificando relowner
    assert "relrowsecurity = false" in sql
    assert "deptype = 'e'" in sql
    assert "current_user" in sql

    # 4. Event Trigger automático ante cualquier CREATE TABLE futuro en public
    assert "CREATE EVENT TRIGGER ensure_rls_on_public" in sql
    assert "ddl_command_end" in sql
    assert "rls_auto_enable" in sql


def _audit_post_governance_migration_source(source: str, mig_name: str) -> None:
    """Valida invariantes AST sobre una migración posterior al baseline de gobernanza."""
    tree = ast.parse(source, filename=mig_name)

    assert "DISABLE ROW LEVEL SECURITY" not in source.upper(), (
        f"Violación de seguridad en {mig_name}: prohibido ejecutar DISABLE ROW LEVEL SECURITY."
    )

    created_tables = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "create_table"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            created_tables.append(node.args[0].value)

    for tbl in created_tables:
        assert "ENABLE ROW LEVEL SECURITY" in source.upper() and tbl in source, (
            f"Violación en {mig_name}: create_table('{tbl}') sin ENABLE ROW LEVEL SECURITY explícito."
        )
        assert "REVOKE ALL" in source.upper(), (
            f"Violación en {mig_name}: create_table('{tbl}') sin REVOKE ALL para roles públicos."
        )


def test_alembic_rls_head_migration_and_future_table_invariants():
    versions_dir = REPO_ROOT / "migrations" / "versions"
    migration_files = sorted(versions_dir.glob("*.py"))
    assert migration_files, "No se encontraron migraciones en migrations/versions/"

    canonical_found = False

    for mig_file in migration_files:
        source = mig_file.read_text(encoding="utf-8-sig")
        assert "DISABLE ROW LEVEL SECURITY" not in source.upper(), (
            f"Prohibido ejecutar DISABLE ROW LEVEL SECURITY en cualquier migración ({mig_file.name})."
        )
        tree = ast.parse(source, filename=str(mig_file))

        revision_id = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "revision":
                        if isinstance(node.value, ast.Constant):
                            revision_id = node.value.value
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "revision":
                    if isinstance(node.value, ast.Constant):
                        revision_id = node.value.value

        if revision_id == "9b4c7d8e1f2a":
            canonical_found = True
            assert "ENABLE ROW LEVEL SECURITY" in source
            assert "REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated" in source
            assert "CREATE EVENT TRIGGER ensure_rls_on_public" in source
            assert "DISABLE ROW LEVEL SECURITY" not in source

        if revision_id in LEGACY_PRE_GOVERNANCE_REVISIONS:
            continue

        _audit_post_governance_migration_source(source, mig_file.name)

    assert canonical_found, (
        "Falta la migración canónica 9b4c7d8e1f2a que aplica RLS, REVOKE y Event Trigger en Supabase."
    )


def test_rls_ast_validator_rejects_unprotected_migration():
    """Caso negativo: verifica que el auditor AST rechaza tablas nuevas sin RLS o con DISABLE RLS."""
    unsafe_create = (
        "def upgrade():\n"
        "    op.create_table('leaked_table', sa.Column('id', sa.Integer()))\n"
    )
    with pytest.raises(AssertionError, match="ENABLE ROW LEVEL SECURITY"):
        _audit_post_governance_migration_source(unsafe_create, "unsafe_01.py")

    unsafe_downgrade = (
        "def downgrade():\n"
        "    op.execute('ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;')\n"
    )
    with pytest.raises(AssertionError, match="DISABLE ROW LEVEL SECURITY"):
        _audit_post_governance_migration_source(unsafe_downgrade, "unsafe_02.py")


def test_alembic_upgrade_head_succeeds_over_precreated_schema(tmp_path, monkeypatch):
    """
    Simula una BD preexistente creada con Base.metadata.create_all() sin estampar
    y verifica que `alembic upgrade head` es 100% idempotente y alcanza la revision `head` vigente.
    """
    from alembic import command
    from alembic.config import Config
    from src.domain.models import Base
    from src.core.config import settings

    db_file = tmp_path / "preexisting_oraculo.db"
    db_url = f"sqlite:///{db_file.as_posix()}"

    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    monkeypatch.setenv("SUPABASE_DATABASE_URL", db_url)
    monkeypatch.setattr(settings, "SUPABASE_DATABASE_URL", db_url, raising=False)

    alembic_cfg = Config(str(REPO_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(REPO_ROOT / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(alembic_cfg, "head")

    verify_engine = create_engine(db_url)
    with verify_engine.connect() as conn:
        ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    verify_engine.dispose()

    from alembic.script import ScriptDirectory

    assert ver == ScriptDirectory.from_config(alembic_cfg).get_current_head()


def test_no_shadow_migrators_or_startup_rls_locks():
    # 1. Ningún servicio en src/application o src/interfaces puede importar universal_migrator
    for folder in ("application", "interfaces"):
        for py_file in (REPO_ROOT / "src" / folder).rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8-sig"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and "universal_migrator" in node.module:
                    pytest.fail(
                        f"Migrador en sombra prohibido en {py_file.relative_to(REPO_ROOT)}: "
                        "no importar universal_migrator en servicios de aplicación o API."
                    )
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "universal_migrator" in alias.name:
                            pytest.fail(
                                f"Migrador en sombra prohibido en {py_file.relative_to(REPO_ROOT)}."
                            )

    # 2. init_cloud_db() NO debe ejecutar ENABLE ROW LEVEL SECURITY (evita ACCESS EXCLUSIVE LOCK en :6543)
    db_cloud_src = (REPO_ROOT / "src" / "infrastructure" / "database_cloud.py").read_text(encoding="utf-8-sig")
    assert "ENABLE ROW LEVEL SECURITY" not in db_cloud_src.upper(), (
        "Prohibido ejecutar ENABLE ROW LEVEL SECURITY en database_cloud.py (causa locks en pooler :6543)."
    )
    db_cloud_tree = ast.parse(db_cloud_src, filename="database_cloud.py")
    executable_alters = [
        node
        for node in ast.walk(db_cloud_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "text"
        and node.args
        and "ALTER TABLE" in ast.unparse(node.args[0]).upper()
    ]
    assert len(executable_alters) <= 1, (
        f"Prohibido añadir DDL ALTER TABLE en database_cloud.py (encontrados {len(executable_alters)} > 1). Usa Alembic."
    )
    assert "ALTER TABLE character_lore" not in db_cloud_src and '"character_lore"' not in db_cloud_src, (
        "El esquema de character_lore se gestiona exclusivamente con Alembic (a7c3e91f04b2)."
    )

    # 3. universal_migrator.py no debe resucitar origin_category y debe proteger Postgres si se ejecuta por CLI
    um_src = (REPO_ROOT / "src" / "infrastructure" / "universal_migrator.py").read_text(encoding="utf-8")
    assert "origin_category" not in um_src, (
        "universal_migrator.py no debe recrear la columna obsoleta origin_category eliminada por Alembic."
    )
    assert "ENABLE ROW LEVEL SECURITY" in um_src, (
        "universal_migrator.py debe aplicar salvaguarda RLS si se ejecuta manualmente contra PostgreSQL."
    )


def test_agents_md_and_scrapers_workflow_enforce_db_security_rule():
    agents_md = (REPO_ROOT / ".agents" / "AGENTS.md").read_text(encoding="utf-8")
    assert "Row-Level Security" in agents_md or "RLS" in agents_md, (
        ".agents/AGENTS.md debe documentar la regla obligatoria de RLS y seguridad de base de datos."
    )
    assert "DISABLE ROW LEVEL SECURITY" in agents_md, (
        ".agents/AGENTS.md debe prohibir explícitamente DISABLE ROW LEVEL SECURITY."
    )

    scrapers_yml = (REPO_ROOT / ".github" / "workflows" / "scrapers.yml").read_text(encoding="utf-8")
    assert "relrowsecurity" in scrapers_yml, (
        ".github/workflows/scrapers.yml debe incluir el centinela continuo de tablas sin RLS en public."
    )
