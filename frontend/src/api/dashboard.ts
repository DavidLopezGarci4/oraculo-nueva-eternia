import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export interface DashboardStats {
    total_products: number;
    owned_count: number;
    total_value: number;
    match_count: number;
    shop_distribution: {
        shop: string;
        count: number;
    }[];
}

export interface TopDeal {
    id: number;
    product_name: string;
    price: number;
    currency: string;
    shop_name: string;
    url: string;
    image_url?: string;
}

export interface MatchHistoryEntry {
    id: number;
    product_name: string;
    shop_name: string;
    price: number;
    action_type: string;
    timestamp: string;
}

export interface MatchStat {
    shop: string;
    count: number;
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
    const response = await axios.get(`${API_BASE}/dashboard/stats`);
    return response.data;
};

export const getTopDeals = async (userId: number = 2): Promise<TopDeal[]> => {
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
