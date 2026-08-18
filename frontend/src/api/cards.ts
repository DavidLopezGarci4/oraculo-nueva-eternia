import axios from 'axios';

export interface CardAiEnhancePayload {
    product_name: string;
    sub_category?: string;
    style: 'oil_vintage' | 'comic_retro' | 'cinematic_4k' | 'rpg_lore';
    condition?: string;
    grading?: number;
}

export interface CardAiEnhanceResult {
    style: string;
    style_name: string;
    image_base64?: string | null;
    lore?: string | null;
    stats?: {
        fuerza: number;
        magia: number;
        defensa: number;
        agilidad: number;
    } | null;
    special_move?: string | null;
    rarity_class?: string | null;
}

export const enhanceCardWithAI = async (payload: CardAiEnhancePayload): Promise<CardAiEnhanceResult> => {
    const token = localStorage.getItem('token');
    const response = await axios.post<CardAiEnhanceResult>(
        '/api/cards/ai-enhance',
        payload,
        {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
    );
    return response.data;
};
