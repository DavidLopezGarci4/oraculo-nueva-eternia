
from src.core.brain_engine import PythonBrainEngine

engine = PythonBrainEngine()

scraped_name = "Figura Panthor Master del Universo Origins Articulada 18 cms - Frikiverso"
db_name = "Roboto (Origins)"

is_match, score, reason = engine.calculate_match(db_name, scraped_name)

print(f"Scraped: {scraped_name}")
print(f"DB: {db_name}")
print(f"Is Match: {is_match}")
print(f"Score: {score:.4f}")
print(f"Reason: {reason}")

tokens_db = engine.normalize(db_name)
tokens_scraped = engine.normalize(scraped_name)

print(f"Tokens DB: {tokens_db}")
print(f"Tokens Scraped: {tokens_scraped}")

# Check weights
weights = {}
for t in tokens_db | tokens_scraped:
    if t in engine.series_specific: weights[t] = 10.0
    elif t in engine.identity_tokens: weights[t] = 5.0
    elif t in engine.series_generic: weights[t] = 1.0
    else: weights[t] = 1.0

print(f"Weights: {weights}")
