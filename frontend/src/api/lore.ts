import { apiClient as axios } from './client';

// NOTA: `apiClient` ya define `baseURL: '/api'`; las rutas de este módulo son relativas ('/lore/...').

export type LoreThemeKey =
    | 'castle_grayskull'
    | 'snake_mountain'
    | 'evil_horde'
    | 'snake_men'
    | 'great_rebellion'
    | 'cosmic_enforcers';

// Catálogo cerrado de facciones (espejo de VALID_FACTIONS / FACTION_TO_THEME en el backend).
export const FACTION_TO_THEME: Record<string, LoreThemeKey> = {
    'Guerreros Heroicos': 'castle_grayskull',
    'Guerreros del Mal': 'snake_mountain',
    'La Horda del Terror': 'evil_horde',
    'Los Hombres Serpiente': 'snake_men',
    'La Gran Rebelión': 'great_rebellion',
    'Guardianes Cósmicos': 'cosmic_enforcers',
    'Gobernantes de Solaria': 'castle_grayskull',
    'Alianzas del Multiverso': 'castle_grayskull'
};

export const MOTU_FACTIONS: string[] = Object.keys(FACTION_TO_THEME);

/** Longitud orientativa (no bloqueante) del texto de biografía para que encaje en el cromo TCG. */
export const LORE_RECOMMENDED_LENGTH = 180;

export interface CharacterLore {
    slug: string;
    canonical_name: string;
    subtitle?: string;
    faction: string;
    theme_key: LoreThemeKey;
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
    theme_key: LoreThemeKey;
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
    theme_key: LoreThemeKey;
    type_line: string;
    special_move: string;
    quote?: string;
    flavor_quote_author?: string;
    lore: string;
    mana_cost?: string;
    fuerza: number;
    magia: number;
    defensa: number;
    agilidad: number;
    is_customized: boolean;
}

export interface ProductLoreListResponse {
    items: ProductLoreListItem[];
    total: number;
}

// ─── ENDPOINTS LORE POR FIGURA / ÍTEM (ORIGINS) ───

export const fetchProductLore = async (productId: number): Promise<ProductLore> => {
    const res = await axios.get<ProductLore>(`/lore/product/${productId}`);
    return res.data;
};

export const updateProductLore = async (
    productId: number,
    data: Partial<ProductLore>
): Promise<ProductLore> => {
    const res = await axios.put<ProductLore>(`/lore/product/${productId}`, data);
    return res.data;
};

export const fetchProductLoreList = async (params?: {
    search?: string;
    faction?: string;
    sub_category?: string;
    skip?: number;
    limit?: number;
}): Promise<ProductLoreListResponse> => {
    const res = await axios.get<ProductLoreListResponse>('/lore/products', { params });
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
    const res = await axios.get<CharacterLoreListResponse>('/lore/characters', { params });
    return res.data;
};

export const fetchCharacterLore = async (slug: string): Promise<CharacterLore> => {
    const res = await axios.get<CharacterLore>(`/lore/${encodeURIComponent(slug)}`);
    return res.data;
};

export const updateCharacterLore = async (
    slug: string,
    data: Partial<CharacterLore>
): Promise<CharacterLore> => {
    const res = await axios.put<CharacterLore>(`/lore/${encodeURIComponent(slug)}`, data);
    return res.data;
};

/** Devuelve 409 Conflict si el personaje ya está verificado y `force` es false. */
export const harvestCharacterLore = async (
    characterName: string,
    force: boolean = false
): Promise<CharacterLore> => {
    const res = await axios.post<CharacterLore>('/lore/harvest', {
        character_name: characterName,
        force
    });
    return res.data;
};

/** Devuelve 409 Conflict si el personaje ya está verificado y `force` es false. */
export const harvestProductLore = async (
    productId: number,
    force: boolean = false
): Promise<CharacterLore> => {
    const res = await axios.post<CharacterLore>(`/lore/harvest-product/${productId}`, null, {
        params: { force }
    });
    return res.data;
};

export const seedInitialLore = async (force: boolean = false): Promise<{ status: string; result: any }> => {
    const res = await axios.post<{ status: string; result: any }>('/lore/seed', null, {
        params: { force }
    });
    return res.data;
};
