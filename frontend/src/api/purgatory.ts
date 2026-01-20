import axios from 'axios';

const API_BASE = '/api';
// Nota: En una app real, esto vendría de un estado global o .env
const ORACULO_API_KEY = 'eternia-shield-2026';

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
    start_time: string;
    end_time?: string;
    error_message?: string;
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

export const getScrapersStatus = async (): Promise<ScraperStatus[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/status`, adminHeaders);
    return response.data;
};

export const runScrapers = async (scraperName: string = 'harvester', triggerType: string = 'manual') => {
    const response = await axios.post(`${API_BASE}/scrapers/run`, {
        scraper_name: scraperName,
        trigger_type: triggerType
    }, adminHeaders);
    return response.data;
};

export const getScraperLogs = async (): Promise<ScraperExecutionLog[]> => {
    const response = await axios.get(`${API_BASE}/scrapers/logs`, adminHeaders);
    return response.data;
};

export const resetSmartMatches = async () => {
    const response = await axios.post(`${API_BASE}/admin/reset-smartmatches`, {}, adminHeaders);
    return response.data;
};
