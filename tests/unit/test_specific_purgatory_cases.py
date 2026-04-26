import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.matching import SmartMatcher

def test_specific_cases():
    matcher = SmartMatcher()
    
    # --- CASE 1: Skeletor Origins (Correct) ---
    # DB: "Skeletor" with sub_category "Origins"
    # Scraped: "Figura Skeletor Master of the Univers Origins Articulada 15 cms"
    db_name_correct = "Skeletor Origins" # As passed by admin.py with sub_category
    scraped_title_1 = "Figura Skeletor Master of the Univers Origins Articulada 15 cms"
    
    is_match_1, score_1, reason_1 = matcher.match(db_name_correct, scraped_title_1, "http://frikiverso.com/skeletor-origins")
    print(f"CASE 1a (Skeletor Origins vs Scraped Origins): Match={is_match_1}, Score={score_1:.2f}, Reason={reason_1}")
    
    # --- CASE 1b: Skeletor Art of Engineering (Should FAIL) ---
    db_name_aoe = "Skeletor (Art of Engineering) Origins Exclusives"
    is_match_1b, score_1b, reason_1b = matcher.match(db_name_aoe, scraped_title_1, "http://frikiverso.com/skeletor-origins")
    print(f"CASE 1b (Skeletor AoE vs Scraped Origins): Match={is_match_1b}, Score={score_1b:.2f}, Reason={reason_1b}")
    
    # --- CASE 2: Teela TMNT (Correct) ---
    # DB: "Teela" with sub_category "Turtles of Grayskull"
    db_name_teela_tmnt = "Teela Turtles of Grayskull"
    scraped_title_2 = "Figura Teela MOTU X TMNT Turtles Of Grayskull Masters Of The Universe Teenage Mutant Ninja Turtles Articulada 14 cms"
    
    is_match_2, score_2, reason_2 = matcher.match(db_name_teela_tmnt, scraped_title_2, "http://frikiverso.com/teela-tmnt")
    print(f"CASE 2a (Teela Turtles vs Scraped TMNT): Match={is_match_2}, Score={score_2:.2f}, Reason={reason_2}")
    
    # --- CASE 2b: Grayskull Ring (Should FAIL because no Teela) ---
    db_name_ring = "Grayskull Ring Masters of the WWE Universe Rin"
    is_match_2b, score_2b, reason_2b = matcher.match(db_name_ring, scraped_title_2, "http://frikiverso.com/teela-tmnt")
    print(f"CASE 2b (Grayskull Ring vs Scraped Teela TMNT): Match={is_match_2b}, Score={score_2b:.2f}, Reason={reason_2b}")

if __name__ == "__main__":
    test_specific_cases()
