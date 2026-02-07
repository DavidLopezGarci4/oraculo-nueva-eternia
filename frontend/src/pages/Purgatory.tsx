import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Flame,
    Zap,
    Trash2,
    Link,
    ExternalLink,
    Loader2,
    RefreshCcw,
    Search,
    CheckCircle2,
    ShieldAlert,
    Database,
    Copy,
    ChevronLeft,
    ChevronRight,
    X,
    LineChart as ChartIcon
} from 'lucide-react';
import { getPurgatory, matchItem, discardItem, discardItemsBulk } from '../api/purgatory';
import MarketIntelligenceModal from '../components/MarketIntelligenceModal';
import QuickPreviewModal from '../components/QuickPreviewModal';
import axios from 'axios';
import { useEffect, useRef } from 'react';

const PERSISTENCE_KEY = 'purgatory_offline_actions';

const Purgatory: React.FC = React.memo(() => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [manualSearchTerm, setManualSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
    const [pendingActions, setPendingActions] = useState<any[]>(() => {
        const saved = localStorage.getItem(PERSISTENCE_KEY);
        return saved ? JSON.parse(saved) : [];
    });

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 15;
    const [showForensic, setShowForensic] = useState(false);
    const [intelProductId, setIntelProductId] = useState<number | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    // Helper: Check if URL is from Wallapop
    const isWallapopUrl = (url: string) => url?.toLowerCase().includes('wallapop.com');

    // Helper: Copy URL to clipboard
    const copyToClipboard = async (url: string) => {
        try {
            await navigator.clipboard.writeText(url);
            setCopiedUrl(url);
            setTimeout(() => setCopiedUrl(null), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    // Persistence Persistence
    useEffect(() => {
        localStorage.setItem(PERSISTENCE_KEY, JSON.stringify(pendingActions));
    }, [pendingActions]);

    // Mutations
    const discardBulkMutation = useMutation({
        mutationFn: (ids: number[]) => discardItemsBulk(ids),
        onMutate: async (ids) => {
            // Find names/urls for forensic context
            const affectedItems = queryClient.getQueryData<any[]>(['purgatory'])?.filter(i => ids.includes(i.id)) || [];

            // Persistence: Add to local buffer immediately
            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'bulk-discard',
                pendingIds: ids,
                items: affectedItems.map(i => ({ id: i.id, name: i.scraped_name, url: i.url })),
                timestamp: new Date().toISOString()
            }]);

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            // Snapshot the previous value
            const previousItems = queryClient.getQueryData(['purgatory']);
            // Optimistically update the cache
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => !ids.includes(item.id))
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Bulk discard failed:', err);
        },
        onSuccess: (_, ids) => {
            // Success: Remove from local buffer
            setPendingActions(prev => prev.filter(a => !(a.type === 'bulk-discard' && JSON.stringify(a.pendingIds) === JSON.stringify(ids))));
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
        },
        onSettled: () => {
            setSelectedIds([]);
        }
    });

    // Queries
    const { data: pendingItems, isLoading: isLoadingPending } = useQuery({
        queryKey: ['purgatory'],
        queryFn: getPurgatory,
        refetchInterval: 30000 // Aumentado de 5s a 30s para reducir carga en navegación
    });

    const { data: products } = useQuery({
        queryKey: ['products-purgatory'],
        queryFn: async () => {
            const response = await axios.get('/api/products');
            return response.data;
        }
    });


    const discardMutation = useMutation({
        mutationFn: (id: number) => discardItem(id),
        onMutate: async (id) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === id);

            // Persistence: Add to local buffer
            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'discard',
                pendingIds: [id],
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== id)
            );
            return { previousItems };
        },
        onError: (err, _id, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Individual discard failed:', err);
        },
        onSuccess: (_, id) => {
            // Success: Remove from local buffer
            setPendingActions(prev => prev.filter(a => !(a.type === 'discard' && a.pendingIds[0] === id)));
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
        }
    });

    const matchMutation = useMutation({
        mutationFn: ({ pendingId, productId }: { pendingId: number, productId: number }) =>
            matchItem(pendingId, productId),
        onMutate: async ({ pendingId, productId }) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);

            // Persistence: Add to local buffer
            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'match',
                pendingIds: [pendingId],
                productId,
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Match failed:', err);
        },
        onSuccess: (_, variables) => {
            // Success: Remove from local buffer
            setPendingActions(prev => prev.filter(a => !(a.type === 'match' && a.pendingIds[0] === variables.pendingId)));
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedPendingId(null);
            setManualSearchTerm('');
        }
    });


    // Forensic Failures State
    const [failedActions, setFailedActions] = useState<any[]>(() => {
        const saved = localStorage.getItem('purgatory_sync_failures');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('purgatory_sync_failures', JSON.stringify(failedActions));
    }, [failedActions]);

    // Background Sync Engine (Refined Phase 31 - Non-blocking & Forensic)
    const isSyncing = useRef(false);

    useEffect(() => {
        if (pendingActions.length === 0 || isSyncing.current) return;

        const syncPending = async () => {
            if (isSyncing.current || pendingActions.length === 0) return;
            isSyncing.current = true;

            // Use a local copy for processing. We filter out actions that are already in failedActions
            // to avoid re-attempting known poisoned actions automatically unless manually triggered.
            const failedIds = new Set(failedActions.map(f => f.action.id));
            const actionsToProcess = [...pendingActions].filter(a => !failedIds.has(a.id));

            if (actionsToProcess.length === 0) {
                isSyncing.current = false;
                return;
            }

            for (const action of actionsToProcess) {
                try {
                    if (action.type === 'discard') {
                        await discardItem(action.pendingIds[0]);
                    } else if (action.type === 'bulk-discard') {
                        await discardItemsBulk(action.pendingIds);
                    } else if (action.type === 'match') {
                        await matchItem(action.pendingIds[0], action.productId);
                    }

                    // Success: Remove from local state
                    setPendingActions(prev => prev.filter(a => a.id !== action.id));

                    // Small delay to prevent overwhelming the server
                    await new Promise(resolve => setTimeout(resolve, 300));
                } catch (err: any) {
                    console.error('Persistence sync failed for action:', action.id, err);

                    // Forensic mark: Move to failed actions with error context
                    const errorMessage = err.response?.data?.detail || err.message || 'Unknown Error';

                    setFailedActions(prev => {
                        // Avoid duplicates if already there
                        if (prev.some(f => f.action.id === action.id)) return prev;
                        return [...prev, {
                            action,
                            error: errorMessage,
                            timestamp: new Date().toISOString(),
                            // Store metadata for easy forensic access
                            url: action.action_url || null, // We might need to ensure actions contain the URL
                            productId: action.productId || null
                        }];
                    });

                    // NON-BLOCKING: We DON'T break anymore. We continue with the next one.
                }
            }

            isSyncing.current = false;
        };

        const interval = setInterval(syncPending, 30000); // Retry every 30s
        const initialTimeout = setTimeout(syncPending, 3000); // Initial delay

        return () => {
            clearInterval(interval);
            clearTimeout(initialTimeout);
        };
    }, [pendingActions.length, failedActions.length]); // Re-run mainly to ensure the check continues


    const filteredProducts = (products || [])?.filter((p: any) =>
        (p.name || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase()) ||
        (p.figure_id || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase())
    ).slice(0, 20);

    // Dynamic Filter for Pending Items (Main List)
    const pendingIdsToHide = new Set(pendingActions.flatMap(a => a.pendingIds));

    const filteredPendingItems = (pendingItems || []).filter((item: any) => {
        // Persistence Ghost Mode: Filter out locally hidden items
        if (pendingIdsToHide.has(item.id)) return false;

        const term = (searchTerm || "").toLowerCase();
        const matchesSearch = !searchTerm || (
            (item.scraped_name || "").toLowerCase().includes(term) ||
            (item.shop_name || "").toLowerCase().includes(term) ||
            (item.ean || "").toLowerCase().includes(term) ||
            item.id.toString().includes(term)
        );

        // ALWAYS keep the selected item visible so they don't lose context while matching
        if (item.id === selectedPendingId) return true;

        return matchesSearch;
    });

    // Pagination Logic
    const totalItems = filteredPendingItems.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedItems = filteredPendingItems.slice(startIndex, startIndex + itemsPerPage);

    // Ensure we don't stay on an empty page after items are matched/discarded
    if (currentPage > 1 && paginatedItems.length === 0 && totalItems > 0) {
        setCurrentPage(Math.max(1, totalPages));
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-in fade-in duration-700">
            {/* Header / Purgatory Status */}
            <div className="relative overflow-hidden rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.05] to-black p-8 md:p-12 backdrop-blur-xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px]"></div>

                <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Flame className="h-5 w-5" />
                            <span className="text-xs font-black uppercase tracking-[0.3em] opacity-70">El Espejo de Eternia</span>
                        </div>
                        <h2 className="text-4xl md:text-6xl font-black tracking-tighter text-white flex items-center gap-4">
                            Purgatorio
                            {!isLoadingPending && pendingItems && pendingItems.length > 0 && (
                                <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 animate-in zoom-in-95 duration-500">
                                    <div className="h-2 w-2 rounded-full bg-brand-primary animate-pulse"></div>
                                    <span className="text-xs font-black uppercase tracking-widest text-brand-primary/80">
                                        {pendingItems.length} <span className="hidden sm:inline">Reliquias en el Abismo</span>
                                    </span>
                                </div>
                            )}
                        </h2>
                        <p className="max-w-xl text-sm md:text-lg leading-relaxed text-white/40">
                            Filtra, vincula y purifica las reliquias detectadas en las incursiones para que puedan ser manifestadas en el catálogo de Nueva Eternia.
                        </p>
                    </div>

                    {/* Persistence Sync Indicator (Condensed) */}
                    {pendingActions.length > 0 && (
                        <div className="flex items-center gap-6 px-6 py-4 rounded-3xl bg-brand-primary/10 border border-brand-primary/20 animate-in slide-in-from-right-4 duration-500 backdrop-blur-md">
                            <div className="relative">
                                <Loader2 className={`h-6 w-6 ${isSyncing.current ? 'animate-spin text-brand-primary' : 'text-white/20'}`} />
                                {failedActions.length > 0 && (
                                    <div className="absolute -right-1.5 -top-1.5 h-4 w-4 rounded-full bg-red-500 border-2 border-black flex items-center justify-center">
                                        <span className="text-[10px] font-black text-white leading-none">!</span>
                                    </div>
                                )}
                            </div>
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
                                                setFailedActions([]);
                                                localStorage.removeItem(PERSISTENCE_KEY);
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
                                className="text-[10px] font-black uppercase tracking-widest text-white/40 hover:text-brand-primary transition-colors flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-brand-primary/20"
                            >
                                <CheckCircle2 className="h-3 w-3" /> Seleccionar Todos los Resultados
                            </button>
                        )}
                    </div>
                )}
            </div>


            {/* Purgatory List */}
            <div className="grid grid-cols-1 gap-6">
                {isLoadingPending ? (
                    <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/30">
                        <Loader2 className="h-10 w-10 animate-spin" />
                        <p className="text-sm">Escaneando el abismo...</p>
                    </div>
                ) : pendingItems?.length === 0 ? (
                    <div className="flex min-h-[300px] flex-col items-center justify-center gap-6 rounded-3xl border-2 border-dashed border-white/5 bg-white/[0.02] text-center">
                        <CheckCircle2 className="h-12 w-12 text-green-500/40" />
                        <div className="max-w-xs space-y-1">
                            <p className="text-lg font-bold text-white/60">Purgatorio Vacío</p>
                            <p className="text-sm text-white/30">Todas las reliquias han sido purificadas o descartadas.</p>
                        </div>
                    </div>
                ) : (
                    <>
                        <div className="flex items-center justify-between mb-4 px-4 py-3 rounded-2xl bg-white/[0.03] border border-white/5">
                            <div className="flex items-center gap-4">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input
                                        type="checkbox"
                                        checked={paginatedItems.length > 0 && paginatedItems.every(item => selectedIds.includes(item.id))}
                                        onChange={(e) => {
                                            const pageIds = paginatedItems.map(i => i.id);
                                            if (e.target.checked) {
                                                setSelectedIds(prev => Array.from(new Set([...prev, ...pageIds])));
                                            } else {
                                                setSelectedIds(prev => prev.filter(id => !pageIds.includes(id)));
                                            }
                                        }}
                                        className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                    />
                                    <span className="text-[10px] font-black uppercase tracking-widest text-white/40 group-hover:text-white/60 transition-colors">Seleccionar Página</span>
                                </label>
                                <div className="h-4 w-px bg-white/10"></div>
                                <div className="text-[10px] font-black uppercase tracking-widest text-white/30 italic">
                                    Fragmento {startIndex + 1} - {Math.min(startIndex + itemsPerPage, totalItems)} <span className="text-white/10 mx-1">/</span> Total: {totalItems}
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-colors"
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </button>
                                <div className="text-xs font-black text-white/60">Página {currentPage} de {totalPages}</div>
                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-colors"
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </button>
                            </div>
                        </div>

                        {paginatedItems.map((item: any) => (
                            <div key={item.id} className={`group relative overflow-hidden rounded-3xl border transition-all duration-500 ${selectedPendingId === item.id ? 'bg-brand-primary/[0.03] border-brand-primary/30 shadow-[0_0_30px_rgba(var(--brand-primary-rgb),0.1)]' : 'bg-white/[0.02] border-white/5 hover:border-white/10'}`}>

                                {/* Card Main Body */}
                                <div className="p-5 md:p-6 flex flex-col gap-6 md:flex-row md:items-start">
                                    {/* Selection Checkbox */}
                                    <div className="pt-1">
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.includes(item.id)}
                                            onChange={(e) => {
                                                if (e.target.checked) setSelectedIds([...selectedIds, item.id]);
                                                else setSelectedIds(selectedIds.filter(id => id !== item.id));
                                            }}
                                            className="h-5 w-5 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                        />
                                    </div>

                                    {/* Thumbnail & Mobile Header */}
                                    <div className="flex items-start gap-5 w-full md:w-auto">
                                        <div className="relative h-24 w-24 md:h-32 md:w-32 shrink-0 overflow-hidden rounded-2xl bg-black border border-white/10 shadow-lg">
                                            {item.image_url ? (
                                                <img src={item.image_url} alt={item.scraped_name} className="h-full w-full object-cover p-1 transition-transform duration-700 group-hover:scale-110 opacity-80 group-hover:opacity-100" />
                                            ) : (
                                                <div className="flex h-full w-full items-center justify-center text-[10px] text-white/20 uppercase font-black tracking-widest">No IMG</div>
                                            )}
                                            {/* Shop Badge (Mobile Overlay) */}
                                            <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm py-1 text-center md:hidden">
                                                <span className="text-[9px] font-black text-white/60 uppercase tracking-tighter">{item.shop_name}</span>
                                            </div>
                                        </div>

                                        {/* Mobile Only Info Block */}
                                        <div className="flex-1 md:hidden space-y-2">
                                            <h3 className="text-sm font-bold text-white leading-snug line-clamp-3">{item.scraped_name}</h3>
                                            <div className="flex items-baseline gap-2">
                                                <span className="text-xl font-black text-brand-primary tracking-tight">{item.price} {item.currency}</span>
                                            </div>
                                            <span className="text-[10px] font-bold text-white/30">{new Date(item.found_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>

                                    {/* Desktop Info */}
                                    <div className="hidden md:flex flex-1 flex-col gap-3">
                                        <div className="flex items-center gap-3">
                                            <span className={`rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-widest border ${['kidinn', 'tradeinn', 'diveinn', 'bikeinn', 'motardinn', 'dressinn', 'smashinn', 'trekkinn', 'runnerinn', 'snowinn', 'swiminn', 'waveinn', 'traininn', 'goalinn', 'xtremeinn'].includes(item.shop_name?.toLowerCase()) ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' : 'bg-white/5 border-white/10 text-white/40'}`}>
                                                {item.shop_name}
                                            </span>
                                            <span className="text-[10px] text-white/20 font-bold tracking-wider">
                                                DETECTADO: {new Date(item.found_at).toLocaleString()}
                                            </span>
                                        </div>

                                        <h3 className="text-lg font-bold text-white/90 leading-snug max-w-2xl group-hover:text-white transition-colors">
                                            {item.scraped_name}
                                        </h3>

                                        <div className="flex items-center gap-6 pt-1">
                                            <div className="flex flex-col">
                                                <span className="text-[10px] font-black text-white/30 uppercase tracking-wider">Precio Detectado</span>
                                                <span className="text-2xl font-black text-white tracking-tight">{item.price} <span className="text-sm text-white/40">{item.currency}</span></span>
                                            </div>
                                            {item.ean && (
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-black text-white/30 uppercase tracking-wider">EAN / Ref</span>
                                                    <span className="text-sm font-mono font-bold text-white/60">{item.ean}</span>
                                                </div>
                                            )}
                                            <div className="flex-1"></div>
                                            <div className="flex flex-wrap gap-2">
                                                {isWallapopUrl(item.url) ? (
                                                    <button
                                                        onClick={() => copyToClipboard(item.url)}
                                                        className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-black uppercase tracking-wider transition-all ${copiedUrl === item.url ? 'bg-green-500/20 border-green-500/50 text-green-400' : 'bg-white/5 border-white/5 text-white/40 hover:bg-white/10 hover:text-white'}`}
                                                    >
                                                        {copiedUrl === item.url ? 'Copiado!' : 'Copiar URL'} <Copy className="h-3 w-3" />
                                                    </button>
                                                ) : (
                                                    <a href={item.url} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-xs font-black text-white/40 hover:bg-white/10 hover:text-white transition-all uppercase tracking-wider">
                                                        Fuente Original <ExternalLink className="h-3 w-3" />
                                                    </a>
                                                )}

                                                {/* Phase 40: Visión Rápida Trigger */}
                                                <button
                                                    onClick={() => setPreviewUrl(item.url)}
                                                    className="inline-flex items-center gap-2 rounded-xl bg-brand-primary/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-brand-primary transition-all hover:bg-brand-primary/20 border border-brand-primary/20 shadow-lg shadow-brand-primary/10"
                                                >
                                                    <CheckCircle2 className="h-3 w-3" />
                                                    Visión Rápida
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Actions Footer */}
                                <div className="border-t border-white/5 bg-black/20 p-4 md:px-6 flex items-center justify-between gap-4">
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-white/20 uppercase tracking-wider">
                                        <Database className="h-3 w-3" /> ID: #{item.id}
                                    </div>
                                    <div className="flex items-center gap-3 w-full md:w-auto">
                                        {isWallapopUrl(item.url) ? (
                                            <button
                                                onClick={() => copyToClipboard(item.url)}
                                                className={`h-12 md:h-10 w-12 md:w-10 flex items-center justify-center rounded-xl border transition-all ${copiedUrl === item.url ? 'bg-green-500/20 border-green-500/50 text-green-400' : 'bg-white/5 border-white/10 text-white/40 hover:text-white hover:bg-white/10'}`}
                                                title="Copiar URL (Wallapop bloquea links directos)"
                                            >
                                                <Copy className="h-5 w-5 md:h-4 md:w-4" />
                                            </button>
                                        ) : (
                                            <a
                                                href={item.url}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="h-12 md:h-10 w-12 md:w-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white/40 hover:text-white hover:bg-white/10 transition-all"
                                                title="Ver en Tienda"
                                            >
                                                <ExternalLink className="h-5 w-5 md:h-4 md:w-4" />
                                            </a>
                                        )}
                                        <button
                                            onClick={() => discardMutation.mutate(item.id)}
                                            className="h-12 md:h-10 w-12 md:w-auto md:px-5 flex items-center justify-center rounded-xl bg-red-500/5 text-red-500/60 border border-red-500/10 hover:bg-red-500 hover:text-white hover:border-red-500 transition-all"
                                            title="Descartar Item"
                                        >
                                            <Trash2 className="h-5 w-5 md:h-4 md:w-4 md:mr-2" />
                                            <span className="hidden md:inline text-[10px] font-black uppercase tracking-widest">Descartar</span>
                                        </button>
                                        <button
                                            onClick={() => {
                                                setSelectedPendingId(selectedPendingId === item.id ? null : item.id);
                                                setManualSearchTerm('');
                                            }}
                                            className={`h-12 md:h-10 flex-1 md:flex-initial md:px-8 flex items-center justify-center rounded-xl text-xs font-black uppercase tracking-widest transition-all shadow-lg ${selectedPendingId === item.id
                                                ? 'bg-white text-black shadow-white/10'
                                                : 'bg-brand-primary text-white shadow-brand-primary/20 hover:brightness-110'}`}
                                        >
                                            {selectedPendingId === item.id ? 'Cerrar Vinculación' : 'Vincular Item'}
                                            <Link className="ml-2 h-4 w-4" />
                                        </button>
                                    </div>
                                </div>

                                {/* Matcher Drawer (The "Banner" Area) */}
                                {selectedPendingId === item.id && (
                                    <div className="border-t border-white/10 bg-gradient-to-b from-brand-primary/[0.02] to-transparent p-5 md:p-8 animate-in slide-in-from-top-4 duration-500">
                                        <div className="max-w-4xl mx-auto space-y-8">

                                            {/* Section 1: Oracle Suggestions (The Main Banner) */}
                                            {item.suggestions && item.suggestions.length > 0 && !manualSearchTerm && (
                                                <div className="space-y-4">
                                                    <div className="flex items-center gap-3">
                                                        <div className="h-8 w-8 rounded-full bg-brand-primary/20 flex items-center justify-center animate-pulse">
                                                            <Zap className="h-4 w-4 text-brand-primary" />
                                                        </div>
                                                        <div>
                                                            <h4 className="text-sm font-black text-white uppercase tracking-widest">Sugerencias del Oráculo</h4>
                                                            <p className="text-[10px] font-bold text-white/40">Basado en coincidencia de nombre y metadatos</p>
                                                        </div>
                                                    </div>

                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                        {item.suggestions.map((sug: any) => (
                                                            <div key={sug.product_id} className="group/btn relative flex items-center gap-4 overflow-hidden rounded-2xl border border-brand-primary/20 bg-brand-primary/5 p-4 text-left transition-all hover:border-brand-primary hover:bg-brand-primary/10 hover:shadow-[0_0_30px_rgba(var(--brand-primary-rgb),0.15)]">
                                                                {/* Score Ring */}
                                                                <div className="relative h-14 w-14 shrink-0 flex items-center justify-center rounded-full bg-black border-2 border-brand-primary/30 group-hover/btn:border-brand-primary transition-colors">
                                                                    <span className="text-xs font-black text-brand-primary">{sug.match_score}%</span>
                                                                </div>

                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2 mb-1">
                                                                        <span className="px-1.5 py-0.5 rounded bg-brand-primary/20 text-[9px] font-black text-brand-primary uppercase tracking-tighter">
                                                                            {sug.reason?.toUpperCase() || 'MATCH'}
                                                                        </span>
                                                                        <span className="text-[9px] font-bold text-white/30 uppercase tracking-widest truncate">{sug.sub_category}</span>
                                                                    </div>
                                                                    <h5 className="text-sm font-bold text-white leading-tight truncate">{sug.name}</h5>
                                                                    <p className="text-[10px] text-white/40 font-mono mt-0.5">{sug.figure_id}</p>
                                                                </div>

                                                                <div className="flex items-center gap-2">
                                                                    <button
                                                                        onClick={() => setIntelProductId(sug.product_id)}
                                                                        className="h-8 w-8 flex items-center justify-center rounded-lg bg-brand-primary/10 text-brand-primary border border-brand-primary/20 hover:bg-brand-primary hover:text-white transition-all shadow-sm"
                                                                        title="Análisis de Mercado 3OX"
                                                                    >
                                                                        <ChartIcon className="h-4 w-4" />
                                                                    </button>
                                                                    <button
                                                                        onClick={() => matchMutation.mutate({ pendingId: item.id, productId: sug.product_id })}
                                                                        disabled={matchMutation.isPending}
                                                                        className="flex items-center gap-2 rounded-xl bg-brand-primary/10 px-4 py-2 text-[10px] font-black uppercase text-brand-primary border border-brand-primary/20 hover:bg-brand-primary hover:text-white transition-all shadow-lg shadow-brand-primary/10 group/match"
                                                                    >
                                                                        <Link className="h-3 w-3" />
                                                                        Vincular
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Section 2: Manual Search */}
                                            <div className="space-y-4 pt-4 border-t border-white/5">
                                                <div className="flex items-center gap-3">
                                                    <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center">
                                                        <Search className="h-4 w-4 text-white/60" />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-sm font-black text-white uppercase tracking-widest">Búsqueda Manual</h4>
                                                        <p className="text-[10px] font-bold text-white/40">Explora el Gran Catálogo de Eternia</p>
                                                    </div>
                                                </div>

                                                <div className="relative group/input">
                                                    <Search className="absolute left-4 top-3.5 h-5 w-5 text-white/30 group-focus-within/input:text-brand-primary transition-colors" />
                                                    <input
                                                        type="text"
                                                        placeholder="Escribe el nombre de la figura..."
                                                        className="w-full rounded-2xl bg-black/40 border border-white/10 py-3.5 pl-12 pr-4 text-sm font-bold text-white placeholder:text-white/20 outline-none focus:border-brand-primary/50 focus:bg-black/60 transition-all focus:ring-1 focus:ring-brand-primary/20"
                                                        value={manualSearchTerm}
                                                        onChange={(e) => setManualSearchTerm(e.target.value)}
                                                    />
                                                </div>

                                                {/* Results List - Expanded height for Phase 32 */}
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-[400px] overflow-y-auto custom-scrollbar pr-2">
                                                    {(manualSearchTerm ? filteredProducts : []).map((p: any) => (
                                                        <button
                                                            key={p.id}
                                                            onClick={() => matchMutation.mutate({ pendingId: item.id, productId: p.id })}
                                                            className="flex items-center gap-3 rounded-xl bg-white/5 p-3 text-left hover:bg-white/10 border border-transparent hover:border-white/20 transition-all group/res"
                                                        >
                                                            <div className="h-10 w-10 shrink-0 rounded-lg bg-black/40 border border-white/5 flex items-center justify-center text-[9px] font-black text-white/30">
                                                                IMG
                                                            </div>
                                                            <div className="flex-1 min-w-0">
                                                                <div className="text-xs font-bold text-white truncate">{p.name}</div>
                                                                <div className="text-[9px] font-black text-white/30 uppercase tracking-widest">{p.figure_id}</div>
                                                            </div>
                                                            <CheckCircle2 className="h-4 w-4 text-brand-primary opacity-0 group-hover/res:opacity-100 transition-opacity" />
                                                        </button>
                                                    ))}
                                                    {manualSearchTerm && filteredProducts?.length === 0 && (
                                                        <div className="col-span-full py-8 text-center">
                                                            <p className="text-xs font-bold text-white/30">El Oráculo no ve nada...</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                        }

                        {/* Bottom Pagination */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-center gap-4 py-8">
                                <button
                                    onClick={() => {
                                        setCurrentPage(p => Math.max(1, p - 1));
                                        window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    disabled={currentPage === 1}
                                    className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-all text-[10px] font-black uppercase tracking-widest text-white"
                                >
                                    Anterior
                                </button>
                                <div className="flex items-center gap-1">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        // Simple sliding window for page numbers
                                        let pageNum = currentPage;
                                        if (currentPage <= 3) pageNum = i + 1;
                                        else if (currentPage >= totalPages - 2) pageNum = totalPages - 4 + i;
                                        else pageNum = currentPage - 2 + i;

                                        if (pageNum <= 0 || pageNum > totalPages) return null;

                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => {
                                                    setCurrentPage(pageNum);
                                                    window.scrollTo({ top: 0, behavior: 'smooth' });
                                                }}
                                                className={`w-10 h-10 rounded-xl text-[10px] font-black transition-all ${currentPage === pageNum ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/40 hover:bg-white/10'}`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}
                                </div>
                                <button
                                    onClick={() => {
                                        setCurrentPage(p => Math.min(totalPages, p + 1));
                                        window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    disabled={currentPage === totalPages}
                                    className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-all text-[10px] font-black uppercase tracking-widest text-white"
                                >
                                    Siguiente
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Bulk Action Bar */}
            {
                selectedIds.length > 0 && (
                    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-8 duration-500">
                        <div className="bg-black/80 backdrop-blur-2xl border border-brand-primary/30 rounded-full px-8 py-4 flex items-center gap-8 shadow-[0_0_50px_rgba(14,165,233,0.3)]">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Seleccionados</span>
                                <span className="text-xl font-black text-white">{selectedIds.length} <span className="text-sm text-white/40">ITEMS</span></span>
                            </div>
                            <div className="h-8 w-px bg-white/10"></div>
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => setSelectedIds([])}
                                    className="text-xs font-black text-white/40 hover:text-white uppercase tracking-widest transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={() => discardBulkMutation.mutate(selectedIds)}
                                    disabled={discardBulkMutation.isPending}
                                    className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-full text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-red-500/20 flex items-center gap-2 disabled:opacity-50"
                                >
                                    {discardBulkMutation.isPending ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                    Descartar Seleccionados
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Forensic Inspection Modal */}
            {
                showForensic && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/90 backdrop-blur-xl animate-in fade-in duration-300">
                        <div className="relative w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden rounded-[2.5rem] border border-white/10 bg-gradient-to-br from-white/5 to-black shadow-2xl">
                            <div className="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-3">
                                        <ShieldAlert className="h-6 w-6 text-red-400" />
                                        <h3 className="text-2xl font-black text-white uppercase tracking-tight">Sala de Autopsia Forense</h3>
                                    </div>
                                    <p className="text-xs text-white/40 uppercase tracking-widest font-bold">Inspección de acciones estancadas en el búfer ({failedActions.length} items)</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    {failedActions.length > 1 && (
                                        <button
                                            onClick={() => {
                                                setFailedActions([]);
                                                // Removing from failures allows the sync engine to pick them up in the next cycle
                                            }}
                                            className="px-6 py-2.5 rounded-2xl bg-brand-primary/20 border border-brand-primary/30 text-brand-primary text-[10px] font-black uppercase tracking-widest hover:bg-brand-primary hover:text-white transition-all"
                                        >
                                            Reintentar Todo ({failedActions.length})
                                        </button>
                                    )}
                                    <button
                                        onClick={() => setShowForensic(false)}
                                        className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-white transition-all"
                                    >
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                                {failedActions.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center gap-4 text-white/20">
                                        <CheckCircle2 className="h-12 w-12" />
                                        <p className="text-sm font-bold uppercase tracking-widest">No hay fallos registrados en esta sesión</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {failedActions.map((f, idx) => (
                                            <div key={idx} className="group relative overflow-hidden rounded-2xl border border-red-500/20 bg-red-500/[0.02] p-6 hover:bg-red-500/[0.04] transition-all">
                                                <div className="flex flex-col md:flex-row gap-6 items-start">
                                                    <div className="flex-1 space-y-4 min-w-0">
                                                        <div className="flex items-center gap-3">
                                                            <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter ${f.action.type === 'match' ? 'bg-brand-primary text-white' : 'bg-orange-500 text-white'}`}>
                                                                {f.action.type === 'match' ? 'VINCULACIÓN' : 'DESCARTE'}
                                                            </span>
                                                            <span className="text-[10px] font-bold text-white/20 font-mono">ID ACCIÓN: {f.action.id}</span>
                                                        </div>

                                                        <div className="space-y-1">
                                                            <h4 className="text-lg font-bold text-white leading-tight truncate" title={f.action.scrapedName || f.action.action_url || 'Sin Nombre'}>
                                                                {f.action.scrapedName || (f.action.action_url ? `URL: ${f.action.action_url.substring(0, 50)}...` : 'Ítem sin nombre (Carga previa)')}
                                                            </h4>
                                                            <div className="flex items-center gap-4">
                                                                {(f.action.action_url || f.url) && (
                                                                    <a href={f.action.action_url || f.url} target="_blank" rel="noreferrer" className="text-[10px] font-bold text-brand-primary hover:underline flex items-center gap-1">
                                                                        <ExternalLink className="h-3 w-3" /> Ver Oferta Original
                                                                    </a>
                                                                )}
                                                                {f.action.productId && (
                                                                    <span className="text-[10px] font-bold text-white/30 truncate">
                                                                        Objetivo: Producto #{f.action.productId}
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>

                                                        <div className="p-3 rounded-xl bg-black/40 border border-white/5">
                                                            <p className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-1 opacity-50">Log del Servidor:</p>
                                                            <p className="text-xs font-mono font-bold text-red-300 break-words">{f.error}</p>
                                                        </div>
                                                    </div>

                                                    <div className="flex flex-row md:flex-col gap-2 w-full md:w-auto shrink-0">
                                                        <button
                                                            onClick={() => {
                                                                // Force retry: Remove from failedActions to let the sync engine pick it up again
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                            }}
                                                            className="flex-1 md:w-32 py-2.5 rounded-xl bg-brand-primary text-white text-[10px] font-black uppercase tracking-widest hover:brightness-110 transition-all"
                                                        >
                                                            Reintentar
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                // Forced return to abyss: Remove from failedActions AND pendingActions
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                                setPendingActions(prev => prev.filter(a => a.id !== f.action.id));
                                                            }}
                                                            className="flex-1 md:w-32 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/60 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 hover:text-white transition-all"
                                                        >
                                                            Devolver al Abismo
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                // Remove from failures but keep in ghost mode (uncommon case, but available)
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                            }}
                                                            className="p-2.5 rounded-xl bg-red-500/10 text-red-500/60 hover:bg-red-500 hover:text-white transition-all"
                                                            title="Limpiar Log de Error"
                                                        >
                                                            <Trash2 className="h-4 w-4 mx-auto" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="p-6 border-t border-white/5 bg-black/40 flex justify-end">
                                <button
                                    onClick={() => setShowForensic(false)}
                                    className="px-8 py-3 rounded-2xl bg-white/10 text-white text-xs font-black uppercase tracking-widest hover:bg-white/20 transition-all"
                                >
                                    Salir de Autopsia
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Phase 41: Market Intelligence Modal */}
            {
                intelProductId && (
                    <MarketIntelligenceModal
                        productId={intelProductId}
                        onClose={() => setIntelProductId(null)}
                    />
                )
            }

            {/* Phase 40: Wallapop Oracle Bridge - Quick Preview */}
            {
                previewUrl && (
                    <QuickPreviewModal
                        url={previewUrl}
                        onClose={() => setPreviewUrl(null)}
                    />
                )
            }
        </div>
    );
});

export default Purgatory;
