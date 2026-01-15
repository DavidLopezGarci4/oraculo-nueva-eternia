import axios from 'axios';

const API_BASE_URL = '/api';

export interface Product {
    id: number;
    name: string;
    ean?: string | null;
    category: string;
    sub_category: string;
    figure_id: string;
    image_url: string | null;
    retail_price?: number;

    // Financial Intelligence
    purchase_price?: number;
    market_value?: number;
    is_grail?: boolean;
    grail_score?: number;
    is_wish?: boolean;
    acquired_at?: string | null;
}

export const getCollection = async (userId: number): Promise<Product[]> => {
    const response = await axios.get(`${API_BASE_URL}/collection`, {
        params: { user_id: userId }
    });
    return response.data;
};

export const toggleCollection = async (productId: number, userId: number, wish: boolean = false) => {
    const response = await axios.post(`${API_BASE_URL}/collection/toggle`, {
        product_id: productId,
        user_id: userId,
        wish
    });
    return response.data;
};
