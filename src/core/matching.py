import re
import unicodedata
from typing import Set, Tuple, List
from urllib.parse import urlparse
from src.domain.schemas import ProductSchema
from src.core.rust_bridge import kernel

class SmartMatcher:
    def __init__(self):
        self.stop_words = {
            "mattel", "figure", "figura", "action", "toy", "juguete", "cm", "inch",
            "wave", "deluxe", "collection", "collector", "edicion", "edition",
            "new", "nuevo", "caja", "box", "original", "authentic",
            "super7", "reaction", "pop", "funko", "vinyl", "of", "the", "del", "de", "y", "and",
            "comprar", "venta", "oferta", "precio", "barato", "envio", "gratis"
        }
        
        # Specific series lines (High weight: 10.0)
        self.series_specific = {
            "origins", "masterverse", "cgi", "netflix", "filmation", "200x", "vintage", "commemorative",
            "turtles", "grayskull", "stranger", "things", "cartoon", "collection", "sun", "man", "rulers", "sunman",
            "engineering", "art", "classics", "revelation", "revolution", "mondo", "super7"
        }
        # Generic branding (Low weight: 1.0) - these are often in both and don't help differentiate
        self.series_generic = {"tmnt", "motu", "masters", "universe", "universo"}
        
        self.series_tokens = self.series_specific | self.series_generic
        
        # High Weight Tokens: If these don't match or are present in one but not the other, 
        # the overall score should drop significantly or fail.
        self.identity_tokens = {
            "skeletor", "teela", "heman", "manatarms", "beastman", "trapjaw", "evillyn", "fisto", "ramman",
            "orko", "stratos", "merman", "jitsu", "triklops", "hordak", "she-ra", "man-at-arms", "he-man",
            "sorceress", "faker", "mossman", "clawful", "whiplash", "stinkor", "spikor", "scareglow",
            "snake", "shredder", "splinter", "krang", "donatello", "leonardo", "michelangelo", "raphael"
        }

    def normalize(self, text: str) -> Set[str]:
        """
        Converts text to improved set of significant tokens.
        """
        if not text:
            return set()
            
        # URL Handling: extract slug
        if text.startswith("http"):
            try:
                path = urlparse(text).path
                # Keep significant parts of URL? often they contain the clean name
                text = path.split('/')[-1] # usage of last segment is usually better
                text = text.replace("-", " ").replace("_", " ").replace(".html", "")
            except:
                pass
        
        # Standardize
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower()
        text = re.sub(r'[^a-z0-9]', ' ', text)
        
        tokens = set(text.split())
        
        # --- SYNONYM NORMALIZATION ---
        synonyms = {
            "tmnt": "turtles",
            "motu": "masters",
            "masters": "masters",
            "universe": "masters",
            "universo": "masters",
            "origenes": "origins"
        }
        
        normalized_tokens = set()
        for t in tokens:
            normalized_tokens.add(synonyms.get(t, t))

        # Core Logic: Keep all tokens that are either NOT stop words OR ARE series tokens
        significant = (normalized_tokens - self.stop_words) | (normalized_tokens & self.series_tokens)
        return {t for t in significant if len(t) > 1 or t.isdigit()}

    def match(self, product_name: str, scraped_title: str, scraped_url: str, db_ean: str = None, scraped_ean: str = None) -> Tuple[bool, float, str]:
        """
        Returns (IsMatch, Score, Reason)
        Priority 1: EAN/GTIN Match (Universal Fingerprint - Optional)
        Priority 2: Semantic Score (Jaccard - Fallback Default)
        
        NOTE: EAN is a trust multiplier, NOT a gatekeeper. If EAN is missing or invalid, 
        the system MUST proceed to semantic fallback.
        """
        # --- PHASE 3: RUST KERNEL ACCELERATION ---
        is_match, score = kernel.match_items(product_name, scraped_title, db_ean, scraped_ean)
        if is_match is not None:
            reason = "Rust Kernel Match" if is_match else "Rust Kernel Mismatch"
            return is_match, score, f"3OX.Engine :: {reason} (Score: {score:.4f})"

        # --- EAN MATCH (PHASE 10 & 19: PRECISION) ---
        if db_ean and scraped_ean:
            # Clean both EANs (remove spaces/dashes)
            clean_db = re.sub(r'[^0-9]', '', str(db_ean))
            clean_scraped = re.sub(r'[^0-9]', '', str(scraped_ean))
            
            # EAN-13 Validation (Phase 19)
            is_valid_ean = lambda x: len(x) == 13 and x.isdigit()
            
            if is_valid_ean(clean_db) and is_valid_ean(clean_scraped):
                if clean_db == clean_scraped:
                    return True, 1.0, f"Perfect EAN-13 Match: {db_ean}"
                else:
                    return False, 0.0, f"EAN-13 Mismatch: {db_ean} vs {scraped_ean}"
            elif clean_db == clean_scraped and len(clean_db) >= 8: # Fallback for shorter codes
                return True, 1.0, f"Perfect GTIN Match: {db_ean}"
            
            # If EANs are invalid or mismatching formats, we DON'T return False yet.
            # We let the Semantic Fallback decide to avoid blocking items with "dirty" EAN data.

        # --- SEMANTIC FALLBACK ---
        # 1. DB Tokens (The Truth)
        db_tokens = self.normalize(product_name)
        if not db_tokens:
            return False, 0.0, "Empty DB Name"

        # 2. Scraped Tokens (Merge Title + URL)
        title_tokens = self.normalize(scraped_title)
        url_tokens = self.normalize(scraped_url)
        scraped_tokens = title_tokens | url_tokens
        
        if not scraped_tokens:
            return False, 0.0, "Empty Scraped Data"
        
        # 3. Intersection Logic
        common = db_tokens.intersection(scraped_tokens)
        missing_from_db = db_tokens - common
        extra_in_scraped = scraped_tokens - db_tokens

        # Rule 1: Recall (Must match all significant DB tokens)
        if len(missing_from_db) > 0:
            return False, 0.0, f"Missing DB tokens: {missing_from_db}"

        # Rule 2: Precision (Jaccard Index)
        # --- PHASE 20: STRATEGIC WEIGHTED SCORING ---
        # Series tokens are now the TOP PRIORITY (x10), Identity (x5), others (x1)
        weights = {}
        all_unique_tokens = db_tokens | scraped_tokens
        for t in all_unique_tokens:
            if t in self.series_specific: weights[t] = 10.0
            elif t in self.identity_tokens: weights[t] = 5.0
            elif t in self.series_generic: weights[t] = 1.0
            else: weights[t] = 1.0
            
        def get_weighted_sum(token_set):
            return sum(weights.get(t, 1.0) for t in token_set)
            
        common_weight = get_weighted_sum(common)
        union_weight = get_weighted_sum(db_tokens | scraped_tokens)
        weighted_score = common_weight / union_weight if union_weight else 0.0
        
        # Rule 3: Series Hard Filter & Tension
        db_series = db_tokens.intersection(self.series_tokens)
        scr_series = scraped_tokens.intersection(self.series_tokens)
        
        # Identity Hard Check: If an identity token is in DB but NOT in Scraped, it's a FAIL.
        db_identity = db_tokens.intersection(self.identity_tokens)
        scr_identity = scraped_tokens.intersection(self.identity_tokens)
        
        if db_identity:
            missing_ids = db_identity - scr_identity
            if missing_ids:
                return False, 0.0, f"Identity Missing: {missing_ids}"
        
        if db_series:
            missing_series = db_series - scr_series
            # Synonyms are already normalized in self.normalize(), 
            # so 'tmnt' is already 'turtles'. No extra logic needed here now.
            if missing_series:
                return False, 0.0, f"Series Missing: {missing_series}"

        # Tension A: Conflict (e.g. Origins vs Masterverse)
        if db_series and scr_series:
            if not db_series.intersection(scr_series):
                return False, 0.0, f"Series Conflict: DB={db_series} vs Scraped={scr_series}"
        
        if weighted_score >= 0.7:
            return True, weighted_score, "Series-Dominant Match"
        else:
            return False, weighted_score, f"Insufficient Weighted Score: {weighted_score:.2f}"
