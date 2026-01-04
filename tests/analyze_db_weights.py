
import math
import re
import unicodedata
from collections import Counter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import ProductModel

# Configuration
DB_URL = "sqlite:///oraculo.db" # Standard path for this project
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

def normalize(text: str) -> set:
    if not text: return set()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', ' ', text)
    tokens = set(text.split())
    # Basic filtering to avoid too much noise but keep series for analysis
    return {t for t in tokens if len(t) > 1 or t.isdigit()}

def analyze_tokens():
    products = session.query(ProductModel).all()
    total_docs = len(products)
    print(f"Total Products: {total_docs}")
    
    token_df = Counter()
    for p in products:
        # We combine Name and SubCategory as they define the "Identity" in this system
        combined_name = f"{p.name} {p.sub_category or ''}"
        tokens = normalize(combined_name)
        for t in tokens:
            token_df[t] += 1
            
    # Calculate Weights (pseudo-IDF)
    # Range: 1.0 (very common) to 10.0 (very rare)
    weights = {}
    for t, count in token_df.items():
        # IDF formula: log(N/df)
        # We scale it to our target range [1, 10]
        idf = math.log10(total_docs / count) if count > 0 else 0
        # Simple scaling: if idf is 0 (all docs), weight=1. If idf is max, weight=10.
        # Max IDF is log10(N)
        max_idf = math.log10(total_docs) if total_docs > 0 else 1
        scale = 9 * (idf / max_idf) if max_idf > 0 else 0
        weights[t] = 1.0 + scale

    # Sort and print Top & Bottom
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    print("\n--- RAREST TOKENS (Identity Candidates) ---")
    for t, w in sorted_weights[:20]:
        print(f"{t}: {w:.2f} (df={token_df[t]})")
        
    print("\n--- MOST COMMON TOKENS (Series/Generic Candidates) ---")
    for t, w in sorted_weights[-20:]:
        print(f"{t}: {w:.2f} (df={token_df[t]})")

    return weights

if __name__ == "__main__":
    analyze_tokens()
    session.close()
