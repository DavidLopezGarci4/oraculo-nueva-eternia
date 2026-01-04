import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.matching import SmartMatcher
from src.infrastructure.database import SessionLocal
from src.domain.models import ProductModel, PendingMatchModel

def analyze_purgatory():
    matcher = SmartMatcher()
    db = SessionLocal()
    
    pending_items = db.query(PendingMatchModel).all()
    all_products = db.query(ProductModel).all()
    
    print(f"--- ANALISIS DE PURGATORIO ({len(pending_items)} items) ---")
    
    for item in pending_items:
        print(f"\nITEM: {item.scraped_name}")
        print(f"URL: {item.url}")
        
        matches_found = []
        for p in all_products:
            db_search_name = f"{p.name} {p.sub_category or ''}"
            is_match, score, reason = matcher.match(db_search_name, item.scraped_name, item.url)
            
            if is_match or score > 0.3:
                matches_found.append((p.name, p.sub_category, is_match, score, reason))
        
        # Sort by score descending
        matches_found.sort(key=lambda x: x[3], reverse=True)
        
        if not matches_found:
            print("  [!] NO SE ENCONTRO NINGUNA SUGERENCIA (> 0.3)")
            # Try to find the closest one manually to see tokens
            # ... (rest of debug logic)
        else:
            print(f"  TOP SUGGESTIONS:")
            for name, sub, valid, score, reason in matches_found[:3]:
                status = "OK" if valid else "BLOQUEADO"
                print(f"    - {status} | Score: {score:.2f} | {name} ({sub}) | Reason: {reason}")

    db.close()

if __name__ == "__main__":
    analyze_purgatory()
