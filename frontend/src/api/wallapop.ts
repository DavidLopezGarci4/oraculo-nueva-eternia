import axios from 'axios';

const API_BASE = '/api';

export interface WallapopProduct {
    title: string;
    price: number;
    url: string;
    imageUrl?: string;
}

export interface WallapopImportResult {
    status: string;
    imported: number;
    total_received: number;
}

/**
 * Importa productos de Wallapop al Purgatorio.
 * Acepta una lista de productos parseados.
 */
export const importWallapopProducts = async (products: WallapopProduct[]): Promise<WallapopImportResult> => {
    const response = await axios.post(`${API_BASE}/wallapop/import`, { products });
    return response.data;
};

/**
 * Parsea texto en formato simple: Nombre | Precio | URL
 */
export const parseWallapopText = (text: string): WallapopProduct[] => {
    const products: WallapopProduct[] = [];
    const lines = text.trim().split('\n');

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;

        // Formato: Nombre | Precio | URL
        if (trimmed.includes('|')) {
            const parts = trimmed.split('|').map(p => p.trim());
            if (parts.length >= 3) {
                const priceStr = parts[1].replace(/[^\d.,]/g, '').replace(',', '.');
                const price = parseFloat(priceStr) || 0;

                if (parts[2].includes('wallapop.com')) {
                    products.push({
                        title: parts[0],
                        price: price,
                        url: parts[2]
                    });
                }
            }
        } else {
            // Solo URL
            const urlMatch = trimmed.match(/https?:\/\/(?:es\.)?wallapop\.com\/item\/[^\s]+/);
            if (urlMatch) {
                products.push({
                    title: 'Producto Wallapop',
                    price: 0,
                    url: urlMatch[0]
                });
            }
        }
    }

    return products;
};
