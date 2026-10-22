"""
Tests de la memoria de vinculaciones manuales (reutiliza OfferHistoryModel, sin tablas nuevas).
"""
import json
import unittest
from datetime import datetime
from types import SimpleNamespace

from src.core.link_memory import (
    LEARNED_SCORE_CAP,
    apply_learned_hits,
    find_learned_hits,
    parse_history_rows,
)
from src.core.weight_engine import weights_manager
from src.interfaces.api.routers.purgatory import build_suggestion_context, compute_suggestions
from tests.unit.test_api_purgatory_scoring import CATALOG


def _row(product_id, title, ts=datetime(2026, 9, 14, 10, 0)):
    return (json.dumps({"product_id": product_id, "original_item": {"scraped_name": title}}), ts)


def _item(title):
    return SimpleNamespace(scraped_name=title, ean=None)


class TestLinkMemory(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        weights_manager.refresh()

    def test_parse_ignores_corrupt_and_empty_rows(self):
        rows = [
            ("{not json", datetime(2026, 1, 1)),
            (json.dumps({"product_id": 908}), datetime(2026, 1, 1)),  # sin tÃ­tulo
            (json.dumps({"product_id": "x", "original_item": {"scraped_name": "Skeletor"}}), None),
            _row(908, "Skeletor Origins Wallapop"),
            _row(908, "Skeletor Origins Wallapop", datetime(2026, 9, 20)),
        ]
        entries = parse_history_rows(rows)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].hits, 2)
        self.assertEqual(entries[0].last_linked_at, datetime(2026, 9, 20))

    def test_similar_title_hits_and_different_title_does_not(self):
        entries = parse_history_rows([_row(1249, "Skeletor Origins vendedor madrid")])
        # 4 de 5 tokens en comÃºn -> Jaccard 0.8 (umbral)
        hits = find_learned_hits("Skeletor Origins vendedor madrid barcelona", entries)
        self.assertEqual([h.product_id for h in hits], [1249])
        self.assertEqual(find_learned_hits("He-Man Origins vendedor madrid", entries), [])

    def test_boost_is_capped_and_never_lowers_scores(self):
        entries = parse_history_rows([_row(908, "Skeletor Mattel")])
        hits = find_learned_hits("Skeletor Mattel", entries)
        sugs = [{"product_id": 908, "name": "Skeletor", "match_score": 100.0, "reason": "EAN Match"},
                {"product_id": 943, "name": "Skeletor (200x)", "match_score": 90.0, "reason": "x"}]
        out = apply_learned_hits(sugs, hits, {}, None)
        self.assertEqual(out[0]["match_score"], 100.0)  # no baja una coincidencia exacta
        self.assertTrue(out[0]["is_learned"])
        self.assertIn("Lo vinculaste el 14/09", out[0]["reason"])

        hits = find_learned_hits("Skeletor Mattel", parse_history_rows([_row(943, "Skeletor Mattel")]))
        out = apply_learned_hits(sugs, hits, {}, None)
        learned = next(s for s in out if s["product_id"] == 943)
        self.assertEqual(learned["match_score"], LEARNED_SCORE_CAP)

    def test_learned_boost_reorders_close_candidates(self):
        from src.interfaces.api.routers.purgatory import _suggestion_sort_key

        sugs = [{"product_id": 1, "name": "A", "match_score": 80.0, "reason": "x"},
                {"product_id": 2, "name": "B", "match_score": 70.0, "reason": "x"}]
        hits = find_learned_hits("Skeletor wallapop madrid", parse_history_rows([_row(2, "Skeletor wallapop madrid")]))
        self.assertEqual(len(hits), 1)
        out = sorted(apply_learned_hits(sugs, hits, {}, None), key=_suggestion_sort_key)
        self.assertEqual(out[0]["product_id"], 2)
        self.assertEqual(out[0]["match_score"], 85.0)

    def test_learned_sculpt_is_flagged_but_never_preselected_over_exact_base(self):
        # Vinculaste antes este anuncio al Vintage Sculpt: aparece marcado como aprendido,
        # pero no supera a una coincidencia exacta (mÃ¡x. 99) -> nunca vincula ni preselecciona solo
        learned = parse_history_rows([_row(1249, "Skeletor figura Mattel caja")])
        ctx = build_suggestion_context(CATALOG, learned_links=learned)
        sugs = compute_suggestions(_item("Skeletor figura Mattel caja"), ctx)
        self.assertEqual(sugs[0]["product_id"], 908)
        sculpt = next(s for s in sugs if s["product_id"] == 1249)
        self.assertTrue(sculpt["is_learned"])
        self.assertLessEqual(sculpt["match_score"], LEARNED_SCORE_CAP)
        plain = compute_suggestions(_item("Skeletor figura Mattel caja"), ctx, use_memory=False)
        self.assertFalse(any(s.get("is_learned") for s in plain))

    def test_learned_product_missing_from_candidates_is_added(self):
        learned = parse_history_rows([_row(1135, "Figura rara lote mutante verde")])
        ctx = build_suggestion_context(CATALOG, learned_links=learned)
        sugs = compute_suggestions(_item("Figura rara lote mutante verde"), ctx)
        self.assertIn(1135, [s["product_id"] for s in sugs])
        self.assertTrue(next(s for s in sugs if s["product_id"] == 1135)["is_learned"])


if __name__ == "__main__":
    unittest.main()
