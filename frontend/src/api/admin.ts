import axios from 'axios';

const API_BASE = '/api';
const API_KEY = import.meta.env.VITE_ORACULO_API_KEY || 'eternia-shield-2026';

const adminAxios = axios.create({
    baseURL: API_BASE,
    headers: {
        'X-API-Key': API_KEY
    }
});

export interface ScraperStatus {
    spider_name: string;
    status: string;
    start_time: string | null;
    end_time: string | null;
}

export interface ScraperLog {
    id: number;
    spider_name: string;
    status: string;
    start_time: string;
    end_time: string | null;
    items_found: number;
    trigger_type: string;
    error_message: string | null;
}

export const getScrapersStatus = async (): Promise<ScraperStatus[]> => {
    const response = await adminAxios.get('/scrapers/status');
    return response.data;
};

export const getScrapersLogs = async (): Promise<ScraperLog[]> => {
    const response = await adminAxios.get('/scrapers/logs');
    return response.data;
};

export const runScraper = async (spiderName: string = 'all'): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.post('/scrapers/run', {
        spider_name: spiderName,
        trigger_type: 'manual_ui'
    });
    return response.data;
};

export const updateProduct = async (productId: number, data: any): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.put(`/products/${productId}`, data);
    return response.data;
};

export const getDuplicates = async (): Promise<any[]> => {
    const response = await adminAxios.get('/admin/duplicates');
    return response.data;
};

export const mergeProducts = async (sourceId: number, targetId: number): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.post('/products/merge', {
        source_id: sourceId,
        target_id: targetId
    });
    return response.data;
};

export const syncNexus = async (): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.post('/admin/nexus/sync');
    return response.data;
};

export const updateUserLocation = async (userId: number, location: string): Promise<{ status: string; location: string }> => {
    const response = await adminAxios.post(`/users/${userId}/location`, null, {
        params: { location }
    });
    return response.data;
};

export const getUserSettings = async (userId: number): Promise<any> => {
    const response = await adminAxios.get(`/users/${userId}`);
    return response.data;
};

export const unlinkOffer = async (offerId: number): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.post(`/offers/${offerId}/unlink`);
    return response.data;
};

export const relinkOffer = async (offerId: number, targetProductId: number): Promise<{ status: string; message: string }> => {
    const response = await adminAxios.post(`/offers/${offerId}/relink`, {
        target_product_id: targetProductId
    });
    return response.data;
};
