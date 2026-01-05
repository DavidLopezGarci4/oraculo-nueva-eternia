import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export interface PendingItem {
    id: number;
    scraped_name: string;
    ean?: string;
    price: number;
    currency: string;
    url: string;
    shop_name: string;
    image_url?: string;
    found_at: string;
}

export interface ScraperStatus {
    spider_name: string;
    status: string;
    start_time?: string;
    end_time?: string;
}

export const getPurgatory = async (): Promise<PendingItem[]> => {
    const response = await axios.get(`${API_BASE}/purgatory`);
    return response.data;
};

export const matchItem = async (pendingId: number, productId: number) => {
    const response = await axios.post(`${API_BASE}/purgatory/match`, {
        pending_id: pendingId,
        product_id: productId
    });
    return response.data;
};

export const discardItem = async (pendingId: number, reason: string = 'manual_discard') => {
    const response = await axios.post(`${API_BASE}/purgatory/discard`, {
        pending_id: pendingId,
        reason
    });
    return response.data;
};

export const getScrapersStatus = async (): Promise<ScraperStatus[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/status`);
    return response.data;
};

export const runScrapers = async () => {
    const response = await axios.post(`${API_BASE}/scrapers/run`);
    return response.data;
};
