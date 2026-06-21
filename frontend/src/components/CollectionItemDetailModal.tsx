
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
    X,
    Save,
    Calendar,
    FileText,
    Activity,
    TrendingUp,
    TrendingDown,
    Shield,
    RefreshCw,
    ChevronDown
} from 'lucide-react';
import { updateCollectionItem, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { getOptimizedImageUrl } from '../utils/imageUtils';


interface CollectionItemDetailModalProps {
    product: Product;
    userId: number;
    isIncognito?: boolean;
    onClose: () => void;
}

const CollectionItemDetailModal: React.FC<CollectionItemDetailModalProps> = ({ product, userId, isIncognito = false, onClose }) => {
    void isIncognito;
    const queryClient = useQueryClient();
    const [price, setPrice] = useState<string>(
        product.purchase_price && product.purchase_price > 0 ? String(product.purchase_price) : ''
    );
    const [condition, setCondition] = useState<string>(product.condition || 'MOC');
    const [grading, setGrading] = useState<number>(product.grading || 10.0);
    const [notes, setNotes] = useState<string>(product.notes || '');
    const [acquiredAt, setAcquiredAt] = useState<string>(
        product.acquired_at ? product.acquired_at.split('T')[0] : new Date().toISOString().split('T')[0]
    );
    const [expandedImage, setExpandedImage] = useState<string | null>(null);
    const [showGradingGuide, setShowGradingGuide] = useState(false);


    const updateMutation = useMutation({
        mutationFn: () => updateCollectionItem(product.id, userId, {
            purchase_price: price === '' ? 0.0 : (parseFloat(price) || 0.0),
            condition,
            grading,
            notes,
            acquired_at: acquiredAt,
            acquired: product.is_wish ? true : undefined
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', userId] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats', userId] });
            onClose();
        }
    });

    const toggleMutation = useMutation({
        mutationFn: () => toggleCollection(product.id, userId, false),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', userId] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats', userId] });
            onClose();
        }
    });

    // Advanced Valuation Engine (Frontend Simulation)
    const getMultiplier = (cond: string, grd: number) => {
        const mults: Record<string, number> = { 'MOC': 1.0, 'NEW': 0.75, 'LOOSE': 0.5 };
        const base = mults[cond.toUpperCase()] || 1.0;
        const gradeFactor = 1.0 - ((10.0 - grd) * 0.04);
        return base * Math.max(0.1, gradeFactor);
    };

    const multiplier = getMultiplier(condition, grading);
    const baseMarketVal = product.market_value || 0;
    const adjustedMarketVal = baseMarketVal * multiplier;
    const numericPrice = price === '' ? 0.0 : (parseFloat(price) || 0.0);
    const profitLoss = adjustedMarketVal - numericPrice;
    const roi = numericPrice > 0 ? (profitLoss / numericPrice) * 100 : 0;

    return (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/90 backdrop-blur-xl p-2 md:p-10 animate-in fade-in duration-300">
            <div className="relative w-full max-w-4xl rounded-[3rem] border border-white/10 bg-gradient-to-br from-white/[0.05] to-transparent overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh]">

                {/* Left Side: Product Preview */}
                <div className="w-full md:w-1/3 bg-black/40 border-b md:border-b-0 md:border-r border-white/5 p-3 md:p-8 flex flex-col gap-2 md:gap-4 items-center text-center">
                    <div 
                        className="relative w-full max-w-[120px] md:max-w-full aspect-square md:aspect-auto md:h-64 rounded-2xl md:rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl mx-auto cursor-zoom-in hover:scale-105 transition-transform"
                        onClick={() => setExpandedImage(product.image_url || null)}
                        title="Expandir Reliquia"
                    >
                        <img 
                            src={getOptimizedImageUrl(product.image_url, 600)} 
                            className="h-full w-full object-cover" 
                            alt={product.name} 
                            loading="lazy"
                        />

                        {/* ID Badge - Top Right */}
                        <div className="absolute top-2 right-2 md:top-4 md:right-4 bg-black/70 backdrop-blur-md px-2 py-0.5 md:px-3 md:py-1 rounded-full text-[8px] md:text-[10px] font-black text-white/90 border border-white/20">
                            #{product.figure_id}
                        </div>
                    </div>

                    <div className="space-y-1 md:space-y-2">
                        <p className="text-[8px] md:text-[10px] font-black text-brand-primary uppercase tracking-[0.2em]">{product.sub_category}</p>
                        <h2 className="text-sm md:text-xl font-black text-white leading-tight">{product.name}</h2>
                    </div>
                </div>

                {/* Right Side: Legado Form */}
                <div className="flex-1 flex flex-col overflow-y-auto custom-scrollbar">
                    {/* Header */}
                    <div className="p-3 md:p-8 border-b border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-2 md:gap-3">
                            <Shield className="h-4 w-4 md:h-5 md:w-5 text-brand-primary" />
                            <h3 className="text-white font-black text-xs md:text-lg uppercase tracking-wider">Tu Legado Personal</h3>
                        </div>
                        <button onClick={onClose} className="h-8 w-8 md:h-10 md:w-10 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                            <X className="h-5 w-5 text-white/70" />
                        </button>
                    </div>

                    <div className="p-3 md:p-8 space-y-3 sm:space-y-4 md:space-y-6">
                        {/* Financial Stats */}
                        <div className="grid grid-cols-2 gap-3 sm:gap-4">
                            <div className="bg-white/[0.03] border border-white/5 p-2.5 sm:p-5 rounded-xl md:rounded-3xl space-y-1 md:space-y-2 flex flex-col justify-center">
                                <span className="text-[7px] sm:text-[8px] font-black text-white/60 uppercase tracking-widest block">Inversión (Tu Precio)</span>
                                <div className="flex items-baseline gap-1">
                                    <input
                                        type="text"
                                        inputMode="decimal"
                                        value={price}
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            if (val === '' || /^[0-9]*([.,][0-9]*)?$/.test(val)) {
                                                setPrice(val.replace(',', '.'));
                                            }
                                        }}
                                        placeholder="0"
                                        className="bg-transparent text-base sm:text-2xl font-black text-white border-none focus:ring-0 w-12 sm:w-20 p-0 blur-incognito"
                                    />
                                    <span className="text-xs sm:text-lg font-bold text-white/70">€</span>
                                </div>
                            </div>
                            <div className={`border p-2.5 sm:p-5 rounded-xl md:rounded-3xl space-y-1 md:space-y-2 transition-all flex flex-col justify-center ${profitLoss >= 0 ? 'bg-green-500/5 border-green-500/20' : 'bg-brand-primary/5 border-brand-primary/20'}`}>
                                <span className="text-[7px] sm:text-[8px] font-black text-white/60 uppercase tracking-widest block">Revalorización (ROI)</span>
                                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-1.5">
                                    <div className="flex items-baseline gap-1">
                                        <h4 className={`text-base sm:text-2xl font-black blur-incognito ${profitLoss >= 0 ? 'text-green-400' : 'text-brand-primary'}`}>
                                            {profitLoss >= 0 ? '+' : ''}{profitLoss.toFixed(2)}
                                        </h4>
                                        <span className={`text-xs sm:text-lg font-bold ${profitLoss >= 0 ? 'text-green-400/40' : 'text-brand-primary/40'}`}>€</span>
                                    </div>
                                    <div className={`flex w-fit items-center gap-1 sm:gap-1.5 px-2 py-0.5 sm:px-3 sm:py-1 rounded-full text-[8px] sm:text-[10px] font-black blur-incognito ${profitLoss >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-brand-primary/20 text-brand-primary'}`}>
                                        {profitLoss >= 0 ? <TrendingUp className="h-2 w-2 sm:h-3 sm:w-3" /> : <TrendingDown className="h-2 w-2 sm:h-3 sm:w-3" />}
                                        {roi.toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Form Fields */}
                        <div className="space-y-3 md:space-y-6">
                            <div className="space-y-1.5">
                                <label className="text-[8px] md:text-[10px] font-black text-white/60 uppercase tracking-widest flex items-center gap-2">
                                    <Activity className="h-3 w-3" />
                                    Estado de la Reliquia
                                </label>
                                <div className="grid grid-cols-3 gap-2 md:gap-3">
                                    {['MOC', 'New', 'Loose'].map((opt) => (
                                        <button
                                            key={opt}
                                            onClick={() => setCondition(opt)}
                                            className={`py-1.5 md:py-3 rounded-lg md:rounded-2xl border font-black text-[9px] md:text-[10px] uppercase transition-all ${condition === opt ? 'bg-brand-primary text-white border-brand-primary shadow-lg shadow-brand-primary/20' : 'bg-white/5 border-white/5 text-white/60 hover:bg-white/10'}`}
                                        >
                                            {opt}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-2 md:space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="text-[8px] md:text-[10px] font-black text-white/60 uppercase tracking-widest flex items-center gap-2">
                                        Grado de Conservación (ASTM/C)
                                    </label>
                                    <div className="flex items-center gap-2">
                                        <span className={`text-base md:text-xl font-black ${grading >= 9 ? 'text-green-400' : 'text-brand-primary'}`}>{grading.toFixed(1)}</span>
                                        {grading < 10 && condition === 'MOC' && (
                                            <span className="px-2 py-0.5 rounded-md bg-brand-primary/20 text-brand-primary text-[7px] md:text-[8px] font-black uppercase">Shelf Wear</span>
                                        )}
                                    </div>
                                </div>
                                <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    step="0.5"
                                    value={grading}
                                    onChange={(e) => setGrading(parseFloat(e.target.value))}
                                    className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-brand-primary"
                                />
                                <p className="text-[8px] md:text-[10px] text-white/60 italic">
                                    {grading >= 9.5 ? 'Estado Gema / Mint' : grading >= 8.5 ? 'Excelente con ligero shelf-wear' : 'Estado jugado / con desgaste'}
                                </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                                <div className="space-y-1">
                                    <label className="text-[8px] md:text-[10px] font-black text-white/60 uppercase tracking-widest flex items-center gap-2">
                                        <Calendar className="h-3 w-3" />
                                        Fecha
                                    </label>
                                    <input
                                        type="date"
                                        value={acquiredAt}
                                        onChange={(e) => setAcquiredAt(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl md:rounded-2xl p-2.5 md:p-4 text-white text-xs md:text-sm font-bold focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all color-white"
                                    />
                                </div>
                            </div>

                            <div className="space-y-1">
                                <label className="text-[8px] md:text-[10px] font-black text-white/60 uppercase tracking-widest flex items-center gap-2">
                                    <FileText className="h-3 w-3" />
                                    Notas
                                </label>
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    placeholder="Detalles sobre el vendedor, caja..."
                                    className="w-full bg-white/5 border border-white/10 rounded-xl md:rounded-3xl p-3 text-white text-xs md:text-sm font-medium focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all min-h-[50px] md:min-h-[120px] resize-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-auto p-3 md:p-8 bg-black/40 border-t border-white/5 flex flex-col gap-4">
                        {/* Action Buttons Row */}
                        <div className="flex flex-row justify-center items-center gap-2 md:gap-4 w-full">
                            <button
                                type="button"
                                onClick={() => {
                                    const isVintage = !!product.is_vintage;
                                    const message = isVintage
                                        ? `¿Seguro de desvincular '${product.name}' de tu colección? Volverá a aparecer en Eternia (las estadísticas y ofertas del producto permanecerán intactas).`
                                        : `¿Seguro de liberar '${product.name}' de tu colección?`;
                                    if (confirm(message)) {
                                        toggleMutation.mutate();
                                    }
                                }}
                                disabled={toggleMutation.isPending}
                                className="flex-1 sm:flex-initial min-w-[90px] sm:min-w-[140px] px-3 py-2 md:px-6 md:py-4 rounded-lg md:rounded-2xl bg-red-500/10 text-red-400 border border-red-500/20 font-black uppercase tracking-widest text-[8px] md:text-[10px] hover:bg-red-500 hover:text-white transition-all shadow-lg hover:shadow-red-500/20 flex justify-center items-center gap-2"
                                title={product.is_vintage ? "Desvincular de la Colección" : "Liberar de la Colección"}
                            >
                                {toggleMutation.isPending ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <X className="h-3.5 w-3.5" />}
                                <span>{product.is_vintage ? 'Desvincular' : 'Liberar'}</span>
                            </button>

                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 sm:flex-initial min-w-[90px] sm:min-w-[140px] px-3 py-2 md:px-8 md:py-4 rounded-lg md:rounded-2xl bg-white/5 text-white/70 font-black uppercase tracking-widest text-[8px] md:text-[10px] hover:bg-white/10 transition-all border border-white/5 flex justify-center items-center"
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                onClick={() => updateMutation.mutate()}
                                disabled={updateMutation.isPending}
                                className="flex-1 sm:flex-initial min-w-[95px] sm:min-w-[140px] px-3 py-2 md:px-8 md:py-4 rounded-lg md:rounded-2xl bg-brand-primary text-white font-black uppercase tracking-widest text-[8px] md:text-[10px] shadow-xl shadow-brand-primary/20 hover:brightness-110 transition-all flex justify-center items-center gap-2"
                            >
                                {updateMutation.isPending ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                                <span>{updateMutation.isPending ? 'Guardando...' : 'Guardar Legado'}</span>
                            </button>
                        </div>

                        {/* Collapsible Grading Guide Section */}
                        <div className="w-full border-t border-white/5 pt-3">
                            <button
                                type="button"
                                onClick={() => setShowGradingGuide(!showGradingGuide)}
                                className="w-full flex items-center justify-between px-3 py-2 bg-white/5 hover:bg-white/10 rounded-xl transition-all border border-white/5 group"
                            >
                                <span className="text-[9px] md:text-[10px] font-black text-white/80 uppercase tracking-widest flex items-center gap-2">
                                    📋 Guía Rápida de Conservación (ASTM/C)
                                </span>
                                <ChevronDown className={`h-3 w-3 md:h-4 md:w-4 text-white/50 group-hover:text-white transition-transform duration-300 ${showGradingGuide ? 'rotate-180' : ''}`} />
                            </button>

                            {showGradingGuide && (
                                <div className="mt-2 p-3 bg-white/[0.02] border border-white/5 rounded-xl text-[9px] md:text-[10px] text-white/60 space-y-3 leading-relaxed max-h-[160px] md:max-h-[220px] overflow-y-auto custom-scrollbar">
                                    <div>
                                        <h4 className="font-black text-white uppercase tracking-wider mb-1">1. Estado Base (Empaque)</h4>
                                        <ul className="list-disc pl-3.5 space-y-0.5 text-[8px] md:text-[9px]">
                                            <li><strong className="text-white">MOC (Mint on Card):</strong> Blíster original cerrado de fábrica. (100% valor base)</li>
                                            <li><strong className="text-white">NEW (Open Box):</strong> Caja o blíster abierto; figura nueva. (75% valor base)</li>
                                            <li><strong className="text-white">LOOSE (Loose):</strong> Figura suelta fuera de su empaque. (50% valor base)</li>
                                        </ul>
                                    </div>

                                    <div>
                                        <h4 className="font-black text-white uppercase tracking-wider mb-1">2. Escala C de Conservación (1.0 a 10.0)</h4>
                                        <ul className="list-disc pl-3.5 space-y-0.5 text-[8px] md:text-[9px]">
                                            <li><strong className="text-white">10.0 | Gem Mint (C-10):</strong> Cartón plano perfecto, burbuja impecable.</li>
                                            <li><strong className="text-white">9.5  | Mint (C-9.5):</strong> Casi perfecta. Desgaste invisible a simple vista.</li>
                                            <li><strong className="text-white">9.0  | NM/Mint (C-9.0):</strong> Cartón plano con arruga o doblez leve de almacenaje.</li>
                                            <li><strong className="text-white">8.5  | Near Mint (C-8.5):</strong> Desgaste menor en bordes o marca de etiqueta.</li>
                                            <li><strong className="text-white">8.0  | VG/NM (C-8.0):</strong> Dobleces moderados, rayones leves en plástico.</li>
                                            <li><strong className="text-white">7.0  | Good (C-7.0):</strong> Marcas evidentes de estrés y desgaste en cartón.</li>
                                            <li><strong className="text-white">5.0  | Fair (C-5.0):</strong> Cartón muy desgastado, burbuja amarilleada/semi-despegada.</li>
                                            <li><strong className="text-white">1.0  | Poor (C-1.0):</strong> Blíster roto o reparado con cinta. Figura dañada/incompleta.</li>
                                        </ul>
                                    </div>

                                    <div className="border-t border-white/5 pt-2">
                                        <h4 className="font-black text-white uppercase tracking-wider mb-0.5">3. Algoritmo de Ajuste</h4>
                                        <p className="text-[8px] md:text-[9px]">
                                            Fórmula: <code className="text-brand-primary font-bold">Valor Base × Multiplicador de Estado × Factor de Conservación</code>
                                        </p>
                                        <p className="mt-0.5 text-[8px] md:text-[9px]">
                                            Cada punto menos de la nota (partiendo de 10.0) resta un 4% de valor (2% por cada 0.5 de nota). Ejemplo: nota 9.0 aplica factor 0.96 (4% de descuento). Nota 1.0 aplica descuento de 36%.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* FULLSCREEN IMAGE EXPANSION */}
            {expandedImage && (
                <div
                    className="fixed inset-0 z-[200] flex items-center justify-center p-4 sm:p-20 bg-black/95 backdrop-blur-3xl animate-in zoom-in duration-300 shadow-2xl"
                    onClick={() => setExpandedImage(null)}
                >
                    <div className="relative max-w-full max-h-full group">
                        <img
                            src={expandedImage}
                            alt="Expanded Vintage Relic"
                            className="max-w-full max-h-[90vh] rounded-[2rem] sm:rounded-[3rem] border border-white/10 shadow-[0_0_100px_rgba(0,0,0,0.8)] object-contain"
                            onClick={(e) => e.stopPropagation()}
                        />
                        <button
                            onClick={() => setExpandedImage(null)}
                            className="absolute -top-4 -right-4 sm:-top-8 sm:-right-8 h-10 w-10 sm:h-14 sm:w-14 flex items-center justify-center rounded-2xl bg-white/10 text-white hover:bg-red-500 hover:scale-110 transition-all border border-white/10 backdrop-blur-md shadow-2xl z-[210]"
                        >
                            <X className="h-6 w-6 sm:h-8 sm:w-8" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CollectionItemDetailModal;
