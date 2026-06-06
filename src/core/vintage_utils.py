import re

def check_is_vintage(text: str) -> bool:
    """
    Checks if the given text indicates a vintage item.
    Returns True if the text contains 'vintage' (case-insensitive)
    or a 4-digit year in the range 1980-1989.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    if "vintage" in text_lower:
        return True
        
    # Match any word boundaries containing a year between 1980 and 1989
    years = re.findall(r"\b(198[0-9])\b", text)
    if years:
        return True
        
    return False


# --- MOTU RELEVANCE & BRAND EXCLUSIONS ---
MOTU_CORE_KEYWORDS = [
    r"motu\b", r"masters?\s+of\s+the\s+universe\b", r"masters?\s+del\s+universo\b", r"maitres?\s+de\s+l\s*univers\b", r"maitres?\s+del\s+universo\b", r"maitres?\s+of\s+the\s+universe\b",
    r"he-man\b", r"heman\b", r"skeletor\b", r"origins\b", r"filmation\b", r"grayskull\b",
    r"snake\s+mountain\b", r"she-ra\b", r"shera\b", r"hordak\b", r"new\s+eternia\b", r"turtles\s+of\s+grayskull\b",
    r"sunman\b", r"sun-man\b", r"wundar\b", r"wun-dar\b", r"eternia\b", r"castle\s+grayskull\b", r"revelation\b",
    r"beast\s*man\b", r"man-at-arms\b", r"man\s+at\s+arms\b", r"teela\b", r"evil-lyn\b", r"evilyn\b",
    r"trap\s*jaw\b", r"mer-man\b", r"merman\b", r"tri-klops\b", r"triklops\b", r"ram\s*man\b",
    r"stratos\b", r"faker\b", r"panthor\b", r"clawful\b", r"kobra\s*khan\b", r"jitsu\b", r"fisto\b",
    r"buzz-off\b", r"buzzoff\b", r"webstor\b", r"whiplash\b", r"sy-klone\b", r"syklone\b", r"moss\s*man\b",
    r"two\s*bad\b", r"spikor\b", r"stinkor\b", r"snout\s*spout\b", r"extendar\b", r"rio\s*blast\b",
    r"rokkon\b", r"stonedar\b", r"dragstor\b", r"horde\s+trooper\b", r"multibot\b", r"modulok\b",
    r"mantenna\b", r"leech\b", r"grizzlor\b", r"scareglow\b", r"scare\s+glow\b", r"blast\s*attak\b",
    r"ninjor\b", r"clamp\s*champ\b", r"saurod\b", r"gwildor\b", r"blade\b", r"king\s+randor\b",
    r"sorceress\b", r"rattlor\b", r"tung\s*lashor\b", r"squeeze\b", r"snake\s*face\b",
    r"he-ro\b", r"hero\b", r"eldor\b", r"tila\b", r"man-e-faces\b", r"manefaces\b", r"mekaneck\b", r"zodac\b", r"zodak\b",
    r"king\s+hssss?\b", r"tytis\b", r"megator\b", r"laser\s+light\b", r"monstroid\b", r"spryor\b",
    r"castaspella\b", r"frosta\b", r"bow\b", r"glimmer\b", r"angella\b", r"netossa\b", r"mermista\b", r"spinnerella\b",
    r"perfuma\b", r"flutterina\b", r"peekablue\b", r"sweet\s+bee\b", r"double\s+trouble\b", r"entrapta\b",
    r"catra\b", r"scorpia\b", r"shadow\s*weaver\b", r"imp\b", r"octavia\b", r"fang\s*man\b",
    r"strong\s*arm\b", r"lizard\s*man\b", r"plundor\b", r"ikelator\b",
    r"attack\s*trak\b", r"battle\s*ram\b", r"wind\s*raider\b", r"zoar\b", r"screeech\b", r"point\s+dread\b", r"talon\s+fighter\b",
    r"fright\s+zone\b", r"land\s*shark\b", r"battle\s*bones\b", r"laser\s*bolt\b", r"rotar\b", r"twistoid\b",
    r"turbodactyl\b", r"bionatops\b", r"tyrantisaurus\b", r"lote\s+motu\b", r"figura\s+motu\b"
]

def validate_motu_relevance(text: str) -> tuple[bool, str]:
    """
    Validates if a given text title is relevant to the Masters of the Universe universe.
    Returns (True, '') if valid.
    Returns (False, 'Reason') if it should be auto-discarded (e.g. Pop, Funko, Big Jim, Masterverse).
    """
    if not text:
        return False, "Texto vacío"
        
    text_lower = text.lower()
    
    # 1. Exclusion List (Hard Blacklist)
    blacklist = {
        "funko": r"funko",
        "pop": r"\bpop\b|\bpops\b",
        "big jim": r"big[\s-]*jim",
        "masterverse": r"masterverse",
        "gi joe": r"gi[\s-]*joe|g\.i\.[\s-]*joe",
        "star wars": r"star\s*wars",
        "action man": r"action\s*man",
        "madelman": r"madelman",
        "geyperman": r"geyperman",
        "max steel": r"max\s*steel",
        "barbie": r"barbie",
        "marvel legends": r"marvel\s*legends?",
        "dc multiverse": r"dc\s*multiverse|dc\s*universe|mcfarlane"
    }
    
    for brand, pattern in blacklist.items():
        if re.search(pattern, text_lower):
            return False, f"Marca excluida detectada: {brand.capitalize()}"
            
    # 2. Inclusion List (MOTU Keywords)
    for pattern in MOTU_CORE_KEYWORDS:
        if re.search(pattern, text_lower):
            return True, ""
            
    return False, "No contiene ninguna palabra clave de Masters of the Universe"

