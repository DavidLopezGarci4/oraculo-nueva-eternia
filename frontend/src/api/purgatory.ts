import axios from 'axios';

const API_BASE = '/api';
// Nota: En una app real, esto vendría de un estado global o .env
const ORACULO_API_KEY = import.meta.env.VITE_ORACULO_API_KEY || 'eternia-shield-2026';

const adminHeaders = {
    headers: {
        'X-API-Key': ORACULO_API_KEY
    }
};

export interface PendingItemSuggestion {
    product_id: number;
    name: string;
    figure_id?: string;
    sub_category?: string;
    match_score: number;
    reason: string;
}

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
    suggestions?: PendingItemSuggestion[];
}

export interface ScraperStatus {
    spider_name: string;
    status: string;
    start_time?: string;
    end_time?: string;
}

export interface ScraperExecutionLog {
    id: number;
    spider_name: string;
    status: string;
    items_found: number;
    new_items?: number;
    start_time: string;
    end_time?: string;
    error_message?: string;
    logs?: string;
}

export const getPurgatory = async (): Promise<PendingItem[]> => {
    const response = await axios.get(`${API_BASE}/purgatory`, adminHeaders);
    return response.data;
};

export const matchItem = async (pendingId: number, productId: number) => {
    const response = await axios.post(`${API_BASE}/purgatory/match`, {
        pending_id: pendingId,
        product_id: productId
    }, adminHeaders);
    return response.data;
};

export const discardItem = async (pendingId: number, reason: string = 'manual_discard') => {
    const response = await axios.post(`${API_BASE}/purgatory/discard`, {
        pending_id: pendingId,
        reason
    }, adminHeaders);
    return response.data;
};

export const discardItemsBulk = async (pendingIds: number[], reason: string = 'manual_bulk_discard') => {
    const response = await axios.post(`${API_BASE}/purgatory/discard/bulk`, {
        pending_ids: pendingIds,
        reason
    }, adminHeaders);
    return response.data;
};

export const matchItemsBulk = async (matches: { pending_id: number, product_id: number }[]) => {
    const response = await axios.post(`${API_BASE}/purgatory/match/bulk`, { matches }, adminHeaders);
    return response.data;
};

export const getScrapersStatus = async (): Promise<ScraperStatus[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/status`, adminHeaders);
    return response.data;
};

export const runScrapers = async (spiderName: string = 'all', triggerType: string = 'manual') => {
    const response = await axios.post(`${API_BASE}/scrapers/run`, {
        spider_name: spiderName,
        trigger_type: triggerType
    }, adminHeaders);
    return response.data;
};

export const getScraperLogs = async (): Promise<ScraperExecutionLog[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/logs`, adminHeaders);
    return response.data;
};

export const stopScrapers = async () => {
    const response = await axios.post(`${API_BASE}/scrapers/stop`, {}, adminHeaders);
    return response.data;
};

export const resetSmartMatches = async () => {
    const response = await axios.post(`${API_BASE}/admin/reset-smartmatches`, {}, adminHeaders);
    return response.data;
};

export const matchVintageItem = async (pendingId: number, customName?: string, productId?: number, isVintage: boolean = true, subCategory?: string) => {
    const response = await axios.post(`${API_BASE}/purgatory/${pendingId}/vintage`, {
        custom_name: customName,
        product_id: productId,
        is_vintage: isVintage,
        sub_category: subCategory
    }, adminHeaders);
    return response.data;
};

export const revertVintageItem = async (offerId: number) => {
    const response = await axios.post(`${API_BASE}/vintage/revert-offer/${offerId}`, {}, adminHeaders);
    return response.data;
};

export interface VintageMiscellaneousItem {
    id: number;
    title: string;
    url: string;
    price: number;
    currency: string;
    shop_name: string;
    image_url?: string | null;
    condition: string;
    grading?: number;
    notes?: string;
    added_at?: string;
}

export const matchMiscellaneousItem = async (pendingId: number) => {
    const response = await axios.post(`${API_BASE}/purgatory/${pendingId}/miscellaneous`, {}, adminHeaders);
    return response.data;
};

export const revertMiscellaneousItem = async (itemId: number) => {
    const response = await axios.post(`${API_BASE}/vintage/miscellaneous/revert/${itemId}`, {}, adminHeaders);
    return response.data;
};

export const getMiscellaneousItems = async (): Promise<VintageMiscellaneousItem[]> => {
    const response = await axios.get(`${API_BASE}/vintage/miscellaneous`, adminHeaders);
    return response.data;
};

export const deleteMiscellaneousItem = async (itemId: number) => {
    const response = await axios.delete(`${API_BASE}/vintage/miscellaneous/${itemId}`, adminHeaders);
    return response.data;
};


export interface WallapopIpLog {
    id: number;
    ip_address: string;
    status: string;
    environment?: string;
    response_code?: number;
    details?: string;
    recorded_at: string;
}

export const getWallapopIpLogs = async (): Promise<WallapopIpLog[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/wallapop/ip-logs`, adminHeaders);
    return response.data;
};

export const downloadWallapopIpLogs = async (): Promise<void> => {
    const response = await axios.get(`${API_BASE}/scrapers/wallapop/ip-logs/download`, {
        ...adminHeaders,
        responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/plain' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'wallapop_ip_logs.txt');
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
};

export const runWallaManualHtml = async () => {
    const response = await axios.post(`${API_BASE}/scrapers/wallapop/import-manual-html`, {}, adminHeaders);
    return response.data;
};
