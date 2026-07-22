import { apiClient } from './client';

const API_BASE = '';
// Autenticación centralizada (JWT) en './client'. Sin API key en el navegador.
// `adminHeaders` se mantiene como objeto vacío para no romper las llamadas existentes.
const adminHeaders = {};

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
    const response = await apiClient.get(`${API_BASE}/purgatory`, adminHeaders);
    return response.data;
};

export const matchItem = async (pendingId: number, productId: number) => {
    const response = await apiClient.post(`${API_BASE}/purgatory/match`, {
        pending_id: pendingId,
        product_id: productId
    }, adminHeaders);
    return response.data;
};

export const discardItem = async (pendingId: number, reason: string = 'manual_discard') => {
    const response = await apiClient.post(`${API_BASE}/purgatory/discard`, {
        pending_id: pendingId,
        reason
    }, adminHeaders);
    return response.data;
};

export const discardItemsBulk = async (pendingIds: number[], reason: string = 'manual_bulk_discard') => {
    const response = await apiClient.post(`${API_BASE}/purgatory/discard/bulk`, {
        pending_ids: pendingIds,
        reason
    }, adminHeaders);
    return response.data;
};

export const matchItemsBulk = async (matches: { pending_id: number, product_id: number }[]) => {
    const response = await apiClient.post(`${API_BASE}/purgatory/match/bulk`, { matches }, adminHeaders);
    return response.data;
};

export const getScrapersStatus = async (): Promise<ScraperStatus[]> => {
    const response = await apiClient.get(`${API_BASE}/scrapers/status`, adminHeaders);
    return response.data;
};

export const runScrapers = async (spiderName: string = 'all', triggerType: string = 'manual', query?: string) => {
    const response = await apiClient.post(`${API_BASE}/scrapers/run`, {
        spider_name: spiderName,
        trigger_type: triggerType,
        query: query || null
    }, adminHeaders);
    return response.data;
};

export const getScraperLogs = async (): Promise<ScraperExecutionLog[]> => {
    const response = await apiClient.get(`${API_BASE}/scrapers/logs`, adminHeaders);
    return response.data;
};

export const stopScrapers = async () => {
    const response = await apiClient.post(`${API_BASE}/scrapers/stop`, {}, adminHeaders);
    return response.data;
};

export const resetSmartMatches = async () => {
    const response = await apiClient.post(`${API_BASE}/admin/reset-smartmatches`, {}, adminHeaders);
    return response.data;
};

export const matchVintageItem = async (pendingId: number, customName?: string, productId?: number, isVintage: boolean = true, subCategory?: string) => {
    const response = await apiClient.post(`${API_BASE}/purgatory/${pendingId}/vintage`, {
        custom_name: customName,
        product_id: productId,
        is_vintage: isVintage,
        sub_category: subCategory
    }, adminHeaders);
    return response.data;
};

export const revertVintageItem = async (offerId: number) => {
    const response = await apiClient.post(`${API_BASE}/vintage/revert-offer/${offerId}`, {}, adminHeaders);
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
    const response = await apiClient.post(`${API_BASE}/purgatory/${pendingId}/miscellaneous`, {}, adminHeaders);
    return response.data;
};

export const revertMiscellaneousItem = async (itemId: number) => {
    const response = await apiClient.post(`${API_BASE}/vintage/miscellaneous/revert/${itemId}`, {}, adminHeaders);
    return response.data;
};

export const getMiscellaneousItems = async (): Promise<VintageMiscellaneousItem[]> => {
    const response = await apiClient.get(`${API_BASE}/vintage/miscellaneous`, adminHeaders);
    return response.data;
};

export const deleteMiscellaneousItem = async (itemId: number) => {
    const response = await apiClient.delete(`${API_BASE}/vintage/miscellaneous/${itemId}`, adminHeaders);
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
    const response = await apiClient.get(`${API_BASE}/scrapers/wallapop/ip-logs`, adminHeaders);
    return response.data;
};

export const downloadWallapopIpLogs = async (): Promise<void> => {
    const response = await apiClient.get(`${API_BASE}/scrapers/wallapop/ip-logs/download`, {
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

export const runWallaManualHtml = async (file?: File) => {
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        const headers = {
            ...adminHeaders,
            'Content-Type': 'multipart/form-data',
        };
        const response = await apiClient.post(`${API_BASE}/scrapers/wallapop/import-manual-html`, formData, { headers });
        return response.data;
    } else {
        const response = await apiClient.post(`${API_BASE}/scrapers/wallapop/import-manual-html`, {}, adminHeaders);
        return response.data;
    }
};

// --- Nexus Local Bridge (Fase 2) ---

export interface WallapopJob {
    id: number;
    query: string;
    status: 'pending' | 'running' | 'done' | 'error';
    result_count: number;
    error_message?: string | null;
    worker_id?: string | null;
    created_at: string;
    claimed_at?: string | null;
    completed_at?: string | null;
}

export const createWallapopJob = async (query: string = 'auto'): Promise<{ status: string; job_id: number; message: string }> => {
    const response = await apiClient.post(`${API_BASE}/wallapop/jobs`, { query }, adminHeaders);
    return response.data;
};

export const getWallapopJobs = async (limit: number = 20): Promise<WallapopJob[]> => {
    const response = await apiClient.get(`${API_BASE}/wallapop/jobs`, { ...adminHeaders, params: { limit } });
    return response.data;
};
