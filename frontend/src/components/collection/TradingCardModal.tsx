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
    Move
} from 'lucide-react';
import { toPng } from 'html-to-image';
import { MOTUImage } from '../ui/MOTUImage';
import { enhanceCardWithAI, type CardAiEnhanceResult } from '../../api/cards';

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

const FACTION_VISUAL_THEMES: Record<string, FactionVisualTheme> = {
    castle_grayskull: {
        faction: 'Guerreros Heroicos',
        typeLine: 'Criatura Legendaria — Guerrero Heroico',
        frameAsset: '/frames/frame_castle_grayskull.webp',
        specialMoveColor: '#ffdb70',
        loreTextColor: '#e2eedd'
    },
    snake_mountain: {
        faction: 'Guerreros del Mal',
        typeLine: 'Criatura Legendaria — Guerrero del Mal',
        frameAsset: '/frames/frame_snake_mountain.webp',
        specialMoveColor: '#ff8a3d',
        loreTextColor: '#eedac5'
    },
    evil_horde: {
        faction: 'La Horda del Terror',
        typeLine: 'Tirano Legendario — Soldado de la Horda',
        frameAsset: '/frames/frame_evil_horde.webp',
        specialMoveColor: '#fca5a5',
        loreTextColor: '#fee2e2'
    },
    snake_men: {
        faction: 'Los Hombres Serpiente',
        typeLine: 'Monarca Ofídico — Hombre Serpiente',
        frameAsset: '/frames/frame_snake_men.webp',
        specialMoveColor: '#bef264',
        loreTextColor: '#ecfccb'
    },
    great_rebellion: {
        faction: 'La Gran Rebelión',
        typeLine: 'Princesa del Poder — Gran Rebelión',
        frameAsset: '/frames/frame_great_rebellion.webp',
        specialMoveColor: '#fbcfe8',
        loreTextColor: '#fdf2f8'
    },
    cosmic_enforcers: {
        faction: 'Guardianes Cósmicos',
        typeLine: 'Ejecutor Cósmico — Juez del Equilibrio',
        frameAsset: '/frames/frame_cosmic_enforcers.webp',
        specialMoveColor: '#7dd3fc',
        loreTextColor: '#e0f2fe'
    }
};

export interface FactionCardLayout {
    header: { top: string; left: string; width: string; height: string };
    textBox: { top: string; left: string; width: string; height: string };
    powerPlate: {
        height: string;
        fontSize: string;
        border: string;
        bg: string;
    };
    lore: {
        fontSize: string;
        lineHeight: string;
    };
    typeLine: {
        fontSize: string;
        color: string;
    };
    leftSocket: { top: string; left: string; width: string; height: string };
    rightSocket: { top: string; right: string; width: string; height: string };
    canvas: {
        header: { x: number; y: number };
        powerBox: { x: number; y: number; w: number; h: number };
        powerText: { y: number; fontSize: number };
        loreText: { y: number; maxW: number; lineH: number; fontSize: number };
        typeLine: { y: number; fontSize: number };
        leftSocket: { x: number; y: number };
        rightSocket: { x: number; y: number };
    };
}

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
        leftSocket: { top: '86.8%', left: '14.5%', width: '31.5%', height: '4.5%' },
        rightSocket: { top: '86.8%', right: '14.5%', width: '31.5%', height: '4.5%' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 655, w: 636, h: 48 },
            powerText: { y: 686, fontSize: 18 },
            loreText: { y: 730, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            leftSocket: { x: 240, y: 1045 },
            rightSocket: { x: 655, y: 1045 }
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%' },
        canvas: {
            header: { x: 124, y: 126 },
            powerBox: { x: 130, y: 658, w: 636, h: 48 },
            powerText: { y: 689, fontSize: 18 },
            loreText: { y: 732, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            leftSocket: { x: 240, y: 1045 },
            rightSocket: { x: 655, y: 1045 }
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
        leftSocket: { top: '86.6%', left: '14.0%', width: '32.0%', height: '4.5%' },
        rightSocket: { top: '86.6%', right: '14.0%', width: '32.0%', height: '4.5%' },
        canvas: {
            header: { x: 120, y: 123 },
            powerBox: { x: 130, y: 648, w: 636, h: 48 },
            powerText: { y: 679, fontSize: 18 },
            loreText: { y: 722, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 835, fontSize: 15 },
            leftSocket: { x: 240, y: 1042 },
            rightSocket: { x: 655, y: 1042 }
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 655, w: 636, h: 48 },
            powerText: { y: 686, fontSize: 18 },
            loreText: { y: 730, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 840, fontSize: 15 },
            leftSocket: { x: 240, y: 1045 },
            rightSocket: { x: 655, y: 1045 }
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 652, w: 636, h: 48 },
            powerText: { y: 683, fontSize: 18 },
            loreText: { y: 726, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 838, fontSize: 15 },
            leftSocket: { x: 240, y: 1045 },
            rightSocket: { x: 655, y: 1045 }
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%' },
        canvas: {
            header: { x: 120, y: 126 },
            powerBox: { x: 130, y: 650, w: 636, h: 48 },
            powerText: { y: 681, fontSize: 18 },
            loreText: { y: 724, maxW: 600, lineH: 26, fontSize: 17 },
            typeLine: { y: 836, fontSize: 15 },
            leftSocket: { x: 240, y: 1045 },
            rightSocket: { x: 655, y: 1045 }
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

// Obtiene la imagen individual pura con el encuadre y zoom personalizados como DataURL HD
const getSingleIllustrationDataUrl = async (
    item: any,
    aiImageBase64?: string | null,
    zoom: number = 1,
    pan: { x: number; y: number } = { x: 0, y: 0 }
): Promise<string> => {
    if (zoom === 1 && pan.x === 0 && pan.y === 0 && aiImageBase64) {
        return aiImageBase64;
    }
    const targetSrc = aiImageBase64 || item.image_url;
    if (!targetSrc) return '';

    return new Promise((resolve) => {
        const img = new window.Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = 900;
            canvas.height = 1200;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = '#090d16';
                ctx.fillRect(0, 0, 900, 1200);

                ctx.save();
                ctx.translate(450 + pan.x * (900 / 320), 600 + pan.y * (1200 / 224));
                ctx.scale(zoom, zoom);

                const imgAspect = img.width / img.height;
                const canvasAspect = 900 / 1200;
                let drawW = 900;
                let drawH = 1200;
                if (imgAspect > canvasAspect) {
                    drawW = 1200 * imgAspect;
                } else {
                    drawH = 900 / imgAspect;
                }
                ctx.drawImage(img, -drawW / 2, -drawH / 2, drawW, drawH);
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

            const titleParts = formatCardTitle(item.product_name || item.name || 'HE-MAN');
            const themeKey = profileData?.themeKey || 'castle_grayskull';
            const layout = FACTION_CARD_LAYOUTS[themeKey] || FACTION_CARD_LAYOUTS.castle_grayskull;
            const faction = profileData?.faction || 'Guerreros Heroicos';
            const specialMove = profileData?.specialMove || 'Furia del Relámpago de Grayskull';
            const loreText = aiLore || profileData?.lore || '¡Por el poder de Grayskull, la justicia siempre prevalecerá!';
            const stats = profileData?.stats || { fuerza: 99, magia: 88, defensa: 95, agilidad: 90 };
            const frameSrc = profileData?.frameAsset || '/frames/frame_castle_grayskull.webp';

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

                    // 3. Placa de Poder de Alto Impacto (En la parte superior de la losa de piedra)
                    const pb = layout.canvas.powerBox;
                    ctx.fillStyle = 'rgba(15, 20, 25, 0.90)';
                    ctx.fillRect(pb.x, pb.y, pb.w, pb.h);
                    ctx.strokeStyle = '#eab308';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(pb.x, pb.y, pb.w, pb.h);

                    ctx.textAlign = 'center';
                    ctx.fillStyle = profileData?.specialMoveColor || '#ffdb70';
                    const powerText = `⚡ PODER: ${specialMove.toUpperCase()}`;
                    ctx.font = `900 ${layout.canvas.powerText.fontSize}px serif`;
                    if (ctx.measureText(powerText).width > 590) {
                        ctx.font = '900 15px serif';
                    }
                    ctx.fillText(powerText, width / 2, layout.canvas.powerText.y);

                    // 4. Flavor Lore Canónico en Cursiva (En el centro de la losa de texto)
                    ctx.textAlign = 'center';
                    ctx.fillStyle = profileData?.loreTextColor || '#f5f5f0';
                    ctx.font = `italic ${layout.canvas.loreText.fontSize}px serif`;
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

                    // 5. Barra de Categorización / Tipo (DEBAJO del texto de descripción)
                    ctx.fillStyle = layout.typeLine.color || '#fde68a';
                    ctx.font = `bold ${layout.canvas.typeLine.fontSize}px serif`;
                    ctx.textAlign = 'center';
                    ctx.fillText(`— ${profileData?.typeLine || `CRIATURA LEGENDARIA • ${faction.toUpperCase()}`} —`, width / 2, layout.canvas.typeLine.y);

                    // 6. Sockets de Combate Centrados
                    // Izquierdo: FUE | MAG
                    ctx.textAlign = 'center';
                    ctx.fillStyle = '#fef08a';
                    ctx.font = 'bold 20px serif';
                    ctx.fillText(`FUE ${stats.fuerza}  |  MAG ${stats.magia}`, layout.canvas.leftSocket.x, layout.canvas.leftSocket.y);

                    // Derecho: DEF | AGI
                    ctx.fillText(`DEF ${stats.defensa}  |  AGI ${stats.agilidad}`, layout.canvas.rightSocket.x, layout.canvas.rightSocket.y);

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
                        const drawX = 135;
                        const drawY = 160;
                        const drawW = 626;
                        const drawH = 390;
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

    if (!isOpen || !item) return null;

    const name = item.product_name || item.name || 'Figura MOTU';
    const condition = (item.condition || 'MOC').toUpperCase();
    const grade = item.grading || 10.0;

    // Perfil canónico local y tema visual de facción
    const localProfile = getLocalMotuProfile(name, item.sub_category);
    const themeKey = aiResult?.frame_theme || localProfile.themeKey;
    const theme = FACTION_VISUAL_THEMES[themeKey] || FACTION_VISUAL_THEMES.castle_grayskull;
    const layout = FACTION_CARD_LAYOUTS[themeKey] || FACTION_CARD_LAYOUTS.castle_grayskull;
    const factionName = aiResult?.faction || localProfile.faction;
    const typeLineText = aiResult?.type_line || localProfile.typeLine;
    const specialMoveText = aiResult?.special_move || localProfile.specialMove;
    const loreText = aiResult?.lore || localProfile.lore;
    const statsData = aiResult?.stats || localProfile.stats;

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

    // Control de Zoom con Rueda del Ratón
    const handleImgWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        e.stopPropagation();
        const delta = e.deltaY < 0 ? 0.08 : -0.08;
        setImgZoom((prev) => Math.min(3.5, Math.max(0.4, +(prev + delta).toFixed(2))));
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
            setImgZoom(Math.min(3.5, Math.max(0.4, +(touchStartRef.current.startZoom * scale).toFixed(2))));
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
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor
                });
                filename = `Carta_TCG_${name.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${name.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
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
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor
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
                    faction: factionName,
                    typeLine: typeLineText,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData,
                    frameAsset: theme.frameAsset,
                    specialMoveColor: theme.specialMoveColor
                });
                filename = `Carta_TCG_${name.replace(/\s+/g, '_')}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${name.replace(/\s+/g, '_')}.png`;
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
                        className="absolute top-3 right-3 p-2 rounded-full bg-slate-800/90 hover:bg-red-500 text-slate-300 hover:text-white transition z-30 shadow-lg"
                        title="Cerrar Cromo"
                    >
                        <X className="h-4 w-4" />
                    </button>

                    {/* Título de la Ficha */}
                    <div className="flex items-center gap-2 mb-2.5 text-center">
                        <Sparkles className="h-4 w-4 text-amber-400" />
                        <h2 className="text-xs sm:text-sm font-black uppercase tracking-widest text-amber-300 font-cinzel">
                            Cromo Coleccionista Digital
                        </h2>
                        <Sparkles className="h-4 w-4 text-amber-400" />
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

                    {/* CONTENEDOR 3D DEL CROMO MAGIC SHOWCASE (3 CAPAS REALES) */}
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
                            className="relative w-full max-w-[340px] sm:max-w-[360px] rounded-[24px] select-none overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.95)] bg-slate-950 font-cinzel"
                        >
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
                                onContextMenu={(e) => {
                                    e.preventDefault();
                                    resetFraming();
                                }}
                                onDoubleClick={(e) => {
                                    e.preventDefault();
                                    resetFraming();
                                }}
                                className={`absolute z-0 overflow-hidden flex items-center justify-center bg-[#070b10] ${
                                    isDraggingImg ? 'cursor-grabbing' : 'cursor-grab'
                                }`}
                                style={{
                                    top: '13.5%',
                                    left: '14.5%',
                                    width: '71%',
                                    height: '33%',
                                    borderRadius: '16px 16px 6px 6px'
                                }}
                                title="Arrastra con el ratón o usa la rueda para ampliar y encuadrar"
                            >
                                {/* Capa de la Imagen con Zoom y Desplazamiento */}
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
                                            style={{
                                                width: '320px',
                                                height: 'auto',
                                                minHeight: '200px',
                                                display: 'block'
                                            }}
                                        />
                                    ) : (
                                        <div className="flex items-center justify-center pointer-events-none select-none" style={{ width: '320px', height: '200px' }}>
                                            <MOTUImage
                                                productId={item.id}
                                                src={item.image_url}
                                                alt={name}
                                                className="max-h-full max-w-full object-contain p-2 z-10 drop-shadow-[0_10px_20px_rgba(0,0,0,0.95)] pointer-events-none select-none"
                                            />
                                        </div>
                                    )}
                                </div>

                                {/* Mini Barra de Zoom Flotante (OCULTA EN EXPORTACIÓN) */}
                                {!exporting && (
                                    <div className="export-exclude absolute top-2 right-2 z-30 flex items-center gap-1 bg-black/85 backdrop-blur-md px-1.5 py-1 rounded-lg border border-slate-700/80 shadow-md opacity-80 group-hover:opacity-100 transition-opacity">
                                        <button
                                            type="button"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setImgZoom((prev) => Math.min(3.5, +(prev + 0.15).toFixed(2)));
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
                                                setImgZoom((prev) => Math.max(0.4, +(prev - 0.15).toFixed(2)));
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

                                {!exporting && (
                                    <div className="export-exclude absolute bottom-2 left-2 z-20 pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity">
                                        <span className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-black/75 border border-slate-800 text-[8px] font-mono text-slate-300">
                                            <Move className="h-2.5 w-2.5 text-amber-400" />
                                            {imgZoom !== 1 ? `${Math.round(imgZoom * 100)}%` : 'Arrastra / Zoom'}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* CAPA 2 (Marco HD Esculpido): Plantilla WebP Transparente */}
                            <img
                                src={theme.frameAsset}
                                alt="Marco TCG"
                                draggable={false}
                                className="absolute inset-0 w-full h-full object-fill pointer-events-none z-10 select-none drop-shadow-2xl"
                            />

                            {/* CAPA 3 (Frente): Tipografía Vectorial Nítida y Datos Canónicos Individualizados */}
                            {/* 1. TÍTULO EN LA CABECERA (Nombre + Subtítulo con formato de lujo) */}
                            {(() => {
                                const titleParts = formatCardTitle(name);
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

                            {/* 2. CAJA DE TEXTO UNIFICADA (Losa de Piedra: Poder + Lore + Categorización de Tipo) */}
                            <div
                                className="absolute z-20 flex flex-col justify-between pointer-events-none px-2.5 py-1.5 overflow-hidden rounded-xl bg-black/35 backdrop-blur-[1px] shadow-inner"
                                style={{
                                    top: layout.textBox.top,
                                    left: layout.textBox.left,
                                    width: layout.textBox.width,
                                    height: layout.textBox.height
                                }}
                            >
                                {/* 2a. PLACA DE PODER / HABILIDAD ESPECIAL DE ALTO IMPACTO (Arriba en la losa) */}
                                <div
                                    className={`flex items-center justify-center gap-1.5 px-2 py-0.5 rounded-lg border ${layout.powerPlate.border} bg-gradient-to-r ${layout.powerPlate.bg} shadow-[0_2px_8px_rgba(0,0,0,0.9)] shrink-0`}
                                    style={{ minHeight: '24px' }}
                                >
                                    <Zap className="h-3 w-3 fill-amber-400 text-amber-400 shrink-0 animate-pulse" />
                                    <span
                                        className="font-black uppercase tracking-wider whitespace-nowrap overflow-hidden text-ellipsis tcg-gold-emboss"
                                        style={{
                                            fontSize: layout.powerPlate.fontSize,
                                            color: theme.specialMoveColor
                                        }}
                                    >
                                        PODER: {specialMoveText}
                                    </span>
                                </div>

                                {/* 2b. TEXTO DE DESCRIPCIÓN / LORE CANÓNICO (En el cuerpo central) */}
                                <div className="flex-1 flex items-center justify-center text-center my-1 overflow-hidden">
                                    <p
                                        className="italic leading-relaxed text-stone-100 line-clamp-3 drop-shadow-[0_1px_3px_rgba(0,0,0,1)]"
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

                                {/* 2c. CATEGORIZACIÓN DE TIPO (Debajo del texto de descripción) */}
                                <div className="flex items-center justify-center text-center shrink-0 pt-0.5 border-t border-amber-500/20">
                                    <span
                                        className="font-black uppercase tracking-wider truncate drop-shadow-[0_1px_3px_rgba(0,0,0,0.95)]"
                                        style={{
                                            fontSize: layout.typeLine.fontSize,
                                            color: layout.typeLine.color
                                        }}
                                    >
                                        — {typeLineText} —
                                    </span>
                                </div>
                            </div>

                            {/* 3. SOCKETS DE COMBATE CENTRADOS EN LAS CASILLAS DE PIEDRA */}
                            {/* Sockets Izquierdo: FUE | MAG */}
                            <div
                                className="absolute z-20 flex items-center justify-center pointer-events-none"
                                style={{
                                    top: layout.leftSocket.top,
                                    left: layout.leftSocket.left,
                                    width: layout.leftSocket.width,
                                    height: layout.leftSocket.height
                                }}
                            >
                                <div className="flex items-center justify-center gap-1.5 text-[9px] sm:text-[9.5px] font-bold text-amber-200">
                                    <span>FUE <strong className="text-white text-[11px] font-black">{statsData.fuerza}</strong></span>
                                    <span className="text-amber-400/40">|</span>
                                    <span>MAG <strong className="text-white text-[11px] font-black">{statsData.magia}</strong></span>
                                </div>
                            </div>

                            {/* Sockets Derecho: DEF | AGI */}
                            <div
                                className="absolute z-20 flex items-center justify-center pointer-events-none"
                                style={{
                                    top: layout.rightSocket.top,
                                    right: layout.rightSocket.right,
                                    width: layout.rightSocket.width,
                                    height: layout.rightSocket.height
                                }}
                            >
                                <div className="flex items-center justify-center gap-1.5 text-[9px] sm:text-[9.5px] font-bold text-amber-200">
                                    <span>DEF <strong className="text-white text-[11px] font-black">{statsData.defensa}</strong></span>
                                    <span className="text-amber-400/40">|</span>
                                    <span>AGI <strong className="text-white text-[11px] font-black">{statsData.agilidad}</strong></span>
                                </div>
                            </div>

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



