/**
 * Oráculo de Eternia - Wallapop Content Script
 * Este script se ejecuta en las páginas de Wallapop y extrae los datos de productos.
 */

// Configuración del servidor del Oráculo
const ORACULO_API = 'http://localhost:8000/api/wallapop/import';

// Selectores de Wallapop (pueden cambiar, actualizar si es necesario)
const SELECTORS = {
    // Contenedor de items en resultados de búsqueda
    itemCard: '[class*="ItemCard"]',
    itemLink: 'a[href*="/item/"]',
    itemTitle: '[class*="ItemCard__title"], [class*="ItemCard__info"]',
    itemPrice: '[class*="ItemCard__price"]',
    itemImage: 'img[class*="ItemCard"]'
};

/**
 * Extrae todos los productos visibles en la página actual.
 */
function extractProducts() {
    const products = [];

    // Buscar todos los enlaces a items
    const itemLinks = document.querySelectorAll(SELECTORS.itemLink);

    itemLinks.forEach(link => {
        try {
            const card = link.closest('[class*="ItemCard"]') || link.parentElement;
            if (!card) return;

            // URL
            const url = link.href;
            if (!url || !url.includes('/item/')) return;

            // Evitar duplicados
            if (products.some(p => p.url === url)) return;

            // Título
            const titleEl = card.querySelector(SELECTORS.itemTitle);
            const title = titleEl ? titleEl.textContent.trim() : 'Producto Wallapop';

            // Precio
            const priceEl = card.querySelector(SELECTORS.itemPrice);
            let price = 0;
            if (priceEl) {
                const priceText = priceEl.textContent.replace(/[^\d,\.]/g, '').replace(',', '.');
                price = parseFloat(priceText) || 0;
            }

            // Imagen
            const imgEl = card.querySelector('img');
            const imageUrl = imgEl ? imgEl.src : null;

            products.push({
                title: title,
                price: price,
                url: url,
                imageUrl: imageUrl
            });

        } catch (e) {
            console.error('[Oráculo] Error extrayendo producto:', e);
        }
    });

    return products;
}

/**
 * Crea el botón flotante del Oráculo
 */
function createOracleButton() {
    // Evitar duplicados
    if (document.getElementById('oraculo-fab')) return;

    const fab = document.createElement('div');
    fab.id = 'oraculo-fab';
    fab.innerHTML = `
        <div class="oraculo-fab-button">
            <span class="oraculo-fab-icon">👁️</span>
            <span class="oraculo-fab-text">Enviar al Oráculo</span>
        </div>
        <div class="oraculo-fab-counter" id="oraculo-counter">0</div>
    `;

    fab.addEventListener('click', handleSendToOraculo);
    document.body.appendChild(fab);

    // Actualizar contador
    updateCounter();
}

/**
 * Actualiza el contador de productos detectados
 */
function updateCounter() {
    const products = extractProducts();
    const counter = document.getElementById('oraculo-counter');
    if (counter) {
        counter.textContent = products.length;
        counter.style.display = products.length > 0 ? 'flex' : 'none';
    }
}

/**
 * Envía los productos al Oráculo
 */
async function handleSendToOraculo() {
    const products = extractProducts();

    if (products.length === 0) {
        showNotification('No se encontraron productos en esta página', 'warning');
        return;
    }

    // Obtener la URL del servidor y la clave de extensión guardadas
    const config = await chrome.storage.sync.get(['serverUrl', 'apiKey']);
    const serverUrl = config.serverUrl || 'http://localhost:8000';

    if (!config.apiKey) {
        showNotification('❌ Configura la Clave de la Extensión en el popup del Oráculo', 'error');
        return;
    }

    try {
        showNotification(`Enviando ${products.length} productos...`, 'info');

        const response = await fetch(`${serverUrl}/api/wallapop/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Extension-Key': config.apiKey
            },
            body: JSON.stringify({ products: products })
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`✅ ${result.imported} productos enviados al Purgatorio`, 'success');
        } else {
            throw new Error(`Error ${response.status}`);
        }

    } catch (error) {
        console.error('[Oráculo] Error enviando:', error);

        // Fallback: copiar al portapapeles en formato compatible
        const textData = products.map(p => `${p.title} | ${p.price} | ${p.url}`).join('\n');

        try {
            await navigator.clipboard.writeText(textData);
            showNotification(`📋 Copiado al portapapeles (${products.length} productos). Pégalo en import_wallapop.bat`, 'info');
        } catch (clipError) {
            showNotification('❌ Error de conexión. Revisa que el Oráculo esté activo.', 'error');
        }
    }
}

/**
 * Muestra una notificación temporal
 */
function showNotification(message, type = 'info') {
    // Eliminar notificaciones anteriores
    const existing = document.getElementById('oraculo-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.id = 'oraculo-notification';
    notification.className = `oraculo-notification oraculo-notification--${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto-eliminar después de 4 segundos
    setTimeout(() => notification.remove(), 4000);
}

// Inicialización
function init() {
    // Solo activar en páginas de búsqueda o listados
    if (window.location.pathname.includes('/search') ||
        window.location.pathname.includes('/app/search') ||
        window.location.pathname === '/') {

        createOracleButton();

        // Actualizar contador cuando cambia el contenido
        const observer = new MutationObserver(() => {
            setTimeout(updateCounter, 500);
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
