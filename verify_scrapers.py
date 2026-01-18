import sys
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper
from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
from src.infrastructure.scrapers.motuclassics_de_scraper import MotuClassicsDEScraper
from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
from src.infrastructure.scrapers.vendiloshop_scraper import VendiloshopITScraper

scrapers = [
    ActionToysScraper, BigBadToyStoreScraper, DeToyboysNLScraper, ElectropolisScraper,
    FantasiaScraper, FrikiversoScraper, MotuClassicsDEScraper,
    PixelatoyScraper, Time4ActionToysDEScraper, ToymiEUScraper,
    VendiloshopITScraper
]

for s_class in scrapers:
    try:
        instance = s_class()
        print(f"[OK] {s_class.__name__} instantiated successfully.")
    except TypeError as e:
        print(f"[ERROR] {s_class.__name__} FAILED: {e}")
    except Exception as e:
        print(f"[FAIL] {s_class.__name__} error: {e}")
