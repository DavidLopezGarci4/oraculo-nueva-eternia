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
    Save,
    ChevronDown,
    ChevronUp,
    Quote,
    Package,
    Users,
    Sparkles
} from 'lucide-react';
import {
    fetchCharacterLoreList,
    updateCharacterLore,
    harvestCharacterLore,
    seedInitialLore,
    fetchProductLoreList,
    updateProductLore,
    type CharacterLore,
    type ProductLoreListItem
} from '../../api/lore';
import { MOTUImage } from '../ui/MOTUImage';
import { getOptimizedImageUrl } from '../../utils/imageUtils';

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
    // Modo de vista: 'products' (Figuras Origins) o 'characters' (Personajes Canónicos)
    const [activeView, setActiveView] = useState<'products' | 'characters'>('products');

    // Estado para Figuras Origins
    const [products, setProducts] = useState<ProductLoreListItem[]>([]);
    const [expandedProductId, setExpandedProductId] = useState<number | null>(null);
    const [editingProductId, setEditingProductId] = useState<number | null>(null);
    const [prodEditForm, setProdEditForm] = useState<Partial<ProductLoreListItem>>({});
    const [savingProd, setSavingProd] = useState(false);

    // Estado para Personajes Arquetípicos
    const [characters, setCharacters] = useState<CharacterLore[]>([]);
    const [editingChar, setEditingChar] = useState<CharacterLore | null>(null);
    const [pendingOnly, setPendingOnly] = useState(false);
    const [pendingCount, setPendingCount] = useState(0);

    // Estados Comunes
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [factionFilter, setFactionFilter] = useState('ALL');
    const [saving, setSaving] = useState(false);
    const [harvesting, setHarvesting] = useState(false);
    const [seeding, setSeeding] = useState(false);
    const [toastMessage, setToastMessage] = useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        try {
            if (activeView === 'products') {
                const data = await fetchProductLoreList({
                    search: search || undefined,
                    faction: factionFilter !== 'ALL' ? factionFilter : undefined,
                    limit: 150
                });
                setProducts(data.items);
            } else {
                const data = await fetchCharacterLoreList({
                    search: search || undefined,
                    faction: factionFilter !== 'ALL' ? factionFilter : undefined,
                    pending_only: pendingOnly
                });
                setCharacters(data.items);
                setPendingCount(data.pending_count);
            }
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
    }, [activeView, search, factionFilter, pendingOnly]);

    const showToast = (msg: string) => {
        setToastMessage(msg);
        setTimeout(() => setToastMessage(null), 3500);
    };

    // Guardado de Personaje Canónico
    const handleSaveChar = async () => {
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

    // Guardado de Figura Origins
    const handleSaveProductLore = async (productId: number) => {
        setSavingProd(true);
        try {
            const updated = await updateProductLore(productId, {
                canonical_name: prodEditForm.canonical_name,
                subtitle: prodEditForm.subtitle,
                faction: prodEditForm.faction,
                quote: prodEditForm.quote,
                flavor_quote_author: prodEditForm.flavor_quote_author,
                lore: prodEditForm.lore,
                special_move: prodEditForm.special_move
            });
            setProducts((prev) =>
                prev.map((p) =>
                    p.product_id === productId
                        ? {
                              ...p,
                              canonical_name: updated.canonical_name,
                              subtitle: updated.subtitle,
                              faction: updated.faction,
                              quote: updated.quote,
                              flavor_quote_author: updated.flavor_quote_author,
                              lore: updated.lore,
                              special_move: updated.special_move,
                              is_customized: true
                          }
                        : p
                )
            );
            setEditingProductId(null);
            showToast(`✅ Lore de "${updated.canonical_name}" persistido en base de datos`);
        } catch (e) {
            console.error('Error al guardar figura:', e);
            showToast('❌ Error al persistir el lore de la figura');
        } finally {
            setSavingProd(false);
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
            showToast(`🎉 Sembrado completado: ${res.result.created} figuras creadas, ${res.result.updated} actualizadas.`);
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
                                Origins & Canon
                            </span>
                        </h2>
                        <p className="text-xs text-slate-400">
                            Base de datos canónica de figuras Origins, dorsos de blíster, lemas y personajes arquetípicos.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSeedAll}
                        disabled={seeding}
                        className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-bold font-cinzel transition active:scale-95 disabled:opacity-50"
                        title="Vuelve a sembrar los textos canónicos y de blíster para figuras Origins"
                    >
                        <RefreshCw className={`h-4 w-4 ${seeding ? 'animate-spin' : ''}`} />
                        <span>Sincronizar Lore Origins</span>
                    </button>
                </div>
            </div>

            {/* Selector de Modo: Figuras Origins vs Personajes Canónicos */}
            <div className="flex items-center gap-2 p-1.5 bg-slate-900/90 border border-slate-800 rounded-xl">
                <button
                    onClick={() => setActiveView('products')}
                    className={`flex-1 py-2 px-4 rounded-lg text-xs font-bold font-cinzel uppercase tracking-wider flex items-center justify-center gap-2 transition ${
                        activeView === 'products'
                            ? 'bg-amber-500 text-slate-950 shadow-md font-black'
                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                    }`}
                >
                    <Package className="h-4 w-4" />
                    <span>📦 Figuras Origins del Catálogo ({products.length > 0 ? products.length : 'Origins'})</span>
                </button>
                <button
                    onClick={() => setActiveView('characters')}
                    className={`flex-1 py-2 px-4 rounded-lg text-xs font-bold font-cinzel uppercase tracking-wider flex items-center justify-center gap-2 transition ${
                        activeView === 'characters'
                            ? 'bg-amber-500 text-slate-950 shadow-md font-black'
                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                    }`}
                >
                    <Users className="h-4 w-4" />
                    <span>👤 Personajes Arquetípicos ({characters.length > 0 ? characters.length : 'Canónicos'})</span>
                </button>
            </div>

            {/* Notificación Toast */}
            {toastMessage && (
                <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-slate-900 border border-amber-500/50 shadow-2xl text-sm font-semibold text-white animate-fade-in flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    <span>{toastMessage}</span>
                </div>
            )}

            {/* Barra de Filtros y Búsqueda */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                {/* 1. Buscador */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder={activeView === 'products' ? 'Buscar figura o frase de blíster...' : 'Buscar personaje canónico...'}
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

                {/* 3. Filtro según modo */}
                {activeView === 'characters' ? (
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
                ) : (
                    <div className="flex items-center justify-center px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-amber-400/80">
                        <span>🛡️ Exclusivo MOTU Origins (Vintage excluido)</span>
                    </div>
                )}
            </div>

            {/* Contenido según el modo activo */}
            {loading ? (
                <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
                    <RefreshCw className="h-8 w-8 animate-spin text-amber-400" />
                    <p className="text-sm font-cinzel">Consultando los Archivos del Oráculo...</p>
                </div>
            ) : activeView === 'products' ? (
                /* ─── VISTA 1: FIGURAS ORIGINS (CAJAS DE TÍTULO DESPLEGABLE) ─── */
                products.length === 0 ? (
                    <div className="p-12 text-center text-slate-500 rounded-xl bg-slate-900/40 border border-dashed border-slate-800">
                        <Package className="h-10 w-10 mx-auto mb-2 opacity-40 text-amber-400" />
                        <p className="text-sm">No se encontraron figuras Origins con los filtros seleccionados.</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {products.map((prod) => {
                            const isExpanded = expandedProductId === prod.product_id;
                            const isEditingThis = editingProductId === prod.product_id;

                            return (
                                <div
                                    key={prod.product_id}
                                    className="rounded-xl border border-slate-800 bg-slate-900/80 hover:border-amber-500/30 transition shadow-sm overflow-hidden"
                                >
                                    {/* Cabecera Desplegable del Ítem */}
                                    <div
                                        onClick={() => setExpandedProductId(isExpanded ? null : prod.product_id)}
                                        className="p-3.5 flex items-center justify-between gap-3 cursor-pointer hover:bg-white/[0.02] transition select-none"
                                    >
                                        <div className="flex items-center gap-3 min-w-0">
                                            {/* Miniatura */}
                                            <div className="h-12 w-12 rounded-lg bg-black/40 border border-white/10 shrink-0 overflow-hidden">
                                                {prod.image_url ? (
                                                    <MOTUImage
                                                        productId={prod.product_id}
                                                        src={getOptimizedImageUrl(prod.image_url, 150)}
                                                        alt={prod.product_name}
                                                        className="h-full w-full object-cover"
                                                    />
                                                ) : (
                                                    <div className="h-full w-full flex items-center justify-center text-slate-600 text-xs">
                                                        MOTU
                                                    </div>
                                                )}
                                            </div>

                                            {/* Textos Principales */}
                                            <div className="min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <h4 className="text-sm font-bold text-white truncate font-cinzel">
                                                        {prod.canonical_name || prod.product_name}
                                                    </h4>
                                                    {prod.is_customized && (
                                                        <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[8px] font-black uppercase tracking-wider border border-amber-500/30">
                                                            Editado
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-[11px] text-slate-400 truncate">
                                                    {prod.subtitle || prod.product_name}
                                                    {prod.sub_category ? ` • ${prod.sub_category}` : ''}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2 shrink-0">
                                            <span
                                                className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${getFactionBadgeColor(
                                                    prod.faction
                                                )}`}
                                            >
                                                {prod.faction}
                                            </span>
                                            {isExpanded ? (
                                                <ChevronUp className="h-4 w-4 text-amber-400" />
                                            ) : (
                                                <ChevronDown className="h-4 w-4 text-slate-400" />
                                            )}
                                        </div>
                                    </div>

                                    {/* Cuerpo Desplegado */}
                                    {isExpanded && (
                                        <div className="p-4 border-t border-slate-800 bg-slate-950/70 space-y-3">
                                            {isEditingThis ? (
                                                /* Formulario de Edición de Figura */
                                                <div className="space-y-3 text-left">
                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                        <div>
                                                            <label className="block text-[9px] font-bold uppercase text-amber-300 mb-1">
                                                                Nombre en Cromo / Lore:
                                                            </label>
                                                            <input
                                                                type="text"
                                                                value={prodEditForm.canonical_name || ''}
                                                                onChange={(e) =>
                                                                    setProdEditForm({ ...prodEditForm, canonical_name: e.target.value })
                                                                }
                                                                className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-slate-700 text-white text-xs"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="block text-[9px] font-bold uppercase text-amber-300 mb-1">
                                                                Subtítulo / Rango:
                                                            </label>
                                                            <input
                                                                type="text"
                                                                value={prodEditForm.subtitle || ''}
                                                                onChange={(e) =>
                                                                    setProdEditForm({ ...prodEditForm, subtitle: e.target.value })
                                                                }
                                                                className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-slate-700 text-white text-xs"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                        <div>
                                                            <label className="block text-[9px] font-bold uppercase text-amber-300 mb-1">
                                                                Frase del Reverso de Blíster (Cardback Quote):
                                                            </label>
                                                            <input
                                                                type="text"
                                                                value={prodEditForm.quote || ''}
                                                                onChange={(e) =>
                                                                    setProdEditForm({ ...prodEditForm, quote: e.target.value })
                                                                }
                                                                className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-slate-700 text-amber-200 text-xs italic font-serif"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="block text-[9px] font-bold uppercase text-amber-300 mb-1">
                                                                Poder / Habilidad Especial:
                                                            </label>
                                                            <input
                                                                type="text"
                                                                value={prodEditForm.special_move || ''}
                                                                onChange={(e) =>
                                                                    setProdEditForm({ ...prodEditForm, special_move: e.target.value })
                                                                }
                                                                className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-slate-700 text-white text-xs"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-[9px] font-bold uppercase text-amber-300 mb-1">
                                                            Biografía Canónica de la Figura (Español):
                                                        </label>
                                                        <textarea
                                                            value={prodEditForm.lore || ''}
                                                            onChange={(e) =>
                                                                setProdEditForm({ ...prodEditForm, lore: e.target.value })
                                                            }
                                                            rows={3}
                                                            className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-slate-700 text-stone-200 text-xs font-serif resize-none"
                                                        />
                                                    </div>

                                                    <div className="flex justify-end gap-2 pt-1 border-t border-white/5">
                                                        <button
                                                            type="button"
                                                            onClick={() => setEditingProductId(null)}
                                                            className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 text-xs font-bold"
                                                        >
                                                            Cancelar
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => handleSaveProductLore(prod.product_id)}
                                                            disabled={savingProd}
                                                            className="px-4 py-1 rounded-lg bg-gradient-to-r from-amber-500 to-yellow-600 hover:brightness-110 text-slate-950 text-xs font-black uppercase flex items-center gap-1.5 shadow-md shadow-amber-500/20"
                                                        >
                                                            {savingProd ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                                                            <span>Guardar en BD</span>
                                                        </button>
                                                    </div>
                                                </div>
                                            ) : (
                                                /* Vista Normal de la Figura */
                                                <div className="space-y-2 text-left">
                                                    {prod.quote && (
                                                        <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-200">
                                                            <div className="flex items-start gap-2">
                                                                <Quote className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                                                                <p className="text-xs italic font-serif">"{prod.quote}"</p>
                                                            </div>
                                                        </div>
                                                    )}

                                                    <p className="text-xs text-stone-300 font-serif leading-relaxed">
                                                        {prod.lore}
                                                    </p>

                                                    <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[11px]">
                                                        <div className="flex items-center gap-2 text-stone-400">
                                                            {prod.special_move && (
                                                                <span className="flex items-center gap-1 font-semibold text-amber-300">
                                                                    <Sparkles className="h-3 w-3 text-yellow-400" />
                                                                    {prod.special_move}
                                                                </span>
                                                            )}
                                                        </div>
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                setEditingProductId(prod.product_id);
                                                                setProdEditForm({
                                                                    canonical_name: prod.canonical_name,
                                                                    subtitle: prod.subtitle,
                                                                    faction: prod.faction,
                                                                    quote: prod.quote,
                                                                    flavor_quote_author: prod.flavor_quote_author,
                                                                    lore: prod.lore,
                                                                    special_move: prod.special_move
                                                                });
                                                            }}
                                                            className="px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-[10px] font-black uppercase tracking-wider flex items-center gap-1 transition"
                                                        >
                                                            <Edit3 className="h-3 w-3" />
                                                            <span>Editar Lore</span>
                                                        </button>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )
            ) : (
                /* ─── VISTA 2: PERSONAJES ARQUETÍPICOS ─── */
                characters.length === 0 ? (
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
                                            <span
                                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getFactionBadgeColor(
                                                    char.faction
                                                )}`}
                                            >
                                                {char.faction}
                                            </span>
                                        </div>
                                    </div>

                                    {char.subtitle && (
                                        <p className="text-xs italic text-amber-200/90 mb-2 font-serif">
                                            "{char.subtitle}"
                                        </p>
                                    )}

                                    <p className="text-xs text-slate-300 line-clamp-3 mb-3 leading-relaxed">
                                        {char.lore}
                                    </p>
                                </div>

                                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                                    <span className="text-[10px] text-slate-400 flex items-center gap-1">
                                        <Zap className="h-3 w-3 text-amber-400" />
                                        <span className="truncate">{char.special_move}</span>
                                    </span>

                                    <button
                                        onClick={() => setEditingChar(char)}
                                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-bold transition"
                                    >
                                        <Edit3 className="h-3 w-3" />
                                        <span>Editar</span>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )
            )}

            {/* Modal de Edición de Personaje Canónico */}
            {editingChar && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
                    <div className="w-full max-w-2xl rounded-2xl bg-slate-900 border border-amber-500/40 shadow-2xl p-6 overflow-y-auto max-h-[90vh] space-y-4">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                            <h3 className="text-lg font-bold text-white font-cinzel flex items-center gap-2">
                                <Edit3 className="h-5 w-5 text-amber-400" />
                                Editar Lore: {editingChar.canonical_name}
                            </h3>
                            <button
                                onClick={() => setEditingChar(null)}
                                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </div>

                        <div className="space-y-3">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                        Nombre Canónico:
                                    </label>
                                    <input
                                        type="text"
                                        value={editingChar.canonical_name}
                                        onChange={(e) => setEditingChar({ ...editingChar, canonical_name: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                        Subtítulo / Epíteto:
                                    </label>
                                    <input
                                        type="text"
                                        value={editingChar.subtitle || ''}
                                        onChange={(e) => setEditingChar({ ...editingChar, subtitle: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                        Facción:
                                    </label>
                                    <select
                                        value={editingChar.faction}
                                        onChange={(e) => setEditingChar({ ...editingChar, faction: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm"
                                    >
                                        {FACTION_OPTIONS.filter((f) => f.value !== 'ALL').map((f) => (
                                            <option key={f.value} value={f.value}>
                                                {f.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                        Tema Visual de Marco:
                                    </label>
                                    <select
                                        value={editingChar.theme_key}
                                        onChange={(e) => setEditingChar({ ...editingChar, theme_key: e.target.value as any })}
                                        className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm"
                                    >
                                        {THEME_OPTIONS.map((t) => (
                                            <option key={t.value} value={t.value}>
                                                {t.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                    Ataque o Poder Especial:
                                </label>
                                <input
                                    type="text"
                                    value={editingChar.special_move}
                                    onChange={(e) => setEditingChar({ ...editingChar, special_move: e.target.value })}
                                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
                                    Biografía y Lore Canónico:
                                </label>
                                <textarea
                                    value={editingChar.lore}
                                    onChange={(e) => setEditingChar({ ...editingChar, lore: e.target.value })}
                                    rows={4}
                                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm resize-none"
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                            <button
                                type="button"
                                onClick={() => handleHarvest(editingChar.canonical_name)}
                                disabled={harvesting}
                                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 text-xs font-bold hover:bg-indigo-500/30 transition disabled:opacity-50"
                            >
                                <Globe className="h-4 w-4" />
                                <span>{harvesting ? 'Cosechando...' : 'Re-cosechar de Wiki'}</span>
                            </button>

                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setEditingChar(null)}
                                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={handleSaveChar}
                                    disabled={saving}
                                    className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 hover:brightness-110 text-slate-950 text-xs font-black uppercase tracking-wider transition shadow-md shadow-amber-500/20"
                                >
                                    {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                                    <span>Guardar y Verificar</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoreTab;
