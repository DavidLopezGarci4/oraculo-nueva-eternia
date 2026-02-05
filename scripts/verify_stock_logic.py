import os
import sys
import asyncio
import logging

# Bootstrap path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bs4 import BeautifulSoup
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyStock")

async def test_action_toys():
    scraper = ActionToysScraper()
    # Mocking a list item from the user's snippet (Pre-pedido)
    html_prepedido = """
    <li class="product">
        <a href="https://example.com/mer-man" class="woocommerce-LoopProduct-link">
            <h2 class="woocommerce-loop-product__title">Mer-Man Cartoon</h2>
        </a>
        <span class="price"><bdi>21,99€</bdi></span>
        <a href="#" class="button product_type_simple add_to_cart_button porto-pre-order">Pre-Pedido</a>
    </li>
    """
    soup = BeautifulSoup(html_prepedido, 'html.parser')
    item = soup.select_one('li.product')
    offer = scraper._parse_html_item(item)
    
    logger.info(f"ActionToys Pre-Order: {offer.product_name} - Available: {offer.is_available} (Expected: False)")
    assert offer.is_available is False

    # Mocking an out of stock item
    html_oos = """
    <li class="product">
        <h2 class="woocommerce-loop-product__title">Skeletor</h2>
        <span class="price"><bdi>19,99€</bdi></span>
        <span class="out-of-stock-badge">Agotado</span>
        <a href="#" class="button product_type_simple add_to_cart_button">Leer más</a>
    </li>
    """
    soup = BeautifulSoup(html_oos, 'html.parser')
    item = soup.select_one('li.product')
    offer = scraper._parse_html_item(item)
    logger.info(f"ActionToys OOS: {offer.product_name} - Available: {offer.is_available} (Expected: False)")
    assert offer.is_available is False

async def test_time4actiontoys():
    scraper = Time4ActionToysDEScraper()
    # Mocking a pre-order from Wave 29
    html_preorder = """
    <div class="product-box">
        <a href="https://example.com/wave29" class="product-title">Wave 29 Box</a>
        <span class="price">67,97 €</span>
        <div class="product-info">Dieses Produkt erscheint am 15. März 2026</div>
    </div>
    """
    soup = BeautifulSoup(html_preorder, 'html.parser')
    item = soup.select_one('.product-box')
    offer = scraper._parse_item(item)
    logger.info(f"Time4ActionToys Pre-Order: {offer.product_name} - Available: {offer.is_available} (Expected: False)")
    assert offer.is_available is False

    # Mocking an available item
    html_avl = """
    <div class="product-box">
        <a href="https://example.com/he-man" class="product-title">He-Man</a>
        <span class="price">19,99 €</span>
        <button class="buy-btn">In den Warenkorb</button>
    </div>
    """
    soup = BeautifulSoup(html_avl, 'html.parser')
    item = soup.select_one('.product-box')
    offer = scraper._parse_item(item)
    logger.info(f"Time4ActionToys Available: {offer.product_name} - Available: {offer.is_available} (Expected: True)")
    assert offer.is_available is True

async def main():
    logger.info("Starting Stock Logic Verification...")
    await test_action_toys()
    await test_time4actiontoys()
    logger.info("Verification Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
