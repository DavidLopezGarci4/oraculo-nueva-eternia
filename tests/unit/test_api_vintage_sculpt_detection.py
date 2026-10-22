import unittest

from src.core.vintage_utils import check_is_vintage


class TestCheckIsVintageOriginsSculpt(unittest.TestCase):
    def test_vintage_sculpt_origins_titles_are_not_vintage(self):
        self.assertFalse(check_is_vintage("Skeletor Vintage Sculpt Origins"))
        self.assertFalse(check_is_vintage("He-Man vintage-sculpt MOTU Masters of the Universe"))
        self.assertFalse(check_is_vintage("MOTU Origins He-Man (Vintage Sculpt) nuevo"))

    def test_real_vintage_titles_are_still_vintage(self):
        self.assertTrue(check_is_vintage("Skeletor vintage 1982 loose"))
        self.assertTrue(check_is_vintage("He-Man vintage completo"))
        self.assertTrue(check_is_vintage("Skeletor 1983 Mattel"))

    def test_sculpt_phrase_does_not_hide_other_vintage_signals(self):
        self.assertTrue(check_is_vintage("He-Man Vintage Sculpt 1983"))
        self.assertTrue(check_is_vintage("Lote vintage: Skeletor Vintage Sculpt y Beast Man"))

    def test_empty_and_modern_titles(self):
        self.assertFalse(check_is_vintage(""))
        self.assertFalse(check_is_vintage(None))
        self.assertFalse(check_is_vintage("Skeletor Origins Mattel 2020"))


if __name__ == "__main__":
    unittest.main()
