import axios from 'axios';

const API_BASE = '/api';

export interface PriceHistoryPoint {
    date: string;
    price: number;
}

export interface ProductPriceHistory {
    shop_name: string;
    history: PriceHistoryPoint[];
}

export const getProductPriceHistory = async (productId: number): Promise<ProductPriceHistory[]> => {
    const response = await axios.get(`${API_BASE}/products/${productId}/price-history`);
    return response.data;
};
