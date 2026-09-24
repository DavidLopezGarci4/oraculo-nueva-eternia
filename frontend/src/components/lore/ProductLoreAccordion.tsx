import React, { useState, useEffect } from 'react';
import {
    BookOpen,
    ChevronDown,
    ChevronUp,
    Edit3,
    Save,
    RefreshCw,
    CheckCircle2,
    Quote,
    Sparkles
} from 'lucide-react';
import { fetchProductLore, updateProductLore, type ProductLore } from '../../api/lore';

interface ProductLoreAccordionProps {
    productId: number;
    productName: string;
    isVintage?: boolean;
}

const FACTION_CHOICES = [
    'Guerreros Heroicos',
    'Guerreros del Mal',
    'La Horda del Terror',
    'Los Hombres Serpiente',
    'La Gran Rebelión',
    'Guardianes Cósmicos'
];

export const ProductLoreAccordion: React.FC<ProductLoreAccordionProps> = ({
    productId,
    productName,
    isVintage = false
}) => {
    // REGLA ESTRICTA: El Grimorio solo aplica a figuras Origins (no vintage)
    if (isVintage) return null;

    const [isExpanded, setIsExpanded] = useState(false);
    const [loreData, setLoreData] = useState<ProductLore | null>(null);
    const [loading, setLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [saving, setSaving] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Form fields
    const [editSubtitle, setEditSubtitle] = useState('');
    const [editQuote, setEditQuote] = useState('');
    const [editQuoteAuthor, setEditQuoteAuthor] = useState('');
    const [editLore, setEditLore] = useState('');
    const [editSpecialMove, setEditSpecialMove] = useState('');
    const [editFaction, setEditFaction] = useState('Guerreros Heroicos');

    const loadLore = async () => {
        setLoading(true);
        try {
            const data = await fetchProductLore(productId);
            setLoreData(data);
            setEditSubtitle(data.subtitle || '');
            setEditQuote(data.quote || '');
            setEditQuoteAuthor(data.flavor_quote_author || '');
            setEditLore(data.lore || '');
            setEditSpecialMove(data.special_move || '');
            setEditFaction(data.faction || 'Guerreros Heroicos');
        } catch (err) {
            console.error('Error al cargar lore del producto:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isExpanded && !loreData && !loading) {
            loadLore();
        }
    }, [isExpanded, productId]);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            const updated = await updateProductLore(productId, {
                subtitle: editSubtitle.trim() || undefined,
                quote: editQuote.trim() || undefined,
                flavor_quote_author: editQuoteAuthor.trim() || undefined,
                lore: editLore.trim(),
                special_move: editSpecialMove.trim() || undefined,
                faction: editFaction
            });
            setLoreData(updated);
            setIsEditing(false);
            setSuccessMessage('¡Lore guardado en la base de datos!');
            setTimeout(() => setSuccessMessage(null), 3500);
        } catch (err) {
            console.error('Error al guardar lore:', err);
        } finally {
            setSaving(false);
        }
    };

    const handleCancelEdit = () => {
        if (loreData) {
            setEditSubtitle(loreData.subtitle || '');
            setEditQuote(loreData.quote || '');
            setEditQuoteAuthor(loreData.flavor_quote_author || '');
            setEditLore(loreData.lore || '');
            setEditSpecialMove(loreData.special_move || '');
            setEditFaction(loreData.faction || 'Guerreros Heroicos');
        }
        setIsEditing(false);
    };

    return (
        <div className="w-full my-3 rounded-2xl border border-amber-500/30 bg-slate-950/80 shadow-lg backdrop-blur-md overflow-hidden transition-all duration-200">
            {/* Cabecera Plegable / Título Desplegable */}
            <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                title={`Grimorio Lore de ${productName}`}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/[0.04] transition-colors cursor-pointer text-left focus:outline-none"
            >
                <div className="flex items-center gap-2.5">
                    <BookOpen className="h-4 w-4 text-amber-400 shrink-0" />
                    <span className="text-xs font-black tracking-wider uppercase text-amber-300 font-cinzel">
                        Grimorio Lore: Reverso de Blíster & Canon
                    </span>
                    {loreData?.is_customized && (
                        <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[8px] font-black uppercase tracking-widest border border-amber-500/30">
                            Personalizado
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[9px] font-mono text-amber-400/80 hidden sm:inline">
                        {isExpanded ? 'Plegar' : 'Desplegar'}
                    </span>
                    {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-amber-400 shrink-0" />
                    ) : (
                        <ChevronDown className="h-4 w-4 text-amber-400 shrink-0" />
                    )}
                </div>
            </button>

            {/* Contenido Desplegado */}
            {isExpanded && (
                <div className="p-4 border-t border-amber-500/20 bg-slate-900/60 animate-in fade-in duration-200">
                    {loading ? (
                        <div className="flex items-center justify-center py-6 gap-2 text-amber-400 text-xs font-bold">
                            <RefreshCw className="h-4 w-4 animate-spin" />
                            <span>Consultando los Pergaminos de Grayskull...</span>
                        </div>
                    ) : isEditing ? (
                        /* Modo Edición Directa */
                        <form onSubmit={handleSave} className="space-y-3">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
                                <div>
                                    <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                        Subtítulo / Rango de la Figura:
                                    </label>
                                    <input
                                        type="text"
                                        value={editSubtitle}
                                        onChange={(e) => setEditSubtitle(e.target.value)}
                                        placeholder="Ej: El Hombre Más Poderoso del Universo"
                                        className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-white text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                        Facción / Bando:
                                    </label>
                                    <select
                                        value={editFaction}
                                        onChange={(e) => setEditFaction(e.target.value)}
                                        className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-white text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                    >
                                        {FACTION_CHOICES.map((f) => (
                                            <option key={f} value={f} className="bg-slate-900">
                                                {f}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
                                <div>
                                    <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                        Poder / Habilidad Especial:
                                    </label>
                                    <input
                                        type="text"
                                        value={editSpecialMove}
                                        onChange={(e) => setEditSpecialMove(e.target.value)}
                                        placeholder="Ej: Por el Poder de Grayskull"
                                        className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-amber-200 text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                        Autor de la Cita / Frase:
                                    </label>
                                    <input
                                        type="text"
                                        value={editQuoteAuthor}
                                        onChange={(e) => setEditQuoteAuthor(e.target.value)}
                                        placeholder="Ej: He-Man / Dorso Mattel"
                                        className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-white text-xs font-semibold focus:border-amber-400 focus:outline-none"
                                    />
                                </div>
                            </div>

                            <div className="text-left">
                                <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                    Frase Célebre del Dorso del Blíster (Cardback Quote):
                                </label>
                                <input
                                    type="text"
                                    value={editQuote}
                                    onChange={(e) => setEditQuote(e.target.value)}
                                    placeholder="Ej: ¡Por el poder de Grayskull... Yo tengo el poder!"
                                    className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-amber-300 italic text-xs font-serif focus:border-amber-400 focus:outline-none"
                                />
                            </div>

                            <div className="text-left">
                                <label className="block text-[9px] font-bold uppercase text-amber-300/80 mb-1">
                                    Biografía de la Figura (Lore Canónico en Español):
                                </label>
                                <textarea
                                    value={editLore}
                                    onChange={(e) => setEditLore(e.target.value)}
                                    rows={3}
                                    placeholder="Biografía concisa de la figura y sus accesorios..."
                                    className="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-slate-700 text-stone-200 text-xs leading-relaxed focus:border-amber-400 focus:outline-none resize-none font-serif"
                                />
                            </div>

                            <div className="flex items-center justify-end gap-2 pt-1 border-t border-white/10">
                                <button
                                    type="button"
                                    onClick={handleCancelEdit}
                                    className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 text-[10px] font-bold uppercase transition"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-yellow-600 hover:brightness-110 text-slate-950 text-[10px] font-black uppercase tracking-wider transition flex items-center gap-1.5 shadow-md shadow-amber-500/20"
                                >
                                    {saving ? <RefreshCw className="h-3 w-3 animate-spin" /> : <Save className="h-3 w-3" />}
                                    <span>{saving ? 'Guardando...' : 'Guardar en Base de Datos'}</span>
                                </button>
                            </div>
                        </form>
                    ) : (
                        /* Modo Lectura Compacto & Elegante */
                        <div className="space-y-2.5 text-left">
                            {successMessage && (
                                <div className="flex items-center gap-2 p-2 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-bold">
                                    <CheckCircle2 className="h-4 w-4" />
                                    <span>{successMessage}</span>
                                </div>
                            )}

                            {/* Cita / Frase del reverso */}
                            {loreData?.quote && (
                                <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200">
                                    <div className="flex items-start gap-2">
                                        <Quote className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                                        <div className="flex-1">
                                            <p className="text-xs italic font-serif leading-snug">
                                                "{loreData.quote}"
                                            </p>
                                            {loreData.flavor_quote_author && (
                                                <p className="text-[10px] text-right text-amber-400/90 font-bold mt-1 font-sans">
                                                    — {loreData.flavor_quote_author}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Biografía concisa */}
                            <div className="text-stone-300 text-xs leading-relaxed font-serif pl-1">
                                {loreData?.lore || (
                                    <span className="italic text-white/40">Sin biografía disponible.</span>
                                )}
                            </div>

                            {/* Detalles breves: Subtítulo & Habilidad */}
                            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/10 text-[10px]">
                                <div className="flex items-center gap-3 text-white/60">
                                    {loreData?.subtitle && (
                                        <span className="text-amber-300/90 font-medium italic font-serif">
                                            {loreData.subtitle}
                                        </span>
                                    )}
                                    {loreData?.special_move && (
                                        <span className="flex items-center gap-1 font-semibold text-stone-200">
                                            <Sparkles className="h-2.5 w-2.5 text-yellow-400" />
                                            {loreData.special_move}
                                        </span>
                                    )}
                                    {loreData?.faction && (
                                        <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 font-bold text-white/80">
                                            {loreData.faction}
                                        </span>
                                    )}
                                </div>

                                <button
                                    type="button"
                                    onClick={() => setIsEditing(true)}
                                    className="px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-[9.5px] font-black uppercase tracking-wider flex items-center gap-1 transition"
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
};

export default ProductLoreAccordion;
