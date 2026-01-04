import re
import unicodedata

def normalize(text):
    if not text: return set()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', ' ', text)
    tokens = set(text.split())
    
    # Current synonyms in the app
    synonyms = {"tmnt": "turtles", "motu": "masters", "universe": "masters", "origenes": "origins", "masters": "masters"}
    normalized = set()
    for t in tokens:
        normalized.add(synonyms.get(t, t))
    
    stop_words = {"figura", "articulada", "cms", "cm", "frikiverso", "de", "the", "of"}
    series_tokens = {"origins", "masters", "turtles", "grayskull", "motu", "tmnt"}
    
    significant = (normalized - stop_words) | (normalized & series_tokens)
    return {t for t in significant if len(t) > 1 or t.isdigit()}

def calculate(name1, name2):
    t1 = normalize(name1)
    t2 = normalize(name2)
    common = t1.intersection(t2)
    union = t1.union(t2)
    
    weights = {}
    series_specific = {"origins", "turtles", "grayskull"}
    identity_tokens = {"skeletor", "teela"}
    
    for t in union:
        if t in series_specific: weights[t] = 10.0
        elif t in identity_tokens: weights[t] = 5.0
        else: weights[t] = 1.0
        
    w_common = sum(weights.get(t, 1.0) for t in common)
    w_union = sum(weights.get(t, 1.0) for t in union)
    
    score = w_common / w_union if w_union > 0 else 0.0
    return t1, t2, common, score

# Case 1: Skeletor
n1 = "Skeletor Origins"
n2 = "Figura Skeletor Master of the Univers Origins Articulada 15 cms - Frikiverso"
t1, t2, common, score = calculate(n1, n2)
print(f"CASE SKELETOR:")
print(f"  DB Tokens: {t1}")
print(f"  SCR Tokens: {t2}")
print(f"  Common: {common}")
print(f"  Score: {score:.4f}")

# Case 2: Teela
n1 = "Teela (Turtles of Grayskull)"
n2 = "Figura Teela MOTU X TMNT Turtles Of Grayskull Masters Of The Universe Teenage Mutant Ninja Turtles Articulada 14 cms - Frikiverso"
t1, t2, common, score = calculate(n1, n2)
print(f"\nCASE TEELA:")
print(f"  DB Tokens: {t1}")
print(f"  SCR Tokens: {t2}")
print(f"  Common: {common}")
print(f"  Score: {score:.4f}")
