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

export const fetchCharacterLoreList = async (params?: {
    search?: string;
    faction?: string;
    pending_only?: boolean;
    skip?: number;
    limit?: number;
}): Promise<CharacterLoreListResponse> => {
    const res = await axios.get<CharacterLoreListResponse>('/api/lore', { params });
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

export const seedInitialLore = async (): Promise<{ status: string; result: any }> => {
    const res = await axios.post<{ status: string; result: any }>('/api/lore/seed');
    return res.data;
};
