
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
    Target,
    Loader2
} from 'lucide-react';
import { updateCollectionItem } from '../api/collection';
import type { Product } from '../api/collection';
import MarketIntelligenceModal from './MarketIntelligenceModal';

interface CollectionItemDetailModalProps {
    product: Product;
    userId: number;
    onClose: () => void;
}

const CollectionItemDetailModal: React.FC<CollectionItemDetailModalProps> = ({ product, userId, onClose }) => {
    const queryClient = useQueryClient();
    const [price, setPrice] = useState<number>(product.purchase_price || 0);
    const [condition, setCondition] = useState<string>(product.condition || 'New');
    const [grading, setGrading] = useState<number>(product.grading || 10.0);
    const [notes, setNotes] = useState<string>(product.notes || '');
    const [acquiredAt, setAcquiredAt] = useState<string>(
        product.acquired_at ? product.acquired_at.split('T')[0] : new Date().toISOString().split('T')[0]
    );
    const [showMarketIntel, setShowMarketIntel] = useState(false);

    const updateMutation = useMutation({
        mutationFn: () => updateCollectionItem(product.id, userId, {
            purchase_price: price,
            condition,
            grading,
            notes,
            acquired_at: acquiredAt
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', userId] });
            onClose();
        }
    });

    // Advanced Valuation Engine (Frontend Simulation)
    const getMultiplier = (cond: string, grd: number) => {
        const mults: Record<string, number> = { 'MOC': 1.0, 'NEW': 0.75, 'LOOSE': 0.5 };
        const base = mults[cond.toUpperCase()] || 0.75;
        const gradeFactor = 1.0 - ((10.0 - grd) * 0.04);
        return base * Math.max(0.1, gradeFactor);
    };

    const multiplier = getMultiplier(condition, grading);
    const baseMarketVal = product.market_value || 0;
    const adjustedMarketVal = baseMarketVal * multiplier;
    const profitLoss = adjustedMarketVal - price;
    const roi = price > 0 ? (profitLoss / price) * 100 : 0;

    return (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/90 backdrop-blur-xl p-4 md:p-10 animate-in fade-in duration-300">
            <div className="relative w-full max-w-4xl rounded-[3rem] border border-white/10 bg-gradient-to-br from-white/[0.05] to-transparent overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh]">

                {/* Left Side: Product Preview */}
                <div className="w-full md:w-1/3 bg-black/40 border-r border-white/5 p-8 flex flex-col gap-6 items-center text-center">
                    <div className="relative w-full aspect-square rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl">
                        <img src={product.image_url || ''} className="h-full w-full object-cover" alt={product.name} />
                        <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-black text-white/90 border border-white/20">
                            #{product.figure_id}
                        </div>
                    </div>
                    <div className="space-y-2">
                        <p className="text-[10px] font-black text-brand-primary uppercase tracking-[0.2em]">{product.sub_category}</p>
                        <h2 className="text-xl font-black text-white leading-tight">{product.name}</h2>
                    </div>

                    <button
                        onClick={() => setShowMarketIntel(true)}
                        className="mt-4 w-full flex items-center justify-center gap-3 py-4 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary text-[10px] font-black uppercase tracking-widest hover:bg-brand-primary hover:text-white transition-all shadow-lg shadow-brand-primary/10"
                    >
                        <Target className="h-4 w-4" />
                        Ver Inteligencia de Mercado
                    </button>
                </div>

                {/* Right Side: Legado Form */}
                <div className="flex-1 flex flex-col overflow-y-auto custom-scrollbar">
                    {/* Header */}
                    <div className="p-8 border-b border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Shield className="h-5 w-5 text-brand-primary" />
                            <h3 className="text-white font-black text-lg uppercase tracking-wider">Tu Legado Personal</h3>
                        </div>
                        <button onClick={onClose} className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                            <X className="h-5 w-5 text-white/40" />
                        </button>
                    </div>

                    <div className="p-8 space-y-8">
                        {/* Financial Stats */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/[0.03] border border-white/5 p-6 rounded-3xl space-y-2">
                                <span className="text-[8px] font-black text-white/20 uppercase tracking-widest block">Inversión (Tu Precio)</span>
                                <div className="flex items-baseline gap-1">
                                    <input
                                        type="number"
                                        value={price}
                                        onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
                                        className="bg-transparent text-2xl font-black text-white border-none focus:ring-0 w-24 p-0"
                                    />
                                    <span className="text-lg font-bold text-white/40">€</span>
                                </div>
                            </div>
                            <div className={`border p-6 rounded-3xl space-y-2 transition-all ${profitLoss >= 0 ? 'bg-green-500/5 border-green-500/20' : 'bg-brand-primary/5 border-brand-primary/20'}`}>
                                <span className="text-[8px] font-black text-white/20 uppercase tracking-widest block">Revalorización (ROI)</span>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-baseline gap-1">
                                        <h4 className={`text-2xl font-black ${profitLoss >= 0 ? 'text-green-400' : 'text-brand-primary'}`}>
                                            {profitLoss >= 0 ? '+' : ''}{profitLoss.toFixed(2)}
                                        </h4>
                                        <span className={`text-lg font-bold ${profitLoss >= 0 ? 'text-green-400/40' : 'text-brand-primary/40'}`}>€</span>
                                    </div>
                                    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black ${profitLoss >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-brand-primary/20 text-brand-primary'}`}>
                                        {profitLoss >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                                        {roi.toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Form Fields */}
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-white/20 uppercase tracking-widest flex items-center gap-2">
                                    <Activity className="h-3 w-3" />
                                    Estado de la Reliquia
                                </label>
                                <div className="grid grid-cols-3 gap-3">
                                    {['MOC', 'New', 'Loose'].map((opt) => (
                                        <button
                                            key={opt}
                                            onClick={() => setCondition(opt)}
                                            className={`py-3 rounded-2xl border font-black text-[10px] uppercase transition-all ${condition === opt ? 'bg-brand-primary text-white border-brand-primary shadow-lg shadow-brand-primary/20' : 'bg-white/5 border-white/5 text-white/30 hover:bg-white/10'}`}
                                        >
                                            {opt}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="text-[10px] font-black text-white/20 uppercase tracking-widest flex items-center gap-2">
                                        <Target className="h-3 w-3" />
                                        Grado de Conservación (ASTM/C)
                                    </label>
                                    <div className="flex items-center gap-2">
                                        <span className={`text-xl font-black ${grading >= 9 ? 'text-green-400' : 'text-brand-primary'}`}>{grading.toFixed(1)}</span>
                                        {grading < 10 && condition === 'MOC' && (
                                            <span className="px-2 py-0.5 rounded-md bg-brand-primary/20 text-brand-primary text-[8px] font-black uppercase">Shelf Wear</span>
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
                                    className="w-full h-1.5 bg-white/5 rounded-lg appearance-none cursor-pointer accent-brand-primary"
                                />
                                <p className="text-[10px] text-white/30 italic">
                                    {grading >= 9.5 ? 'Estado Gema / Mint' : grading >= 8.5 ? 'Excelente con ligero shelf-wear' : 'Estado jugado / con desgaste'}
                                </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-white/20 uppercase tracking-widest flex items-center gap-2">
                                        <Calendar className="h-3 w-3" />
                                        Fecha de Adquisición
                                    </label>
                                    <input
                                        type="date"
                                        value={acquiredAt}
                                        onChange={(e) => setAcquiredAt(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-white text-sm font-bold focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all color-white"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-white/20 uppercase tracking-widest flex items-center gap-2">
                                    <FileText className="h-3 w-3" />
                                    Notas del Archivo
                                </label>
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    placeholder="Detalles sobre el vendedor, estado de la caja, accesorios..."
                                    className="w-full bg-white/5 border border-white/10 rounded-3xl p-6 text-white text-sm font-medium focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all min-h-[120px] resize-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-auto p-8 bg-black/40 border-t border-white/5 flex gap-4">
                        <button
                            onClick={onClose}
                            className="px-8 py-4 rounded-2xl bg-white/5 text-white/40 font-black text-[10px] uppercase tracking-widest hover:bg-white/10 transition-all border border-white/5"
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={() => updateMutation.mutate()}
                            disabled={updateMutation.isPending}
                            className="flex-1 flex items-center justify-center gap-3 py-4 rounded-2xl bg-brand-primary text-white font-black text-[10px] uppercase tracking-widest shadow-xl shadow-brand-primary/20 hover:brightness-110 transition-all"
                        >
                            {updateMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                            {updateMutation.isPending ? 'Sincronizando...' : 'Guardar en Legado'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Nested Market Intelligence Modal */}
            {showMarketIntel && (
                <MarketIntelligenceModal
                    productId={product.id}
                    onClose={() => setShowMarketIntel(false)}
                />
            )}
        </div>
    );
};

export default CollectionItemDetailModal;
