import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.matching import SmartMatcher

def test_precision():
    matcher = SmartMatcher()
    
    # CASE 1: Generic Skeletor vs Specific Skeletor (Art of Engineering)
    # The name in DB has "Art of Engineering"
    db_name = "Skeletor (Art of Engineering)"
    scraped_title = "Figura Skeletor Masters of the Universe Origins Articulada 15 cms"
    
    # In this case, "Origins" vs "Origins Exclusives" (Series Tension)
    # and "Art of Engineering" is missing in Scraped.
    match, score, reason = matcher.match(db_name, scraped_title, "http://frikiverso.com/skeletor-origins")
    print(f"CASE 1 (Skeletor AoE vs Origins): Match={match}, Score={score:.2f}, Reason={reason}")
    
    # CASE 2: Identity Conflict
    db_name_2 = "Teela"
    scraped_title_2 = "Figura Skeletor Origins"
    match2, score2, reason2 = matcher.match(db_name_2, scraped_title_2, "http://frikiverso.com/skeletor")
    print(f"CASE 2 (Teela vs Skeletor): Match={match2}, Score={score2:.2f}, Reason={reason2}")

    # CASE 3: Good Match (Series + Identity)
    db_name_3 = "Teela (Turtles of Grayskull)"
    scraped_title_3 = "Figura Teela MOTU X TMNT Turtles Of Grayskull"
    match3, score3, reason3 = matcher.match(db_name_3, scraped_title_3, "http://frikiverso.com/teela-turtles")
    print(f"CASE 3 (Turtles Match): Match={match3}, Score={score3:.2f}, Reason={reason3}")

if __name__ == "__main__":
    test_precision()
