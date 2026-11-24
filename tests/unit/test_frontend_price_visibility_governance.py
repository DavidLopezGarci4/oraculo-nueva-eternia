"""
Deterministic governance tests for unified price visibility & manual price privacy.

Enforces AGENTS.md Rule 2 under the unified Header Eye (Incognito Mode) model:
- Open Eye (isIncognito = false): all amounts, costs, ROI, and manual inputs are visible.
- Closed Eye (isIncognito = true / .mode-incognito): all amounts and manual inputs blur
  with zero hover/focus/tooltip leaks, and no secondary Settings lock remains.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"


def _parse_css_rules(css_text: str) -> list[tuple[list[str], str]]:
    """Strip CSS comments and return (selectors, body) pairs."""
    cleaned = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    rules: list[tuple[list[str], str]] = []
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", cleaned):
        selectors = [s.strip() for s in match.group(1).split(",") if s.strip()]
        body = match.group(2)
        rules.append((selectors, body))
    return rules


def test_css_manual_price_only_blurs_in_incognito_mode() -> None:
    css = (FRONTEND_SRC / "index.css").read_text(encoding="utf-8")

    assert ".reveal-manual-prices" not in css, (
        "Secondary .reveal-manual-prices CSS class must be removed under unified Eye control."
    )

    rules = _parse_css_rules(css)

    # No .blur-manual-price selector outside .mode-incognito may apply blur or reduced opacity
    for selectors, body in rules:
        for sel in selectors:
            if ".blur-manual-price" in sel and ".mode-incognito" not in sel:
                assert not re.search(r"filter\s*:\s*blur", body), (
                    f"Selector {sel!r} blurs outside .mode-incognito: {body!r}"
                )
                assert not re.search(r"opacity\s*:\s*0\.", body), (
                    f"Selector {sel!r} dims opacity outside .mode-incognito: {body!r}"
                )

    def _find_rule_body(required_selectors: set[str]) -> str:
        for selectors, body in rules:
            if required_selectors.issubset(set(selectors)):
                return body
        raise AssertionError(f"Missing CSS rule covering selectors: {sorted(required_selectors)}")

    incognito_body = _find_rule_body({
        ".mode-incognito .blur-incognito",
        ".mode-incognito .blur-incognito:hover",
        ".mode-incognito .blur-incognito:focus",
    })
    assert re.search(r"filter\s*:\s*blur\(8px\)\s*!important", incognito_body)
    assert re.search(r"user-select\s*:\s*none\s*!important", incognito_body)
    assert re.search(r"pointer-events\s*:\s*none\s*!important", incognito_body)

    manual_body = _find_rule_body({
        ".mode-incognito .blur-manual-price",
        ".mode-incognito .blur-manual-price:hover",
        ".mode-incognito .blur-manual-price:focus",
    })
    assert re.search(r"filter\s*:\s*blur\(8px\)\s*!important", manual_body)
    assert re.search(r"opacity\s*:\s*0\.45\s*!important", manual_body)
    assert re.search(r"user-select\s*:\s*none\s*!important", manual_body)
    assert re.search(r"pointer-events\s*:\s*none\s*!important", manual_body)


def test_no_secondary_manual_price_lock_in_frontend() -> None:
    forbidden_tokens = (
        "manualPriceRevealPref",
        "reveal-manual-prices",
        "oraculo:manual-price-reveal",
    )
    allowed_suffixes = {".ts", ".tsx", ".css", ".json"}
    offenders: list[str] = []

    for path in FRONTEND_SRC.rglob("*"):
        if not path.is_file() or path.suffix not in allowed_suffixes:
            continue
        content = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in content:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {token}")
        sanitized = (
            content.replace("localStorage.removeItem('allowManualPriceReveal')", "")
            if path.name == "App.tsx"
            else content
        )
        if "allowManualPriceReveal" in sanitized:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: allowManualPriceReveal")

    assert not offenders, f"Secondary manual-price lock leftovers found: {offenders}"

    app_tsx = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
    assert "localStorage.removeItem('allowManualPriceReveal')" in app_tsx
    assert "document.body.classList.toggle('mode-incognito', isIncognito)" in app_tsx


def test_readonly_badges_use_blur_incognito_without_manual_lock() -> None:
    dashboard = (FRONTEND_SRC / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
    assert "blur-manual-price" not in dashboard
    assert "PVP Salida:" in dashboard and "Coste:" in dashboard
    assert len(re.findall(r"Coste:\s*<span[^>]*blur-incognito", dashboard)) >= 2

    emi_widget = (FRONTEND_SRC / "components" / "dashboard" / "EterniaMarketIndexWidget.tsx").read_text(
        encoding="utf-8"
    )
    assert "blur-manual-price" not in emi_widget
    assert "blur-incognito" in emi_widget

    detail_modal = (FRONTEND_SRC / "components" / "CollectionItemDetailModal.tsx").read_text(
        encoding="utf-8"
    )
    assert detail_modal.count("blur-manual-price") == 1, (
        "CollectionItemDetailModal should only keep blur-manual-price on the manual price <input>."
    )
    assert re.search(
        r"className=\{`[^`]*blur-incognito[^`]*`\}>\s*\{buyProfitLoss >= 0 \? 'Ahorro' : 'Sobreprecio'\}",
        detail_modal,
    )
    assert re.search(
        r"<h4 className=\{`[^`]*blur-incognito[^`]*`\}>",
        detail_modal,
    )
    assert re.search(
        r"className=\{`[^`]*blur-incognito[^`]*`\}>\s*\{buyProfitLoss >= 0 \? <TrendingUp",
        detail_modal,
    )

    collection = (FRONTEND_SRC / "pages" / "Collection.tsx").read_text(encoding="utf-8")
    assert collection.count("blur-manual-price") == 1, (
        "Collection.tsx should only keep blur-manual-price on the manual retail_price <input>."
    )
    assert re.search(
        r'<span className="blur-incognito">\{roi >= 0 \? \'\+\' : \'\'\}\{roi\.toFixed\(1\)\}%</span>',
        collection,
    )
    assert re.search(
        r'<span className="blur-incognito">\{product\.purchase_price\.toFixed\(0\)\}€</span>',
        collection,
    )


def test_manual_price_inputs_block_hover_and_focus_in_incognito() -> None:
    targets = [
        (
            FRONTEND_SRC / "components" / "CollectionItemDetailModal.tsx",
            "Inversión manual en euros",
        ),
        (
            FRONTEND_SRC / "components" / "catalog" / "EditProductModal.tsx",
            "editingProduct.retail_price",
        ),
        (
            FRONTEND_SRC / "pages" / "Collection.tsx",
            "editingProduct.retail_price",
        ),
    ]

    for path, marker in targets:
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(
            r"<input\b(?:(?!/\s*>).)*?" + re.escape(marker) + r"(?:(?!/\s*>).)*?/\s*>",
            re.S,
        )
        match = pattern.search(text)
        assert match is not None, f"Could not locate manual price <input> ({marker}) in {path}"
        tag = match.group(0)

        assert "blur-incognito" in tag, f"Missing blur-incognito on {marker} in {path.name}"
        assert "blur-manual-price" in tag, f"Missing blur-manual-price on {marker} in {path.name}"
        assert "readOnly={isIncognito}" in tag, f"Missing readOnly={{isIncognito}} on {marker} in {path.name}"
        assert "tabIndex={isIncognito ? -1 : undefined}" in tag, (
            f"Missing tabIndex guard on {marker} in {path.name}"
        )

        title_match = re.search(r"title=\{isIncognito\s*\?\s*'([^']*)'\s*:", tag)
        assert title_match is not None, f"Missing incognito-safe title guard on {marker} in {path.name}"
        assert "{" not in title_match.group(1) and "€" not in title_match.group(1), (
            f"Incognito title must not leak price in {path.name}: {title_match.group(1)!r}"
        )
