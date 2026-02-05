import axios from 'axios';

const API_BASE = '/api';

export interface FinancialHealth {
    total_invested: number;
    market_value: number;
    landed_market_value: number;
    profit_loss: number;
    roi: number;
}

export interface DashboardStats {
    total_products: number;
    owned_count: number;
    match_count: number;
    financial: FinancialHealth;
    shop_distribution: {
        shop: string;
        count: number;
    }[];
}

export interface TopDeal {
    id: number;
    product_name: string;
    price: number;
    landing_price: number;
    currency: string;
    shop_name: string;
    url: string;
    image_url?: string;
}

export interface P2POpportunity {
    id: number;
    product_name: string;
    ean: string | null;
    image_url: string | null;
    price: number;
    p25_price: number;
    avg_market_price: number;
    saving: number;
    saving_pct: number;
    shop_name: string;
    url: string;
    landing_price: number;
}

export interface MatchHistoryEntry {
    id: number;
    product_name: string;
    shop_name: string;
    price: number;
    action_type: string;
    timestamp: string;
    offer_url: string;
}

export interface MatchStat {
    shop: string;
    count: number;
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
    const userId = localStorage.getItem('active_user_id') || '1';
    const response = await axios.get(`${API_BASE}/dashboard/stats`, {
        params: { user_id: userId }
    });
    return response.data;
};

export const getTopDeals = async (): Promise<TopDeal[]> => {
    const userId = localStorage.getItem('active_user_id') || '1';
    const response = await axios.get(`${API_BASE}/dashboard/top-deals`, {
        params: { user_id: userId }
    });
    return response.data;
};

export const getDashboardHistory = async (): Promise<MatchHistoryEntry[]> => {
    const response = await axios.get(`${API_BASE}/dashboard/history`);
    return response.data;
};

export const getDashboardMatchStats = async (): Promise<MatchStat[]> => {
    const response = await axios.get(`${API_BASE}/dashboard/match-stats`);
    return response.data;
};

export const revertDashboardAction = async (historyId: number): Promise<{ status: string; message: string }> => {
    const response = await axios.post(`${API_BASE}/dashboard/revert`, { history_id: historyId });
    return response.data;
};

export interface HallOfFameItem {
    id: number;
    name: string;
    image_url: string | null;
    market_value: number;
    invested_value: number;
    roi_percentage: number;
}

export interface HallOfFameResponse {
    top_value: HallOfFameItem[];
    top_roi: HallOfFameItem[];
}

export const getHallOfFame = async (): Promise<HallOfFameResponse> => {
    const userId = localStorage.getItem('active_user_id') || '1';
    const response = await axios.get(`${API_BASE}/dashboard/hall-of-fame`, {
        params: { user_id: userId }
    });
    return response.data;
};

export const getPeerToPeerOpportunities = async (): Promise<P2POpportunity[]> => {
    const userId = localStorage.getItem('active_user_id') || '1';
    const response = await axios.get(`${API_BASE}/radar/p2p-opportunities`, {
        params: { user_id: userId }
    });
    return response.data;
};
