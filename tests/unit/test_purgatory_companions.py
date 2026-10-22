"""
Tests del acompañante Vintage Sculpt (figuras Origins, NO vintage) en las predicciones del Purgatorio.
"""
import unittest
from types import SimpleNamespace

from src.core.weight_engine import weights_manager
from src.interfaces.api.routers.purgatory import build_suggestion_context, compute_suggestions
from tests.unit.test_purgatory_scoring import CATALOG

HE_MAN_ORIGINS, SKELETOR_ORIGINS = 906, 908
HE_MAN_SCULPT, SKELETOR_SCULPT = 922, 1249
HE_MAN_THUNDERCATS, SKELETOR_TOG = 1164, 1142


def _item(title):
    return SimpleNamespace(scraped_name=title, ean=None)


class TestVintageSculptCompanions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = build_suggestion_context(CATALOG)

    @classmethod
    def tearDownClass(cls):
        weights_manager.refresh()

    def _sugs(self, title, ctx=None):
        return compute_suggestions(_item(title), ctx or self.ctx)

    def _ids(self, sugs):
        return [s["product_id"] for s in sugs]

    def test_plain_skeletor_gets_sculpt_right_after_base(self):
        sugs = self._sugs("Skeletor figura Mattel")
        ids = self._ids(sugs)
        self.assertEqual(ids[0], SKELETOR_ORIGINS)
        self.assertEqual(ids[1], SKELETOR_SCULPT)
        companion = sugs[1]
        self.assertTrue(companion["is_companion"])
        self.assertFalse(companion["is_vintage"])
        self.assertEqual(companion["match_score"], sugs[0]["match_score"] - 1.0)
        self.assertEqual(ids.count(SKELETOR_SCULPT), 1)

    def test_plain_he_man_gets_sculpt_right_after_base(self):
        ids = self._ids(self._sugs("He-Man Origins Masters del Universo"))
        self.assertEqual(ids[:2], [HE_MAN_ORIGINS, HE_MAN_SCULPT])

    def test_other_lines_do_not_trigger_companion(self):
        sugs = self._sugs("He-Man Thundercats Masters of the Universe")
        self.assertEqual(sugs[0]["product_id"], HE_MAN_THUNDERCATS)
        self.assertFalse(any(s.get("is_companion") for s in sugs))

        sugs = self._sugs("Skeletor Turtles of Grayskull")
        self.assertEqual(sugs[0]["product_id"], SKELETOR_TOG)
        self.assertFalse(any(s.get("is_companion") for s in sugs))

    def test_companion_only_follows_main_origins_base(self):
        sugs = self._sugs("Skeletor Mattel")
        ids = self._ids(sugs)
        self.assertIn(SKELETOR_TOG, ids)
        companions = [s for s in sugs if s.get("is_companion")]
        self.assertEqual(len(companions), 1)
        self.assertEqual(ids[ids.index(SKELETOR_SCULPT) - 1], SKELETOR_ORIGINS)

    def test_variant_listings_do_not_get_companion(self):
        for title in ("Figura Battle Armor He-Man Origins", "Skeletor Terror Claws Origins", "Snake Armor Skeletor"):
            sugs = self._sugs(title)
            self.assertFalse(any(s.get("is_companion") for s in sugs), title)

    def test_sculpt_listing_keeps_sculpt_first(self):
        sugs = self._sugs("Skeletor Vintage Sculpt Origins Mattel")
        ids = self._ids(sugs)
        self.assertEqual(ids[0], SKELETOR_SCULPT)
        self.assertEqual(ids.count(SKELETOR_SCULPT), 1)

    def test_vintage_suggestions_never_take_modern_slots(self):
        sugs = self._sugs("He-Man Mattel")
        flags = [bool(s.get("is_vintage")) for s in sugs]
        self.assertEqual(flags, sorted(flags))  # todas las modernas antes que las vintage
        modern = [s for s in sugs if not s.get("is_vintage") and not s.get("is_companion")]
        self.assertLessEqual(len(modern), 5)
        self.assertIn(1252, self._ids(sugs))  # la vintage sigue disponible para el modal vintage

    def test_missing_companion_in_catalog_is_harmless(self):
        catalog = [p for p in CATALOG if p.id != SKELETOR_SCULPT]
        ctx = build_suggestion_context(catalog)
        try:
            sugs = self._sugs("Skeletor figura", ctx)
            self.assertEqual(sugs[0]["product_id"], SKELETOR_ORIGINS)
            self.assertFalse(any(s.get("is_companion") for s in sugs))
        finally:
            build_suggestion_context(CATALOG)


if __name__ == "__main__":
    unittest.main()
