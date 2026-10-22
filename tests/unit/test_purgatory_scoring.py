"""
Tests de precisión del matching del Purgatorio con un catálogo ficticio controlado.
No dependen de la base de datos: los pesos IDF se calculan con refresh_from_products().
"""
import unittest
from types import SimpleNamespace

from src.core.brain_engine import engine
from src.core.text_normalization import tokenize, split_catalog_name
from src.core.weight_engine import weights_manager
from src.interfaces.api.routers.purgatory import build_suggestion_context, compute_suggestions


def _p(pid, name, sub="Origins", vintage=False):
    return SimpleNamespace(
        id=pid, name=name, sub_category=sub, is_vintage=vintage, ean=None,
        figure_id=f"F{pid}", release_year=2021, variant_name=None,
    )


CATALOG = [
    _p(906, "He-Man"),
    _p(908, "Skeletor"),
    _p(922, "He-Man (Vintage Sculpt)"),
    _p(1249, "Skeletor (Vintage Sculpt)"),
    _p(940, "He-Man (200x)"),
    _p(943, "Skeletor (200x)"),
    _p(968, "He-Man (Cartoon Collection)"),
    _p(977, "Skeletor (Cartoon Collection)"),
    _p(1026, "He-Man - Battle Armor (Deluxe)", "Origins Deluxe"),
    _p(1030, "Skeletor - Battle Armor (Deluxe)", "Origins Deluxe"),
    _p(1034, "Terror Claw Skeletor (Deluxe)", "Origins Deluxe"),
    _p(1039, "Thunder Punch He-Man (Deluxe)", "Origins Deluxe"),
    _p(951, "Snake Armor He-Man"),
    _p(955, "Snake Armor Skeletor"),
    _p(1164, "He-Man", "Thundercats Crossover"),
    _p(1142, "Skeletor", "Turtles of Grayskull"),
    _p(1135, "Mutated He-Man", "Turtles of Grayskull"),
    _p(1150, "Donatello (v2)", "Turtles of Grayskull"),
    _p(1151, "Leonardo", "Turtles of Grayskull"),
    _p(1152, "Shredder", "Turtles of Grayskull"),
    _p(1165, "Cheetara", "Thundercats Crossover"),
    _p(1166, "Lion-O", "Thundercats Crossover"),
    _p(960, "Man-At-Arms"),
    _p(961, "Man-At-Arms (Cartoon Collection)"),
    _p(962, "Beast Man"),
    _p(963, "Teela"),
    _p(964, "Evil-Lyn"),
    _p(965, "Trap Jaw"),
    _p(966, "Mer-Man"),
    _p(967, "Stratos"),
    _p(969, "Zodac (200x - Cartoon Collection)"),
    _p(970, "The Collector (Cartoon Collection)"),
    _p(971, "Panthor (Flocked)", "Beasts, Vehicles and Playsets"),
    _p(972, "Battle Cat", "Beasts, Vehicles and Playsets"),
    _p(973, "Castle Grayskull", "Beasts, Vehicles and Playsets"),
    _p(974, "She-Ra"),
    _p(975, "Hordak"),
    _p(976, "Ram Man"),
    _p(1252, "He-Man", "Masters of the Universe Vintage", vintage=True),
    _p(1255, "Skeletor", "Masters of the Universe Vintage", vintage=True),
    _p(1274, "Battle Armor He-Man", "Masters of the Universe Vintage", vintage=True),
    _p(1279, "He-Man (The Original)", "Masters of the Universe Vintage", vintage=True),
]


def _item(title):
    return SimpleNamespace(scraped_name=title, ean=None)


class TestPurgatoryScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = build_suggestion_context(CATALOG)

    @classmethod
    def tearDownClass(cls):
        weights_manager.refresh()  # restaurar pesos del arranque para otros tests

    def _top(self, title, include_vintage=False):
        sugs = compute_suggestions(_item(title), self.ctx)
        return [s for s in sugs if include_vintage or not s.get("is_vintage")]

    # --- Normalización ---
    def test_he_man_spellings_are_equivalent(self):
        self.assertEqual(tokenize("He-Man figura"), tokenize("heman"))
        self.assertEqual(tokenize("He Man Mattel"), {"heman"})
        r1 = [(s["product_id"], s["match_score"]) for s in self._top("He-Man Origins Mattel")]
        r2 = [(s["product_id"], s["match_score"]) for s in self._top("heman origins mattel")]
        r3 = [(s["product_id"], s["match_score"]) for s in self._top("he man origins mattel")]
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)
        self.assertEqual(r1[0][0], 906)

    def test_multilingual_titles(self):
        top = self._top("Maitres de l'univers Skeletor figurine neuf")
        self.assertEqual(top[0]["product_id"], 908)
        self.assertEqual(top[0]["match_score"], 100.0)
        castle = self._top("Castillo Grayskull Masters del Universo")
        self.assertEqual(castle[0]["product_id"], 973)

    def test_catalog_qualifiers_are_split(self):
        core, quals = split_catalog_name("Skeletor (Vintage Sculpt)")
        self.assertEqual(core, {"skeletor"})
        self.assertEqual(quals, {"vintage", "sculpt"})

    # --- Variantes ---
    def test_battle_armor_variant_beats_base_figure(self):
        top = self._top("Figura Masters of the Universe Battle Armor He-Man")
        self.assertEqual(top[0]["product_id"], 1026)
        base = next(s for s in top if s["product_id"] == 906)
        self.assertLess(base["match_score"], top[0]["match_score"])

    def test_terror_claws_variant_beats_base_figure(self):
        top = self._top("Skeletor Terror Claws Origins")
        self.assertEqual(top[0]["product_id"], 1034)

    def test_line_in_title_prefers_that_line(self):
        top = self._top("Skeletor Turtles of Grayskull Mattel")
        self.assertEqual(top[0]["product_id"], 1142)
        top = self._top("He-Man Thundercats Masters of the Universe")
        self.assertEqual(top[0]["product_id"], 1164)

    def test_parenthetical_qualifier_does_not_veto(self):
        _, score, reason = engine.calculate_match("Skeletor (Vintage Sculpt)", "Skeletor figura Mattel")
        self.assertGreater(score, 0.30, reason)
        _, base, _ = engine.calculate_match("Skeletor", "Skeletor figura Mattel")
        self.assertGreater(base, score)
        top = self._top("Panthor Masters of the Universe Origins")
        self.assertEqual(top[0]["product_id"], 971)

    def test_core_identity_tokens_still_veto(self):
        _, score, reason = engine.calculate_match("Terror Claw Skeletor (Deluxe)", "Skeletor figura")
        self.assertEqual(score, 0.0)
        self.assertIn("Identity Conflict", reason)

    def test_the_collector_is_not_a_wildcard_for_cartoon_collection(self):
        top = self._top("Masters of the Universe Origins Cartoon Collection Zodac")
        self.assertEqual(top[0]["product_id"], 969)

    # --- Correcciones del verificador independiente ---
    def test_the_original_is_not_collapsed_into_base_name(self):
        self.assertEqual(tokenize("He-Man (The Original)") - {"heman"}, {"theoriginal"})
        _, score_orig, _ = engine.calculate_match("He-Man (The Original)", "He-Man The Original Mattel")
        _, score_base, _ = engine.calculate_match("He-Man", "He-Man The Original Mattel")
        self.assertGreater(score_orig, score_base)

    def test_years_and_numbers_do_not_count_as_variants(self):
        _, with_year, reason = engine.calculate_match("Skeletor", "Skeletor 1982 Mattel 3")
        self.assertEqual(with_year, 1.0, reason)

    def test_context_tokens_are_compared_fuzzily(self):
        # "Exclusive" (singular) en el anuncio no penaliza a un candidato de "Origins Exclusives"
        _, s1, r1 = engine.calculate_match("Stratos", "Stratos Exclusive", db_context="Origins Exclusives")
        _, s2, _ = engine.calculate_match("Stratos", "Stratos Exclusives", db_context="Origins Exclusives")
        self.assertEqual(s1, s2, r1)

    def test_ean_keys_ignore_formatting_and_leading_zeros(self):
        from src.interfaces.api.routers.purgatory import _ean_key
        self.assertEqual(_ean_key("0887961-123456"), _ean_key("887961123456"))
        self.assertEqual(_ean_key(None), "")

    def test_smartmatcher_strict_mode_keeps_qualifier_veto(self):
        _, score, reason = engine.calculate_match(
            "Skeletor (Vintage Sculpt)", "Skeletor figura", soft_qualifiers=False, penalize_extra=False
        )
        self.assertEqual(score, 0.0, reason)

    # --- Desempate ---
    def test_deterministic_tie_break_prefers_modern_main_origins_line(self):
        top = self._top("He-Man Mattel", include_vintage=True)
        ids = [s["product_id"] for s in top]
        self.assertEqual(ids[0], 906)
        self.assertLess(ids.index(906), ids.index(1164))
        if 1252 in ids:
            self.assertLess(ids.index(1164), ids.index(1252))


if __name__ == "__main__":
    unittest.main()
