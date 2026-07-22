import { motion } from 'framer-motion';
import { Package, GitMerge, RefreshCw, CheckCircle2, ArrowRight, ArrowDown } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { CHART_COLORS } from './configHelpers';
import { getTemporaryProducts, type TemporaryProduct } from '../../api/admin';

interface MatchStat {
    shop: string;
    count: number;
}

interface InventoryTabProps {
    matchStats: MatchStat[];
    isAdmin: boolean;
    handleCardClick: (shop: string) => void;

    temporaryProducts: TemporaryProduct[];
    setTemporaryProducts: (products: TemporaryProduct[]) => void;
    loadingTemporary: boolean;
    setLoadingTemporary: (v: boolean) => void;

    freeMergeMode: boolean;
    setFreeMergeMode: (v: boolean) => void;
    mergeSource: any;
    setMergeSource: (p: any) => void;
    mergeTarget: any;
    setMergeTarget: (p: any) => void;
    mergeSearchQuery: string;
    setMergeSearchQuery: (v: string) => void;
    mergeTargetSuggestions: any[];
    setMergeTargetSuggestions: (v: any[]) => void;
    searchingTarget: boolean;
    isFusing: boolean;
    freeMergeSourceQuery: string;
    setFreeMergeSourceQuery: (v: string) => void;
    freeMergeSourceSuggestions: any[];
    setFreeMergeSourceSuggestions: (v: any[]) => void;
    showMergePanel: boolean;
    setShowMergePanel: (v: boolean) => void;
    handleConfirmMerge: () => void;
}

/** Fase AAA-4a: extraido de Config.tsx (pestaña "inventory" / "Conquistas de Mercado"). */
export default function InventoryTab({
    matchStats,
    isAdmin,
    handleCardClick,
    temporaryProducts,
    setTemporaryProducts,
    loadingTemporary,
    setLoadingTemporary,
    freeMergeMode,
    setFreeMergeMode,
    mergeSource,
    setMergeSource,
    mergeTarget,
    setMergeTarget,
    mergeSearchQuery,
    setMergeSearchQuery,
    mergeTargetSuggestions,
    searchingTarget,
    isFusing,
    freeMergeSourceQuery,
    setFreeMergeSourceQuery,
    freeMergeSourceSuggestions,
    setFreeMergeSourceSuggestions,
    showMergePanel,
    setShowMergePanel,
    handleConfirmMerge,
}: InventoryTabProps) {
    const totalMatches = matchStats?.reduce((sum, item) => sum + item.count, 0) || 0;
    const sortedMatchStats = matchStats ? [...matchStats].sort((a, b) => b.count - a.count) : [];
    const chartData = sortedMatchStats.map(item => ({
        name: item.shop,
        value: item.count
    }));

    return (
        <motion.div
            key="inventory"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-6"
        >
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Package className="w-6 h-6 text-brand-primary" />
                        Conquistas de Mercado (Inventario)
                    </h2>
                    <p className="text-white/70 text-sm">Resumen de reliquias indexadas por cada portal del mercado.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 md:gap-8">
                {/* Left Column: Sorted market cards grid */}
                <div className="xl:col-span-7 rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 space-y-6">
                    <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-2">Desglose de Conquistas</h3>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
                        {sortedMatchStats.map((item) => (
                            <button
                                key={item.shop}
                                onClick={() => handleCardClick(item.shop)}
                                className="flex flex-col gap-1 rounded-2xl bg-white/[0.03] p-3 md:p-4 border border-white/5 text-left hover:bg-white/[0.08] hover:border-white/10 active:scale-[0.98] transition-all cursor-pointer w-full group outline-none focus:ring-1 focus:ring-brand-primary/50"
                            >
                                <span className="text-[8px] md:text-[9px] font-black uppercase text-white/60 tracking-widest truncate w-full">{item.shop}</span>
                                <span className="text-xl md:text-2xl font-black text-white">{item.count}</span>
                            </button>
                        ))}
                        {sortedMatchStats.length === 0 && (
                            <div className="col-span-full py-6 text-center text-white/60 uppercase font-black text-[9px] tracking-widest">
                                Sin estadísticas de mercado
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: Beautiful Doughnut Chart */}
                <div className="xl:col-span-5 rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 flex flex-col justify-between space-y-6 min-h-[350px]">
                    <div>
                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-1">Cuota de Mercado</h3>
                        <p className="text-[9px] font-bold text-white/50 uppercase tracking-wider leading-relaxed">Representación de la presencia de tus reliquias en diferentes portales.</p>
                    </div>

                    {sortedMatchStats.length > 0 ? (
                        <>
                            <div className="relative flex-1 flex items-center justify-center min-h-[260px]">
                                <ResponsiveContainer width="100%" height={260}>
                                    <PieChart>
                                        <Pie
                                            data={chartData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={70}
                                            outerRadius={95}
                                            paddingAngle={3}
                                            dataKey="value"
                                        >
                                            {chartData.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <RechartsTooltip
                                            content={({ active, payload }: any) => {
                                                if (active && payload && payload.length) {
                                                    return (
                                                        <div className="bg-black/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md flex flex-col gap-0.5 select-none">
                                                            <span className="text-[9px] font-black uppercase tracking-widest text-white/50">
                                                                {payload[0].name}
                                                            </span>
                                                            <span className="text-xs font-black text-brand-primary uppercase tracking-wider">
                                                                {payload[0].value} Reliquias
                                                            </span>
                                                        </div>
                                                    );
                                                }
                                                return null;
                                            }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute flex flex-col items-center justify-center pointer-events-none">
                                    <span className="text-[9px] font-black uppercase tracking-[0.2em] text-white/30">Total</span>
                                    <span className="text-3xl font-black text-white tracking-tighter leading-none my-1">{totalMatches}</span>
                                    <span className="text-[8px] font-bold uppercase tracking-wider text-brand-primary">Vinculadas</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-2 mt-2">
                                {sortedMatchStats.slice(0, 6).map((item, index) => {
                                    const pct = totalMatches > 0 ? ((item.count / totalMatches) * 100).toFixed(1) : '0.0';
                                    return (
                                        <div key={item.shop} className="flex items-center gap-2 bg-white/[0.01] border border-white/[0.03] px-3 py-1.5 rounded-xl min-w-0">
                                            <span
                                                className="w-2.5 h-2.5 rounded-full shrink-0"
                                                style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                                            />
                                            <div className="flex flex-col min-w-0 flex-1">
                                                <span className="text-[8px] font-black uppercase text-white/50 truncate tracking-wider">{item.shop}</span>
                                                <span className="text-[10px] font-black text-white leading-tight">{pct}% <span className="text-[8px] font-bold text-white/40">({item.count})</span></span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-white/20 uppercase font-black text-[9px] tracking-widest">
                            Sin datos de mercado para graficar
                        </div>
                    )}
                </div>
            </div>

            {isAdmin && (
                <div className="col-span-full rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 space-y-6 mt-6">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/10 pb-4">
                        <div>
                            <h3 className="text-lg font-black uppercase tracking-[0.15em] text-white flex items-center gap-2">
                                <GitMerge className="h-5 w-5 text-amber-500" />
                                Nexo de Fusión Divina
                            </h3>
                            <p className="text-[11px] text-white/50 uppercase tracking-wider font-bold mt-1">
                                Consolida el catálogo unificando reliquias temporales con oficiales o fusionando duplicados.
                            </p>
                        </div>

                        {/* Selector de Modo */}
                        <div className="flex bg-white/[0.03] border border-white/10 rounded-xl p-1 shrink-0">
                            <button
                                onClick={() => {
                                    setFreeMergeMode(false);
                                    setMergeSource(null);
                                    setMergeTarget(null);
                                    setMergeSearchQuery('');
                                }}
                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${!freeMergeMode ? 'bg-amber-500 text-black shadow-md' : 'text-white/60 hover:text-white'}`}
                            >
                                ⚡ Fusión Rápida (Customs)
                            </button>
                            <button
                                onClick={() => {
                                    setFreeMergeMode(true);
                                    setMergeSource(null);
                                    setMergeTarget(null);
                                    setMergeSearchQuery('');
                                    setFreeMergeSourceQuery('');
                                }}
                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${freeMergeMode ? 'bg-amber-500 text-black shadow-md' : 'text-white/60 hover:text-white'}`}
                            >
                                🔮 Fusión Libre (Manual)
                            </button>
                        </div>
                    </div>

                    {/* Modos */}
                    {!freeMergeMode ? (
                        /* MODO FUSIÓN RÁPIDA (LISTA DE TEMPORALES) */
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-[9px] font-black uppercase text-white/45 tracking-wider">
                                    Reliquias Temporales Detectadas ({temporaryProducts.length})
                                </span>
                                <button
                                    onClick={async () => {
                                        setLoadingTemporary(true);
                                        try {
                                            const res = await getTemporaryProducts();
                                            setTemporaryProducts(res);
                                        } catch (e) {
                                            console.error(e);
                                        } finally {
                                            setLoadingTemporary(false);
                                        }
                                    }}
                                    className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:text-white flex items-center gap-1"
                                >
                                    <RefreshCw className={`h-3 w-3 ${loadingTemporary ? 'animate-spin' : ''}`} />
                                    Recargar Lista
                                </button>
                            </div>

                            {temporaryProducts.length === 0 ? (
                                <div className="rounded-2xl border border-dashed border-white/10 p-8 flex flex-col items-center justify-center text-center space-y-3 bg-white/[0.01]">
                                    <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                        <CheckCircle2 className="h-5 w-5 text-green-400" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-black text-white uppercase tracking-wider">Nexo en Armonía</p>
                                        <p className="text-[10px] text-white/40 uppercase tracking-widest mt-1">No hay figuras temporales (VINT-/ORIG-) pendientes de consolidación.</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {temporaryProducts.map(p => {
                                        const isVintage = p.figure_id.startsWith('VINT');
                                        return (
                                            <div key={p.id} className="glass p-4 rounded-2xl border border-white/5 bg-white/[0.02] flex items-center justify-between gap-4 hover:border-white/10 transition-colors">
                                                <div className="flex items-center gap-3 min-w-0">
                                                    <div className="h-12 w-12 rounded-xl overflow-hidden bg-black/40 border border-white/10 shrink-0 flex items-center justify-center">
                                                        {p.image_url ? (
                                                            <img src={p.image_url} alt={p.name} className="h-full w-full object-cover" />
                                                        ) : (
                                                            <Package className="h-5 w-5 text-white/20" />
                                                        )}
                                                    </div>
                                                    <div className="min-w-0">
                                                        <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{p.name}</h4>
                                                        <div className="flex items-center gap-1.5 mt-1">
                                                            <span className={`text-[8px] font-black px-1.5 py-0.5 rounded tracking-widest uppercase font-mono ${isVintage ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'}`}>
                                                                {p.figure_id}
                                                            </span>
                                                            <span className="text-[8px] font-bold text-white/45 uppercase tracking-wider">
                                                                {p.offer_count} offers • {p.collection_count} coll
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => {
                                                        setMergeSource(p);
                                                        setMergeTarget(null);
                                                        setMergeSearchQuery('');
                                                        setShowMergePanel(true);
                                                    }}
                                                    className="bg-brand-primary/10 hover:bg-brand-primary text-brand-primary hover:text-black border border-brand-primary/20 px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all shrink-0 flex items-center gap-1 cursor-pointer"
                                                >
                                                    <GitMerge className="h-3 w-3" />
                                                    Unificar
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    ) : (
                        /* MODO FUSIÓN LIBRE (BUSCADOR DUAL) */
                        <div className="space-y-4">
                            <p className="text-[10px] text-white/50 uppercase tracking-wider leading-relaxed">
                                Selecciona libremente cualquier figura de catálogo como origen y destino. Ideal para unificar duplicados oficiales con IDs diferentes.
                            </p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
                                {/* Buscador Origen */}
                                <div className="space-y-2 relative">
                                    <label className="text-[9px] font-black uppercase tracking-widest text-white/40">1. Seleccionar Figura Origen (Será Eliminada)</label>
                                    {mergeSource ? (
                                        <div className="glass p-4 rounded-2xl border border-red-500/25 bg-red-500/5 flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="h-10 w-10 rounded-xl overflow-hidden bg-black/40 border border-white/10 flex items-center justify-center">
                                                    {mergeSource.image_url ? (
                                                        <img src={mergeSource.image_url} alt={mergeSource.name} className="h-full w-full object-cover" />
                                                    ) : (
                                                        <Package className="h-4 w-4 text-white/20" />
                                                    )}
                                                </div>
                                                <div>
                                                    <h4 className="text-xs font-black text-white uppercase tracking-wider">{mergeSource.name}</h4>
                                                    <span className="text-[8px] font-mono text-white/60 tracking-wider bg-white/10 px-1.5 py-0.5 rounded">{mergeSource.figure_id || `#${mergeSource.id}`}</span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => setMergeSource(null)}
                                                className="text-[9px] font-black uppercase text-red-400 hover:text-white cursor-pointer"
                                            >
                                                Remover
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="relative">
                                            <input
                                                type="text"
                                                value={freeMergeSourceQuery}
                                                onChange={(e) => setFreeMergeSourceQuery(e.target.value)}
                                                placeholder="Escribe el nombre de la figura origen..."
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary transition-all"
                                            />
                                            {freeMergeSourceQuery.trim().length > 1 && freeMergeSourceSuggestions.length > 0 && (
                                                <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-2xl max-h-48 overflow-y-auto shadow-2xl custom-scrollbar">
                                                    {freeMergeSourceSuggestions.map((p: any) => (
                                                        <div
                                                            key={p.id}
                                                            onClick={() => {
                                                                setMergeSource(p);
                                                                setFreeMergeSourceQuery('');
                                                                setFreeMergeSourceSuggestions([]);
                                                            }}
                                                            className="px-4 py-2.5 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                                        >
                                                            {p.name} <span className="opacity-45 ml-2 font-mono text-[10px]">#{p.figure_id}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Buscador Destino */}
                                <div className="space-y-2 relative">
                                    <label className="text-[9px] font-black uppercase tracking-widest text-white/40">2. Seleccionar Figura Destino (Conservada)</label>
                                    {mergeTarget ? (
                                        <div className="glass p-4 rounded-2xl border border-green-500/25 bg-green-500/5 flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="h-10 w-10 rounded-xl overflow-hidden bg-black/40 border border-white/10 flex items-center justify-center">
                                                    {mergeTarget.image_url ? (
                                                        <img src={mergeTarget.image_url} alt={mergeTarget.name} className="h-full w-full object-cover" />
                                                    ) : (
                                                        <Package className="h-4 w-4 text-white/20" />
                                                    )}
                                                </div>
                                                <div>
                                                    <h4 className="text-xs font-black text-white uppercase tracking-wider">{mergeTarget.name}</h4>
                                                    <span className="text-[8px] font-mono text-white/60 tracking-wider bg-white/10 px-1.5 py-0.5 rounded">{mergeTarget.figure_id || `#${mergeTarget.id}`}</span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => setMergeTarget(null)}
                                                className="text-[9px] font-black uppercase text-green-400 hover:text-white cursor-pointer"
                                            >
                                                Remover
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="relative">
                                            <input
                                                type="text"
                                                value={mergeSearchQuery}
                                                onChange={(e) => setMergeSearchQuery(e.target.value)}
                                                placeholder="Escribe el nombre de la figura destino..."
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary transition-all"
                                            />
                                            {mergeSearchQuery.trim().length > 1 && mergeTargetSuggestions.length > 0 && (
                                                <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-2xl max-h-48 overflow-y-auto shadow-2xl custom-scrollbar">
                                                    {mergeTargetSuggestions.map((p: any) => (
                                                        <div
                                                            key={p.id}
                                                            onClick={() => {
                                                                setMergeTarget(p);
                                                                setMergeSearchQuery('');
                                                            }}
                                                            className="px-4 py-2.5 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                                        >
                                                            {p.name} <span className="opacity-45 ml-2 font-mono text-[10px]">#{p.figure_id}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* PANEL CONFIRMACIÓN DE FUSIÓN */}
                    {mergeSource && (showMergePanel || mergeTarget) && (
                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-4">
                            <div className="flex items-center justify-between border-b border-white/5 pb-2">
                                <span className="text-[10px] font-black uppercase text-brand-primary tracking-wider">Flujo de Fusión Divina</span>
                                <button
                                    onClick={() => {
                                        setShowMergePanel(false);
                                        setMergeSource(null);
                                        setMergeTarget(null);
                                        setMergeSearchQuery('');
                                    }}
                                    className="text-[9px] font-black uppercase text-white/40 hover:text-white cursor-pointer"
                                >
                                    Cancelar
                                </button>
                            </div>

                            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-4">
                                {/* Origen */}
                                <div className="glass p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-center min-w-[200px] max-w-[250px]">
                                    <span className="text-[8px] font-black uppercase tracking-widest text-red-400 block mb-1">ORIGEN (SE ELIMINA)</span>
                                    <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{mergeSource.name}</h4>
                                    <span className="text-[8px] font-mono text-white/50 mt-1 inline-block bg-white/10 px-1 py-0.5 rounded">{mergeSource.figure_id || `#${mergeSource.id}`}</span>
                                </div>

                                <div className="flex flex-col items-center">
                                    <ArrowRight className="h-6 w-6 text-brand-primary animate-pulse hidden sm:block" />
                                    <ArrowDown className="h-6 w-6 text-brand-primary animate-pulse sm:hidden" />
                                </div>

                                {/* Destino */}
                                <div className="min-w-[200px] max-w-[250px] space-y-2">
                                    {mergeTarget ? (
                                        <div className="glass p-4 rounded-xl border border-green-500/20 bg-green-500/5 text-center">
                                            <span className="text-[8px] font-black uppercase tracking-widest text-green-400 block mb-1">DESTINO (SE CONSERVA)</span>
                                            <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{mergeTarget.name}</h4>
                                            <span className="text-[8px] font-mono text-white/50 mt-1 inline-block bg-white/10 px-1 py-0.5 rounded">{mergeTarget.figure_id || `#${mergeTarget.id}`}</span>
                                        </div>
                                    ) : (
                                        <div className="relative">
                                            <label className="text-[8px] font-black uppercase tracking-widest text-white/40 block mb-1">Buscar Destino</label>
                                            <input
                                                type="text"
                                                value={mergeSearchQuery}
                                                onChange={(e) => setMergeSearchQuery(e.target.value)}
                                                placeholder="Buscar destino..."
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary"
                                            />
                                            {searchingTarget && <span className="text-[8px] text-white/50 uppercase tracking-widest mt-1 block">Buscando...</span>}

                                            {mergeSearchQuery.trim().length > 1 && mergeTargetSuggestions.length > 0 && (
                                                <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-xl max-h-36 overflow-y-auto shadow-2xl custom-scrollbar">
                                                    {mergeTargetSuggestions.map((p: any) => (
                                                        <div
                                                            key={p.id}
                                                            onClick={() => {
                                                                setMergeTarget(p);
                                                                setMergeSearchQuery('');
                                                            }}
                                                            className="px-3 py-2 hover:bg-white/5 text-[11px] text-white/70 hover:text-white cursor-pointer font-bold border-b border-white/5 last:border-0"
                                                        >
                                                            {p.name} <span className="opacity-40 text-[9px] font-mono">#{p.figure_id}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {mergeTarget && (
                                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/25 space-y-3">
                                    <p className="text-[10px] text-red-400 font-bold uppercase leading-normal">
                                        ⚠️ ADVERTENCIA CRÍTICA: Al fusionar, se transferirán de forma atómica todas las ofertas, dueños de la colección, alias y alertas a '{mergeTarget.name}'. El ítem '{mergeSource.name}' ({mergeSource.figure_id || `#${mergeSource.id}`}) será permanentemente destruido. Las ofertas se ajustarán a {mergeTarget.is_vintage ? 'Vintage' : 'Nueva Eternia'}.
                                    </p>

                                    <div className="flex gap-3 justify-end pt-2">
                                        <button
                                            onClick={() => {
                                                setShowMergePanel(false);
                                                setMergeSource(null);
                                                setMergeTarget(null);
                                                setMergeSearchQuery('');
                                            }}
                                            className="px-4 py-2 border border-white/10 rounded-xl text-[10px] font-black uppercase text-white/60 hover:text-white cursor-pointer"
                                        >
                                            Cancelar
                                        </button>
                                        <button
                                            onClick={handleConfirmMerge}
                                            disabled={isFusing}
                                            className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center gap-1 shadow-lg shadow-red-600/25 cursor-pointer"
                                        >
                                            {isFusing ? 'Fusionando...' : '🔥 Ejecutar Fusión Divina'}
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </motion.div>
    );
}
