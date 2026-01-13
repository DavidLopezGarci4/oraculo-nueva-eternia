import axios from 'axios';

const API_BASE_URL = '/api';

export interface Product {
    id: number;
    name: string;
    category: string;
    sub_category: string;
    figure_id: string;
    image_url: string | null;

    // Financial Intelligence
    purchase_price?: number;
    market_value?: number;
    is_grail?: boolean;
    grail_score?: number;
}

export const getCollection = async (userId: number): Promise<Product[]> => {
    const response = await axios.get(`${API_BASE_URL}/collection`, {
        params: { user_id: userId }
    });
    return response.data;
};

export const toggleCollection = async (productId: number, userId: number) => {
    const response = await axios.post(`${API_BASE_URL}/collection/toggle`, {
        product_id: productId,
        user_id: userId
    });
    return response.data;
};
