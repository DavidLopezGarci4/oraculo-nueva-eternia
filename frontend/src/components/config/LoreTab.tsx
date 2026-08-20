import React, { useState, useEffect } from 'react';
import {
    BookOpen,
    Search,
    CheckCircle2,
    AlertTriangle,
    RefreshCw,
    Edit3,
    Zap,
    Globe,
    X,
    Save
} from 'lucide-react';
import {
    fetchCharacterLoreList,
    updateCharacterLore,
    harvestCharacterLore,
    seedInitialLore,
    type CharacterLore
} from '../../api/lore';

const FACTION_OPTIONS = [
    { value: 'ALL', label: 'Todas las Facciones' },
    { value: 'Guerreros Heroicos', label: '🛡️ Guerreros Heroicos' },
    { value: 'Guerreros del Mal', label: '💀 Guerreros del Mal' },
    { value: 'La Horda del Terror', label: '🦇 La Horda del Terror' },
    { value: 'Los Hombres Serpiente', label: '🐍 Los Hombres Serpiente' },
    { value: 'La Gran Rebelión', label: '✨ La Gran Rebelión' },
    { value: 'Guardianes Cósmicos', label: '🌌 Guardianes Cósmicos' }
];

const THEME_OPTIONS = [
    { value: 'castle_grayskull', label: 'Castillo Grayskull (Verde Musgo & Oro)' },
    { value: 'snake_mountain', label: 'Snake Mountain (Basalto & Lava)' },
    { value: 'evil_horde', label: 'La Horda (Bio-Metal Carmesí)' },
    { value: 'snake_men', label: 'Hombres Serpiente (Escamas & Cobra)' },
    { value: 'great_rebellion', label: 'Gran Rebelión (Mármol & Cristal)' },
    { value: 'cosmic_enforcers', label: 'Guardianes Cósmicos (Titanio Estelar)' }
];

export const LoreTab: React.FC = () => {
    const [characters, setCharacters] = useState<CharacterLore[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [factionFilter, setFactionFilter] = useState('ALL');
    const [pendingOnly, setPendingOnly] = useState(false);
    const [pendingCount, setPendingCount] = useState(0);
    const [editingChar, setEditingChar] = useState<CharacterLore | null>(null);
    const [saving, setSaving] = useState(false);
    const [harvesting, setHarvesting] = useState(false);
    const [seeding, setSeeding] = useState(false);
    const [toastMessage, setToastMessage] = useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        try {
            const data = await fetchCharacterLoreList({
                search: search || undefined,
                faction: factionFilter !== 'ALL' ? factionFilter : undefined,
                pending_only: pendingOnly
            });
            setCharacters(data.items);
            setPendingCount(data.pending_count);
        } catch (e) {
            console.error('Error al cargar lore:', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            loadData();
        }, 300);
        return () => clearTimeout(timer);
    }, [search, factionFilter, pendingOnly]);

    const showToast = (msg: string) => {
        setToastMessage(msg);
        setTimeout(() => setToastMessage(null), 3500);
    };

    const handleSave = async () => {
        if (!editingChar) return;
        setSaving(true);
        try {
            const updated = await updateCharacterLore(editingChar.slug, editingChar);
            setCharacters((prev) => prev.map((c) => (c.slug === updated.slug ? updated : c)));
            if (pendingOnly && updated.is_verified) {
                setCharacters((prev) => prev.filter((c) => c.slug !== updated.slug));
            }
            setPendingCount((prev) => Math.max(0, prev - (editingChar.is_verified ? 0 : 1)));
            setEditingChar(null);
            showToast(`✅ Lore de "${updated.canonical_name}" guardado y verificado`);
        } catch (e) {
            console.error('Error al guardar lore:', e);
            showToast('❌ Error al guardar los cambios');
        } finally {
            setSaving(false);
        }
    };

    const handleHarvest = async (charName: string) => {
        setHarvesting(true);
        try {
            const harvested = await harvestCharacterLore(charName);
            setEditingChar(harvested);
            showToast(`🌐 Datos recabados de Wiki Grayskull para "${harvested.canonical_name}"`);
        } catch (e) {
            console.error('Error al cosechar:', e);
            showToast('❌ No se pudo cosechar de la wiki');
        } finally {
            setHarvesting(false);
        }
    };

    const handleSeedAll = async () => {
        setSeeding(true);
        try {
            const res = await seedInitialLore();
            showToast(`🎉 Sembrado completado: ${res.result.seeded_characters} personajes, ${res.result.linked_products} muñecos vinculados.`);
            loadData();
        } catch (e) {
            console.error('Error al sembrar lore:', e);
            showToast('❌ Error al ejecutar el sembrado inicial');
        } finally {
            setSeeding(false);
        }
    };

    const getFactionBadgeColor = (faction: string) => {
        switch (faction) {
            case 'Guerreros Heroicos':
                return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
            case 'Guerreros del Mal':
                return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
            case 'La Horda del Terror':
                return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
            case 'Los Hombres Serpiente':
                return 'bg-lime-500/20 text-lime-300 border-lime-500/40';
            case 'La Gran Rebelión':
                return 'bg-pink-500/20 text-pink-300 border-pink-500/40';
            case 'Guardianes Cósmicos':
                return 'bg-sky-500/20 text-sky-300 border-sky-500/40';
            default:
                return 'bg-slate-700/50 text-slate-300 border-slate-600';
        }
    };

    return (
        <div className="space-y-6">
            {/* Cabecera del Grimorio */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-amber-500/20 shadow-xl">
                <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
                        <BookOpen className="h-6 w-6" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white font-cinzel flex items-center gap-2">
                            Grimorio de Lore Canónico MOTU
                            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono">
                                Coste 0€ / Caché Fija
                            </span>
                        </h2>
                        <p className="text-xs text-slate-400">
                            Base de datos canónica de personajes, facciones, habilidades especiales y frases míticas para los cromos TCG.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSeedAll}
                        disabled={seeding}
                        className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-bold font-cinzel transition active:scale-95 disabled:opacity-50"
                    >
                        <RefreshCw className={`h-4 w-4 ${seeding ? 'animate-spin' : ''}`} />
                        <span>Sincronizar 507 Muñecos</span>
                    </button>
                </div>
            </div>

            {/* Notificación Toast */}
            {toastMessage && (
                <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-slate-900 border border-amber-500/50 shadow-2xl text-sm font-semibold text-white animate-fade-in">
                    {toastMessage}
                </div>
            )}

            {/* Barra de Filtros y Búsqueda */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                {/* 1. Buscador */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Buscar personaje o frase..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500/60 focus:outline-none transition"
                    />
                </div>

                {/* 2. Selector de Facción */}
                <select
                    value={factionFilter}
                    onChange={(e) => setFactionFilter(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500/60 focus:outline-none transition"
                >
                    {FACTION_OPTIONS.map((f) => (
                        <option key={f.value} value={f.value}>
                            {f.label}
                        </option>
                    ))}
                </select>

                {/* 3. Filtro de Pendientes */}
                <button
                    onClick={() => setPendingOnly(!pendingOnly)}
                    className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                        pendingOnly
                            ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20'
                            : 'bg-slate-950 border border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                >
                    <AlertTriangle className={`h-4 w-4 ${pendingOnly ? 'text-slate-950' : 'text-amber-400'}`} />
                    <span>Pendientes de Revisión ({pendingCount})</span>
                </button>
            </div>

            {/* Cuadrícula de Personajes */}
            {loading ? (
                <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
                    <RefreshCw className="h-8 w-8 animate-spin text-amber-400" />
                    <p className="text-sm font-cinzel">Consultando el Grimorio de Eternia...</p>
                </div>
            ) : characters.length === 0 ? (
                <div className="p-12 text-center text-slate-500 rounded-xl bg-slate-900/40 border border-dashed border-slate-800">
                    <BookOpen className="h-10 w-10 mx-auto mb-2 opacity-40 text-amber-400" />
                    <p className="text-sm">No se encontraron personajes con los filtros seleccionados.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {characters.map((char) => (
                        <div
                            key={char.slug}
                            className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-amber-500/40 transition-all group relative flex flex-col justify-between"
                        >
                            <div>
                                {/* Cabecera de la Tarjeta */}
                                <div className="flex items-start justify-between gap-2 mb-2">
                                    <div>
                                        <h3 className="text-base font-bold text-white font-cinzel group-hover:text-amber-300 transition">
                                            {char.canonical_name}
                                        </h3>
                                        <span className="text-[10px] font-mono text-slate-400">
                                            slug: {char.slug}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-1.5 shrink-0">
                                        {char.is_verified ? (
                                            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-semibold">
                                                <CheckCircle2 className="h-3 w-3" /> Verificado
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-semibold animate-pulse">
                                                <AlertTriangle className="h-3 w-3" /> Pendiente
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Bando & Línea de Tipo */}
                                <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
                                    <span
                                        className={`px-2 py-0.5 rounded-md border text-[10px] font-bold ${getFactionBadgeColor(
                                            char.faction
                                        )}`}
                                    >
                                        {char.faction}
                                    </span>
                                    <span className="text-[10px] text-slate-400 truncate">
                                        • {char.type_line}
                                    </span>
                                </div>

                                {/* Poder Especial */}
                                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-black/50 border border-amber-500/20 text-amber-300 text-xs font-bold mb-2.5">
                                    <Zap className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                                    <span className="truncate">{char.special_move}</span>
                                </div>

                                {/* Lore Canónico */}
                                <p className="text-xs text-slate-300 italic line-clamp-3 leading-relaxed mb-3">
                                    "{char.lore}"
                                </p>
                            </div>

                            {/* Stats & Botón de Edición */}
                            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                                <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                                    <span>FUE <strong className="text-white">{char.fuerza}</strong></span>
                                    <span>MAG <strong className="text-white">{char.magia}</strong></span>
                                    <span>DEF <strong className="text-white">{char.defensa}</strong></span>
                                    <span>AGI <strong className="text-white">{char.agilidad}</strong></span>
                                </div>

                                <button
                                    onClick={() => setEditingChar({ ...char })}
                                    className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-amber-500/20 text-slate-300 hover:text-amber-300 border border-slate-700 hover:border-amber-500/40 text-xs font-semibold transition"
                                >
                                    <Edit3 className="h-3.5 w-3.5" />
                                    <span>Editar</span>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* MODAL EDITOR DE LORE */}
            {editingChar && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                    <div className="w-full max-w-2xl bg-slate-900 border border-amber-500/40 rounded-2xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
                        <button
                            onClick={() => setEditingChar(null)}
                            className="absolute top-4 right-4 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition"
                        >
                            <X className="h-5 w-5" />
                        </button>

                        <div className="flex items-center justify-between mb-4 pr-8">
                            <div className="flex items-center gap-2">
                                <BookOpen className="h-5 w-5 text-amber-400" />
                                <h3 className="text-lg font-bold text-white font-cinzel">
                                    Editar Lore: {editingChar.canonical_name}
                                </h3>
                            </div>

                            <button
                                onClick={() => handleHarvest(editingChar.canonical_name)}
                                disabled={harvesting}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/40 text-xs font-semibold transition active:scale-95 disabled:opacity-50"
                                title="Re-cosechar de Wiki Grayskull sin coste"
                            >
                                <Globe className={`h-3.5 w-3.5 ${harvesting ? 'animate-spin' : ''}`} />
                                <span>{harvesting ? 'Consultando...' : 'Re-cosechar de Wiki'}</span>
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {/* Nombre */}
                                <div>
                                    <label className="text-xs font-semibold text-slate-300 mb-1 block">
                                        Nombre Canónico
                                    </label>
                                    <input
                                        type="text"
                                        value={editingChar.canonical_name}
                                        onChange={(e) =>
                                            setEditingChar({ ...editingChar, canonical_name: e.target.value })
                                        }
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none"
                                    />
                                </div>

                                {/* Facción */}
                                <div>
                                    <label className="text-xs font-semibold text-slate-300 mb-1 block">
                                        Facción
                                    </label>
                                    <select
                                        value={editingChar.faction}
                                        onChange={(e) =>
                                            setEditingChar({ ...editingChar, faction: e.target.value })
                                        }
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none"
                                    >
                                        {FACTION_OPTIONS.filter((f) => f.value !== 'ALL').map((f) => (
                                            <option key={f.value} value={f.value}>
                                                {f.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {/* Marco Visual TCG */}
                                <div>
                                    <label className="text-xs font-semibold text-slate-300 mb-1 block">
                                        Marco Visual TCG
                                    </label>
                                    <select
                                        value={editingChar.theme_key}
                                        onChange={(e) =>
                                            setEditingChar({
                                                ...editingChar,
                                                theme_key: e.target.value as any
                                            })
                                        }
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none"
                                    >
                                        {THEME_OPTIONS.map((t) => (
                                            <option key={t.value} value={t.value}>
                                                {t.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Poder Especial */}
                                <div>
                                    <label className="text-xs font-semibold text-slate-300 mb-1 block">
                                        Poder / Habilidad de Alto Impacto
                                    </label>
                                    <input
                                        type="text"
                                        value={editingChar.special_move}
                                        onChange={(e) =>
                                            setEditingChar({ ...editingChar, special_move: e.target.value })
                                        }
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none"
                                    />
                                </div>
                            </div>

                            {/* Línea de Tipo */}
                            <div>
                                <label className="text-xs font-semibold text-slate-300 mb-1 block">
                                    Línea de Tipo (Subtítulo en cromo)
                                </label>
                                <input
                                    type="text"
                                    value={editingChar.type_line}
                                    onChange={(e) =>
                                        setEditingChar({ ...editingChar, type_line: e.target.value })
                                    }
                                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none"
                                />
                            </div>

                            {/* Texto de Lore / Frase Mítica */}
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <label className="text-xs font-semibold text-slate-300">
                                        Lore Canónico & Frase Mítica (Espacio Losa TCG)
                                    </label>
                                    <span
                                        className={`text-[11px] font-mono ${
                                            editingChar.lore.length > 180 ? 'text-amber-400' : 'text-slate-500'
                                        }`}
                                    >
                                        {editingChar.lore.length} / 180 caracteres
                                    </span>
                                </div>
                                <textarea
                                    rows={3}
                                    value={editingChar.lore}
                                    onChange={(e) =>
                                        setEditingChar({ ...editingChar, lore: e.target.value })
                                    }
                                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:border-amber-500 focus:outline-none resize-none"
                                />
                            </div>

                            {/* Estadísticas RPG */}
                            <div>
                                <label className="text-xs font-semibold text-slate-300 mb-2 block">
                                    Matriz de Combate (FUE / MAG / DEF / AGI)
                                </label>
                                <div className="grid grid-cols-4 gap-2">
                                    <div>
                                        <span className="text-[10px] text-slate-400 block mb-1">FUE</span>
                                        <input
                                            type="number"
                                            value={editingChar.fuerza}
                                            onChange={(e) =>
                                                setEditingChar({
                                                    ...editingChar,
                                                    fuerza: parseInt(e.target.value) || 0
                                                })
                                            }
                                            className="w-full px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center text-sm font-bold text-amber-300"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block mb-1">MAG</span>
                                        <input
                                            type="number"
                                            value={editingChar.magia}
                                            onChange={(e) =>
                                                setEditingChar({
                                                    ...editingChar,
                                                    magia: parseInt(e.target.value) || 0
                                                })
                                            }
                                            className="w-full px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center text-sm font-bold text-amber-300"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block mb-1">DEF</span>
                                        <input
                                            type="number"
                                            value={editingChar.defensa}
                                            onChange={(e) =>
                                                setEditingChar({
                                                    ...editingChar,
                                                    defensa: parseInt(e.target.value) || 0
                                                })
                                            }
                                            className="w-full px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center text-sm font-bold text-amber-300"
                                        />
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block mb-1">AGI</span>
                                        <input
                                            type="number"
                                            value={editingChar.agilidad}
                                            onChange={(e) =>
                                                setEditingChar({
                                                    ...editingChar,
                                                    agilidad: parseInt(e.target.value) || 0
                                                })
                                            }
                                            className="w-full px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center text-sm font-bold text-amber-300"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Botones de Acción */}
                        <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-slate-800">
                            <button
                                onClick={() => setEditingChar(null)}
                                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 text-slate-950 text-sm font-bold font-cinzel transition shadow-lg shadow-amber-500/20 active:scale-95 disabled:opacity-50"
                            >
                                <Save className="h-4 w-4" />
                                <span>{saving ? 'Guardando...' : 'Guardar y Verificar'}</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
