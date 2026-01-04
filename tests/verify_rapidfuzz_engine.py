from src.core.rust_bridge import kernel
from loguru import logger

# Desactivar logs ruidosos para el test
logger.remove()
logger.add(lambda msg: print(msg), level="INFO")

test_cases = [
    {
        "db": "Skeletor Origins",
        "scr": "Figura Skeletor Master of the Univers Origins Articulada 15 cms - Frikiverso (10.0€)",
        "url": "https://frikiverso.es/skeletor-origins"
    },
    {
        "db": "Teela (Turtles of Grayskull)",
        "scr": "Figura Teela MOTU X TMNT Turtles Of Grayskull Masters Of The Universe Teenage Mutant Ninja Turtles Articulada 14 cms - Frikiverso (6.88€)",
        "url": "https://frikiverso.es/teela-turtles"
    }
]

print(f"{'DB NAME':<25} | {'IS MATCH':<10} | {'SCORE':<10} | {'REASON'}")
print("-" * 80)

for case in test_cases:
    is_match, score, reason = kernel.match_items(case["db"], case["scr"])
    print(f"{case['db'][:25]:<25} | {str(is_match):<10} | {score:<10.4f} | {reason}")
