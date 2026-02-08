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
    avg_retail_price?: number;
    p25_retail_price?: number;
    p25_price?: number; // Alias or direct p25 metric
    avg_p2p_price?: number;
    p25_p2p_price?: number;

    // Financial Intelligence
    purchase_price?: number;
    market_value?: number;
    landing_price?: number; // Phase 15 Logistics
    is_grail?: boolean;
    grail_score?: number;
    is_wish?: boolean;
    acquired_at?: string | null;
    condition?: string;
    grading?: number;
    notes?: string;

    // Phase 50: Sentiment Intelligence
    popularity_score?: number;
    market_momentum?: number;
    asin?: string | null;
    upc?: string | null;
    avg_market_price?: number;

    // Best Offer Tracking (Phase 44)
    best_p2p_price?: number;
    best_p2p_source?: string | null;
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

export const updateCollectionItem = async (productId: number, userId: number, data: {
    condition?: string;
    grading?: number;
    purchase_price?: number;
    notes?: string;
    acquired_at?: string;
}) => {
    const response = await axios.patch(`${API_BASE_URL}/collection/${productId}`, {
        user_id: userId,
        ...data
    });
    return response.data;
};
