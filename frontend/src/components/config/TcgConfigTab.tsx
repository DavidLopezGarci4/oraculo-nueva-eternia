import { useState, useEffect } from 'react';
import { Sparkles, Save, RotateCcw, Copy, Check, Eye, Swords, Info } from 'lucide-react';
import { getSystemTcgLayouts, saveSystemTcgLayouts } from '../../api/admin';

export interface StatSocketCoord {
    top: string;
    left: string;
    fontSize: string;
    labelFontSize?: string;
}

export interface FactionCardLayout {
    header: { top: string; left: string; width: string; height: string; fontSizeMain?: string };
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
    // 4 Engarces de Orbes 3D Calibrables Individualmente
    statFue: StatSocketCoord;
    statMag: StatSocketCoord;
    statDef: StatSocketCoord;
    statAgi: StatSocketCoord;
    // Compatibilidad
    leftSocket?: { top: string; left: string; width: string; height: string; fontSize?: string };
    rightSocket?: { top: string; right: string; width: string; height: string; fontSize?: string };
    canvas: {
        header: { x: number; y: number };
        powerBox: { x: number; y: number; w: number; h: number };
        powerText: { y: number; fontSize: number };
        loreText: { y: number; maxW: number; lineH: number; fontSize: number };
        typeLine: { y: number; fontSize: number };
        statFue: { x: number; y: number };
        statMag: { x: number; y: number };
        statDef: { x: number; y: number };
        statAgi: { x: number; y: number };
        leftSocket?: { x: number; y: number };
        rightSocket?: { x: number; y: number };
    };
}

export const DEFAULT_FACTION_CARD_LAYOUTS: Record<string, FactionCardLayout> = {
    castle_grayskull: {
        header: { top: '10.4%', left: '13.5%', width: '62%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '53.5%', left: '13.5%', width: '73%', height: '31.5%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-amber-400/90',
            bg: 'from-black/90 via-amber-950/90 to-black/90'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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
        header: { top: '10.5%', left: '13.8%', width: '60%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '54.5%', left: '13.5%', width: '73%', height: '30.5%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-orange-500/90',
            bg: 'from-black/90 via-stone-950/90 to-black/90'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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
        header: { top: '10.2%', left: '13.5%', width: '60%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '53.8%', left: '13.5%', width: '73%', height: '31.0%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-rose-500/90',
            bg: 'from-black/90 via-red-950/90 to-black/90'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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
        header: { top: '10.4%', left: '13.5%', width: '60%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '54.2%', left: '13.5%', width: '73%', height: '30.8%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-lime-400/90',
            bg: 'from-black/90 via-emerald-950/90 to-black/90'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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
        header: { top: '10.4%', left: '13.5%', width: '60%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '54.0%', left: '13.5%', width: '73%', height: '31.0%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-pink-400/90',
            bg: 'from-black/85 via-pink-950/85 to-black/85'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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
        header: { top: '10.4%', left: '13.5%', width: '60%', height: '4.2%', fontSizeMain: '12px' },
        textBox: { top: '53.8%', left: '13.5%', width: '73%', height: '31.0%' },
        powerPlate: {
            height: '24px',
            fontSize: '9.5px',
            border: 'border-sky-400/90',
            bg: 'from-black/90 via-sky-950/90 to-black/90'
        },
        lore: { fontSize: '9.5px', lineHeight: '1.45' },
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

const FRAME_CACHE_VERSION = 'v=4cavities_3d_v2';

const FACTION_OPTIONS = [
    { key: 'castle_grayskull', name: 'Guerreros Heroicos', icon: '🏰', frame: `/frames/frame_castle_grayskull.webp?${FRAME_CACHE_VERSION}`, color: 'text-amber-400', border: 'border-amber-500/40' },
    { key: 'snake_mountain', name: 'Guerreros del Mal', icon: '🌋', frame: `/frames/frame_snake_mountain.webp?${FRAME_CACHE_VERSION}`, color: 'text-orange-400', border: 'border-orange-500/40' },
    { key: 'evil_horde', name: 'La Horda del Terror', icon: '🦇', frame: `/frames/frame_evil_horde.webp?${FRAME_CACHE_VERSION}`, color: 'text-red-400', border: 'border-red-500/40' },
    { key: 'snake_men', name: 'Los Hombres Serpiente', icon: '🐍', frame: `/frames/frame_snake_men.webp?${FRAME_CACHE_VERSION}`, color: 'text-lime-400', border: 'border-lime-500/40' },
    { key: 'great_rebellion', name: 'La Gran Rebelión', icon: '✨', frame: `/frames/frame_great_rebellion.webp?${FRAME_CACHE_VERSION}`, color: 'text-pink-400', border: 'border-pink-500/40' },
    { key: 'cosmic_enforcers', name: 'Guardianes Cósmicos', icon: '🌌', frame: `/frames/frame_cosmic_enforcers.webp?${FRAME_CACHE_VERSION}`, color: 'text-sky-400', border: 'border-sky-500/40' }
];

const SAMPLE_CHARACTERS: Record<string, { name: string; sub: string; power: string; lore: string; typeLine: string; stats: { fue: number; mag: number; def: number; agi: number } }> = {
    castle_grayskull: {
        name: 'BUZZ-OFF',
        sub: 'ORIGINS',
        power: 'FURIA DEL RELÁMPAGO DE GRAYSKULL',
        lore: 'Espía alado y noble defensor de la corte real de Eternia. Con su visión omnidireccional y aguijón letal, vigila los cielos protegiendo la paz sagrada de Grayskull.',
        typeLine: 'CRIATURA LEGENDARIA — GUERRERO HEROICO',
        stats: { fue: 88, mag: 78, def: 95, agi: 90 }
    },
    snake_mountain: {
        name: 'SKELETOR',
        sub: 'ORIGINS',
        power: 'DESCARGA DE SOMBRAS ARCANAS',
        lore: 'Señor de la destrucción y tirano nigromántico de Snake Mountain cuya sed de conquista amenaza la existencia. Empuñando el Báculo del Caos, canaliza las artes oscuras prohibidas de Subternia.',
        typeLine: 'CRIATURA LEGENDARIA — GUERRERO DEL MAL',
        stats: { fue: 92, mag: 99, def: 88, agi: 89 }
    },
    evil_horde: {
        name: 'HORDAK',
        sub: 'ORIGINS',
        power: 'CAÑÓN DE TRANSFORMACIÓN TECNO-MÁGICA',
        lore: 'Gobernante supremo de la Horda del Terror y antiguo maestro de Skeletor. Con su implacable tecnología alienígena y magia arcana, somete mundos enteros.',
        typeLine: 'TIRANO LEGENDARIO — LA HORDA DEL TERROR',
        stats: { fue: 95, mag: 96, def: 92, agi: 91 }
    },
    snake_men: {
        name: 'KING HISS',
        sub: 'ORIGINS',
        power: 'METAMORFOSIS DE SERPIENTES VENENOSAS',
        lore: 'Antiguo y despiadado rey de los Hombres Serpiente. Oculta bajo su apariencia regia un nido de serpientes monstruosas dotadas de un veneno demoledor.',
        typeLine: 'MONARCA OFÍDICO — LOS HOMBRES SERPIENTE',
        stats: { fue: 94, mag: 95, def: 90, agi: 93 }
    },
    great_rebellion: {
        name: 'SHE-RA',
        sub: 'ORIGINS',
        power: 'ESPADA DE PROTECCIÓN DE ETHERIA',
        lore: 'Defensora suprema del honor y la libertad de Etheria. Hermana gemela de He-Man, lidera la Gran Rebelión contra las garras de la Horda del Terror.',
        typeLine: 'PRINCESA DEL PODER — LA GRAN REBELIÓN',
        stats: { fue: 98, mag: 96, def: 94, agi: 95 }
    },
    cosmic_enforcers: {
        name: 'HE-RO',
        sub: 'PRETERNIA',
        power: 'MAGIA ANCESTRAL DE PRETERNIA',
        lore: 'El Mago más poderoso del Universo en la remota Preternia. Portador del báculo con la piedra de la sabiduría y ancestro del poder sagrado de Grayskull.',
        typeLine: 'MAGO PRETERNIANO — GUARDIANES CÓSMICOS',
        stats: { fue: 92, mag: 99, def: 94, agi: 93 }
    }
};

export default function TcgConfigTab() {
    const [selectedFaction, setSelectedFaction] = useState('castle_grayskull');
    const [layouts, setLayouts] = useState<Record<string, FactionCardLayout>>(DEFAULT_FACTION_CARD_LAYOUTS);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [copiedJson, setCopiedJson] = useState(false);

    // Cargar configuraciones guardadas de Supabase/Backend
    useEffect(() => {
        const loadConfigs = async () => {
            try {
                const remote = await getSystemTcgLayouts();
                if (remote && Object.keys(remote).length > 0) {
                    setLayouts(prev => ({
                        ...prev,
                        ...remote
                    }));
                } else {
                    const localStored = localStorage.getItem('tcg_card_layouts');
                    if (localStored) {
                        try {
                            setLayouts(JSON.parse(localStored));
                        } catch {}
                    }
                }
            } catch (err) {
                console.warn("Usando layouts locales por defecto:", err);
            } finally {
                setLoading(false);
            }
        };
        loadConfigs();
    }, []);

    const activeLayout = layouts[selectedFaction] || DEFAULT_FACTION_CARD_LAYOUTS[selectedFaction];
    const currentFactionInfo = FACTION_OPTIONS.find(f => f.key === selectedFaction) || FACTION_OPTIONS[0];
    const sampleChar = SAMPLE_CHARACTERS[selectedFaction] || SAMPLE_CHARACTERS.castle_grayskull;

    // Helper para actualizar propiedad específica en el layout actual
    const updateActiveCoord = (section: keyof FactionCardLayout, key: string, value: string) => {
        setLayouts(prev => {
            const current = { ...(prev[selectedFaction] || DEFAULT_FACTION_CARD_LAYOUTS[selectedFaction]) };
            const currentSection = { ...(current[section] as any) };
            currentSection[key] = value;

            const updated = {
                ...prev,
                [selectedFaction]: {
                    ...current,
                    [section]: currentSection
                }
            };
            // Cache local inmediata
            localStorage.setItem('tcg_card_layouts', JSON.stringify(updated));
            return updated;
        });
    };

    // Guardar en Backend / Supabase
    const handleSave = async () => {
        setSaving(true);
        try {
            await saveSystemTcgLayouts(layouts);
            localStorage.setItem('tcg_card_layouts', JSON.stringify(layouts));
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (err) {
            console.error("Error al guardar layouts TCG:", err);
            alert("No se pudo guardar la configuración en la nube. Se mantuvo en caché local.");
        } finally {
            setSaving(false);
        }
    };

    // Restablecer la facción actual a los valores por defecto
    const handleResetFaction = () => {
        if (!confirm(`¿Restablecer las coordenadas de ${currentFactionInfo.name} a los valores canónicos por defecto?`)) return;
        setLayouts(prev => {
            const updated = {
                ...prev,
                [selectedFaction]: { ...DEFAULT_FACTION_CARD_LAYOUTS[selectedFaction] }
            };
            localStorage.setItem('tcg_card_layouts', JSON.stringify(updated));
            return updated;
        });
    };

    // Restablecer todas las facciones
    const handleResetAll = () => {
        if (!confirm("¿Restablecer TODAS las 6 facciones a los valores canónicos por defecto?")) return;
        setLayouts(DEFAULT_FACTION_CARD_LAYOUTS);
        localStorage.setItem('tcg_card_layouts', JSON.stringify(DEFAULT_FACTION_CARD_LAYOUTS));
    };

    // Copiar JSON
    const handleCopyJson = () => {
        navigator.clipboard.writeText(JSON.stringify(layouts, null, 2));
        setCopiedJson(true);
        setTimeout(() => setCopiedJson(false), 2500);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20 text-white/50 gap-3">
                <div className="h-5 w-5 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                <span>Cargando calibrador visual de cromos...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-300">
            {/* Header del Calibrador TCG */}
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-purple-500/5 to-transparent border border-amber-500/20 backdrop-blur-md">
                <div className="flex items-center gap-3.5">
                    <div className="p-3 rounded-xl bg-amber-500/20 border border-amber-400/30 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
                        <Sparkles className="h-6 w-6 text-amber-400 animate-pulse" />
                    </div>
                    <div>
                        <h3 className="text-lg font-black text-white flex items-center gap-2">
                            Taller de Calibración de Cromos Digitales (TCG Studio)
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/40 uppercase tracking-widest font-mono">
                                Admin Studio
                            </span>
                        </h3>
                        <p className="text-xs text-white/60">
                            Ajusta y posiciona al milímetro los textos, losas y zócalos de cada una de las 6 plantillas canónicas de cromos.
                        </p>
                    </div>
                </div>

                {/* Acciones Maestras */}
                <div className="flex items-center gap-2 flex-wrap">
                    <button
                        onClick={handleCopyJson}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-bold text-white/80 transition-all cursor-pointer"
                        title="Copiar JSON de coordenadas al portapapeles"
                    >
                        {copiedJson ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5 text-white/60" />}
                        {copiedJson ? '¡Copiado!' : 'Copiar JSON'}
                    </button>
                    <button
                        onClick={handleResetFaction}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/30 text-xs font-bold text-white/70 hover:text-red-300 transition-all cursor-pointer"
                        title="Restablecer facción actual a valores por defecto"
                    >
                        <RotateCcw className="h-3.5 w-3.5" />
                        Restablecer Facción
                    </button>
                    <button
                        onClick={handleResetAll}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/30 text-xs font-bold text-white/70 hover:text-red-300 transition-all cursor-pointer"
                        title="Restablecer todas las facciones a valores por defecto"
                    >
                        <RotateCcw className="h-3.5 w-3.5" />
                        Restablecer Todas
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-black text-xs uppercase tracking-wider shadow-[0_0_20px_rgba(245,158,11,0.4)] transition-all cursor-pointer disabled:opacity-50"
                    >
                        {saving ? (
                            <div className="h-3.5 w-3.5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                        ) : saveSuccess ? (
                            <Check className="h-3.5 w-3.5 text-black" />
                        ) : (
                            <Save className="h-3.5 w-3.5 text-black" />
                        )}
                        {saveSuccess ? '¡Guardado en la Nube!' : 'Guardar Coordenadas'}
                    </button>
                </div>
            </div>

            {/* Selector de Facción / Plantilla */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
                {FACTION_OPTIONS.map(fac => {
                    const isSelected = selectedFaction === fac.key;
                    return (
                        <button
                            key={fac.key}
                            onClick={() => setSelectedFaction(fac.key)}
                            className={`flex flex-col items-center justify-center gap-1.5 p-3 rounded-2xl border transition-all cursor-pointer text-center ${
                                isSelected
                                    ? `bg-amber-500/15 ${fac.border} ring-2 ring-amber-400/50 shadow-[0_0_20px_rgba(245,158,11,0.25)]`
                                    : 'bg-black/30 border-white/5 hover:bg-white/5 hover:border-white/20'
                            }`}
                        >
                            <span className="text-xl">{fac.icon}</span>
                            <span className={`text-[11px] font-black uppercase tracking-wider ${isSelected ? fac.color : 'text-white/70'}`}>
                                {fac.name}
                            </span>
                        </button>
                    );
                })}
            </div>

            {/* Panel Principal: Simulador en Vivo + Controles */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* COLUMNA IZQUIERDA: Simulador Visual en Tiempo Real (5 columnas) */}
                <div className="lg:col-span-5 flex flex-col items-center gap-4 bg-black/40 border border-white/10 p-5 rounded-3xl sticky top-6 shadow-2xl backdrop-blur-xl">
                    <div className="flex items-center justify-between w-full px-2">
                        <span className="text-[11px] font-black uppercase tracking-widest text-amber-400 flex items-center gap-1.5">
                            <Eye className="h-3.5 w-3.5" />
                            Simulador en Tiempo Real
                        </span>
                        <span className="text-[10px] font-mono text-white/50">
                            {currentFactionInfo.name} (896 × 1200)
                        </span>
                    </div>

                    {/* Cromo Renderizado en Vivo */}
                    <div className="relative w-[300px] sm:w-[320px] h-[400px] sm:h-[426px] rounded-2xl overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.9)] border border-white/10 select-none bg-[#060a0f]">
                        {/* Capa 1: Fondo e Ilustración Simulada (Abarca todo el Arco Libre hasta la cúspide) */}
                        <div className="absolute inset-0 z-0 bg-gradient-to-b from-slate-900 via-indigo-950 to-black overflow-hidden">
                            <div
                                className="absolute flex flex-col items-center justify-center text-center p-3 rounded-t-3xl bg-amber-500/10 border border-amber-400/20 shadow-inner"
                                style={{
                                    top: '5.5%',
                                    left: '8.0%',
                                    width: '84%',
                                    height: '50%'
                                }}
                            >
                                <Swords className="h-10 w-10 text-amber-400/40 mb-1 animate-pulse" />
                                <span className="text-[10px] font-bold text-amber-200/60 uppercase">Ilustración MOTU</span>
                            </div>
                        </div>

                        {/* Capa 2: Plantilla Marco HD WebP */}
                        <img
                            src={currentFactionInfo.frame}
                            alt="Marco TCG"
                            className="absolute inset-0 w-full h-full object-fill pointer-events-none z-10 select-none drop-shadow-2xl"
                        />

                        {/* Capa 3: Textos Parametrizados en Tiempo Real */}
                        {/* 1. Cabecera (Nombre + Subtítulo) */}
                        <div
                            className="absolute z-20 flex items-center justify-start pointer-events-none overflow-hidden px-1"
                            style={{
                                top: activeLayout.header.top,
                                left: activeLayout.header.left,
                                width: activeLayout.header.width,
                                height: activeLayout.header.height
                            }}
                        >
                            <div className="flex items-center gap-1 min-w-0">
                                <h4
                                    className="font-black text-white uppercase tracking-wider truncate drop-shadow-[0_2px_4px_rgba(0,0,0,1)]"
                                    style={{ fontSize: activeLayout.header.fontSizeMain || '12px' }}
                                >
                                    {sampleChar.name}
                                </h4>
                                <span className="text-[8px] font-semibold text-amber-200 uppercase tracking-tight truncate shrink-0 drop-shadow-[0_1px_2px_rgba(0,0,0,0.9)]">
                                    • {sampleChar.sub}
                                </span>
                            </div>
                        </div>

                        {/* 2. Losa de Piedra Unificada (Lore Canónico) */}
                        <div
                            className="absolute z-20 flex flex-col items-center justify-center text-center pointer-events-none px-3 py-2 overflow-hidden rounded-xl bg-black/40 backdrop-blur-[1px] shadow-inner"
                            style={{
                                top: activeLayout.textBox.top,
                                left: activeLayout.textBox.left,
                                width: activeLayout.textBox.width,
                                height: activeLayout.textBox.height
                            }}
                        >
                            {/* Texto de Lore Canónico Centrado */}
                            <p
                                className="italic leading-relaxed text-stone-100 line-clamp-4 drop-shadow-[0_1px_3px_rgba(0,0,0,1)] text-center my-auto"
                                style={{
                                    fontSize: activeLayout.lore.fontSize,
                                    lineHeight: activeLayout.lore.lineHeight,
                                    textShadow: '0 1px 2px rgba(0,0,0,1), 0 0 4px rgba(0,0,0,0.8)'
                                }}
                            >
                                "{sampleChar.lore}"
                            </p>
                        </div>

                        {/* 3. Engarces de Combate 3D Nativos (4 Orbes Calibrados Individualmente) */}
                        {/* Fuerza */}
                        <div
                            className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                            style={{
                                top: activeLayout.statFue?.top || '87.2%',
                                left: activeLayout.statFue?.left || '21.2%'
                            }}
                        >
                            <span
                                className="font-black text-red-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.statFue?.labelFontSize || '7px' }}
                            >
                                FUE
                            </span>
                            <span
                                className="font-black text-white leading-none tcg-gold-emboss mt-0.5"
                                style={{ fontSize: activeLayout.statFue?.fontSize || '11.5px' }}
                            >
                                {sampleChar.stats.fue}
                            </span>
                        </div>

                        {/* Magia */}
                        <div
                            className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                            style={{
                                top: activeLayout.statMag?.top || '87.2%',
                                left: activeLayout.statMag?.left || '34.4%'
                            }}
                        >
                            <span
                                className="font-black text-purple-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.statMag?.labelFontSize || '7px' }}
                            >
                                MAG
                            </span>
                            <span
                                className="font-black text-white leading-none tcg-gold-emboss mt-0.5"
                                style={{ fontSize: activeLayout.statMag?.fontSize || '11.5px' }}
                            >
                                {sampleChar.stats.mag}
                            </span>
                        </div>

                        {/* Defensa */}
                        <div
                            className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                            style={{
                                top: activeLayout.statDef?.top || '87.2%',
                                left: activeLayout.statDef?.left || '65.6%'
                            }}
                        >
                            <span
                                className="font-black text-sky-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.statDef?.labelFontSize || '7px' }}
                            >
                                DEF
                            </span>
                            <span
                                className="font-black text-white leading-none tcg-gold-emboss mt-0.5"
                                style={{ fontSize: activeLayout.statDef?.fontSize || '11.5px' }}
                            >
                                {sampleChar.stats.def}
                            </span>
                        </div>

                        {/* Agilidad */}
                        <div
                            className="absolute z-20 flex flex-col items-center justify-center pointer-events-none -translate-x-1/2 -translate-y-1/2"
                            style={{
                                top: activeLayout.statAgi?.top || '87.2%',
                                left: activeLayout.statAgi?.left || '78.8%'
                            }}
                        >
                            <span
                                className="font-black text-emerald-300 uppercase tracking-widest leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.statAgi?.labelFontSize || '7px' }}
                            >
                                AGI
                            </span>
                            <span
                                className="font-black text-white leading-none tcg-gold-emboss mt-0.5"
                                style={{ fontSize: activeLayout.statAgi?.fontSize || '11.5px' }}
                            >
                                {sampleChar.stats.agi}
                            </span>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-white/50">
                        <Info className="h-3.5 w-3.5 text-amber-400" />
                        <span>Mueve los sliders a la derecha para ver los cambios en directo.</span>
                    </div>
                </div>

                {/* COLUMNA DERECHA: Controles de Calibración por Secciones (7 columnas) */}
                <div className="lg:col-span-7 space-y-5">
                    {/* SECCIÓN 1: CABECERA Y TÍTULO */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-amber-400" />
                                1. Cabecera y Título del Personaje
                            </h4>
                            <span className="text-[10px] font-mono text-amber-400/70">header</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Top */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Posición Vertical (Top)</span>
                                    <span className="text-amber-300 font-mono">{activeLayout.header.top}</span>
                                </div>
                                <input
                                    type="range"
                                    min="5.0"
                                    max="18.0"
                                    step="0.1"
                                    value={parseFloat(activeLayout.header.top)}
                                    onChange={(e) => updateActiveCoord('header', 'top', `${e.target.value}%`)}
                                    className="w-full accent-amber-400"
                                />
                            </div>

                            {/* Left */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Posición Horizontal (Left)</span>
                                    <span className="text-amber-300 font-mono">{activeLayout.header.left}</span>
                                </div>
                                <input
                                    type="range"
                                    min="8.0"
                                    max="25.0"
                                    step="0.1"
                                    value={parseFloat(activeLayout.header.left)}
                                    onChange={(e) => updateActiveCoord('header', 'left', `${e.target.value}%`)}
                                    className="w-full accent-amber-400"
                                />
                            </div>

                            {/* Width */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Ancho Útil (Width)</span>
                                    <span className="text-amber-300 font-mono">{activeLayout.header.width}</span>
                                </div>
                                <input
                                    type="range"
                                    min="45.0"
                                    max="75.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.header.width)}
                                    onChange={(e) => updateActiveCoord('header', 'width', `${e.target.value}%`)}
                                    className="w-full accent-amber-400"
                                />
                            </div>

                            {/* Font Size Main */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Tamaño Título (Font Size)</span>
                                    <span className="text-amber-300 font-mono">{activeLayout.header.fontSizeMain || '12px'}</span>
                                </div>
                                <input
                                    type="range"
                                    min="9.0"
                                    max="16.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.header.fontSizeMain || '12px')}
                                    onChange={(e) => updateActiveCoord('header', 'fontSizeMain', `${e.target.value}px`)}
                                    className="w-full accent-amber-400"
                                />
                            </div>
                        </div>
                    </div>

                    {/* SECCIÓN 2: LOSA DE PIEDRA (CAJA DE TEXTO UNIFICADA) */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-orange-400" />
                                2. Losa de Piedra (Caja de Texto Unificada)
                            </h4>
                            <span className="text-[10px] font-mono text-orange-400/70">textBox</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Top */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Posición Vertical (Top)</span>
                                    <span className="text-orange-300 font-mono">{activeLayout.textBox.top}</span>
                                </div>
                                <input
                                    type="range"
                                    min="48.0"
                                    max="62.0"
                                    step="0.1"
                                    value={parseFloat(activeLayout.textBox.top)}
                                    onChange={(e) => updateActiveCoord('textBox', 'top', `${e.target.value}%`)}
                                    className="w-full accent-orange-400"
                                />
                            </div>

                            {/* Left */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Posición Horizontal (Left)</span>
                                    <span className="text-orange-300 font-mono">{activeLayout.textBox.left}</span>
                                </div>
                                <input
                                    type="range"
                                    min="8.0"
                                    max="20.0"
                                    step="0.1"
                                    value={parseFloat(activeLayout.textBox.left)}
                                    onChange={(e) => updateActiveCoord('textBox', 'left', `${e.target.value}%`)}
                                    className="w-full accent-orange-400"
                                />
                            </div>

                            {/* Width */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Ancho Losa (Width)</span>
                                    <span className="text-orange-300 font-mono">{activeLayout.textBox.width}</span>
                                </div>
                                <input
                                    type="range"
                                    min="60.0"
                                    max="82.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.textBox.width)}
                                    onChange={(e) => updateActiveCoord('textBox', 'width', `${e.target.value}%`)}
                                    className="w-full accent-orange-400"
                                />
                            </div>

                            {/* Height */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Alto Losa (Height)</span>
                                    <span className="text-orange-300 font-mono">{activeLayout.textBox.height}</span>
                                </div>
                                <input
                                    type="range"
                                    min="24.0"
                                    max="38.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.textBox.height)}
                                    onChange={(e) => updateActiveCoord('textBox', 'height', `${e.target.value}%`)}
                                    className="w-full accent-orange-400"
                                />
                            </div>
                        </div>
                    </div>

                    {/* SECCIÓN 3: TIPOGRAFÍA Y ESTILO DEL LORE */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-purple-400" />
                                3. Tipografía y Estilo del Lore Canónico
                            </h4>
                            <span className="text-[10px] font-mono text-purple-400/70">lore</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Lore: Font Size */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Tamaño Fuente Lore</span>
                                    <span className="text-purple-300 font-mono">{activeLayout.lore.fontSize}</span>
                                </div>
                                <input
                                    type="range"
                                    min="7.5"
                                    max="14.0"
                                    step="0.2"
                                    value={parseFloat(activeLayout.lore.fontSize)}
                                    onChange={(e) => updateActiveCoord('lore', 'fontSize', `${e.target.value}px`)}
                                    className="w-full accent-purple-400"
                                />
                            </div>

                            {/* Lore: Line Height */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Interlineado (Line Height)</span>
                                    <span className="text-purple-300 font-mono">{activeLayout.lore.lineHeight}</span>
                                </div>
                                <input
                                    type="range"
                                    min="1.1"
                                    max="2.0"
                                    step="0.05"
                                    value={parseFloat(activeLayout.lore.lineHeight)}
                                    onChange={(e) => updateActiveCoord('lore', 'lineHeight', e.target.value)}
                                    className="w-full accent-purple-400"
                                />
                            </div>
                        </div>
                    </div>

                    {/* SECCIÓN 4: CALIBRACIÓN INDIVIDUAL DE LOS 4 ORBES 3D */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-5">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                                4. Calibración Milimétrica de los 4 Orbes de Poder 3D
                            </h4>
                            <span className="text-[10px] font-mono text-emerald-400/70">statFue / statMag / statDef / statAgi</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* ORBE 1: FUERZA (FUE) */}
                            <div className="p-3.5 rounded-xl bg-red-950/30 border border-red-500/30 space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-black text-red-400 uppercase tracking-wider flex items-center gap-1.5">
                                        <span className="h-2 w-2 rounded-full bg-red-500" />
                                        🔴 Fuerza (FUE)
                                    </span>
                                    <span className="text-[10px] font-mono text-red-300">
                                        {activeLayout.statFue?.left || '21.2%'} / {activeLayout.statFue?.top || '87.2%'}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px]">
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición X (Left)</span>
                                        <input
                                            type="range"
                                            min="14.0"
                                            max="28.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statFue?.left || '21.2%')}
                                            onChange={(e) => updateActiveCoord('statFue', 'left', `${e.target.value}%`)}
                                            className="w-full accent-red-400"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición Y (Top)</span>
                                        <input
                                            type="range"
                                            min="82.0"
                                            max="93.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statFue?.top || '87.2%')}
                                            onChange={(e) => updateActiveCoord('statFue', 'top', `${e.target.value}%`)}
                                            className="w-full accent-red-400"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* ORBE 2: MAGIA (MAG) */}
                            <div className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/30 space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-black text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
                                        <span className="h-2 w-2 rounded-full bg-purple-500" />
                                        🟣 Magia (MAG)
                                    </span>
                                    <span className="text-[10px] font-mono text-purple-300">
                                        {activeLayout.statMag?.left || '34.4%'} / {activeLayout.statMag?.top || '87.2%'}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px]">
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición X (Left)</span>
                                        <input
                                            type="range"
                                            min="28.0"
                                            max="42.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statMag?.left || '34.4%')}
                                            onChange={(e) => updateActiveCoord('statMag', 'left', `${e.target.value}%`)}
                                            className="w-full accent-purple-400"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición Y (Top)</span>
                                        <input
                                            type="range"
                                            min="82.0"
                                            max="93.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statMag?.top || '87.2%')}
                                            onChange={(e) => updateActiveCoord('statMag', 'top', `${e.target.value}%`)}
                                            className="w-full accent-purple-400"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* ORBE 3: DEFENSA (DEF) */}
                            <div className="p-3.5 rounded-xl bg-sky-950/30 border border-sky-500/30 space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-black text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                                        <span className="h-2 w-2 rounded-full bg-sky-500" />
                                        🔵 Defensa (DEF)
                                    </span>
                                    <span className="text-[10px] font-mono text-sky-300">
                                        {activeLayout.statDef?.left || '65.6%'} / {activeLayout.statDef?.top || '87.2%'}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px]">
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición X (Left)</span>
                                        <input
                                            type="range"
                                            min="58.0"
                                            max="72.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statDef?.left || '65.6%')}
                                            onChange={(e) => updateActiveCoord('statDef', 'left', `${e.target.value}%`)}
                                            className="w-full accent-sky-400"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición Y (Top)</span>
                                        <input
                                            type="range"
                                            min="82.0"
                                            max="93.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statDef?.top || '87.2%')}
                                            onChange={(e) => updateActiveCoord('statDef', 'top', `${e.target.value}%`)}
                                            className="w-full accent-sky-400"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* ORBE 4: AGILIDAD (AGI) */}
                            <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-black text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                                        🟢 Agilidad (AGI)
                                    </span>
                                    <span className="text-[10px] font-mono text-emerald-300">
                                        {activeLayout.statAgi?.left || '78.8%'} / {activeLayout.statAgi?.top || '87.2%'}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px]">
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición X (Left)</span>
                                        <input
                                            type="range"
                                            min="72.0"
                                            max="86.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statAgi?.left || '78.8%')}
                                            onChange={(e) => updateActiveCoord('statAgi', 'left', `${e.target.value}%`)}
                                            className="w-full accent-emerald-400"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-white/60 font-bold block mb-1">Posición Y (Top)</span>
                                        <input
                                            type="range"
                                            min="82.0"
                                            max="93.0"
                                            step="0.1"
                                            value={parseFloat(activeLayout.statAgi?.top || '87.2%')}
                                            onChange={(e) => updateActiveCoord('statAgi', 'top', `${e.target.value}%`)}
                                            className="w-full accent-emerald-400"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
