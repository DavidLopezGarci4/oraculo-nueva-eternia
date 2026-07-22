import React from 'react';
import { Flame, Search, X, CheckCircle2, LayoutGrid, LayoutList } from 'lucide-react';

interface PurgatoryToolbarProps {
    isLoadingPending: boolean;
    pendingItems: any[] | undefined;
    pendingActions: any[];
    isSyncing: React.RefObject<boolean>;
    setShowForensic: (show: boolean) => void;
    setPendingActions: React.Dispatch<React.SetStateAction<any[]>>;
    setLocallyProcessedIds: React.Dispatch<React.SetStateAction<Set<number>>>;
    setFailedActions: React.Dispatch<React.SetStateAction<any[]>>;
    persistenceKey: string;
    selectedPendingId: number | null;
    searchTerm: string;
    setSearchTerm: (term: string) => void;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    filteredPendingItems: any[];
    setSelectedIds: React.Dispatch<React.SetStateAction<number[]>>;
    viewLayout: 'mazo' | 'lista';
    setViewLayout: (layout: 'mazo' | 'lista') => void;
    sortBy: 'newest' | 'oldest' | 'highest_match' | 'lowest_match';
    setSortBy: (sort: 'newest' | 'oldest' | 'highest_match' | 'lowest_match') => void;
    shopFilter: string;
    setShopFilter: (shop: string) => void;
    uniqueShopsInPending: string[];
    enableTransitFilter: boolean;
    setEnableTransitFilter: (enabled: boolean) => void;
    transitType: 'all' | 'retail' | 'p2p';
    setTransitType: (type: 'all' | 'retail' | 'p2p') => void;
}

const PurgatoryToolbar: React.FC<PurgatoryToolbarProps> = ({
    isLoadingPending,
    pendingItems,
    pendingActions,
    isSyncing,
    setShowForensic,
    setPendingActions,
    setLocallyProcessedIds,
    setFailedActions,
    persistenceKey,
    selectedPendingId,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredPendingItems,
    setSelectedIds,
    viewLayout,
    setViewLayout,
    sortBy,
    setSortBy,
    shopFilter,
    setShopFilter,
    uniqueShopsInPending,
    enableTransitFilter,
    setEnableTransitFilter,
    transitType,
    setTransitType
}) => {
    return (
        <>
            {/* Header / Purgatory Status */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px] pointer-events-none"></div>

                <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div className="relative z-10 flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Flame className="h-3 w-3 md:h-4 md:w-4" />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                <span className="text-brand-primary">Purgatorio</span>
                            </h2>
                            {!isLoadingPending && pendingItems && pendingItems.length > 0 && (
                                <div className="ml-2 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-primary/10 border border-brand-primary/20 animate-in zoom-in-95 duration-500">
                                    <div className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-pulse"></div>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary">
                                        {pendingItems.length}
                                    </span>
                                </div>
                            )}
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium uppercase tracking-[0.1em]">
                            Purifica las reliquias para manifestarlas en el catálogo
                        </p>
                    </div>

                    {/* Persistence Sync Indicator (Condensed) */}
                    {pendingActions.length > 0 && (
                        <div className="flex items-center gap-6 px-6 py-4 rounded-3xl bg-brand-primary/10 border border-brand-primary/20 animate-in slide-in-from-right-4 duration-500 backdrop-blur-md">
                            <div className="space-y-1">
                                <p className="text-[10px] font-black uppercase tracking-widest text-brand-primary leading-none">
                                    Sincronización {isSyncing.current ? 'Activa' : 'Pendiente'}
                                </p>
                                <p className="text-[11px] font-bold text-white/50">{pendingActions.length} acciones restantes</p>
                                <div className="flex items-center gap-4">
                                    <button onClick={() => setShowForensic(true)} className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:text-white transition-colors">Forensics</button>
                                    <button
                                        onClick={() => {
                                            if (confirm('¿Limpiar el búfer local? Esto cancelará las acciones no sincronizadas.')) {
                                                setPendingActions([]);
                                                setLocallyProcessedIds(new Set());
                                                setFailedActions([]);
                                                localStorage.removeItem(persistenceKey);
                                                localStorage.removeItem('purgatory_sync_failures');
                                            }
                                        }}
                                        className="text-[9px] font-black uppercase tracking-widest text-red-500/40 hover:text-red-400 transition-colors"
                                    >
                                        Limpiar
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>




            {/* Global Search Bar */}
            <div className={`space-y-6 transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>

                {/* Search Bar */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
                        <Search className={`h-5 w-5 transition-colors ${searchTerm ? 'text-brand-primary' : 'text-white/20'}`} />
                    </div>
                    <input
                        type="text"
                        placeholder="Buscar reliquia en el abismo por nombre, tienda, EAN o ID..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="w-full bg-white/[0.02] border border-white/5 hover:border-white/10 focus:border-brand-primary/50 focus:bg-white/[0.04] rounded-3xl py-6 pl-16 pr-16 text-white placeholder:text-white/20 outline-none transition-all text-sm font-bold shadow-2xl"
                    />
                    {searchTerm && (
                        <button
                            onClick={() => setSearchTerm('')}
                            className="absolute inset-y-0 right-6 flex items-center text-white/20 hover:text-white transition-colors"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    )}
                </div>
                {searchTerm && !selectedPendingId && (
                    <div className="absolute -bottom-6 left-6 animate-in slide-in-from-top-1 flex items-center gap-4">
                        <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary bg-brand-primary/10 px-3 py-1 rounded-full border border-brand-primary/20">
                            Filtrando: {filteredPendingItems.length} resultados
                        </span>
                        {filteredPendingItems.length > 0 && (
                            <button
                                onClick={() => {
                                    const allIds = filteredPendingItems.map(i => i.id);
                                    setSelectedIds(prev => Array.from(new Set([...prev, ...allIds])));
                                }}
                                className="text-[10px] font-black uppercase tracking-widest text-white/65 hover:text-brand-primary transition-colors flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-brand-primary/20"
                            >
                                <CheckCircle2 className="h-3 w-3" /> Seleccionar Todos los Resultados
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Controles y Filtros del Purgatorio */}
            <div className={`space-y-4 bg-white/[0.01] border border-white/5 p-5 rounded-3xl backdrop-blur-md transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* 1. Selector de Diseño / Layout Toggle */}
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Diseño:</span>
                        <button
                            onClick={() => setViewLayout('mazo')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'mazo' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutGrid className="h-3 w-3" />
                            Modo Mazo
                        </button>
                        <button
                            onClick={() => setViewLayout('lista')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'lista' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutList className="h-3 w-3" />
                            Modo Listado
                        </button>
                    </div>

                    {/* 2. Ordenación del Mazo */}
                    <div className="flex items-center gap-2">
                        <span id="purgatory-sort-label" className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Ordenar por:</span>
                        <select
                            value={sortBy}
                            onChange={(e: any) => setSortBy(e.target.value)}
                            aria-labelledby="purgatory-sort-label"
                            className="bg-black/60 border border-white/10 rounded-xl px-3 py-1.5 text-[10px] font-black uppercase tracking-widest text-white outline-none focus:border-brand-primary/50 transition-all cursor-pointer"
                        >
                            <option value="highest_match">Mayor Probabilidad</option>
                            <option value="lowest_match">Menor Probabilidad</option>
                            <option value="newest">Más Nuevas Primero</option>
                            <option value="oldest">Más Antiguas Primero</option>
                        </select>
                    </div>
                </div>

                <div className="h-px bg-white/5 my-2"></div>

                <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
                    {/* 3. Filtro de Tiendas (Chips Dinámicos) */}
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Tienda:</span>
                        <button
                            onClick={() => setShopFilter('all')}
                            className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === 'all' ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                        >
                            Todas
                        </button>
                        {uniqueShopsInPending.map(shop => (
                            <button
                                key={shop}
                                onClick={() => setShopFilter(shop)}
                                className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === shop ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                            >
                                {shop}
                            </button>
                        ))}
                    </div>

                    <div className="hidden md:block h-4 w-px bg-white/10"></div>

                    {/* 4. Filtro de Tránsito */}
                    <div className="flex items-center gap-3">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={enableTransitFilter}
                                onChange={(e) => {
                                    setEnableTransitFilter(e.target.checked);
                                    setCurrentPage(1);
                                }}
                                className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary"
                            />
                            <span className="text-[9px] font-black uppercase tracking-widest text-white/65 flex items-center gap-1">
                                <span className="h-1 w-1 rounded-full bg-orange-500 animate-pulse"></span>
                                Tránsito (Expr.)
                            </span>
                        </label>

                        {enableTransitFilter && (
                            <div className="flex items-center gap-1.5 animate-in slide-in-from-left-4 duration-300">
                                <button
                                    onClick={() => { setTransitType('all'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'all' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Todos
                                </button>
                                <button
                                    onClick={() => { setTransitType('retail'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'retail' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Retail
                                </button>
                                <button
                                    onClick={() => { setTransitType('p2p'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'p2p' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    P2P
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
};

export default PurgatoryToolbar;
