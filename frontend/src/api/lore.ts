import { apiClient as axios } from './client';

export interface CharacterLore {
    slug: string;
    canonical_name: string;
    subtitle?: string;
    faction: string;
    theme_key: 'castle_grayskull' | 'snake_mountain' | 'evil_horde' | 'snake_men' | 'great_rebellion' | 'cosmic_enforcers';
    type_line: string;
    special_move: string;
    quote?: string;
    flavor_quote_author?: string;
    lore: string;
    text_color?: string;
    card_version?: 'showcase' | 'classic' | 'secret_lair';
    mana_cost?: string;
    fuerza: number;
    magia: number;
    defensa: number;
    agilidad: number;
    source_url?: string;
    is_verified: boolean;
}

export interface CharacterLoreListResponse {
    items: CharacterLore[];
    total: number;
    pending_count: number;
}

export interface ProductLore {
    product_id: number;
    canonical_name: string;
    subtitle?: string;
    faction: string;
    theme_key: 'castle_grayskull' | 'snake_mountain' | 'evil_horde' | 'snake_men' | 'great_rebellion' | 'cosmic_enforcers';
    type_line: string;
    special_move: string;
    quote?: string;
    flavor_quote_author?: string;
    lore: string;
    source_url?: string;
    text_color?: string;
    card_version?: 'showcase' | 'classic' | 'secret_lair';
    mana_cost?: string;
    fuerza: number;
    magia: number;
    defensa: number;
    agilidad: number;
    is_customized: boolean;
}

export interface ProductLoreListItem {
    product_id: number;
    product_name: string;
    sub_category?: string;
    image_url?: string;
    canonical_name: string;
    subtitle?: string;
    faction: string;
    special_move: string;
    quote?: string;
    flavor_quote_author?: string;
    lore: string;
    is_customized: boolean;
}

export interface ProductLoreListResponse {
    items: ProductLoreListItem[];
    total: number;
}

// ─── ENDPOINTS LORE POR FIGURA / ÍTEM (ORIGINS) ───

export const fetchProductLore = async (productId: number): Promise<ProductLore> => {
    const res = await axios.get<ProductLore>(`/api/lore/product/${productId}`);
    return res.data;
};

export const updateProductLore = async (
    productId: number,
    data: Partial<ProductLore>
): Promise<ProductLore> => {
    const res = await axios.put<ProductLore>(`/api/lore/product/${productId}`, data);
    return res.data;
};

export const fetchProductLoreList = async (params?: {
    search?: string;
    faction?: string;
    sub_category?: string;
    skip?: number;
    limit?: number;
}): Promise<ProductLoreListResponse> => {
    const res = await axios.get<ProductLoreListResponse>('/api/lore/products', { params });
    return res.data;
};

// ─── ENDPOINTS LORE ARQUETÍPICO ───

export const fetchCharacterLoreList = async (params?: {
    search?: string;
    faction?: string;
    pending_only?: boolean;
    skip?: number;
    limit?: number;
}): Promise<CharacterLoreListResponse> => {
    const res = await axios.get<CharacterLoreListResponse>('/api/lore/characters', { params });
    return res.data;
};

export const updateCharacterLore = async (
    slug: string,
    data: Partial<CharacterLore>
): Promise<CharacterLore> => {
    const res = await axios.put<CharacterLore>(`/api/lore/${slug}`, data);
    return res.data;
};

export const harvestCharacterLore = async (characterName: string): Promise<CharacterLore> => {
    const res = await axios.post<CharacterLore>('/api/lore/harvest', {
        character_name: characterName
    });
    return res.data;
};

export const harvestProductLore = async (productId: number): Promise<CharacterLore> => {
    const res = await axios.post<CharacterLore>(`/api/lore/harvest-product/${productId}`);
    return res.data;
};

export const seedInitialLore = async (force: boolean = false): Promise<{ status: string; result: any }> => {
    const res = await axios.post<{ status: string; result: any }>('/api/lore/seed', null, {
        params: { force }
    });
    return res.data;
};
