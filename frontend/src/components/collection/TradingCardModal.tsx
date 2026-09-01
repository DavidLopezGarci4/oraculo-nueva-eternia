import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    Sparkles,
    Download,
    Share2,
    Copy,
    Check,
    X,
    Award,
    Loader2,
    Wand2,
    RotateCcw,
    Zap,
    BookOpen,
    Image as ImageIcon,
    Plus,
    Minus,
    Maximize2,
    Edit3,
    Save,
    CheckCircle2,
    RefreshCw,
    Globe,
    Palette
} from 'lucide-react';
import { toPng } from 'html-to-image';
import { MOTUImage } from '../ui/MOTUImage';
import { enhanceCardWithAI, type CardAiEnhanceResult } from '../../api/cards';
import { getSystemTcgLayouts } from '../../api/admin';
import { fetchCharacterLoreList, updateCharacterLore, harvestProductLore, type CharacterLore } from '../../api/lore';
import { refreshProductImage } from '../../api/products';
import { DEFAULT_FACTION_CARD_LAYOUTS, type FactionCardLayout } from '../config/TcgConfigTab';

interface TradingCardModalProps {
    isOpen: boolean;
    onClose: () => void;
    item: {
        id: number;
        product_name?: string;
        name?: string;
        image_url?: string;
        condition?: string;
        grading?: number;
        purchase_price?: number;
        current_value?: number;
        sub_category?: string;
        release_year?: number;
        sku?: string;
        shelf_wear?: string;
    } | null;
}

// Configuración de los marcos fotorrealistas en alta definición por cada facción
interface FactionVisualTheme {
    faction: string;
    typeLine: string;
    frameAsset: string;
    specialMoveColor: string;
    loreTextColor: string;
}

const FRAME_CACHE_VERSION = 'v=4cavities_3d_v2';

const FACTION_VISUAL_THEMES: Record<string, FactionVisualTheme> = {
    castle_grayskull: {
        faction: 'Guerreros Heroicos',
        typeLine: 'Criatura Legendaria — Guerrero Heroico',
        frameAsset: `/frames/frame_castle_grayskull.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#ffdb70',
        loreTextColor: '#e2eedd'
    },
    snake_mountain: {
        faction: 'Guerreros del Mal',
        typeLine: 'Criatura Legendaria — Guerrero del Mal',
        frameAsset: `/frames/frame_snake_mountain.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#ff8a3d',
        loreTextColor: '#eedac5'
    },
    evil_horde: {
        faction: 'La Horda del Terror',
        typeLine: 'Tirano Legendario — Soldado de la Horda',
        frameAsset: `/frames/frame_evil_horde.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#fca5a5',
        loreTextColor: '#fee2e2'
    },
    snake_men: {
        faction: 'Los Hombres Serpiente',
        typeLine: 'Monarca Ofídico — Hombre Serpiente',
        frameAsset: `/frames/frame_snake_men.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#bef264',
        loreTextColor: '#ecfccb'
    },
    great_rebellion: {
        faction: 'La Gran Rebelión',
        typeLine: 'Princesa del Poder — Gran Rebelión',
        frameAsset: `/frames/frame_great_rebellion.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#fbcfe8',
        loreTextColor: '#fdf2f8'
    },
    cosmic_enforcers: {
        faction: 'Guardianes Cósmicos',
        typeLine: 'Ejecutor Cósmico — Juez del Equilibrio',
        frameAsset: `/frames/frame_cosmic_enforcers.webp?${FRAME_CACHE_VERSION}`,
        specialMoveColor: '#7dd3fc',
        loreTextColor: '#e0f2fe'
    }
};

export type { FactionCardLayout };

export const FACTION_CARD_LAYOUTS: Record<string, FactionCardLayout> = {
    castle_grayskull: {
        header: { top: '10.4%', left: '13.5%', width: '58%', height: '4.2%' },
        textBox: { top: '54.2%', left: '13.5%', width: '73%', height: '30.5%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-amber-400/90',
            bg: 'from-black/90 via-amber-950/90 to-black/90'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#fef08a' },
        statFue: { top: '87.5%', left: '21.0%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '87.5%', left: '35.0%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '87.5%', left: '76.3%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '87.5%', left: '90.0%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 655, w: 636, h: 48 },
            powerText: { y: 686, fontSize: 18 },
            loreText: { y: 730, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            statFue: { x: 188, y: 1050 },
            statMag: { x: 314, y: 1050 },
            statDef: { x: 684, y: 1050 },
            statAgi: { x: 806, y: 1050 }
        }
    },
    snake_mountain: {
        header: { top: '10.5%', left: '13.8%', width: '57%', height: '4.2%' },
        textBox: { top: '54.5%', left: '13.5%', width: '73%', height: '30.2%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-orange-500/90',
            bg: 'from-black/90 via-stone-950/90 to-black/90'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#fed7aa' },
        statFue: { top: '87.7%', left: '28.1%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '87.7%', left: '49.1%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '87.7%', left: '69.8%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '87.7%', left: '90.6%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 124, y: 126 },
            powerBox: { x: 130, y: 658, w: 636, h: 48 },
            powerText: { y: 689, fontSize: 18 },
            loreText: { y: 732, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            statFue: { x: 252, y: 1052 },
            statMag: { x: 440, y: 1052 },
            statDef: { x: 626, y: 1052 },
            statAgi: { x: 812, y: 1052 }
        }
    },
    evil_horde: {
        header: { top: '10.2%', left: '13.5%', width: '58%', height: '4.2%' },
        textBox: { top: '53.8%', left: '13.5%', width: '73%', height: '31.0%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-rose-500/90',
            bg: 'from-black/90 via-red-950/90 to-black/90'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#fecaca' },
        statFue: { top: '86.8%', left: '23.2%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '86.8%', left: '44.4%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '86.8%', left: '66.3%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '86.8%', left: '87.9%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 120, y: 123 },
            powerBox: { x: 130, y: 648, w: 636, h: 48 },
            powerText: { y: 679, fontSize: 18 },
            loreText: { y: 722, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 835, fontSize: 15 },
            statFue: { x: 208, y: 1042 },
            statMag: { x: 398, y: 1042 },
            statDef: { x: 594, y: 1042 },
            statAgi: { x: 788, y: 1042 }
        }
    },
    snake_men: {
        header: { top: '10.4%', left: '13.5%', width: '58%', height: '4.2%' },
        textBox: { top: '54.2%', left: '13.5%', width: '73%', height: '30.5%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-lime-400/90',
            bg: 'from-black/90 via-emerald-950/90 to-black/90'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#d9f99d' },
        statFue: { top: '87.7%', left: '27.5%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '87.7%', left: '46.4%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '87.7%', left: '65.2%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '87.7%', left: '84.2%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 655, w: 636, h: 48 },
            powerText: { y: 686, fontSize: 18 },
            loreText: { y: 730, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            statFue: { x: 246, y: 1052 },
            statMag: { x: 416, y: 1052 },
            statDef: { x: 584, y: 1052 },
            statAgi: { x: 754, y: 1052 }
        }
    },
    great_rebellion: {
        header: { top: '10.4%', left: '13.5%', width: '58%', height: '4.2%' },
        textBox: { top: '54.0%', left: '13.5%', width: '73%', height: '30.8%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-pink-400/90',
            bg: 'from-black/85 via-pink-950/85 to-black/85'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#fce7f3' },
        statFue: { top: '87.2%', left: '21.8%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '87.2%', left: '45.8%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '87.2%', left: '65.6%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '87.2%', left: '89.8%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 652, w: 636, h: 48 },
            powerText: { y: 683, fontSize: 18 },
            loreText: { y: 726, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 838, fontSize: 15 },
            statFue: { x: 195, y: 1046 },
            statMag: { x: 410, y: 1046 },
            statDef: { x: 588, y: 1046 },
            statAgi: { x: 805, y: 1046 }
        }
    },
    cosmic_enforcers: {
        header: { top: '10.4%', left: '13.5%', width: '58%', height: '4.2%' },
        textBox: { top: '53.8%', left: '13.5%', width: '73%', height: '31.0%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-sky-400/90',
            bg: 'from-black/90 via-sky-950/90 to-black/90'
        },
        lore: { fontSize: '9px', lineHeight: '1.42' },
        typeLine: { fontSize: '8px', color: '#bae6fd' },
        statFue: { top: '86.8%', left: '23.7%', fontSize: '11.5px', labelFontSize: '7px' },
        statMag: { top: '86.8%', left: '44.9%', fontSize: '11.5px', labelFontSize: '7px' },
        statDef: { top: '86.8%', left: '66.3%', fontSize: '11.5px', labelFontSize: '7px' },
        statAgi: { top: '86.8%', left: '87.5%', fontSize: '11.5px', labelFontSize: '7px' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 650, w: 636, h: 48 },
            powerText: { y: 681, fontSize: 18 },
            loreText: { y: 724, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 836, fontSize: 15 },
            statFue: { x: 212, y: 1042 },
            statMag: { x: 402, y: 1042 },
            statDef: { x: 594, y: 1042 },
            statAgi: { x: 784, y: 1042 }
        }
    }
};


export interface MotuProfile {
    themeKey: 'castle_grayskull' | 'snake_mountain' | 'evil_horde' | 'snake_men' | 'great_rebellion' | 'cosmic_enforcers';
    faction: string;
    typeLine: string;
    specialMove: string;
    lore: string;
    stats: {
        fuerza: number;
        magia: number;
        defensa: number;
        agilidad: number;
    };
}

/**
 * BASE DE DATOS CANÓNICA DE PERSONAJES MOTU
 * Define de forma personalizada e independiente el lore, facción,
 * poder especial y estadísticas de cada figura del universo Masters of the Universe.
 */
export const MOTU_CHARACTER_PROFILES: { match: RegExp; profile: MotuProfile }[] = [
    // -------------------------------------------------------------
    // MULTIVERSO OSCURO / ANTI-ETERNIA (Prioridad Máxima sobre He-Man)
    // -------------------------------------------------------------
    {
        match: /anti[\s\-]?eternia|anti[\s\-]?he[\s\-]?man/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Doble Oscuro — Multiverso Anti-Eternia',
            specialMove: 'Estallido de Sombras de Anti-Eternia',
            lore: 'Nacido del reflejo infernal del World Converter en el Multiverso Oscuro, es un tirano implacable de ojos incandescentes cuyo poder busca aniquilar la luz de Eternia.',
            stats: { fuerza: 99, magia: 92, defensa: 95, agilidad: 92 }
        }
    },
    {
        match: /he[\s\-]?skeletor/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Campeón Oscuro — Multiverso Anti-Eternia',
            specialMove: 'Relámpago Destructor de Skeletor',
            lore: 'El Campeón del Multiverso Oscuro donde Keldor abrazó el poder del Relámpago de Grayskull combinándolo con la nigromancia tártara.',
            stats: { fuerza: 96, magia: 98, defensa: 93, agilidad: 88 }
        }
    },

    // -------------------------------------------------------------
    // PRETERNIA & GUARDIANES CÓSMICOS
    // -------------------------------------------------------------
    {
        match: /great\s+black\s+wizard/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Hechicero Legendario — Guerrero Oscuro',
            specialMove: 'Conjuro Ancestral de Sombras Preternianas',
            lore: 'Antiguo y enigmático hechicero oscuro de la era preterniana, maestro de las artes arcanas prohibidas y guardián de hechizos milenarios.',
            stats: { fuerza: 88, magia: 99, defensa: 85, agilidad: 88 }
        }
    },
    {
        match: /\bhe[\s\-]?ro\b/i,
        profile: {
            themeKey: 'cosmic_enforcers',
            faction: 'Guardianes Cósmicos',
            typeLine: 'Mago Preterniano — Ancestro de Grayskull',
            specialMove: 'Magia Ancestral de Preternia',
            lore: 'El Mago más poderoso del Universo en la remota Preternia. Portador del báculo con la piedra de la sabiduría y ancestro del poder de Grayskull.',
            stats: { fuerza: 92, magia: 99, defensa: 94, agilidad: 93 }
        }
    },
    {
        match: /\beldor\b/i,
        profile: {
            themeKey: 'cosmic_enforcers',
            faction: 'Guardianes Cósmicos',
            typeLine: 'Sabio de Preternia — Custodio del Libro',
            specialMove: 'Sabiduría de los Antiguos',
            lore: 'Antiguo sabio de Preternia y mentor de He-Ro, guardián del Libro de los Hechizos Vivientes que salvaguarda la historia secreta.',
            stats: { fuerza: 85, magia: 98, defensa: 90, agilidad: 86 }
        }
    },
    {
        match: /\bzodac\b|\bzodak\b/i,
        profile: {
            themeKey: 'cosmic_enforcers',
            faction: 'Guardianes Cósmicos',
            typeLine: 'Ejecutor Cósmico — Juez del Equilibrio',
            specialMove: 'Descarga Cósmica de Zodac',
            lore: 'Enforcer Cósmico neutral que vela por el equilibrio universal entre la luz y las sombras con su sabiduría e intelecto infinitos.',
            stats: { fuerza: 90, magia: 95, defensa: 92, agilidad: 91 }
        }
    },

    // -------------------------------------------------------------
    // GUERREROS HEROICOS (CASTLE GRAYSKULL)
    // -------------------------------------------------------------
    {
        match: /\bhe[\s\-]?man\b|\bprince\s+adam\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Campeón Legendario — Guerrero Heroico',
            specialMove: 'Por el Poder de Grayskull',
            lore: '¡Por el poder de Grayskull, yo tengo el poder! El hombre más poderoso del universo y defensor eterno de los secretos del castillo.',
            stats: { fuerza: 99, magia: 88, defensa: 95, agilidad: 90 }
        }
    },
    {
        match: /\bsorceress\b|\bhechicera\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Guardiana Mística — Guerrera Heroica',
            specialMove: 'Escudo del Halcón Místico',
            lore: 'Custodia inmortal del Castillo Grayskull y canalizadora de la magia más poderosa de Eternia bajo el manto de Zoar.',
            stats: { fuerza: 80, magia: 99, defensa: 92, agilidad: 89 }
        }
    },
    {
        match: /\bman[\s\-]?at[\s\-]?arms\b|\bduncan\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Maestro de Armas — Guerrero Heroico',
            specialMove: 'Ráfaga Fotónica Man-At-Arms',
            lore: 'Duncan, maestro de armas de la corte real de Eternia e inventor genial de la tecnología defensiva de Grayskull.',
            stats: { fuerza: 91, magia: 75, defensa: 94, agilidad: 87 }
        }
    },
    {
        match: /\bteela\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Capitana de la Guardia — Guerrera Heroica',
            specialMove: 'Estocada Táctica de la Cobra',
            lore: 'Capitana de la Guardia Real y prodigio del combate cuerpo a cuerpo, destinada a heredar los secretos arcanos de Grayskull.',
            stats: { fuerza: 89, magia: 85, defensa: 90, agilidad: 94 }
        }
    },
    {
        match: /\bbattle\s+cat\b|\bcringer\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Felino Blindado — Guerrero Heroico',
            specialMove: 'Desgarro Feroz de la Selva Carmesí',
            lore: 'El fiel corcel acorazado de He-Man, valiente tigre de combate de Grayskull dotado de garras y colmillos titánicos.',
            stats: { fuerza: 95, magia: 70, defensa: 93, agilidad: 95 }
        }
    },
    {
        match: /\bram[\s\-]?man\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Ariete Humano — Guerrero Heroico',
            specialMove: 'Impacto de Ariete Inamovible',
            lore: 'El ariete humano de Eternia, cuya armadura reforzada y coraje demoledor pueden derribar cualquier fortaleza enemiga.',
            stats: { fuerza: 94, magia: 60, defensa: 98, agilidad: 75 }
        }
    },
    {
        match: /\bstratos\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Señor de Avion — Guerrero Heroico',
            specialMove: 'Picado Aéreo de Avion',
            lore: 'Líder de los guerreros alados de Avion y señor de las corrientes aéreas que vigila los cielos de Eternia.',
            stats: { fuerza: 88, magia: 72, defensa: 87, agilidad: 98 }
        }
    },
    {
        match: /\bfisto\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Guerrero Titánico — Guerrero Heroico',
            specialMove: 'Golpe Demoledor de Murallas',
            lore: 'Luchador legendario cuyo puño metálico gigante es capaz de quebrar montañas y aplastar la maquinaria del mal.',
            stats: { fuerza: 96, magia: 65, defensa: 92, agilidad: 84 }
        }
    },
    {
        match: /\bmoss\s+man\b/i,
        profile: {
            themeKey: 'castle_grayskull',
            faction: 'Guerreros Heroicos',
            typeLine: 'Señor de la Naturaleza — Guerrero Heroico',
            specialMove: 'Crecimiento de Raíces Primitivas',
            lore: 'Espíritu ancestral de la flora y los bosques eternianos, maestro del camuflaje y comunión con el mundo vegetal.',
            stats: { fuerza: 90, magia: 92, defensa: 88, agilidad: 89 }
        }
    },

    // -------------------------------------------------------------
    // GUERREROS DEL MAL (SNAKE MOUNTAIN)
    // -------------------------------------------------------------
    {
        match: /\bskeletor\b|\bkeldor\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Señor de la Destrucción — Guerrero Diabólico',
            specialMove: 'Rayo Destructor del Báculo de Havoc',
            lore: 'Señor de la destrucción y tirano nigromántico de Snake Mountain cuya sed insaciable de conquista amenaza el multiverso.',
            stats: { fuerza: 93, magia: 99, defensa: 91, agilidad: 88 }
        }
    },
    {
        match: /\bevil[\s\-]?lyn\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Hechicera de Subternia — Guerrera Diabólica',
            specialMove: 'Tormenta Ilusoria de Subternia',
            lore: 'Nigromante y hechicera suprema de Subternia, cuyas profecías y magia oscura rivalizan con el poder de Grayskull.',
            stats: { fuerza: 82, magia: 98, defensa: 86, agilidad: 91 }
        }
    },
    {
        match: /\bbeast[\s\-]?man\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Señor de las Bestias — Guerrero Diabólico',
            specialMove: 'Zarpazo Titánico de la Jungla',
            lore: 'Sus garras desgarran, su voluntad domina. El Señor de las Bestias de la Montaña de la Serpiente controla a las criaturas más temibles.',
            stats: { fuerza: 93, magia: 70, defensa: 89, agilidad: 87 }
        }
    },
    {
        match: /\btrap[\s\-]?jaw\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Ciborg de Combate — Guerrero Diabólico',
            specialMove: 'Mordisco de Mandíbula de Acero',
            lore: 'Ciborg armado con mandíbula de acero indestructible y brazo multifunción con armamento intercambiable letal.',
            stats: { fuerza: 92, magia: 65, defensa: 95, agilidad: 85 }
        }
    },
    {
        match: /\btri[\s\-]?klops\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Cazador Letal — Guerrero Diabólico',
            specialMove: 'Láser Óptico de Rastreo Letal',
            lore: 'Visor omnisciente de Snake Mountain dotado de visión gamma, nocturna y rastreo óptico infrarrojo infalible.',
            stats: { fuerza: 89, magia: 78, defensa: 88, agilidad: 93 }
        }
    },
    {
        match: /\bmer[\s\-]?man\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Señor del Océano — Guerrero Diabólico',
            specialMove: 'Tsunami de las Profundidades de Rakash',
            lore: 'Soberano de los océanos de Rakash y señor de las profundidades acuáticas de Eternia, capaz de invocar bestias abisales.',
            stats: { fuerza: 90, magia: 85, defensa: 89, agilidad: 90 }
        }
    },
    {
        match: /\bclawful\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Criatura Legendaria — Guerrero Diabólico',
            specialMove: 'Presa Hidráulica Trituradora',
            lore: 'Combatiente despiadado de las legiones oscuras de Snake Mountain al servicio de Skeletor. Su pinza titánica pulveriza cualquier aleación.',
            stats: { fuerza: 92, magia: 68, defensa: 89, agilidad: 86 }
        }
    },
    {
        match: /\bfaker\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Gólem Cibernético — Guerrero Diabólico',
            specialMove: 'Réplica Macabra de Combate',
            lore: 'Gólem cibernético de piel azul creado por Skeletor como una réplica despiadada de He-Man para engañar al reino.',
            stats: { fuerza: 98, magia: 60, defensa: 94, agilidad: 89 }
        }
    },
    {
        match: /\bscare[\s\-]?glow\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Espectro de la Oscuridad — Guerrero Diabólico',
            specialMove: 'Terror Paralizante de Subternia',
            lore: 'Espectro no-muerto de la oscuridad eterna que infunde un terror paralizante en el corazón de cualquier guerrero.',
            stats: { fuerza: 87, magia: 97, defensa: 85, agilidad: 92 }
        }
    },
    {
        match: /\bwhiplash\b/i,
        profile: {
            themeKey: 'snake_mountain',
            faction: 'Guerreros del Mal',
            typeLine: 'Reptil de Asalto — Guerrero Diabólico',
            specialMove: 'Azote Ofídico Venenoso',
            lore: 'Bruto reptiliano con una cola descomunal capaz de aplastar roca sólida y azotar batallones enteros en combate.',
            stats: { fuerza: 94, magia: 60, defensa: 92, agilidad: 86 }
        }
    },

    // -------------------------------------------------------------
    // LA HORDA DEL TERROR (EVIL HORDE)
    // -------------------------------------------------------------
    {
        match: /\bhordak\b/i,
        profile: {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Tirano Legendario — Líder de la Horda',
            specialMove: 'Flecha de Plasma Carmesí de la Horda',
            lore: 'Tirano supremo de la Zona del Terror y maestro de la tecno-magia oscura, capaz de transmutar su propio cuerpo en armamento mecánico mortal.',
            stats: { fuerza: 95, magia: 96, defensa: 95, agilidad: 87 }
        }
    },
    {
        match: /\bshadow\s+weaver\b/i,
        profile: {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Hechicera de las Sombras — Horda del Terror',
            specialMove: 'Niebla de Sombras Eternas',
            lore: 'Poderosa maga oscura de la Horda del Terror, capaz de manipular la oscuridad y tejer maleficios desde la Zona del Terror.',
            stats: { fuerza: 78, magia: 99, defensa: 85, agilidad: 88 }
        }
    },
    {
        match: /\bcatra\b/i,
        profile: {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Capitana de la Fuerza — Horda del Terror',
            specialMove: 'Transformación Felina de la Máscara',
            lore: 'Líder de asalto de la Horda dotada de la máscara mágica que le permite transformarse en una pantera salvaje letal.',
            stats: { fuerza: 88, magia: 87, defensa: 86, agilidad: 98 }
        }
    },
    {
        match: /\bgrizzlor\b/i,
        profile: {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Bestia Brutal — Horda del Terror',
            specialMove: 'Furia Salvaje Destructora',
            lore: 'Monstruo fiero cubierto de pelaje con una fuerza física descomunal capaz de aplastar cualquier obstáculo.',
            stats: { fuerza: 96, magia: 50, defensa: 94, agilidad: 82 }
        }
    },
    {
        match: /\bmantenna\b|\bleech\b|\bscorpia\b|\bmosquitor\b|\bmodulok\b|\bdragstor\b|\bmulti[\s\-]?bot\b/i,
        profile: {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Monstruo Tecnológico — Soldado de la Horda',
            specialMove: 'Descarga de Plasma de la Horda',
            lore: 'Soldado aberrante y bio-mecánico forjado en los laboratorios oscuros de Hordak para conquistar Eternia y Etheria.',
            stats: { fuerza: 91, magia: 80, defensa: 90, agilidad: 88 }
        }
    },

    // -------------------------------------------------------------
    // LOS HOMBRES SERPIENTE (SNAKE MEN)
    // -------------------------------------------------------------
    {
        match: /\bking\s+hiss\b|\bking\s+hsss\b/i,
        profile: {
            themeKey: 'snake_men',
            faction: 'Los Hombres Serpiente',
            typeLine: 'Monarca Ofídico — Rey de las Serpientes',
            specialMove: 'Mordisco Asfixiante del Rey Hiss',
            lore: 'Antiquísimo monarca ofídico cuyo disfraz oculta una masa de serpientes devoradoras. Regresa del pasado para dominar Eternia.',
            stats: { fuerza: 93, magia: 95, defensa: 91, agilidad: 93 }
        }
    },
    {
        match: /\bkobra\s+khan\b|\bkhan\b/i,
        profile: {
            themeKey: 'snake_men',
            faction: 'Los Hombres Serpiente',
            typeLine: 'Guerrero Reptil — Hombre Serpiente',
            specialMove: 'Chorro Ácido Corrosivo',
            lore: 'Astuto guerrero ofídico capaz de exhalar una niebla somnífera y corrosiva mortal para cualquier adversario.',
            stats: { fuerza: 90, magia: 82, defensa: 88, agilidad: 92 }
        }
    },
    {
        match: /\brattlor\b|\btung\s+lashr\b|\bsssqueeze\b|\bsnake\s+face\b/i,
        profile: {
            themeKey: 'snake_men',
            faction: 'Los Hombres Serpiente',
            typeLine: 'Guerrero Ofídico — Hombre Serpiente',
            specialMove: 'Picadura Venenosa Ancestral',
            lore: 'Guerrero letal de las huestes ofídicas del Foso de las Serpientes devoto a la dominación reptiliana.',
            stats: { fuerza: 91, magia: 85, defensa: 89, agilidad: 91 }
        }
    },

    // -------------------------------------------------------------
    // LA GRAN REBELIÓN (GREAT REBELLION / SHE-RA)
    // -------------------------------------------------------------
    {
        match: /\bshe[\s\-]?ra\b/i,
        profile: {
            themeKey: 'great_rebellion',
            faction: 'La Gran Rebelión',
            typeLine: 'Princesa del Poder — Gran Rebelión',
            specialMove: 'Por el Honor de Grayskull',
            lore: '¡Por el honor de Grayskull, soy She-Ra! Princesa del Poder y líder invicta de la Gran Rebelión en Etheria con su fiel corcel Swift Wind.',
            stats: { fuerza: 98, magia: 94, defensa: 95, agilidad: 96 }
        }
    },
    {
        match: /\bbow\b|\bglimmer\b|\bfrosta\b|\bangella\b|\bmermista\b|\bcastaspella\b|\bnetossa\b|\bkowl\b/i,
        profile: {
            themeKey: 'great_rebellion',
            faction: 'La Gran Rebelión',
            typeLine: 'Aliado de la Luz — Gran Rebelión',
            specialMove: 'Ráfaga de Luz de Etheria',
            lore: 'Valiente protector de Etheria y miembro insigne de la Gran Rebelión que combate la tiranía de la Horda del Terror.',
            stats: { fuerza: 88, magia: 92, defensa: 89, agilidad: 92 }
        }
    }
];

// Resolver canónico determinista para la interfaz local
const getLocalMotuProfile = (productName: string, _subCategory?: string): MotuProfile => {
    const clean = (productName || '').trim();

    for (const entry of MOTU_CHARACTER_PROFILES) {
        if (entry.match.test(clean)) {
            return entry.profile;
        }
    }

    // Default: Guerrero Heroico Genérico (Castle Grayskull)
    return {
        themeKey: 'castle_grayskull',
        faction: 'Guerreros Heroicos',
        typeLine: 'Criatura Legendaria — Guerrero Heroico',
        specialMove: 'Furia del Relámpago de Grayskull',
        lore: '¡Por el poder de Grayskull, yo tengo el poder! Noble defensor de la corte real de Eternia y custodio de la paz sagrada de Grayskull.',
        stats: { fuerza: 88, magia: 78, defensa: 95, agilidad: 90 }
    };
};

// Formateador inteligente de título para cartas coleccionables
const formatCardTitle = (rawName: string) => {
    if (!rawName) return { main: 'FIGURA MOTU', sub: '' };
    const clean = rawName.trim();
    const match = clean.match(/^(.*?)\s*[\(\-\[]\s*(200x|cartoon|origins|masterverse|vintage|new eternia|revelation|club grayskull|commemorative|classics|cgc|moc|loose|deluxe).*?[\)\-\]]?$/i);
    if (match && match[1].trim().length >= 3) {
        return {
            main: match[1].trim(),
            sub: clean.substring(match[1].length).replace(/^[\s\(\-\[]+|[\s\)\-\]]+$/g, '').trim()
        };
    }
    return { main: clean, sub: '' };
};

// Convertidor de DataURL base64 a Blob nativo
const dataUrlToBlob = async (dataUrl: string): Promise<Blob> => {
    const res = await fetch(dataUrl);
    return await res.blob();
};

// Obtiene la imagen individual pura con el encuadre y zoom personalizados como DataURL HD sin márgenes
const getSingleIllustrationDataUrl = async (
    item: any,
    aiImageBase64?: string | null,
    zoom: number = 1,
    pan: { x: number; y: number } = { x: 0, y: 0 }
): Promise<string> => {
    const targetSrc = aiImageBase64 || item.image_url;
    if (!targetSrc) return '';

    return new Promise((resolve) => {
        const img = new window.Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            // Si no hay transformaciones y es una imagen AI pura, exportamos directamente la imagen pura
            if (zoom === 1 && pan.x === 0 && pan.y === 0 && aiImageBase64) {
                resolve(aiImageBase64);
                return;
            }

            const canvas = document.createElement('canvas');
            // Usamos las dimensiones intrínsecas de la ilustración o un estándar HD 3:4 vertical
            const outW = img.naturalWidth || 1024;
            const outH = img.naturalHeight || 1365;
            canvas.width = outW;
            canvas.height = outH;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, outW, outH);

                ctx.save();
                // Escalamos el paneo relativo a las dimensiones del contenedor en pantalla (~320px)
                const scaleFactorX = outW / 320;
                const scaleFactorY = outH / 240;
                ctx.translate(outW / 2 + pan.x * scaleFactorX, outH / 2 + pan.y * scaleFactorY);
                ctx.scale(zoom, zoom);

                // Dibujar la imagen centrada exactamente en sus dimensiones reales
                ctx.drawImage(img, -outW / 2, -outH / 2, outW, outH);
                ctx.restore();

                try {
                    resolve(canvas.toDataURL('image/png'));
                } catch {
                    resolve(targetSrc);
                }
            } else {
                resolve(targetSrc);
            }
        };
        img.onerror = () => resolve(targetSrc);
        img.src = targetSrc;
    });
};

// Generador de Cromo PNG de Alta Fidelidad mediante html-to-image con Canvas 2D Fallback
const generateTradingCardDataUrl = async (
    node: HTMLElement,
    item: any,
    activeImageSrc?: string,
    aiLore?: string | null,
    profileData?: any
): Promise<string> => {
    try {
        return await toPng(node, {
            pixelRatio: 2.5,
            skipFonts: false,
            cacheBust: false,
            filter: (domNode) => {
                if (domNode instanceof HTMLElement && domNode.classList.contains('export-exclude')) {
                    return false;
                }
                return true;
            },
            style: { transform: 'none' }
        });
    } catch (e1) {
        console.warn('html-to-image falló, ejecutando motor de composición directa por Canvas HD:', e1);

        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return reject('No se pudo inicializar contexto Canvas 2D');

            const width = 896;
            const height = 1200;
            canvas.width = width;
            canvas.height = height;

            const rawCardTitle = profileData?.cardTitle || item.product_name || item.name || 'HE-MAN';
            const titleParts = formatCardTitle(rawCardTitle);
            const themeKey = profileData?.themeKey || 'castle_grayskull';
            const layout = profileData?.layout || FACTION_CARD_LAYOUTS[themeKey] || FACTION_CARD_LAYOUTS.castle_grayskull;
            const rawLore = aiLore || profileData?.lore || '¡Por el poder de Grayskull, la justicia siempre prevalecerá!';
            const loreText = rawLore.replace(/^["';\s]+/, '').replace(/["';\s]+$/, '');
            const stats = profileData?.stats || { fuerza: 99, magia: 88, defensa: 95, agilidad: 90 };
            const frameSrc = profileData?.frameAsset || `/frames/frame_castle_grayskull.webp?${FRAME_CACHE_VERSION}`;

            // 1. Fondo base
            ctx.fillStyle = '#060a0f';
            ctx.fillRect(0, 0, width, height);

            const renderOverlayAndText = () => {
                // Marco WebP
                const frameImg = new Image();
                frameImg.crossOrigin = 'anonymous';
                frameImg.onload = () => {
                    ctx.drawImage(frameImg, 0, 0, width, height);

                    // 2. Tipografía en placa de cabecera (individual por facción)
                    ctx.fillStyle = '#ffffff';
                    ctx.font = '900 26px serif';
                    ctx.textAlign = 'left';
                    ctx.fillText(titleParts.main.toUpperCase(), layout.canvas.header.x, layout.canvas.header.y);

                    if (titleParts.sub) {
                        ctx.fillStyle = '#fde68a';
                        ctx.font = 'bold 15px serif';
                        ctx.fillText(`• ${titleParts.sub.toUpperCase()}`, layout.canvas.header.x + ctx.measureText(titleParts.main.toUpperCase()).width + 12, layout.canvas.header.y);
                    }

                    // 3. Flavor Lore Canónico en Cursiva (En el centro de la losa de texto)
                    ctx.textAlign = 'center';
                    ctx.fillStyle = profileData?.loreTextColor || '#f5f5f0';
                    ctx.font = `italic ${layout.canvas.loreText.fontSize || 17}px serif`;
                    const words = `"${loreText}"`.split(' ');
                    let line = '';
                    let yPos = layout.canvas.loreText.y;
                    for (let n = 0; n < words.length; n++) {
                        const testLine = line + words[n] + ' ';
                        const metrics = ctx.measureText(testLine);
                        if (metrics.width > layout.canvas.loreText.maxW && n > 0) {
                            ctx.fillText(line.trim(), width / 2, yPos);
                            line = words[n] + ' ';
                            yPos += layout.canvas.loreText.lineH;
                        } else {
                            line = testLine;
                        }
                    }
                    ctx.fillText(line.trim(), width / 2, yPos);

                    // 4. Engarces de Combate 3D Nativos (4 Orbes Esculpidos en el Marco)
                    const drawStatOnOrb = (
                        cx: number,
                        cy: number,
                        statLabel: string,
                        statVal: number,
                        labelColor: string
                    ) => {
                        ctx.save();
                        ctx.textAlign = 'center';

                        // Nivel 1: Etiqueta superior
                        ctx.fillStyle = labelColor;
                        ctx.font = '900 11px sans-serif';
                        ctx.shadowColor = 'rgba(0,0,0,1)';
                        ctx.shadowBlur = 4;
                        ctx.fillText(statLabel, cx, cy - 5);

                        // Nivel 2: Número de Combate en Relieve Blanco / Oro
                        ctx.fillStyle = '#ffffff';
                        ctx.font = '900 20px serif';
                        ctx.shadowColor = 'rgba(0,0,0,0.95)';
                        ctx.shadowBlur = 6;
                        ctx.fillText(String(statVal), cx, cy + 15);
                        ctx.restore();
                    };

                    const posFue = layout.canvas.statFue || { x: 190, y: 1046 };
                    const posMag = layout.canvas.statMag || { x: 308, y: 1046 };
                    const posDef = layout.canvas.statDef || { x: 588, y: 1046 };
                    const posAgi = layout.canvas.statAgi || { x: 706, y: 1046 };

                    drawStatOnOrb(posFue.x, posFue.y, 'FUE', stats.fuerza, '#fca5a5');
                    drawStatOnOrb(posMag.x, posMag.y, 'MAG', stats.magia, '#d8b4fe');
                    drawStatOnOrb(posDef.x, posDef.y, 'DEF', stats.defensa, '#7dd3fc');
                    drawStatOnOrb(posAgi.x, posAgi.y, 'AGI', stats.agilidad, '#86efac');

                    resolve(canvas.toDataURL('image/png'));
                };
                frameImg.onerror = () => {
                    resolve(canvas.toDataURL('image/png'));
                };
                frameImg.src = frameSrc;
            };

            const targetImgUrl = activeImageSrc || item.image_url;
            if (targetImgUrl) {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = () => {
                    try {
                        const drawX = 72;
                        const drawY = 66;
                        const drawW = 752;
                        const drawH = 600;
                        ctx.drawImage(img, drawX, drawY, drawW, drawH);
                    } catch {}
                    renderOverlayAndText();
                };
                img.onerror = () => renderOverlayAndText();
                img.src = targetImgUrl;
            } else {
                renderOverlayAndText();
            }
        });
    }
};

export const TradingCardModal: React.FC<TradingCardModalProps> = ({ isOpen, onClose, item }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [exporting, setExporting] = useState(false);
    const [copied, setCopied] = useState(false);
    const [shared, setShared] = useState(false);
    const [downloaded, setDownloaded] = useState(false);
    const [rotateX, setRotateX] = useState(0);
    const [rotateY, setRotateY] = useState(0);
    const [glarePos, setGlarePos] = useState({ x: 50, y: 50, opacity: 0 });

    // Estado para la transformación mágica con Gemini
    const [showAiDrawer, setShowAiDrawer] = useState(false);
    const [aiResult, setAiResult] = useState<CardAiEnhanceResult | null>(null);
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [aiError, setAiError] = useState<string | null>(null);

    // Estado para selector dual de exportación (Carta Completa vs Solo Ilustración)
    const [exportTarget, setExportTarget] = useState<'card' | 'image'>('card');

    // Estado para Encuadre y Zoom interactivo de la imagen
    const [imgZoom, setImgZoom] = useState<number>(1);
    const [imgPan, setImgPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
    const [isDraggingImg, setIsDraggingImg] = useState(false);
    const dragStartRef = useRef<{ x: number; y: number; startPanX: number; startPanY: number }>({
        x: 0,
        y: 0,
        startPanX: 0,
        startPanY: 0
    });
    const touchStartRef = useRef<{ dist: number; startZoom: number; x: number; y: number; startPanX: number; startPanY: number }>({
        dist: 0,
        startZoom: 1,
        x: 0,
        y: 0,
        startPanX: 0,
        startPanY: 0
    });

    const resetFraming = () => {
        setImgZoom(1);
        setImgPan({ x: 0, y: 0 });
    };

    // Selector interactivo de bando y layouts dinámicos
    const [userFactionOverride, setUserFactionOverride] = useState<string | null>(null);
    const [customLayouts, setCustomLayouts] = useState<Record<string, any>>(DEFAULT_FACTION_CARD_LAYOUTS);

    // Selector de versión de carta (Showcase Full-Art por defecto vs Clásica 3D)
    const [cardVersion, setCardVersion] = useState<'showcase' | 'classic'>('showcase');

    // Estado para edición libre de textos y atributos del cromo
    const [isEditingTexts, setIsEditingTexts] = useState<boolean>(false);
    const [customCardName, setCustomCardName] = useState<string>('');
    const [customSubtitle, setCustomSubtitle] = useState<string>('');
    const [customManaCost, setCustomManaCost] = useState<string>('');
    const [customSpecialMove, setCustomSpecialMove] = useState<string>('');
    const [customLore, setCustomLore] = useState<string>('');
    const [customQuoteAuthor, setCustomQuoteAuthor] = useState<string>('');
    const [customTypeLine, setCustomTypeLine] = useState<string>('');
    const [customTextColor, setCustomTextColor] = useState<string>('#FFFFFF');
    const [customStats, setCustomStats] = useState<{ fuerza: number; magia: number; defensa: number; agilidad: number } | null>(null);
    const [dbLoreChar, setDbLoreChar] = useState<CharacterLore | null>(null);
    const [savingDbLore, setSavingDbLore] = useState<boolean>(false);
    const [loreSaveSuccess, setLoreSaveSuccess] = useState<boolean>(false);
    const [isHarvestingLore, setIsHarvestingLore] = useState<boolean>(false);
    const [isRefreshingImage, setIsRefreshingImage] = useState<boolean>(false);
    const [activeImageOverride, setActiveImageOverride] = useState<string | null>(null);

    // Cargar personalización persistente al abrir la carta
    React.useEffect(() => {
        if (!isOpen || !item) return;

        const savedKey = `tcg_custom_card_${item.id}`;
        const savedCustom = localStorage.getItem(savedKey);
        if (savedCustom) {
            try {
                const parsed = JSON.parse(savedCustom);
                setCardVersion(parsed.cardVersion || 'showcase');
                setCustomCardName(parsed.customCardName || '');
                setCustomSubtitle(parsed.customSubtitle || '');
                setCustomManaCost(parsed.customManaCost || '');
                setCustomSpecialMove(parsed.customSpecialMove || '');
                setCustomLore(parsed.customLore || '');
                setCustomQuoteAuthor(parsed.customQuoteAuthor || '');
                setCustomTypeLine(parsed.customTypeLine || '');
                setCustomTextColor(parsed.customTextColor || '#FFFFFF');
                setCustomStats(parsed.customStats || null);
                setUserFactionOverride(parsed.userFactionOverride || null);
                if (typeof parsed.imgZoom === 'number') setImgZoom(parsed.imgZoom);
                if (parsed.imgPan && typeof parsed.imgPan.x === 'number') setImgPan(parsed.imgPan);
            } catch (e) {
                console.error('Error cargando personalización guardada de la carta:', e);
            }
        } else {
            // Predeterminados según categoría de la línea
            const subCat = (item.sub_category || '').toLowerCase();
            let defaultType = 'Criatura Legendaria — Guerrero';
            let defaultMove = 'Poder de Ataque Épico';
            if (subCat.includes('beast') || subCat.includes('vehicle') || subCat.includes('playset')) {
                defaultType = 'Artefacto — Equipo / Vehículo';
                defaultMove = 'Aporta asistencia táctica y +2/+0 a criaturas aliadas.';
            } else if (subCat.includes('deluxe') || subCat.includes('exclusive')) {
                defaultType = 'Criatura Legendaria Mítica — Campeón de Grayskull';
            }

            setCardVersion('showcase');
            setUserFactionOverride(null);
            setCustomCardName('');
            setCustomSubtitle('');
            setCustomManaCost('');
            setCustomSpecialMove(defaultMove);
            setCustomLore('');
            setCustomQuoteAuthor('');
            setCustomTypeLine(defaultType);
            setCustomTextColor('#FFFFFF');
            setCustomStats(null);
            setImgZoom(1);
            setImgPan({ x: 0, y: 0 });
        }

        setIsEditingTexts(false);
        setDbLoreChar(null);

        const stored = localStorage.getItem('tcg_card_layouts');
        if (stored) {
            try { setCustomLayouts(JSON.parse(stored)); } catch {}
        }
        getSystemTcgLayouts().then(remote => {
            if (remote && Object.keys(remote).length > 0) {
                setCustomLayouts(prev => ({ ...prev, ...remote }));
            }
        }).catch(() => {});

        // Cargar ficha canónica de lore desde la BD
        const rawName = item.product_name || item.name || '';
        fetchCharacterLoreList({ search: rawName, limit: 5 }).then(res => {
            if (res && res.items && res.items.length > 0) {
                const best = res.items[0];
                setDbLoreChar(best);
                if (best.subtitle && !customSubtitle) setCustomSubtitle(best.subtitle);
                if (best.flavor_quote_author && !customQuoteAuthor) setCustomQuoteAuthor(best.flavor_quote_author);
                if (best.text_color && customTextColor === '#FFFFFF') setCustomTextColor(best.text_color);
                if (best.mana_cost && !customManaCost) setCustomManaCost(best.mana_cost);
            }
        }).catch(() => {});
    }, [isOpen, item?.id]);

    // Guardar automáticamente cualquier cambio en la carta para mantenerlo fijo
    React.useEffect(() => {
        if (!isOpen || !item) return;

        const hasCustomization = Boolean(
            cardVersion !== 'showcase' ||
            customCardName ||
            customSubtitle ||
            customManaCost ||
            customSpecialMove ||
            customLore ||
            customQuoteAuthor ||
            customTypeLine ||
            customTextColor !== '#FFFFFF' ||
            customStats ||
            userFactionOverride ||
            imgZoom !== 1 ||
            imgPan.x !== 0 ||
            imgPan.y !== 0
        );

        const savedKey = `tcg_custom_card_${item.id}`;
        if (hasCustomization) {
            const dataToSave = {
                cardVersion,
                customCardName,
                customSubtitle,
                customManaCost,
                customSpecialMove,
                customLore,
                customQuoteAuthor,
                customTypeLine,
                customTextColor,
                customStats,
                userFactionOverride,
                imgZoom,
                imgPan
            };
            localStorage.setItem(savedKey, JSON.stringify(dataToSave));
        }
    }, [
        isOpen,
        item?.id,
        cardVersion,
        customCardName,
        customSubtitle,
        customManaCost,
        customSpecialMove,
        customLore,
        customQuoteAuthor,
        customTypeLine,
        customTextColor,
        customStats,
        userFactionOverride,
        imgZoom,
        imgPan
    ]);

    if (!isOpen || !item) return null;

    const name = item.product_name || item.name || 'Figura MOTU';
    const condition = (item.condition || 'MOC').toUpperCase();
    const grade = item.grading || 10.0;

    // Perfil canónico local y tema visual de facción dinámico
    const localProfile = getLocalMotuProfile(name, item.sub_category);
    const effectiveDbLore = dbLoreChar;
    const themeKey = userFactionOverride || aiResult?.frame_theme || effectiveDbLore?.theme_key || localProfile.themeKey;
    const theme = FACTION_VISUAL_THEMES[themeKey] || FACTION_VISUAL_THEMES.castle_grayskull;
    const layout = customLayouts[themeKey] || FACTION_CARD_LAYOUTS[themeKey] || FACTION_CARD_LAYOUTS.castle_grayskull;
    const factionName = userFactionOverride ? theme.faction : (aiResult?.faction || effectiveDbLore?.faction || localProfile.faction);

    // Textos computados con prioridad: Edición de usuario > IA > BD Lore > Perfil local
    const displayCardName = customCardName.trim() ? customCardName : (effectiveDbLore?.canonical_name || name);
    const displaySubtitle = customSubtitle.trim() ? customSubtitle : (effectiveDbLore?.subtitle || (item.sub_category ? `${item.sub_category} Edition` : 'Champion of Eternia'));
    const typeLineText = customTypeLine.trim() ? customTypeLine : (userFactionOverride ? theme.typeLine : (aiResult?.type_line || effectiveDbLore?.type_line || localProfile.typeLine));
    const specialMoveText = customSpecialMove.trim() ? customSpecialMove : (aiResult?.special_move || effectiveDbLore?.special_move || localProfile.specialMove);
    const rawLore = customLore.trim() ? customLore : (aiResult?.lore || effectiveDbLore?.lore || localProfile.lore);
    const loreText = rawLore.replace(/^["';\s]+/, '').replace(/["';\s]+$/, '');
    const displayQuoteAuthor = customQuoteAuthor.trim() ? customQuoteAuthor : (effectiveDbLore?.flavor_quote_author || effectiveDbLore?.canonical_name || displayCardName);
    const activeImage = activeImageOverride || aiResult?.image_base64 || item.image_url;

    // Coste de maná computado según facción y tipo
    const defaultManaCostByTheme: Record<string, string> = {
        castle_grayskull: '{2}{W}{W}',
        snake_mountain: '{2}{B}{B}',
        evil_horde: '{3}{B}{R}',
        snake_men: '{2}{B}{G}',
        great_rebellion: '{2}{G}{W}',
        cosmic_enforcers: '{2}{W}{U}'
    };
    const computedDefaultCost = (typeLineText.toLowerCase().includes('artefacto') || typeLineText.toLowerCase().includes('vehículo'))
        ? '{3}'
        : (defaultManaCostByTheme[themeKey] || '{2}{W}{W}');
    const displayManaCost = customManaCost.trim() ? customManaCost : (effectiveDbLore?.mana_cost || computedDefaultCost);

    const statsData = customStats || aiResult?.stats || (effectiveDbLore ? {
        fuerza: effectiveDbLore.fuerza,
        magia: effectiveDbLore.magia,
        defensa: effectiveDbLore.defensa,
        agilidad: effectiveDbLore.agilidad
    } : localProfile.stats);

    // Renderizador de Orbes de Maná de alta fidelidad estilo Secret Lair
    const renderManaCostPips = (costString: string) => {
        if (!costString) return null;
        const matches = costString.match(/\{[^}]+\}|[0-9]+|[WUBRGCwubrgc]/g);
        if (!matches) return null;

        return (
            <div className="flex items-center gap-1 shrink-0">
                {matches.map((pip, idx) => {
                    const clean = pip.replace(/[{}]/g, '').toUpperCase();
                    if (clean === 'W') {
                        return (
                            <div
                                key={idx}
                                className="w-4 h-4 rounded-full bg-gradient-to-br from-amber-100 via-amber-200 to-amber-400 border border-amber-300 shadow-[0_0_6px_rgba(251,191,36,0.6)] flex items-center justify-center text-[9px] font-black text-amber-950 leading-none select-none"
                                title="Maná Blanco / Grayskull (W)"
                            >
                                ☀️
                            </div>
                        );
                    }
                    if (clean === 'U') {
                        return (
                            <div
                                key={idx}
                                className="w-4 h-4 rounded-full bg-gradient-to-br from-sky-200 via-sky-400 to-blue-600 border border-sky-300 shadow-[0_0_6px_rgba(56,189,248,0.6)] flex items-center justify-center text-[9px] font-black text-white leading-none select-none"
                                title="Maná Azul / Místico (U)"
                            >
                                💧
                            </div>
                        );
                    }
                    if (clean === 'B') {
                        return (
                            <div
                                key={idx}
                                className="w-4 h-4 rounded-full bg-gradient-to-br from-stone-900 via-purple-950 to-black border border-purple-400 shadow-[0_0_6px_rgba(168,85,247,0.6)] flex items-center justify-center text-[9px] font-black text-purple-300 leading-none select-none"
                                title="Maná Negro / Mal (B)"
                            >
                                💀
                            </div>
                        );
                    }
                    if (clean === 'R') {
                        return (
                            <div
                                key={idx}
                                className="w-4 h-4 rounded-full bg-gradient-to-br from-orange-400 via-red-500 to-red-700 border border-red-300 shadow-[0_0_6px_rgba(239,68,68,0.6)] flex items-center justify-center text-[9px] font-black text-white leading-none select-none"
                                title="Maná Rojo / Horda (R)"
                            >
                                🔥
                            </div>
                        );
                    }
                    if (clean === 'G') {
                        return (
                            <div
                                key={idx}
                                className="w-4 h-4 rounded-full bg-gradient-to-br from-emerald-300 via-green-500 to-emerald-800 border border-emerald-300 shadow-[0_0_6px_rgba(34,197,94,0.6)] flex items-center justify-center text-[9px] font-black text-white leading-none select-none"
                                title="Maná Verde / Serpiente (G)"
                            >
                                🌲
                            </div>
                        );
                    }
                    return (
                        <div
                            key={idx}
                            className="w-4 h-4 rounded-full bg-gradient-to-b from-stone-700 to-stone-900 border border-stone-400/80 shadow-[0_0_4px_rgba(0,0,0,0.8)] flex items-center justify-center text-[10px] font-black font-sans text-stone-100 leading-none select-none"
                            title={`Maná Genérico: ${clean}`}
                        >
                            {clean}
                        </div>
                    );
                })}
            </div>
        );
    };

    const handleHarvestLoreFromWiki = async () => {
        if (!item) return;
        setIsHarvestingLore(true);
        try {
            const harvested = await harvestProductLore(item.id);
            if (harvested) {
                setDbLoreChar(harvested);
                setCustomCardName(harvested.canonical_name);
                if (harvested.subtitle) setCustomSubtitle(harvested.subtitle);
                if (harvested.type_line) setCustomTypeLine(harvested.type_line);
                if (harvested.special_move) setCustomSpecialMove(harvested.special_move);
                if (harvested.lore) setCustomLore(harvested.lore);
                if (harvested.flavor_quote_author) setCustomQuoteAuthor(harvested.flavor_quote_author);
                if (harvested.text_color) setCustomTextColor(harvested.text_color);
                if (harvested.mana_cost) setCustomManaCost(harvested.mana_cost);
                if (harvested.theme_key) setUserFactionOverride(harvested.theme_key);
                setLoreSaveSuccess(true);
                setTimeout(() => setLoreSaveSuccess(false), 3000);
            }
        } catch (e) {
            console.error('Error cosechando lore de Wiki Fandom:', e);
        } finally {
            setIsHarvestingLore(false);
        }
    };

    const handleRefreshImageFromAF411 = async () => {
        if (!item) return;
        setIsRefreshingImage(true);
        try {
            const res = await refreshProductImage(item.id);
            if (res && res.new_image_url) {
                setActiveImageOverride(res.new_image_url);
                resetFraming();
            }
        } catch (e) {
            console.error('Error refrescando imagen desde AF411:', e);
        } finally {
            setIsRefreshingImage(false);
        }
    };

    const handleSaveToLoreCanon = async () => {
        if (!dbLoreChar && !effectiveDbLore) return;
        const slug = dbLoreChar?.slug || effectiveDbLore?.slug;
        if (!slug) return;
        setSavingDbLore(true);
        try {
            const updated = await updateCharacterLore(slug, {
                canonical_name: customCardName.trim() || undefined,
                subtitle: customSubtitle.trim() || undefined,
                special_move: customSpecialMove.trim() || undefined,
                lore: customLore.trim() || undefined,
                flavor_quote_author: customQuoteAuthor.trim() || undefined,
                type_line: customTypeLine.trim() || undefined,
                text_color: customTextColor,
                card_version: cardVersion,
                mana_cost: customManaCost.trim() || undefined,
                fuerza: customStats?.fuerza,
                magia: customStats?.magia,
                defensa: customStats?.defensa,
                agilidad: customStats?.agilidad,
                theme_key: themeKey as any,
                faction: factionName
            });
            setDbLoreChar(updated);
            setLoreSaveSuccess(true);
            setTimeout(() => setLoreSaveSuccess(false), 3000);
        } catch (e) {
            console.error('Error al guardar en el canon:', e);
        } finally {
            setSavingDbLore(false);
        }
    };

    const handleResetCustomTexts = () => {
        if (item) {
            localStorage.removeItem(`tcg_custom_card_${item.id}`);
        }
        setCardVersion('showcase');
        setCustomCardName('');
        setCustomSubtitle('');
        setCustomManaCost('');
        setCustomSpecialMove('');
        setCustomLore('');
        setCustomQuoteAuthor('');
        setCustomTypeLine('');
        setCustomTextColor('#FFFFFF');
        setCustomStats(null);
        setUserFactionOverride(null);
        setActiveImageOverride(null);
        resetFraming();
    };

    // Manejo de giro 3D holográfico con el ratón
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotX = ((y - centerY) / centerY) * -10;
        const rotY = ((x - centerX) / centerX) * 10;

        setRotateX(rotX);
        setRotateY(rotY);
        setGlarePos({
            x: (x / rect.width) * 100,
            y: (y / rect.height) * 100,
            opacity: 0.55
        });
    };

    const handleMouseLeave = () => {
        setRotateX(0);
        setRotateY(0);
        setGlarePos((prev) => ({ ...prev, opacity: 0 }));
    };

    // Manejador de Transformación con Gemini
    const handleTransformWithAI = async (
        style: 'obrero_norem_80s' | 'alcala_texeira_minicomic' | 'gimenez_santalucia_modern' | 'heavy_metal_dark_eternia'
    ) => {
        try {
            setIsAiLoading(true);
            setAiError(null);
            const res = await enhanceCardWithAI({
                product_name: name,
                sub_category: item.sub_category,
                style,
                condition,
                grading: grade,
                image_url: item.image_url
            });
            setAiResult(res);
            resetFraming();
        } catch (err: any) {
            console.error('Error transformando con Gemini:', err);
            setAiError('No se pudo conectar con Gemini. Inténtalo de nuevo.');
        } finally {
            setIsAiLoading(false);
        }
    };

    // Control de Arrastre con Ratón
    const handleImgMouseDown = (e: React.MouseEvent) => {
        if (e.button !== 0) return;
        e.preventDefault();
        e.stopPropagation();
        setIsDraggingImg(true);
        dragStartRef.current = {
            x: e.clientX,
            y: e.clientY,
            startPanX: imgPan.x,
            startPanY: imgPan.y
        };
    };

    const handleImgMouseMove = (e: React.MouseEvent) => {
        if (!isDraggingImg) return;
        e.preventDefault();
        e.stopPropagation();
        const dx = e.clientX - dragStartRef.current.x;
        const dy = e.clientY - dragStartRef.current.y;
        setImgPan({
            x: dragStartRef.current.startPanX + dx,
            y: dragStartRef.current.startPanY + dy
        });
    };

    const handleImgMouseUp = (e: React.MouseEvent) => {
        if (isDraggingImg) {
            e.stopPropagation();
            setIsDraggingImg(false);
        }
    };

    // Control de Zoom con Rueda del Ratón (PC / Scroll)
    const handleImgWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        e.stopPropagation();
        const delta = e.deltaY < 0 ? 0.15 : -0.15;
        setImgZoom((prev) => Math.min(6.0, Math.max(0.2, +(prev + delta).toFixed(2))));
    };

    // Control Táctil (Móvil)
    const handleImgTouchStart = (e: React.TouchEvent) => {
        e.stopPropagation();
        if (e.touches.length === 1) {
            setIsDraggingImg(true);
            touchStartRef.current = {
                ...touchStartRef.current,
                x: e.touches[0].clientX,
                y: e.touches[0].clientY,
                startPanX: imgPan.x,
                startPanY: imgPan.y
            };
        } else if (e.touches.length === 2) {
            setIsDraggingImg(true);
            const dist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            touchStartRef.current = {
                dist,
                startZoom: imgZoom,
                x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
                y: (e.touches[0].clientY + e.touches[1].clientY) / 2,
                startPanX: imgPan.x,
                startPanY: imgPan.y
            };
        }
    };

    const handleImgTouchMove = (e: React.TouchEvent) => {
        if (!isDraggingImg) return;
        e.stopPropagation();
        if (e.touches.length === 1) {
            const dx = e.touches[0].clientX - touchStartRef.current.x;
            const dy = e.touches[0].clientY - touchStartRef.current.y;
            setImgPan({
                x: touchStartRef.current.startPanX + dx,
                y: touchStartRef.current.startPanY + dy
            });
        } else if (e.touches.length === 2 && touchStartRef.current.dist > 0) {
            const currentDist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            const scale = currentDist / touchStartRef.current.dist;
            setImgZoom(Math.min(6.0, Math.max(0.2, +(touchStartRef.current.startZoom * scale).toFixed(2))));
        }
    };

    const handleImgTouchEnd = (e: React.TouchEvent) => {
        e.stopPropagation();
        if (e.touches.length === 0) {
            setIsDraggingImg(false);
            touchStartRef.current.dist = 0;
        }
    };

    // 1. Descargar PNG HD
    const handleDownload = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            await new Promise((r) => setTimeout(r, 80));

            let dataUrl = '';
            let filename = '';

            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    cardTitle: displayCardName,
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor,
                    themeKey: themeKey,
                    layout: layout
                });
                filename = `Carta_TCG_${displayCardName.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${displayCardName.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            }

            if (!dataUrl) return;

            const link = document.createElement('a');
            link.download = filename;
            link.href = dataUrl;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setDownloaded(true);
            setTimeout(() => setDownloaded(false), 3000);
        } catch (err) {
            console.error('Error descargando:', err);
        } finally {
            setExporting(false);
        }
    };

    // 2. Copiar Imagen al Portapapeles
    const handleCopyImage = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            await new Promise((r) => setTimeout(r, 80));

            let dataUrl = '';
            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    cardTitle: displayCardName,
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor,
                    themeKey: themeKey,
                    layout: layout
                });
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
            }

            if (!dataUrl) return;
            const blob = await dataUrlToBlob(dataUrl);

            if (navigator.clipboard && (window as any).ClipboardItem) {
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);
                setCopied(true);
                setTimeout(() => setCopied(false), 3000);
            } else {
                handleDownload();
            }
        } catch (err) {
            console.error('Error copiando imagen:', err);
            handleDownload();
        } finally {
            setExporting(false);
        }
    };

    // 3. Compartir nativo
    const handleNativeShare = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            await new Promise((r) => setTimeout(r, 80));

            let dataUrl = '';
            let filename = '';

            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    cardTitle: displayCardName,
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor,
                    themeKey: themeKey,
                    layout: layout
                });
                filename = `Carta_TCG_${displayCardName.replace(/\s+/g, '_')}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${displayCardName.replace(/\s+/g, '_')}.png`;
            }

            if (!dataUrl) return;
            const blob = await dataUrlToBlob(dataUrl);
            const file = new File([blob], filename, { type: 'image/png' });

            let shareText = `🏰 Cromo Coleccionista: ${name}\n⚔️ Facción: ${factionName}\n⚡ Técnica: ${specialMoveText}`;
            if (loreText) shareText += `\n\n📜 "${loreText}"`;

            if (navigator.canShare && navigator.canShare({ files: [file] })) {
                await navigator.share({
                    title: `Cromo TCG: ${name}`,
                    text: shareText,
                    files: [file]
                });
                setShared(true);
                setTimeout(() => setShared(false), 3000);
            } else {
                const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;
                const waLink = document.createElement('a');
                waLink.href = waUrl;
                waLink.target = '_blank';
                waLink.rel = 'noopener noreferrer';
                document.body.appendChild(waLink);
                waLink.click();
                document.body.removeChild(waLink);

                setShared(true);
                setTimeout(() => setShared(false), 3000);
            }
        } catch (err) {
            console.error('Error compartiendo:', err);
        } finally {
            setExporting(false);
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[260] flex items-center justify-center p-3 sm:p-4 bg-black/90 backdrop-blur-2xl overflow-y-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.92, y: 15 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.92, y: 15 }}
                    className="relative w-full max-w-sm sm:max-w-md bg-gradient-to-b from-slate-900/95 via-slate-950 to-black border-2 border-amber-500/50 rounded-3xl shadow-[0_0_60px_rgba(0,0,0,0.9)] p-4 sm:p-5 text-white my-auto flex flex-col items-center"
                >
                    {/* Botón cerrar */}
                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 p-2 rounded-full bg-slate-800/90 hover:bg-red-500 text-slate-300 hover:text-white transition z-30 shadow-lg cursor-pointer"
                        title="Cerrar Cromo"
                    >
                        <X className="h-4 w-4" />
                    </button>

                    {/* Título y Selector de Formato de Carta */}
                    <div className="w-full flex flex-col items-center gap-2 mb-2.5">
                        <div className="flex items-center gap-2 text-center">
                            <Sparkles className="h-4 w-4 text-amber-400" />
                            <h2 className="text-xs sm:text-sm font-black uppercase tracking-widest text-amber-300 font-cinzel">
                                Cromo Coleccionista Digital
                            </h2>
                            <Sparkles className="h-4 w-4 text-amber-400" />
                        </div>

                        {/* SELECTOR DE EDICIÓN: SHOWCASE FULL-ART VS CLÁSICO 3D */}
                        <div className="w-full flex items-center justify-center p-1 rounded-xl bg-slate-950/90 border border-amber-500/30 gap-1.5 shadow-inner">
                            <button
                                type="button"
                                onClick={() => setCardVersion('showcase')}
                                className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[10.5px] font-black uppercase tracking-wider transition-all font-cinzel cursor-pointer ${
                                    cardVersion === 'showcase'
                                        ? 'bg-gradient-to-r from-amber-500 to-yellow-600 text-slate-950 shadow-md shadow-amber-500/30 font-black'
                                        : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                                }`}
                            >
                                <Sparkles className="h-3.5 w-3.5" />
                                <span>🌟 Full-Art Showcase</span>
                            </button>
                            <button
                                type="button"
                                onClick={() => setCardVersion('classic')}
                                className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[10.5px] font-black uppercase tracking-wider transition-all font-cinzel cursor-pointer ${
                                    cardVersion === 'classic'
                                        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/30 font-black'
                                        : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                                }`}
                            >
                                <Shield className="h-3.5 w-3.5" />
                                <span>🛡️ Marco Clásico 3D</span>
                            </button>
                        </div>
                    </div>

                    {/* BARRA DE TRANSFORMACIÓN CON GEMINI */}
                    <div className="w-full mb-3">
                        <button
                            onClick={() => setShowAiDrawer(!showAiDrawer)}
                            className="w-full py-1.5 px-3 rounded-xl bg-gradient-to-r from-purple-600/30 via-cyan-600/30 to-amber-600/30 hover:from-purple-600/40 hover:to-amber-600/40 border border-cyan-400/50 text-cyan-200 text-xs font-black uppercase tracking-wider flex items-center justify-between shadow-lg shadow-cyan-500/10 transition"
                        >
                            <span className="flex items-center gap-1.5 truncate font-cinzel">
                                <Wand2 className="h-3.5 w-3.5 text-yellow-300 animate-pulse shrink-0" />
                                <span className="truncate">{aiResult ? `✨ ${aiResult.style_name}` : '🪄 Ilustrar con Maestros MOTU'}</span>
                            </span>
                            <span className="text-[10px] text-cyan-300/80 font-mono shrink-0 ml-1">
                                {showAiDrawer ? '▲ Ocultar' : '▼ 4 Estilos'}
                            </span>
                        </button>

                        {/* Menú Desplegable de Estilos de Ilustradores MOTU */}
                        {showAiDrawer && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="mt-2 p-2 bg-slate-950/90 border border-cyan-500/30 rounded-xl grid grid-cols-2 gap-1.5 text-[10px]"
                            >
                                <button
                                    onClick={() => handleTransformWithAI('obrero_norem_80s')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Sparkles className="h-3 w-3 text-amber-400 shrink-0" />
                                        <span className="font-black font-cinzel">🎨 Óleo Box-Art 80s</span>
                                    </div>
                                    <span className="text-[8px] text-amber-400/70 font-normal">Rudy Obrero & Earl Norem</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('alcala_texeira_minicomic')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Zap className="h-3 w-3 text-cyan-400 shrink-0" />
                                        <span className="font-black font-cinzel">⚔️ Mini-Cómic 80s</span>
                                    </div>
                                    <span className="text-[8px] text-cyan-400/70 font-normal">Alfredo Alcala & Texeira</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('gimenez_santalucia_modern')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Award className="h-3 w-3 text-emerald-400 shrink-0" />
                                        <span className="font-black font-cinzel">✨ Cardback Moderno</span>
                                    </div>
                                    <span className="text-[8px] text-emerald-400/70 font-normal">Axel Gimenez & Santalucia</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('heavy_metal_dark_eternia')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <BookOpen className="h-3 w-3 text-purple-400 shrink-0" />
                                        <span className="font-black font-cinzel">🌌 Dark Fantasy MOTU</span>
                                    </div>
                                    <span className="text-[8px] text-purple-400/70 font-normal">Kenneth Rocafort & Bisley</span>
                                </button>

                                {aiResult && (
                                    <button
                                        onClick={() => setAiResult(null)}
                                        className="col-span-2 mt-1 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 font-bold flex items-center justify-center gap-1 transition"
                                    >
                                        <RotateCcw className="h-3 w-3" />
                                        <span>Restaurar Foto Original</span>
                                    </button>
                                )}
                            </motion.div>
                        )}

                        {isAiLoading && (
                            <div className="mt-2 py-1.5 px-3 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-200 text-[11px] font-bold flex items-center justify-center gap-2 animate-pulse font-cinzel">
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                <span>Recreando figura fuera del blíster con IA en Eternia...</span>
                            </div>
                        )}

                        {aiError && (
                            <div className="mt-1.5 text-center text-red-400 text-[10px]">
                                {aiError}
                            </div>
                        )}
                    </div>

                    {/* SELECTOR INTERACTIVO DE BANDO MOTU */}
                    <div className="w-full mb-2 flex items-center justify-between gap-1.5 p-1 bg-slate-950/80 border border-amber-500/20 rounded-xl overflow-x-auto custom-scrollbar">
                        <div className="flex items-center gap-1.5 shrink-0">
                            <span className="text-[9px] font-black uppercase text-amber-400/90 pl-1.5 shrink-0 flex items-center gap-1">
                                <Shield className="h-3 w-3 text-amber-400" /> Bando:
                            </span>
                            {[
                                { key: 'castle_grayskull', label: 'Heroicos', icon: '🏰' },
                                { key: 'snake_mountain', label: 'Del Mal', icon: '🌋' },
                                { key: 'evil_horde', label: 'Horda', icon: '🦇' },
                                { key: 'snake_men', label: 'Serpientes', icon: '🐍' },
                                { key: 'great_rebellion', label: 'Rebelión', icon: '✨' },
                                { key: 'cosmic_enforcers', label: 'Cósmicos', icon: '🌌' }
                            ].map(f => {
                                const isSelected = themeKey === f.key;
                                return (
                                    <button
                                        key={f.key}
                                        onClick={() => setUserFactionOverride(f.key)}
                                        className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[9.5px] font-black uppercase tracking-wider transition shrink-0 cursor-pointer ${
                                            isSelected
                                                ? 'bg-amber-500/25 border border-amber-400 text-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                                                : 'bg-white/5 border border-transparent text-white/60 hover:text-white hover:bg-white/10'
                                        }`}
                                        title={`Cambiar plantilla a ${f.label}`}
                                    >
                                        <span>{f.icon}</span>
                                        <span>{f.label}</span>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Botón de Abrir/Cerrar Editor de Textos y Poderes */}
                        <button
                            onClick={() => {
                                if (!isEditingTexts) {
                                    setCustomCardName(displayCardName);
                                    setCustomSubtitle(displaySubtitle);
                                    setCustomSpecialMove(specialMoveText);
                                    setCustomLore(loreText);
                                    setCustomQuoteAuthor(displayQuoteAuthor);
                                    setCustomTypeLine(typeLineText);
                                    setCustomStats({ ...statsData });
                                }
                                setIsEditingTexts(!isEditingTexts);
                            }}
                            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[9.5px] font-black uppercase tracking-wider transition shrink-0 cursor-pointer border ${
                                isEditingTexts
                                    ? 'bg-amber-500 text-slate-950 border-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.5)]'
                                    : 'bg-amber-500/15 border-amber-500/40 text-amber-300 hover:bg-amber-500/25'
                            }`}
                        >
                            <Edit3 className="h-3 w-3" />
                            <span>{isEditingTexts ? 'Cerrar Editor' : '✏️ Personalizar Textos'}</span>
                        </button>
                    </div>

                    {/* DRAWER INTERACTIVO DE EDICIÓN DE TEXTOS, CATEGORÍA Y PODERES */}
                    <AnimatePresence>
                        {isEditingTexts && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="w-full mb-3 p-3 bg-slate-900/95 border border-amber-500/40 rounded-xl shadow-2xl flex flex-col gap-2.5 overflow-hidden"
                            >
                                <div className="flex items-center justify-between border-b border-white/10 pb-1.5">
                                    <span className="text-[11px] font-black uppercase tracking-wider text-amber-300 flex items-center gap-1.5 font-cinzel">
                                        <Edit3 className="h-3.5 w-3.5 text-amber-400" />
                                        Personalización de la Carta Digital
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={handleResetCustomTexts}
                                            className="text-[9px] text-stone-400 hover:text-stone-200 underline flex items-center gap-1 cursor-pointer"
                                        >
                                            <RotateCcw className="h-2.5 w-2.5" />
                                            Restablecer
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                                    {/* 1. Nombre en la Carta */}
                                    <div>
                                        <label className="block text-[9px] font-bold uppercase text-amber-200/80 mb-0.5">
                                            Nombre en Carta:
                                        </label>
                                        <input
                                            type="text"
                                            value={customCardName}
                                            onChange={(e) => setCustomCardName(e.target.value)}
                                            placeholder={name}
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-white text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                        />
                                    </div>

                                    {/* 2. Subtítulo / Alter-Ego en Cursiva */}
                                    <div>
                                        <label className="block text-[9px] font-bold uppercase text-amber-200/80 mb-0.5">
                                            Subtítulo / Alter-Ego (Cursiva):
                                        </label>
                                        <input
                                            type="text"
                                            value={customSubtitle}
                                            onChange={(e) => setCustomSubtitle(e.target.value)}
                                            placeholder="Champion of Eternia / Lord of Destruction"
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-amber-300 text-xs italic font-serif focus:border-amber-400 focus:outline-none"
                                        />
                                    </div>

                                    {/* 3. Categoría / Línea de Tipo Libre */}
                                    <div>
                                        <label className="block text-[9px] font-bold uppercase text-amber-200/80 mb-0.5">
                                            Categoría / Línea de Tipo:
                                        </label>
                                        <input
                                            type="text"
                                            value={customTypeLine}
                                            onChange={(e) => setCustomTypeLine(e.target.value)}
                                            placeholder={typeLineText}
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-yellow-200 text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                        />
                                    </div>

                                    {/* 4. Poder / Habilidad Especial */}
                                    <div>
                                        <label className="block text-[9px] font-bold uppercase text-amber-200/80 mb-0.5">
                                            Poder / Habilidad:
                                        </label>
                                        <input
                                            type="text"
                                            value={customSpecialMove}
                                            onChange={(e) => setCustomSpecialMove(e.target.value)}
                                            placeholder={specialMoveText}
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-amber-300 text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                        />
                                    </div>

                                    {/* 5. Cita Célebre / Lore */}
                                    <div className="sm:col-span-2">
                                        <div className="flex justify-between items-center mb-0.5">
                                            <label className="text-[9px] font-bold uppercase text-amber-200/80">
                                                Cita Célebre / Lore Canónico:
                                            </label>
                                            <span className={`text-[9px] font-mono ${customLore.length > 200 ? 'text-amber-400 font-bold' : 'text-stone-400'}`}>
                                                {customLore.length}/200 car.
                                            </span>
                                        </div>
                                        <textarea
                                            value={customLore}
                                            onChange={(e) => setCustomLore(e.target.value)}
                                            placeholder={loreText}
                                            rows={2}
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-stone-200 text-xs leading-snug focus:border-amber-400 focus:outline-none resize-none italic font-serif"
                                        />
                                    </div>

                                    {/* 6. Autor de la Cita */}
                                    <div className="sm:col-span-2">
                                        <label className="block text-[9px] font-bold uppercase text-amber-200/80 mb-0.5">
                                            Autor de la Cita:
                                        </label>
                                        <input
                                            type="text"
                                            value={customQuoteAuthor}
                                            onChange={(e) => setCustomQuoteAuthor(e.target.value)}
                                            placeholder={displayCardName}
                                            className="w-full px-2 py-1 rounded bg-black/60 border border-slate-700 text-stone-300 text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                        />
                                    </div>

                                    {/* 7. Coste de Maná */}
                                    <div className="sm:col-span-2 flex flex-col gap-1.5 p-2 rounded-lg bg-black/50 border border-slate-700">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[9px] font-bold uppercase text-amber-200/90 flex items-center gap-1">
                                                ✨ Coste de Maná:
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-[9px] text-stone-400 font-mono">Actual:</span>
                                                {renderManaCostPips(displayManaCost)}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <input
                                                type="text"
                                                value={customManaCost}
                                                onChange={(e) => setCustomManaCost(e.target.value)}
                                                placeholder={computedDefaultCost}
                                                className="flex-1 px-2 py-1 rounded bg-black/60 border border-slate-700 text-white font-mono text-xs focus:border-amber-400 focus:outline-none"
                                            />
                                            <div className="flex items-center gap-1 shrink-0">
                                                {['{1}', '{2}', '{3}', '{W}', '{U}', '{B}', '{R}', '{G}'].map((sym) => (
                                                    <button
                                                        key={sym}
                                                        type="button"
                                                        onClick={() => setCustomManaCost((prev) => (prev ? `${prev}${sym}` : sym))}
                                                        className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-amber-500 hover:text-slate-950 border border-slate-700 text-[9px] font-bold font-mono transition cursor-pointer"
                                                        title={`Añadir ${sym}`}
                                                    >
                                                        {sym.replace(/[{}]/g, '')}
                                                    </button>
                                                ))}
                                                {customManaCost && (
                                                    <button
                                                        type="button"
                                                        onClick={() => setCustomManaCost('')}
                                                        className="px-1.5 py-0.5 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 text-[9px] font-bold border border-red-500/40 transition cursor-pointer"
                                                        title="Limpiar coste"
                                                    >
                                                        ✕
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* 8. Paleta de Colores para Zonas Translúcidas */}
                                    <div className="sm:col-span-2 flex items-center justify-between p-2 rounded-lg bg-black/50 border border-slate-700">
                                        <span className="text-[9px] font-bold uppercase text-amber-200/90 flex items-center gap-1">
                                            <Palette className="h-3 w-3 text-amber-400" /> Color de Texto Translúcido:
                                        </span>
                                        <div className="flex items-center gap-2">
                                            {[
                                                { label: 'Blanco Puro', color: '#FFFFFF' },
                                                { label: 'Oro Grayskull', color: '#FDE047' },
                                                { label: 'Cian Plasma', color: '#22D3EE' },
                                                { label: 'Violeta Skeletor', color: '#C084FC' },
                                                { label: 'Carmesí Hordak', color: '#F87171' },
                                                { label: 'Verde Serpiente', color: '#4ADE80' }
                                            ].map(p => (
                                                <button
                                                    key={p.color}
                                                    type="button"
                                                    onClick={() => setCustomTextColor(p.color)}
                                                    className={`w-5 h-5 rounded-full border-2 transition-transform cursor-pointer ${
                                                        customTextColor === p.color ? 'scale-125 border-white shadow-[0_0_8px_white]' : 'border-transparent opacity-75 hover:opacity-100'
                                                    }`}
                                                    style={{ backgroundColor: p.color }}
                                                    title={p.label}
                                                />
                                            ))}
                                        </div>
                                    </div>

                                    {/* 8. Estadísticas de Combate RPG */}
                                    <div className="sm:col-span-2 flex items-center justify-between gap-2 p-1.5 bg-black/40 rounded-lg border border-slate-800">
                                        <span className="text-[9px] font-black uppercase text-amber-300 shrink-0">
                                            ⚔️ Poderes / Stats:
                                        </span>
                                        {[
                                            { key: 'fuerza', label: 'FUE', color: 'text-amber-300' },
                                            { key: 'magia', label: 'MAG', color: 'text-cyan-300' },
                                            { key: 'defensa', label: 'DEF', color: 'text-emerald-300' },
                                            { key: 'agilidad', label: 'AGI', color: 'text-purple-300' }
                                        ].map(stat => (
                                            <div key={stat.key} className="flex items-center gap-1">
                                                <span className={`text-[9px] font-bold ${stat.color}`}>{stat.label}:</span>
                                                <input
                                                    type="number"
                                                    min="1"
                                                    max="99"
                                                    value={customStats ? (customStats as any)[stat.key] : (statsData as any)[stat.key]}
                                                    onChange={(e) => {
                                                        const val = Math.min(99, Math.max(1, parseInt(e.target.value) || 0));
                                                        setCustomStats(prev => ({
                                                            ...(prev || statsData),
                                                            [stat.key]: val
                                                        }));
                                                    }}
                                                    className="w-11 px-1 py-0.5 rounded bg-black border border-slate-700 text-white font-mono text-xs text-center focus:border-amber-400 focus:outline-none"
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    {/* 9. Botones de Acción Instantánea: Wiki Fandom & AF411 */}
                                    <div className="sm:col-span-2 flex items-center gap-2 pt-1">
                                        <button
                                            type="button"
                                            onClick={handleHarvestLoreFromWiki}
                                            disabled={isHarvestingLore}
                                            className="flex-1 py-1.5 px-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 text-emerald-300 text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition active:scale-95 disabled:opacity-50 cursor-pointer"
                                        >
                                            {isHarvestingLore ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Globe className="h-3.5 w-3.5" />}
                                            <span>🌐 Cosechar Lore Fandom (Coste 0)</span>
                                        </button>

                                        <button
                                            type="button"
                                            onClick={handleRefreshImageFromAF411}
                                            disabled={isRefreshingImage}
                                            className="flex-1 py-1.5 px-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 text-cyan-300 text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 transition active:scale-95 disabled:opacity-50 cursor-pointer"
                                        >
                                            {isRefreshingImage ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
                                            <span>📸 Refrescar Imagen AF411</span>
                                        </button>
                                    </div>
                                </div>

                                {/* Botón Guardar en el Canon */}
                                {(dbLoreChar || effectiveDbLore) && (
                                    <div className="flex items-center justify-between pt-1 border-t border-white/5">
                                        <span className="text-[9px] text-stone-400">
                                            Guardar estos textos para que todas las cartas de este personaje los hereden.
                                        </span>
                                        <button
                                            type="button"
                                            onClick={handleSaveToLoreCanon}
                                            disabled={savingDbLore}
                                            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-[9.5px] font-black uppercase tracking-wider transition cursor-pointer ${
                                                loreSaveSuccess
                                                    ? 'bg-emerald-500 text-slate-950'
                                                    : 'bg-amber-500/20 border border-amber-500/50 text-amber-300 hover:bg-amber-500 hover:text-slate-950'
                                            }`}
                                        >
                                            {savingDbLore ? (
                                                <Loader2 className="h-3 w-3 animate-spin" />
                                            ) : loreSaveSuccess ? (
                                                <CheckCircle2 className="h-3 w-3 text-slate-950" />
                                            ) : (
                                                <Save className="h-3 w-3" />
                                            )}
                                            <span>{loreSaveSuccess ? '¡Guardado en Canon!' : 'Guardar en Grimorio'}</span>
                                        </button>
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* CONTENEDOR 3D DEL CROMO (SHOWCASE FULL-ART O MARCO CLÁSICO) */}
                    <div
                        className="w-full flex justify-center cursor-grab active:cursor-grabbing"
                        style={{ perspective: 1100 }}
                        onMouseMove={handleMouseMove}
                        onMouseLeave={handleMouseLeave}
                    >
                        <motion.div
                            ref={cardRef}
                            style={{
                                transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
                                transformStyle: 'preserve-3d',
                                transition: 'transform 0.1s ease-out',
                                aspectRatio: '896 / 1200'
                            }}
                            className="relative w-full max-w-[340px] sm:max-w-[360px] rounded-[24px] select-none overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.95)] bg-slate-950 font-cinzel border-2 border-stone-800"
                        >
                            {cardVersion === 'showcase' ? (
                                /* ========================================================================= */
                                /* 🌟 REEDICIÓN FULL-ART SECRET LAIR SHOWCASE (100% ILUSTRACIÓN + CRISTAL)   */
                                /* ========================================================================= */
                                <>
                                    {/* 1. CAPA DUAL: SANGRADO AMBIENTAL + ILUSTRACIÓN INTERACTIVA */}
                                    <div
                                        onMouseDown={handleImgMouseDown}
                                        onMouseMove={handleImgMouseMove}
                                        onMouseUp={handleImgMouseUp}
                                        onMouseLeave={handleImgMouseUp}
                                        onWheel={handleImgWheel}
                                        onTouchStart={handleImgTouchStart}
                                        onTouchMove={handleImgTouchMove}
                                        onTouchEnd={handleImgTouchEnd}
                                        onContextMenu={(e) => { e.preventDefault(); resetFraming(); }}
                                        onDoubleClick={(e) => { e.preventDefault(); resetFraming(); }}
                                        className={`absolute inset-0 z-0 overflow-hidden flex items-center justify-center bg-[#070b10] rounded-[24px] ${
                                            isDraggingImg ? 'cursor-grabbing' : 'cursor-grab'
                                        }`}
                                        title="Arrastra con el ratón o usa la rueda para ampliar y mover libremente"
                                    >
                                        {/* Capa de Sangrado Ambiental Difuso (Respira y rebosa por los 4 costados) */}
                                        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none select-none">
                                            {aiResult?.image_base64 ? (
                                                <img
                                                    src={aiResult.image_base64}
                                                    alt="Ambient bleed"
                                                    aria-hidden="true"
                                                    className="w-full h-full object-cover scale-150 blur-xl opacity-50 brightness-75 select-none"
                                                />
                                            ) : (
                                                <MOTUImage
                                                    productId={item.id}
                                                    src={activeImage}
                                                    alt="Ambient bleed"
                                                    className="w-full h-full object-cover scale-150 blur-xl opacity-50 brightness-75 select-none"
                                                />
                                            )}
                                        </div>

                                        {/* Ilustración Frontal Interactiva */}
                                        <div
                                            className="absolute flex items-center justify-center pointer-events-none select-none w-full h-full z-10"
                                            style={{
                                                transform: `translate(${imgPan.x}px, ${imgPan.y}px) scale(${imgZoom})`,
                                                transformOrigin: 'center center',
                                                transition: isDraggingImg ? 'none' : 'transform 0.1s ease-out'
                                            }}
                                        >
                                            {aiResult?.image_base64 ? (
                                                <img
                                                    src={aiResult.image_base64}
                                                    alt={name}
                                                    draggable={false}
                                                    className="w-full h-full object-contain select-none pointer-events-none drop-shadow-2xl"
                                                />
                                            ) : (
                                                <MOTUImage
                                                    productId={item.id}
                                                    src={activeImage}
                                                    alt={name}
                                                    className="w-full h-full object-contain select-none pointer-events-none drop-shadow-2xl"
                                                />
                                            )}
                                        </div>

                                        {/* Mini Barra de Zoom y Encuadre Flotante */}
                                        {!exporting && (
                                            <div className="export-exclude absolute top-3 right-3 z-30 flex items-center gap-1 bg-black/75 backdrop-blur-md px-1.5 py-1 rounded-lg border border-slate-700/80 shadow-lg opacity-85 hover:opacity-100 transition-opacity">
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setImgZoom((prev) => Math.min(6.0, +(prev + 0.2).toFixed(2)));
                                                    }}
                                                    title="Ampliar Imagen (+)"
                                                    className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                                >
                                                    <Plus className="h-3 w-3" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setImgZoom((prev) => Math.max(0.3, +(prev - 0.2).toFixed(2)));
                                                    }}
                                                    title="Reducir Imagen (-)"
                                                    className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                                >
                                                    <Minus className="h-3 w-3" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setImgZoom(0.65);
                                                        setImgPan({ x: 0, y: -20 });
                                                    }}
                                                    title="Ajuste Multipack / Panorama (Ver 4 Figuras)"
                                                    className="p-1 hover:bg-amber-500/20 text-amber-300 hover:text-amber-200 rounded transition active:scale-90 flex items-center gap-0.5 text-[9px] font-bold font-cinzel"
                                                >
                                                    <Maximize2 className="h-3 w-3" />
                                                </button>
                                                {(imgZoom !== 1 || imgPan.x !== 0 || imgPan.y !== 0) && (
                                                    <button
                                                        type="button"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            resetFraming();
                                                        }}
                                                        title="Restablecer Encuadre Original"
                                                        className="p-1 hover:bg-rose-500/20 text-amber-400 hover:text-rose-300 rounded transition active:scale-90"
                                                    >
                                                        <RotateCcw className="h-3 w-3" />
                                                    </button>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* 2. CINTA FLOTANTE DE TÍTULO + ALTER-EGO + COSTE DE MANÁ (CRISTAL TRANSLÚCIDO SECRET LAIR) */}
                                    <div className="absolute top-3.5 left-3.5 right-3.5 z-20 pointer-events-none">
                                        <div className="bg-gradient-to-r from-black/50 via-slate-950/40 to-black/50 backdrop-blur-[3px] border border-white/25 rounded-2xl px-3.5 py-1.5 shadow-[0_4px_20px_rgba(0,0,0,0.6)] flex items-center justify-between">
                                            <div className="flex flex-col justify-center min-w-0 pr-2">
                                                <h3 className="text-xs sm:text-sm font-black uppercase tracking-wider text-amber-200 font-cinzel truncate drop-shadow-[0_2px_4px_rgba(0,0,0,1)]">
                                                    {displayCardName}
                                                </h3>
                                                {displaySubtitle && (
                                                    <span className="text-[9.5px] italic text-amber-300 font-serif -mt-0.5 truncate drop-shadow-[0_1px_3px_rgba(0,0,0,1)]">
                                                        {displaySubtitle}
                                                    </span>
                                                )}
                                            </div>
                                            {/* Orbes de Coste de Maná */}
                                            {renderManaCostPips(displayManaCost)}
                                        </div>
                                    </div>

                                    {/* 3. CINTA FLOTANTE DE TIPO (CRISTAL TRANSLÚCIDO) */}
                                    <div className="absolute top-[56%] left-3.5 right-3.5 z-20 pointer-events-none">
                                        <div className="bg-gradient-to-r from-black/45 via-slate-900/40 to-black/45 backdrop-blur-[3px] border border-white/20 rounded-xl px-3 py-1 shadow-[0_4px_16px_rgba(0,0,0,0.5)] flex items-center justify-between">
                                            <span className="text-[10px] font-black uppercase tracking-wider font-cinzel truncate drop-shadow-[0_2px_4px_rgba(0,0,0,1)]" style={{ color: customTextColor }}>
                                                {typeLineText}
                                            </span>
                                            <span className="text-[10px] text-amber-400 font-bold drop-shadow-[0_1px_3px_rgba(0,0,0,1)]">★ M 2768</span>
                                        </div>
                                    </div>

                                    {/* 4. CAJA TRANSLÚCIDA INFERIOR: REGLAS, CITA CÉLEBRE Y STATS (OBSIDIAN SMOKE GLASS) */}
                                    <div className="absolute top-[63%] left-3.5 right-3.5 bottom-6 z-20 pointer-events-none">
                                        <div
                                            className="w-full h-full bg-gradient-to-b from-black/35 via-black/45 to-black/55 backdrop-blur-[3px] border border-white/25 rounded-2xl p-2.5 shadow-[0_8px_32px_rgba(0,0,0,0.7)] flex flex-col justify-between"
                                            style={{ color: customTextColor }}
                                        >
                                            {/* Reglas / Poder Especial */}
                                            <div className="text-[10px] sm:text-[10.5px] leading-snug drop-shadow-[0_2px_4px_rgba(0,0,0,1)] font-sans font-semibold">
                                                {specialMoveText}
                                            </div>

                                            {/* Cita de Lore en Cursiva y Autor */}
                                            {loreText && (
                                                <div className="border-t border-white/20 pt-1 mt-0.5">
                                                    <p className="text-[9px] sm:text-[9.5px] italic opacity-95 font-serif leading-tight drop-shadow-[0_2px_4px_rgba(0,0,0,1)]">
                                                        "{loreText}"
                                                    </p>
                                                    {displayQuoteAuthor && (
                                                        <p className="text-[8px] sm:text-[8.5px] text-right opacity-90 font-sans mt-0.5 font-bold drop-shadow-[0_1px_3px_rgba(0,0,0,1)]">
                                                            — {displayQuoteAuthor}
                                                        </p>
                                                    )}
                                                </div>
                                            )}

                                            {/* Placa P/T de Combate Inferior Derecha */}
                                            <div className="flex justify-end pt-1">
                                                <div className="px-2.5 py-0.5 rounded-lg bg-stone-950/80 backdrop-blur-sm border border-amber-400/80 shadow-[0_2px_8px_rgba(0,0,0,0.8)] text-[10px] font-black font-cinzel tracking-wider text-amber-300 drop-shadow">
                                                    {statsData.fuerza > 0 ? `${Math.round(statsData.fuerza / 15)} / ${Math.round(statsData.defensa / 15)}` : '5 / 4'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* 5. PIE DE IMPRENTA DE COLECCIONISTA */}
                                    <div className="absolute bottom-1 left-4 right-4 z-20 pointer-events-none flex items-center justify-between text-[7px] text-stone-300 font-mono drop-shadow">
                                        <span>M 2768 | SLD • ES</span>
                                        <span className="truncate">™ & © 2026 Mattel / Oráculo</span>
                                    </div>
                                </>
                            ) : (
                                /* ========================================================================= */
                                /* 🛡️ MARCO CLÁSICO 3D (PLANTILLA ESCULPIDA Y 4 ENGARCES DE COMBATE NATIVOS) */
                                /* ========================================================================= */
                                <>
                                    {/* CAPA 1 (Fondo): Ventana Interactiva de Ilustración / Foto */}
                                    <div
                                        onMouseDown={handleImgMouseDown}
                                        onMouseMove={handleImgMouseMove}
                                        onMouseUp={handleImgMouseUp}
                                        onMouseLeave={handleImgMouseUp}
                                        onWheel={handleImgWheel}
                                        onTouchStart={handleImgTouchStart}
                                        onTouchMove={handleImgTouchMove}
                                        onTouchEnd={handleImgTouchEnd}
                                        onContextMenu={(e) => { e.preventDefault(); resetFraming(); }}
                                        onDoubleClick={(e) => { e.preventDefault(); resetFraming(); }}
                                        className={`absolute z-0 overflow-hidden flex items-center justify-center bg-[#070b10] ${
                                            isDraggingImg ? 'cursor-grabbing' : 'cursor-grab'
                                        }`}
                                        style={{
                                            top: '5.5%',
                                            left: '8.0%',
                                            width: '84%',
                                            height: '50%',
                                            borderRadius: '24px 24px 0 0'
                                        }}
                                        title="Arrastra con el ratón o usa la rueda para ampliar y mover libremente"
                                    >
                                        <div
                                            className="absolute flex items-center justify-center pointer-events-none select-none"
                                            style={{
                                                transform: `translate(${imgPan.x}px, ${imgPan.y}px) scale(${imgZoom})`,
                                                transformOrigin: 'center center',
                                                transition: isDraggingImg ? 'none' : 'transform 0.1s ease-out'
                                            }}
                                        >
                                            {aiResult?.image_base64 ? (
                                                <img
                                                    src={aiResult.image_base64}
                                                    alt={name}
                                                    draggable={false}
                                                    className="max-w-none max-h-none select-none pointer-events-none animate-in fade-in duration-300"
                                                    style={{ width: '100%', minWidth: '280px', height: 'auto', display: 'block' }}
                                                />
                                            ) : (
                                                <div className="flex items-center justify-center pointer-events-none select-none" style={{ width: '300px', height: '240px' }}>
                                                    <MOTUImage
                                                        productId={item.id}
                                                        src={activeImage}
                                                        alt={name}
                                                        className="max-h-full max-w-full object-contain p-2 z-10 drop-shadow-[0_10px_20px_rgba(0,0,0,0.95)] pointer-events-none select-none"
                                                    />
                                                </div>
                                            )}
                                        </div>

                                        {!exporting && (
                                            <div className="export-exclude absolute top-2 right-2 z-30 flex items-center gap-1 bg-black/85 backdrop-blur-md px-1.5 py-1 rounded-lg border border-slate-700/80 shadow-md opacity-80 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setImgZoom((prev) => Math.min(6.0, +(prev + 0.25).toFixed(2)));
                                                    }}
                                                    title="Ampliar Imagen (+)"
                                                    className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                                >
                                                    <Plus className="h-3 w-3" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setImgZoom((prev) => Math.max(0.2, +(prev - 0.25).toFixed(2)));
                                                    }}
                                                    title="Reducir Imagen (-)"
                                                    className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                                >
                                                    <Minus className="h-3 w-3" />
                                                </button>
                                                {(imgZoom !== 1 || imgPan.x !== 0 || imgPan.y !== 0) && (
                                                    <button
                                                        type="button"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            resetFraming();
                                                        }}
                                                        title="Restablecer Encuadre Original"
                                                        className="p-1 hover:bg-rose-500/20 text-amber-400 hover:text-rose-300 rounded transition active:scale-90"
                                                    >
                                                        <RotateCcw className="h-3 w-3" />
                                                    </button>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* CAPA 2 (Marco HD Esculpido) */}
                                    <img
                                        src={theme.frameAsset}
                                        alt="Marco TCG"
                                        draggable={false}
                                        className="absolute inset-0 w-full h-full object-fill pointer-events-none z-10 select-none drop-shadow-2xl"
                                    />

                                    {/* CAPA 3: Cabecera, Texto y Stats */}
                                    {(() => {
                                        const titleParts = formatCardTitle(displayCardName);
                                        return (
                                            <div
                                                className="absolute z-20 flex items-center justify-start pointer-events-none overflow-hidden px-1"
                                                style={{
                                                    top: layout.header.top,
                                                    left: layout.header.left,
                                                    width: layout.header.width,
                                                    height: layout.header.height
                                                }}
                                            >
                                                <div className="flex items-center gap-1.5 min-w-0">
                                                    <h3 className="text-[11.5px] sm:text-[12.5px] font-black text-white uppercase tracking-wider truncate tcg-gold-emboss">
                                                        {titleParts.main}
                                                    </h3>
                                                    {titleParts.sub && (
                                                        <span className="text-[8px] sm:text-[8.5px] font-semibold text-amber-200 uppercase tracking-tight truncate shrink-0 drop-shadow-[0_1px_2px_rgba(0,0,0,0.9)]">
                                                            • {titleParts.sub}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })()}

                                    <div
                                        className="absolute z-20 flex flex-col items-center justify-center text-center pointer-events-none px-3 py-2 overflow-hidden rounded-xl bg-black/35 backdrop-blur-[1px] shadow-inner"
                                        style={{
                                            top: layout.textBox.top,
                                            left: layout.textBox.left,
                                            width: layout.textBox.width,
                                            height: layout.textBox.height
                                        }}
                                    >
                                        <p
                                            className="italic leading-relaxed text-stone-100 line-clamp-4 drop-shadow-[0_1px_3px_rgba(0,0,0,1)] text-center my-auto"
                                            style={{
                                                fontSize: layout.lore.fontSize,
                                                lineHeight: layout.lore.lineHeight,
                                                color: theme.loreTextColor,
                                                textShadow: '0 1px 2px rgba(0,0,0,1), 0 0 6px rgba(0,0,0,0.8)'
                                            }}
                                        >
                                            "{loreText}"
                                        </p>
                                    </div>

                                    {/* 4 Engarces */}
                                    <div
                                        className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                                        style={{ top: layout.statFue?.top || '87.2%', left: layout.statFue?.left || '21.2%' }}
                                    >
                                        <span className="font-black text-red-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]" style={{ fontSize: layout.statFue?.labelFontSize || '7px' }}>FUE</span>
                                        <span className="font-black text-white leading-none tcg-gold-emboss mt-0.5" style={{ fontSize: layout.statFue?.fontSize || '11.5px' }}>{statsData.fuerza}</span>
                                    </div>

                                    <div
                                        className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                                        style={{ top: layout.statMag?.top || '87.2%', left: layout.statMag?.left || '34.4%' }}
                                    >
                                        <span className="font-black text-purple-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]" style={{ fontSize: layout.statMag?.labelFontSize || '7px' }}>MAG</span>
                                        <span className="font-black text-white leading-none tcg-gold-emboss mt-0.5" style={{ fontSize: layout.statMag?.fontSize || '11.5px' }}>{statsData.magia}</span>
                                    </div>

                                    <div
                                        className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                                        style={{ top: layout.statDef?.top || '87.2%', left: layout.statDef?.left || '65.6%' }}
                                    >
                                        <span className="font-black text-sky-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]" style={{ fontSize: layout.statDef?.labelFontSize || '7px' }}>DEF</span>
                                        <span className="font-black text-white leading-none tcg-gold-emboss mt-0.5" style={{ fontSize: layout.statDef?.fontSize || '11.5px' }}>{statsData.defensa}</span>
                                    </div>

                                    <div
                                        className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                                        style={{ top: layout.statAgi?.top || '87.2%', left: layout.statAgi?.left || '78.8%' }}
                                    >
                                        <span className="font-black text-emerald-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]" style={{ fontSize: layout.statAgi?.labelFontSize || '7px' }}>AGI</span>
                                        <span className="font-black text-white leading-none tcg-gold-emboss mt-0.5" style={{ fontSize: layout.statAgi?.fontSize || '11.5px' }}>{statsData.agilidad}</span>
                                    </div>
                                </>
                            )}

                            {/* Brillo reflectivo holográfico dinámico */}
                            <div
                                className="absolute inset-0 pointer-events-none z-30 transition-opacity duration-200"
                                style={{
                                    opacity: glarePos.opacity,
                                    background: `radial-gradient(circle at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,0.4) 0%, rgba(254,240,138,0.15) 30%, transparent 75%)`
                                }}
                            />
                        </motion.div>
                    </div>

                    {/* SELECTOR DE MODO: CARTA COMPLETA VS SOLO ILUSTRACIÓN */}
                    <div className="w-full flex items-center justify-center p-1 rounded-xl bg-slate-950/90 border border-amber-500/30 gap-1 mt-3 mb-1 shadow-inner">
                        <button
                            onClick={() => setExportTarget('card')}
                            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[11px] font-black uppercase tracking-wider transition-all font-cinzel ${
                                exportTarget === 'card'
                                    ? 'bg-gradient-to-r from-amber-500 to-yellow-600 text-black shadow-md shadow-amber-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                            }`}
                        >
                            <Shield className="h-3.5 w-3.5" />
                            <span>🃏 Carta Completa</span>
                        </button>
                        <button
                            onClick={() => setExportTarget('image')}
                            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[11px] font-black uppercase tracking-wider transition-all font-cinzel ${
                                exportTarget === 'image'
                                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                            }`}
                        >
                            <ImageIcon className="h-3.5 w-3.5" />
                            <span>🖼️ Solo Ilustración</span>
                        </button>
                    </div>

                    {/* BOTONES DE EXPORTACIÓN Y COMPARTIR */}
                    <div className="w-full grid grid-cols-3 gap-2 mt-2">
                        {/* 1. Compartir Nativo a WhatsApp / Móvil */}
                        <button
                            onClick={handleNativeShare}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-[10px] font-bold shadow-lg shadow-emerald-600/30 transition active:scale-95 disabled:opacity-50 font-cinzel"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : shared ? (
                                <Check className="h-4 w-4 text-white" />
                            ) : (
                                <Share2 className="h-4 w-4" />
                            )}
                            <span>{shared ? '¡Compartido!' : 'WhatsApp / Redes'}</span>
                        </button>

                        {/* 2. Copiar Imagen al Portapapeles */}
                        <button
                            onClick={handleCopyImage}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50 font-cinzel"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : copied ? (
                                <Check className="h-4 w-4 text-emerald-400" />
                            ) : (
                                <Copy className="h-4 w-4" />
                            )}
                            <span>
                                {copied
                                    ? '¡Copiado!'
                                    : exportTarget === 'card'
                                    ? 'Copiar Carta'
                                    : 'Copiar Ilustración'}
                            </span>
                        </button>

                        {/* 3. Descargar Imagen HD */}
                        <button
                            onClick={handleDownload}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50 font-cinzel"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin text-amber-300" />
                            ) : downloaded ? (
                                <Check className="h-4 w-4 text-emerald-400" />
                            ) : (
                                <Download className="h-4 w-4" />
                            )}
                            <span>
                                {downloaded
                                    ? '¡Descargado!'
                                    : exportTarget === 'card'
                                    ? 'Descargar Carta'
                                    : 'Descargar HD'}
                            </span>
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TradingCardModal;



