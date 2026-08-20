import { useState, useEffect } from 'react';
import { Sparkles, Save, RotateCcw, Copy, Check, Zap, Eye, Swords, Info } from 'lucide-react';
import { getSystemTcgLayouts, saveSystemTcgLayouts } from '../../api/admin';

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
    leftSocket: { top: string; left: string; width: string; height: string; fontSize?: string };
    rightSocket: { top: string; right: string; width: string; height: string; fontSize?: string };
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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
        leftSocket: { top: '86.6%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.6%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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
        leftSocket: { top: '86.8%', left: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
        rightSocket: { top: '86.8%', right: '14.0%', width: '32.0%', height: '4.5%', fontSize: '9px' },
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

const FACTION_OPTIONS = [
    { key: 'castle_grayskull', name: 'Guerreros Heroicos', icon: '🏰', frame: '/frames/frame_castle_grayskull.webp', color: 'text-amber-400', border: 'border-amber-500/40' },
    { key: 'snake_mountain', name: 'Guerreros del Mal', icon: '🌋', frame: '/frames/frame_snake_mountain.webp', color: 'text-orange-400', border: 'border-orange-500/40' },
    { key: 'evil_horde', name: 'La Horda del Terror', icon: '🦇', frame: '/frames/frame_evil_horde.webp', color: 'text-red-400', border: 'border-red-500/40' },
    { key: 'snake_men', name: 'Los Hombres Serpiente', icon: '🐍', frame: '/frames/frame_snake_men.webp', color: 'text-lime-400', border: 'border-lime-500/40' },
    { key: 'great_rebellion', name: 'La Gran Rebelión', icon: '✨', frame: '/frames/frame_great_rebellion.webp', color: 'text-pink-400', border: 'border-pink-500/40' },
    { key: 'cosmic_enforcers', name: 'Guardianes Cósmicos', icon: '🌌', frame: '/frames/frame_cosmic_enforcers.webp', color: 'text-sky-400', border: 'border-sky-500/40' }
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
                        {/* Capa 1: Fondo e Ilustración Simulada */}
                        <div className="absolute inset-0 z-0 flex items-center justify-center bg-gradient-to-b from-slate-900 via-indigo-950 to-black overflow-hidden">
                            <div className="w-[180px] h-[190px] rounded-2xl bg-amber-500/10 border border-amber-400/20 flex flex-col items-center justify-center text-center p-3 mt-[-80px]">
                                <Swords className="h-10 w-10 text-amber-400/40 mb-1" />
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

                        {/* 2. Losa de Piedra Unificada (Poder + Lore + Categorización) */}
                        <div
                            className="absolute z-20 flex flex-col justify-between pointer-events-none px-2.5 py-1.5 overflow-hidden rounded-xl bg-black/40 backdrop-blur-[1px] shadow-inner"
                            style={{
                                top: activeLayout.textBox.top,
                                left: activeLayout.textBox.left,
                                width: activeLayout.textBox.width,
                                height: activeLayout.textBox.height
                            }}
                        >
                            {/* 2a. Placa de Poder */}
                            <div
                                className={`flex items-center justify-center gap-1 px-2 py-0.5 rounded-lg border ${activeLayout.powerPlate.border} bg-gradient-to-r ${activeLayout.powerPlate.bg} shadow-[0_2px_8px_rgba(0,0,0,0.9)] shrink-0`}
                                style={{ minHeight: activeLayout.powerPlate.height }}
                            >
                                <Zap className="h-2.5 w-2.5 fill-amber-400 text-amber-400 shrink-0" />
                                <span
                                    className="font-black uppercase tracking-wider whitespace-nowrap overflow-hidden text-ellipsis text-amber-300 drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                    style={{ fontSize: activeLayout.powerPlate.fontSize }}
                                >
                                    PODER: {sampleChar.power}
                                </span>
                            </div>

                            {/* 2b. Texto de Lore Canónico */}
                            <div className="flex-1 flex items-center justify-center text-center my-0.5 overflow-hidden">
                                <p
                                    className="italic leading-tight text-stone-100 line-clamp-3 drop-shadow-[0_1px_3px_rgba(0,0,0,1)]"
                                    style={{
                                        fontSize: activeLayout.lore.fontSize,
                                        lineHeight: activeLayout.lore.lineHeight,
                                        textShadow: '0 1px 2px rgba(0,0,0,1), 0 0 4px rgba(0,0,0,0.8)'
                                    }}
                                >
                                    "{sampleChar.lore}"
                                </p>
                            </div>

                            {/* 2c. Categorización / Tipo (Pie de Losa) */}
                            <div className="flex items-center justify-center text-center shrink-0 pt-0.5 border-t border-amber-500/20">
                                <span
                                    className="font-black uppercase tracking-wider truncate drop-shadow-[0_1px_3px_rgba(0,0,0,0.95)]"
                                    style={{
                                        fontSize: activeLayout.typeLine.fontSize,
                                        color: activeLayout.typeLine.color
                                    }}
                                >
                                    — {sampleChar.typeLine} —
                                </span>
                            </div>
                        </div>

                        {/* 3. Sockets de Combate */}
                        {/* Izquierdo: FUE | MAG */}
                        <div
                            className="absolute z-20 flex items-center justify-center pointer-events-none"
                            style={{
                                top: activeLayout.leftSocket.top,
                                left: activeLayout.leftSocket.left,
                                width: activeLayout.leftSocket.width,
                                height: activeLayout.leftSocket.height
                            }}
                        >
                            <div
                                className="flex items-center justify-center gap-1 font-bold text-amber-200 drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.leftSocket.fontSize || '9px' }}
                            >
                                <span>FUE <strong className="text-white font-black">{sampleChar.stats.fue}</strong></span>
                                <span className="text-amber-400/40">|</span>
                                <span>MAG <strong className="text-white font-black">{sampleChar.stats.mag}</strong></span>
                            </div>
                        </div>

                        {/* Derecho: DEF | AGI */}
                        <div
                            className="absolute z-20 flex items-center justify-center pointer-events-none"
                            style={{
                                top: activeLayout.rightSocket.top,
                                right: activeLayout.rightSocket.right,
                                width: activeLayout.rightSocket.width,
                                height: activeLayout.rightSocket.height
                            }}
                        >
                            <div
                                className="flex items-center justify-center gap-1 font-bold text-amber-200 drop-shadow-[0_1px_2px_rgba(0,0,0,1)]"
                                style={{ fontSize: activeLayout.rightSocket.fontSize || '9px' }}
                            >
                                <span>DEF <strong className="text-white font-black">{sampleChar.stats.def}</strong></span>
                                <span className="text-amber-400/40">|</span>
                                <span>AGI <strong className="text-white font-black">{sampleChar.stats.agi}</strong></span>
                            </div>
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

                    {/* SECCIÓN 3: PLACA DE PODER, LORE Y TIPO */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-purple-400" />
                                3. Placa de Poder, Lore y Categorización
                            </h4>
                            <span className="text-[10px] font-mono text-purple-400/70">power / lore / typeLine</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {/* Placa de Poder: Font Size */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Fuente Poder</span>
                                    <span className="text-purple-300 font-mono">{activeLayout.powerPlate.fontSize}</span>
                                </div>
                                <input
                                    type="range"
                                    min="7.5"
                                    max="13.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.powerPlate.fontSize)}
                                    onChange={(e) => updateActiveCoord('powerPlate', 'fontSize', `${e.target.value}px`)}
                                    className="w-full accent-purple-400"
                                />
                            </div>

                            {/* Lore: Font Size */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Fuente Lore</span>
                                    <span className="text-purple-300 font-mono">{activeLayout.lore.fontSize}</span>
                                </div>
                                <input
                                    type="range"
                                    min="7.5"
                                    max="13.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.lore.fontSize)}
                                    onChange={(e) => updateActiveCoord('lore', 'fontSize', `${e.target.value}px`)}
                                    className="w-full accent-purple-400"
                                />
                            </div>

                            {/* TypeLine: Font Size */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Fuente Tipo</span>
                                    <span className="text-purple-300 font-mono">{activeLayout.typeLine.fontSize}</span>
                                </div>
                                <input
                                    type="range"
                                    min="6.5"
                                    max="11.5"
                                    step="0.5"
                                    value={parseFloat(activeLayout.typeLine.fontSize)}
                                    onChange={(e) => updateActiveCoord('typeLine', 'fontSize', `${e.target.value}px`)}
                                    className="w-full accent-purple-400"
                                />
                            </div>
                        </div>
                    </div>

                    {/* SECCIÓN 4: SOCKETS DE COMBATE INFERIORES */}
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-black text-white flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                                4. Sockets de Combate Inferiores (FUE/MAG y DEF/AGI)
                            </h4>
                            <span className="text-[10px] font-mono text-emerald-400/70">sockets</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {/* Top */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Posición Vertical (Top)</span>
                                    <span className="text-emerald-300 font-mono">{activeLayout.leftSocket.top}</span>
                                </div>
                                <input
                                    type="range"
                                    min="82.0"
                                    max="92.0"
                                    step="0.1"
                                    value={parseFloat(activeLayout.leftSocket.top)}
                                    onChange={(e) => {
                                        updateActiveCoord('leftSocket', 'top', `${e.target.value}%`);
                                        updateActiveCoord('rightSocket', 'top', `${e.target.value}%`);
                                    }}
                                    className="w-full accent-emerald-400"
                                />
                            </div>

                            {/* Margen Lateral */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Margen Lateral (Left/Right)</span>
                                    <span className="text-emerald-300 font-mono">{activeLayout.leftSocket.left}</span>
                                </div>
                                <input
                                    type="range"
                                    min="9.0"
                                    max="20.0"
                                    step="0.2"
                                    value={parseFloat(activeLayout.leftSocket.left)}
                                    onChange={(e) => {
                                        updateActiveCoord('leftSocket', 'left', `${e.target.value}%`);
                                        updateActiveCoord('rightSocket', 'right', `${e.target.value}%`);
                                    }}
                                    className="w-full accent-emerald-400"
                                />
                            </div>

                            {/* Font Size Stats */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-white/60 font-bold">
                                    <span>Tamaño Letra Stats</span>
                                    <span className="text-emerald-300 font-mono">{activeLayout.leftSocket.fontSize || '9px'}</span>
                                </div>
                                <input
                                    type="range"
                                    min="7.5"
                                    max="12.0"
                                    step="0.5"
                                    value={parseFloat(activeLayout.leftSocket.fontSize || '9px')}
                                    onChange={(e) => {
                                        updateActiveCoord('leftSocket', 'fontSize', `${e.target.value}px`);
                                        updateActiveCoord('rightSocket', 'fontSize', `${e.target.value}px`);
                                    }}
                                    className="w-full accent-emerald-400"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
