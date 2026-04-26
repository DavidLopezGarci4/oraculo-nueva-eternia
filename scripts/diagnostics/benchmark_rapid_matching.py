
import time
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from src.core.matching import SmartMatcher
from loguru import logger

# Disable trace logs for clean output
logger.remove()
logger.add(sys.stderr, level="INFO")

def benchmark_v3():
    matcher = SmartMatcher()
    
    test_cases = [
        {
            "name": "Skeletor (Perfect Match)",
            "db": "Skeletor (Origins)",
            "scraped": "Figura Skeletor Master of the Univers Origins Articulada 15 cms - Frikiverso",
            "url": "https://frikiverso.com/skeletor-origins",
            "expected": True
        },
        {
            "name": "Teela (Identity Match)",
            "db": "Teela (Masters of the Universe: Origins)",
            "scraped": "Figura Teela Masters of the Universe Origins Articulada 14 cms - Frikiverso",
            "url": "https://frikiverso.com/teela-origins",
            "expected": True
        },
        {
            "name": "Panthor vs Roboto (Series Conflict)",
            "db": "Roboto (Origins)",
            "scraped": "Figura Panthor Master del Universo Origins Articulada 18 cms - Frikiverso",
            "url": "https://frikiverso.com/panthor-origins",
            "expected": False
        },
        {
            "name": "Land Shark vs Roboto (Type Conflict)",
            "db": "Roboto (Origins)",
            "scraped": "Figura Vehículo Tanque Tiburón Masters del Universo Origins - Frikiverso",
            "url": "https://frikiverso.com/tanque-tiburon-origins",
            "expected": False
        },
        {
            "name": "Identity Mismatch (Beast Man vs Skeletor)",
            "db": "Beast Man (Origins)",
            "scraped": "Figura Skeletor Master of the Univers Origins Articulada 15 cms - Frikiverso",
            "url": "https://frikiverso.com/skeletor-origins",
            "expected": False
        }
    ]

    print("\n" + "="*120)
    print(f"{'TEST CASE':<45} | {'RESULT':<10} | {'SCORE':<10} | {'REASON'}")
    print("="*120)
    
    total_passed = 0
    start_time = time.time()
    
    for case in test_cases:
        is_match, score, reason = matcher.match(case["db"], case["scraped"], case["url"])
        passed = is_match == case["expected"]
        if passed: total_passed += 1
        
        status = "PASSED" if passed else "FAILED"
        print(f"{case['name']:<45} | {status:<10} | {score:10.4f} | {reason}")

    duration = time.time() - start_time
    print("="*120)
    print(f"Summary: {total_passed}/{len(test_cases)} cases passed in {duration:.4f}s")
    print("="*120 + "\n")

    if total_passed == len(test_cases):
        print("Final Verdict: System is high-precision and stable.")
    else:
        print("Final Verdict: Improvements needed.")

if __name__ == "__main__":
    benchmark_v3()
