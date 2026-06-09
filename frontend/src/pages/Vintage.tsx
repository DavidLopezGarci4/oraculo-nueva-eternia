import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { History, AlertCircle, Info, RefreshCw, TrendingUp, X, ExternalLink, RotateCcw } from 'lucide-react';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { motion } from 'framer-motion';
import { getProductPriceHistory } from '../api/products';
import { revertVintageItem } from '../api/purgatory';
import PriceHistoryChart from '../components/products/PriceHistoryChart';
import type { Hero } from '../api/admin';
import { MOTUImage } from '../components/ui/MOTUImage';

interface VintageProduct {
    id: number;
    name: string;
    ean?: string;
    image_url?: string;
    category: string;
    sub_category: string;
    figure_id: string;
    release_year?: number;
    offer_id: number;
    best_p2p_price: number;
    best_p2p_source: string;
    url: string;
    condition: string;
    grading: number;
    bids_count?: number;
    time_left_raw?: string;
    sale_type: string;
}

interface VintageProps {
    user?: Hero | null;
}

const Vintage: React.FC<VintageProps> = ({ user }) => {
    const queryClient = useQueryClient();
    const [selectedProduct, setSelectedProduct] = React.useState<VintageProduct | null>(null);
    const [historyProductId, setHistoryProductId] = React.useState<number | null>(null);
    const [expandedImage, setExpandedImage] = React.useState<string | null>(null);
    const [sortBy, setSortBy] = React.useState<'name' | 'price' | 'condition'>('name');

    const isAdmin = user?.role === 'admin' || user?.username === 'David';


    // 1. Fetch de productos vintage individuales
    const { data: vintageItems, isLoading: isLoadingVintage, isError: isErrorVintage } = useQuery<VintageProduct[]>({
        queryKey: ['vintage-products'],
        queryFn: async () => {
            const response = await axios.get('/api/vintage/products');
            return response.data;
        }
    });

    // 2. Histórico de precios (del producto genérico asociado)
    const { data: priceHistory, isLoading: isLoadingHistory } = useQuery({
        queryKey: ['price-history', historyProductId],
        queryFn: () => historyProductId ? getProductPriceHistory(historyProductId) : null,
        enabled: !!historyProductId
    });

    // 3. Mutación para revertir al Purgatorio
    const revertMutation = useMutation({
        mutationFn: (offerId: number) => revertVintageItem(offerId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vintage-products'] });
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedProduct(null);
        },
        onError: (err) => {
            console.error('Error al devolver al Purgatorio:', err);
            alert('No se pudo devolver al Purgatorio. Inténtelo de nuevo.');
        }
    });

    const getConditionStyle = (cond: string) => {
        const lower = cond.toLowerCase();
        if (lower.includes('moc') || lower.includes('caja') || lower.includes('nuevo')) {
            return {
                bg: 'bg-green-500/10 border-green-500/30 text-green-400',
                label: 'MOC (En Caja)'
            };
        }
        if (lower.includes('loose') || lower.includes('blister') || lower.includes('jugado')) {
            return {
                bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
                label: 'Loose (Suelto)'
            };
        }
        return {
            bg: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
            label: cond || 'New (Nuevo)'
        };
    };

    const sortedItems = React.useMemo(() => {
        if (!vintageItems) return [];
        return [...vintageItems].sort((a, b) => {
            if (sortBy === 'name') return a.name.localeCompare(b.name);
            if (sortBy === 'price') return a.best_p2p_price - b.best_p2p_price;
            if (sortBy === 'condition') return a.condition.localeCompare(b.condition);
            return 0;
        });
    }, [vintageItems, sortBy]);

    if (isLoadingVintage) {
        return <PowerSwordLoader variant="fullScreen" text="Desenterrando Reliquias del Purgatorio..." isVintage={true} />;
    }

    if (isErrorVintage) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al acceder a Eternia Vintage</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 md:space-y-3 animate-in fade-in duration-1000">
            {/* Header / Banner */}
            <div className="relative overflow-hidden flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-amber-500/10 blur-[100px] pointer-events-none"></div>
                <div className="relative z-10 flex flex-col gap-1">
                    <div className="flex items-center gap-2 text-amber-500">
                        <History className="h-4 w-4" />
                        <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                            Eternia <span className="text-amber-500">Vintage</span>
                        </h2>
                    </div>
                    <p className="max-w-xl text-[11px] md:text-sm text-white/40 font-medium uppercase tracking-[0.1em]">Coleccionables retro de los 80s presentados individualmente</p>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full md:w-auto">
                    <div className="grid grid-cols-3 gap-1 sm:gap-2 p-1 sm:p-1.5 rounded-xl bg-white/[0.03] border border-white/5 w-full sm:w-auto">
                        <button
                            onClick={() => setSortBy('name')}
                            className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'name' ? 'bg-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                        >
                            Nombre
                        </button>
                        <button
                            onClick={() => setSortBy('price')}
                            className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'price' ? 'bg-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                        >
                            Precio
                        </button>
                        <button
                            onClick={() => setSortBy('condition')}
                            className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'condition' ? 'bg-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                        >
                            Estado
                        </button>
                    </div>
                    <div className="flex items-center justify-between sm:justify-start gap-3 rounded-xl sm:rounded-2xl bg-white/[0.03] px-4 sm:px-6 py-2 sm:py-3 border border-white/5 backdrop-blur-3xl w-full sm:w-auto">
                        <div className="flex items-center gap-2">
                            <History className="h-4 w-4 sm:h-5 sm:w-5 text-amber-500" />
                            <span className="text-xl sm:text-2xl font-black text-white leading-none">{vintageItems?.length}</span>
                        </div>
                        <span className="text-[8px] sm:text-[10px] font-black text-white/20 uppercase tracking-[0.15em] sm:tracking-[0.2em] pt-0.5 leading-tight text-right sm:text-left">
                            Piezas Retro<br className="sm:hidden" /> Únicas
                        </span>
                    </div>
                </div>
            </div>

            {/* Grid */}
            {sortedItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-20 text-white/20 space-y-4">
                    <History className="h-16 w-16 opacity-20" />
                    <p className="text-xl font-black uppercase tracking-widest">Eternia Vintage Vacío...</p>
                    <p className="text-[10px] font-bold uppercase tracking-widest opacity-40">Clasifique reliquias de los 80s en el Purgatorio para verlas aquí.</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 gap-3 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {sortedItems.map((item) => {
                        const condStyle = getConditionStyle(item.condition);
                        return (
                            <div
                                key={item.offer_id}
                                className="group relative flex flex-col gap-1.5 sm:gap-4 rounded-2xl sm:rounded-[2.5rem] border border-white/5 bg-black/25 backdrop-blur-md p-2 sm:p-5 hover:bg-white/[0.05] transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl"
                            >
                                <div
                                    className="relative aspect-square w-full overflow-hidden rounded-2xl sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner group/img cursor-pointer"
                                    onClick={() => setSelectedProduct(item)}
                                >
                                    {item.image_url ? (
                                        <MOTUImage productId={item.id} src={item.image_url} alt={item.name} className="h-full w-full object-cover transition-all duration-700 group-hover/img:scale-110" />
                                    ) : (
                                        <div className="flex h-full w-full items-center justify-center italic text-white/20 text-[10px] sm:text-xs font-black uppercase tracking-widest">Sin Imagen</div>
                                    )}

                                    {/* Condition & Store Badges */}
                                    <div className="absolute top-2 right-2 sm:top-4 sm:right-4 z-40 flex flex-col items-end gap-1 sm:gap-2">
                                        <div className={`flex items-center gap-1 rounded-md sm:rounded-xl px-1.5 py-0.5 sm:px-2.5 sm:py-1 border backdrop-blur-md ${condStyle.bg}`}>
                                            <span className="text-[6px] sm:text-[8px] font-black uppercase tracking-widest">{condStyle.label}</span>
                                        </div>
                                        <div className="flex items-center gap-1 rounded-md sm:rounded-xl bg-amber-500/10 px-1.5 py-0.5 sm:px-2.5 sm:py-1 border border-amber-500/20 backdrop-blur-md">
                                            <span className="text-[6px] sm:text-[8px] font-black uppercase tracking-widest text-amber-500">Grading {item.grading?.toFixed(1) || '---'}</span>
                                        </div>
                                    </div>

                                    {/* Shop Indicator */}
                                    <div className="absolute bottom-2 left-2 sm:bottom-4 sm:left-4 z-40 rounded-lg sm:rounded-xl bg-black/75 px-2 py-1 text-[8px] sm:text-[10px] font-black text-white/50 border border-white/5 backdrop-blur-md uppercase tracking-wider">
                                        {item.best_p2p_source}
                                    </div>
                                </div>

                                <div className="flex flex-1 flex-col gap-1 sm:gap-3 px-1">
                                    <div className="space-y-0.5 sm:space-y-1">
                                        <span className="text-[7px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-amber-500 opacity-80 group-hover:opacity-100 transition-colors line-clamp-1">masters of the universe 198x</span>
                                        <h3 className="line-clamp-2 md:min-h-[2rem] text-[11px] sm:text-lg font-black leading-tight text-white group-hover:text-amber-500 transition-colors">{item.name}</h3>
                                    </div>

                                    <div className="mt-auto flex flex-col gap-2">
                                        <div className="flex flex-col flex-1 min-w-0 justify-end pt-2">
                                            <div className="flex items-center gap-1 sm:gap-1.5 overflow-hidden w-full mb-0.5 sm:mb-1">
                                                <span className="text-[6px] sm:text-[8px] font-black text-white/30 uppercase tracking-widest leading-none shrink-0">Precio Colección</span>
                                            </div>
                                            <div className="text-[16px] sm:text-2xl font-black text-amber-500 leading-[0.8] sm:leading-none tracking-tighter truncate">{item.best_p2p_price || 0} <span className="text-[8px] sm:text-xs text-white/40">€</span></div>
                                        </div>

                                        {/* Action Buttons Row - Symmetrical Center Dock */}
                                        <div className="flex items-center justify-center gap-2 rounded-2xl bg-white/[0.03] p-1.5 border border-white/10 group-hover:border-amber-500/20 transition-all backdrop-blur-sm w-full">
                                            {/* Action: Toggle Price History */}
                                            <button
                                                onClick={() => setHistoryProductId(historyProductId === item.id ? null : item.id)}
                                                className={`flex h-8 w-8 items-center justify-center rounded-xl transition-all border hover:scale-110 active:scale-95 duration-300 shadow-md ${historyProductId === item.id ? 'bg-purple-500/20 text-purple-400 border-purple-500/50' : 'bg-white/5 text-white/30 border-white/10 hover:bg-white/10 hover:text-white'}`}
                                                title="Ver Evolución de Precios"
                                            >
                                                <TrendingUp className="h-4 w-4" />
                                            </button>

                                            {/* Action Button: Detail View */}
                                            <button
                                                onClick={() => setSelectedProduct(item)}
                                                className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-white/40 border border-white/10 transition-all hover:bg-amber-500/20 hover:text-amber-400 hover:border-amber-500/45 hover:scale-110 active:scale-95 duration-300 shadow-md"
                                                title="Ver Detalles Completos"
                                            >
                                                <Info className="h-4 w-4" />
                                            </button>

                                            {/* Action: Revert back to Purgatory */}
                                            {isAdmin && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        if (confirm(`¿Devolver '${item.name}' al Purgatorio?`)) {
                                                            revertMutation.mutate(item.offer_id);
                                                        }
                                                    }}
                                                    disabled={revertMutation.isPending}
                                                    className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-red-500/60 border border-white/10 transition-all hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/50 hover:scale-110 active:scale-95 duration-300 shadow-md"
                                                    title="Devolver al Purgatorio (Reversión)"
                                                >
                                                    <RotateCcw className="h-4 w-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {historyProductId === item.id && (
                                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="overflow-hidden space-y-3 mt-2">
                                            <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-purple-400 pt-2 px-1"><span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> Histórico del Muñeco</span></div>
                                            {isLoadingHistory ? <div className="h-20 flex items-center justify-center"><RefreshCw className="h-4 w-4 animate-spin text-purple-500/50" /></div> : priceHistory && priceHistory.length > 0 ? <PriceHistoryChart data={priceHistory} /> : <div className="p-4 text-[10px] font-bold text-center text-white/10 uppercase italic">Sin datos históricos</div>}
                                        </motion.div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl" onClick={() => setSelectedProduct(null)}>
                    <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-[3rem] border border-white/10 bg-[#0A0A0B] shadow-[0_50px_100px_-20px_rgba(0,0,0,1)] flex flex-col" onClick={(e) => e.stopPropagation()}>
                        <div className="p-8 pb-4 flex items-start justify-between">
                            <div className="flex gap-6 items-center">
                                <div
                                    className="h-24 w-24 shrink-0 overflow-hidden rounded-3xl border border-white/10 bg-black/40 cursor-zoom-in hover:scale-105 transition-transform"
                                    onClick={() => setExpandedImage(selectedProduct.image_url ?? null)}
                                    title="Expandir Reliquia"
                                >
                                    <MOTUImage productId={selectedProduct.id} src={selectedProduct.image_url || ''} className="h-full w-full object-cover" />
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-3xl font-black tracking-tighter text-white">Reliquia <span className="text-amber-500">Vintage</span></h4>
                                    <p className="text-sm font-bold text-white/30 uppercase tracking-widest">{selectedProduct.name}</p>
                                </div>
                            </div>
                            <button onClick={() => setSelectedProduct(null)} className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:bg-red-500/20 hover:text-red-400">&times;</button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 pt-4 custom-scrollbar">
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-4">
                                    <div className="glass p-4 rounded-2xl border border-white/5 flex flex-col items-center justify-center">
                                        <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">Precio</p>
                                        <span className="text-2xl font-black text-amber-500">{selectedProduct.best_p2p_price} €</span>
                                    </div>
                                    <div className="glass p-4 rounded-2xl border border-white/5 flex flex-col items-center justify-center">
                                        <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">Estado Conservación</p>
                                        <span className="text-base font-black text-white">{selectedProduct.condition}</span>
                                    </div>
                                    <div className="glass p-4 rounded-2xl border border-white/5 flex flex-col items-center justify-center">
                                        <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">Grading del Experto</p>
                                        <span className="text-lg font-black text-brand-primary">{selectedProduct.grading?.toFixed(1) || '---'} / 10.0</span>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 px-2">Origen y Enlace</h5>
                                    <div className="flex items-center justify-between gap-4 rounded-3xl p-5 bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all">
                                        <div className="space-y-1">
                                            <div className="text-xs font-black uppercase tracking-widest text-white/80">{selectedProduct.best_p2p_source}</div>
                                            <div className="text-[9px] font-bold text-white/20 uppercase">Categoría: Vintage individual</div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <a
                                                href={selectedProduct.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-white/40 border border-white/10 hover:bg-amber-500 hover:text-black transition-all"
                                                title="Ver en Tienda"
                                            >
                                                <ExternalLink className="h-5 w-5" />
                                            </a>
                                            {isAdmin && (
                                                <button
                                                    onClick={() => {
                                                        if (confirm(`¿Desclasificar y devolver '${selectedProduct.name}' al Purgatorio?`)) {
                                                            revertMutation.mutate(selectedProduct.offer_id);
                                                        }
                                                    }}
                                                    className="flex h-12 px-5 items-center justify-center gap-2 rounded-2xl bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all text-xs font-black uppercase tracking-widest"
                                                >
                                                    <RotateCcw className="h-4 w-4" /> Devolver al Purgatorio
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* FULLSCREEN IMAGE EXPANSION */}
            {expandedImage && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-20 bg-black/95 backdrop-blur-3xl animate-in zoom-in duration-300 shadow-2xl"
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
                            className="absolute -top-4 -right-4 sm:-top-8 sm:-right-8 h-10 w-10 sm:h-14 sm:w-14 flex items-center justify-center rounded-2xl bg-white/10 text-white hover:bg-red-500 hover:scale-110 transition-all border border-white/10 backdrop-blur-md shadow-2xl z-50"
                        >
                            <X className="h-6 w-6 sm:h-8 sm:w-8" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Vintage;
