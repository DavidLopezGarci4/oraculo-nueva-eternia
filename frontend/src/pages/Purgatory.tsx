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
    History,
    Database,
    AlertCircle,
    Copy
} from 'lucide-react';
import { getPurgatory, matchItem, discardItem, discardItemsBulk, getScrapersStatus, runScrapers, getScraperLogs, resetSmartMatches } from '../api/purgatory';
import axios from 'axios';

const Purgatory: React.FC = () => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);
    const [confirmScraper, setConfirmScraper] = useState<string | null>(null);
    const [confirmReset, setConfirmReset] = useState(false);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [copiedUrl, setCopiedUrl] = useState<string | null>(null);

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

    // Mutations
    const discardBulkMutation = useMutation({
        mutationFn: (ids: number[]) => discardItemsBulk(ids),
        onSuccess: () => {
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
        refetchInterval: 5000 // Auto-refresh every 5s while in Purgatory
    });

    const { data: scrapersStatus } = useQuery({
        queryKey: ['scrapers-status'],
        queryFn: getScrapersStatus,
        refetchInterval: 3000
    });

    const isRunning = scrapersStatus?.some((s: any) => s.status === 'running');

    const { data: scrapersLogs } = useQuery({
        queryKey: ['scrapers-logs'],
        queryFn: getScraperLogs,
        refetchInterval: isRunning ? 2000 : 10000
    });

    const { data: products } = useQuery({
        queryKey: ['products-purgatory'],
        queryFn: async () => {
            const response = await axios.get('/api/products');
            return response.data;
        }
    });

    // Mutations
    const runScrapersMutation = useMutation({
        mutationFn: (scraperName: string) => runScrapers(scraperName, 'manual'),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
            queryClient.invalidateQueries({ queryKey: ['scrapers-logs'] });
        }
    });

    const discardMutation = useMutation({
        mutationFn: (id: number) => discardItem(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
        },
        onError: (err) => {
            console.error('Individual discard failed:', err);
        }
    });

    const matchMutation = useMutation({
        mutationFn: ({ pendingId, productId }: { pendingId: number, productId: number }) =>
            matchItem(pendingId, productId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedPendingId(null);
            setSearchTerm('');
        }
    });

    const resetSmartMatchesMutation = useMutation({
        mutationFn: resetSmartMatches,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setConfirmReset(false);
        }
    });


    const filteredProducts = products?.filter((p: any) =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.figure_id?.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 10);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-in fade-in duration-700">
            {/* Header / Scraper Control Panel */}
            <div className="relative overflow-hidden rounded-3xl md:rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.05] to-black p-5 md:p-8 backdrop-blur-xl">
                <div className="absolute -right-20 -top-20 h-48 w-48 md:h-64 md:w-64 rounded-full bg-brand-primary/5 blur-3xl"></div>

                <div className="relative space-y-8">
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-brand-primary">
                                <Flame className="h-4 w-4 md:h-5 md:w-5" />
                                <span className="text-[10px] md:text-xs font-black uppercase tracking-widest opacity-70">El Espejo de Eternia</span>
                            </div>
                            <h2 className="text-3xl md:text-5xl font-black tracking-tight text-white">Purgatorio</h2>
                            <p className="max-w-md text-xs md:text-sm leading-relaxed text-white/50">
                                Gestiona las reliquias que necesitan vinculación manual y despliega incursiones.
                            </p>
                        </div>

                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setConfirmReset(true)}
                                className="px-6 py-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-widest hover:bg-red-500 hover:text-white transition-all shadow-lg shadow-red-500/5 group"
                            >
                                <RefreshCcw className="inline h-3.5 w-3.5 mr-2 group-hover:rotate-180 transition-transform duration-500" />
                                Purificar Datos
                            </button>
                            <div className="text-right hidden sm:block">
                                <p className="text-[10px] font-black uppercase tracking-widest text-white/30">Estado Global</p>
                                <p className={`text-xs font-bold ${isRunning ? 'text-green-400 animate-pulse' : 'text-white/50'}`}>
                                    {isRunning ? 'INCURSIÓN ACTIVA' : 'SISTEMAS EN REPOSO'}
                                </p>
                            </div>
                            <div className={`h-12 w-12 rounded-2xl flex items-center justify-center border ${isRunning ? 'bg-green-500/20 border-green-500/50 text-green-400 animate-pulse' : 'bg-white/5 border-white/10 text-white/20'}`}>
                                <Zap className="h-6 w-6" />
                            </div>
                        </div>
                    </div>

                    {/* Scraper Section Layout */}
                    <div className="space-y-8">
                        {/* Primary Scraper Actions (Global / Manual) */}
                        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                            {/* Global Scan Item */}
                            <button
                                onClick={() => setConfirmScraper('all')}
                                disabled={isRunning}
                                className="group relative flex flex-col gap-3 rounded-2xl border border-brand-primary/30 bg-brand-primary/5 p-4 transition-all hover:bg-brand-primary/10 disabled:opacity-50"
                            >
                                <div className="flex items-center justify-between">
                                    <Zap className="h-5 w-5 text-brand-primary" />
                                    <div className="h-1.5 w-1.5 rounded-full bg-brand-primary"></div>
                                </div>
                                <div className="space-y-1 text-left">
                                    <p className="text-[10px] font-black uppercase tracking-tighter text-brand-primary">Global Scan</p>
                                    <p className="text-xs font-bold text-white uppercase">Toda Eternia</p>
                                </div>
                            </button>

                            {/* Local Harvester Item */}
                            <button
                                onClick={() => setConfirmScraper('harvester')}
                                disabled={isRunning}
                                className="group relative flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 transition-all hover:bg-white/10 disabled:opacity-50"
                            >
                                <div className="flex items-center justify-between">
                                    <RefreshCcw className={`h-5 w-5 ${scrapersStatus?.find((s: any) => s.spider_name === 'harvester')?.status === 'running' ? 'animate-spin text-green-400' : 'text-white/40'}`} />
                                    <div className={`h-1.5 w-1.5 rounded-full ${scrapersStatus?.find((s: any) => s.spider_name === 'harvester')?.status === 'running' ? 'bg-green-400' : 'bg-white/10'}`}></div>
                                </div>
                                <div className="space-y-1 text-left">
                                    <p className="text-[10px] font-black uppercase tracking-tighter text-white/30">Local Playwright</p>
                                    <p className="text-xs font-bold text-white uppercase">Incursión Manual</p>
                                </div>
                            </button>
                        </div>

                        {/* Individual Spider Catalog */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 px-1">
                                <Search className="h-3 w-3 text-white/20" />
                                <h3 className="text-[10px] font-black uppercase tracking-widest text-white/30">Motor de Incursión Individual</h3>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                                {(() => {
                                    if (!scrapersStatus) return null;

                                    const individualScrapers = scrapersStatus.filter((s: any) =>
                                        !['all', 'harvester', 'Harvester'].includes(s.spider_name)
                                    );

                                    const uniqueMap = new Map();
                                    individualScrapers.forEach((s: any) => {
                                        const key = s.spider_name.toLowerCase();
                                        const existing = uniqueMap.get(key);
                                        if (!existing || (s.spider_name.match(/[A-Z]/g) || []).length > (existing.spider_name.match(/[A-Z]/g) || []).length) {
                                            uniqueMap.set(key, s);
                                        }
                                    });

                                    return Array.from(uniqueMap.values())
                                        .sort((a, b) => a.spider_name.localeCompare(b.spider_name))
                                        .map((s: any) => {
                                            const status = s.status;
                                            const isActive = status === 'running';
                                            const hasError = status.startsWith('error');

                                            return (
                                                <button
                                                    key={s.spider_name}
                                                    onClick={() => setConfirmScraper(s.spider_name)}
                                                    disabled={isRunning}
                                                    className={`group relative flex items-center justify-between rounded-xl border p-3 transition-all hover:bg-white/5 disabled:opacity-50 min-h-[52px] ${hasError ? 'border-red-500/20 bg-red-500/5' : 'border-white/5 bg-white/[0.02]'}`}
                                                >
                                                    <div className="flex items-center gap-3 overflow-hidden">
                                                        <div className={`flex-shrink-0 h-1.5 w-1.5 rounded-full ${isActive ? 'bg-brand-primary animate-pulse shadow-[0_0_8px_rgba(var(--brand-primary-rgb),0.6)]' : status === 'completed' ? 'bg-green-500/50' : hasError ? 'bg-red-500' : 'bg-white/10'}`}></div>
                                                        <span className="text-[10px] font-black text-white/70 uppercase tracking-tight group-hover:text-white transition-colors truncate">
                                                            {s.spider_name}
                                                        </span>
                                                    </div>
                                                    <Search className={`flex-shrink-0 h-3 w-3 ${isActive ? 'text-brand-primary' : hasError ? 'text-red-400' : 'text-white/10'}`} />
                                                </button>
                                            );
                                        });
                                })()}
                            </div>
                        </div>
                    </div>

                    {/* Compact Execution Logs */}
                    <div className="space-y-4 pt-6 border-t border-white/5">
                        <div className="flex items-center justify-between px-2">
                            <div className="flex items-center gap-2 text-white/30">
                                <History className="h-3.5 w-3.5" />
                                <h3 className="text-[10px] font-black uppercase tracking-widest text-white/40">Bitácora de Incursiones</h3>
                            </div>
                            {isRunning && (
                                <div className="flex items-center gap-2">
                                    <Loader2 className="h-3 w-3 animate-spin text-brand-primary" />
                                    <span className="text-[9px] font-bold text-brand-primary uppercase animate-pulse">Sincronizando...</span>
                                </div>
                            )}
                        </div>

                        <div className="max-h-60 overflow-y-auto rounded-2xl border border-white/5 bg-black/20 custom-scrollbar pr-1">
                            <table className="w-full text-left">
                                <thead className="sticky top-0 z-10 border-b border-white/5 bg-black/80 backdrop-blur-md hidden md:table-header-group">
                                    <tr>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Registro</th>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Hallazgos</th>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5 block md:table-row-group">
                                    {scrapersLogs?.map((log) => (
                                        <tr key={log.id} className="group hover:bg-white/[0.01] transition-colors flex flex-col md:table-row p-3 md:p-0 border-b border-white/5 md:border-none gap-2 md:gap-0">
                                            <td className="px-0 md:px-4 py-1 md:py-3 flex justify-between md:table-cell">
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-black text-white/80 uppercase tracking-tight">{log.spider_name}</span>
                                                    <span className="text-[9px] text-white/20 font-bold">{new Date(log.start_time).toLocaleTimeString()}</span>
                                                </div>
                                                {/* Mobile Status placed here for space efficiency */}
                                                <div className="md:hidden">
                                                    <div className="flex items-center gap-2">
                                                        <div className={`h-1.5 w-1.5 rounded-full ${log.status === 'success' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : log.status === 'running' ? 'bg-orange-500 animate-pulse' : 'bg-red-500'}`}></div>
                                                        <span className={`text-[9px] font-black uppercase ${log.status === 'success' ? 'text-green-500/60' : log.status === 'running' ? 'text-orange-500/60' : 'text-red-500/60'}`}>
                                                            {log.status === 'success' ? 'OK' : log.status === 'running' ? 'WORK' : 'KO'}
                                                        </span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-0 md:px-4 py-1 md:py-3 md:table-cell">
                                                <div className="flex items-center gap-2">
                                                    <Database className="h-3 w-3 text-brand-primary/40" />
                                                    <span className="text-[10px] font-bold text-white/60">{log.items_found} items</span>
                                                </div>
                                            </td>
                                            <td className="px-0 md:px-4 py-1 md:py-3 hidden md:table-cell">
                                                <div className="flex flex-col gap-1">
                                                    <div className="flex items-center gap-2">
                                                        <div className={`h-1 w-1 rounded-full ${log.status === 'success' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : log.status === 'running' ? 'bg-orange-500 animate-pulse' : 'bg-red-500'}`}></div>
                                                        <span className={`text-[9px] font-black uppercase ${log.status === 'success' ? 'text-green-500/60' : log.status === 'running' ? 'text-orange-500/60' : 'text-red-500/60'}`}>
                                                            {log.status === 'success' ? 'OK' : log.status === 'running' ? 'WORK' : 'KO'}
                                                        </span>
                                                        {log.error_message && (
                                                            <AlertCircle className="h-3 w-3 text-red-500/40" />
                                                        )}
                                                    </div>
                                                    {log.error_message && (
                                                        <span className="text-[10px] font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20 max-w-[200px] truncate" title={log.error_message}>
                                                            <AlertCircle className="inline h-3 w-3 mr-1 mb-0.5" />
                                                            {log.error_message}
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            {/* Mobile Error Message */}
                                            {log.error_message && (
                                                <td className="px-0 pb-2 md:hidden max-w-0">
                                                    <div className="w-full overflow-hidden">
                                                        <span className="text-[10px] font-bold text-red-400 bg-red-500/10 px-2 py-1 rounded border border-red-500/20 block w-full truncate" title={log.error_message}>
                                                            {log.error_message}
                                                        </span>
                                                    </div>
                                                </td>
                                            )}
                                        </tr>
                                    ))}
                                    {(!scrapersLogs || scrapersLogs.length === 0) && (
                                        <tr>
                                            <td colSpan={3} className="px-4 py-8 text-center text-[9px] text-white/10 uppercase tracking-widest font-bold">
                                                Sin registros previos
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            {/* Confirmation Modal */}
            {confirmScraper && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
                    <div className="relative w-full max-w-md overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 to-black p-8 shadow-2xl">
                        <div className="flex flex-col items-center gap-6 text-center">
                            <div className="h-16 w-16 rounded-full bg-orange-500/20 flex items-center justify-center border border-orange-500/50">
                                <ShieldAlert className="h-8 w-8 text-orange-400" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="text-2xl font-black text-white uppercase tracking-tight">¿Confirmar Incursión?</h3>
                                <p className="text-sm text-white/50 leading-relaxed">
                                    Estás a punto de desplegar el extractor <span className="text-white font-bold uppercase">"{confirmScraper}"</span>. Esta acción consume recursos de red y actualiza la base de datos.
                                </p>
                            </div>
                            <div className="grid w-full grid-cols-2 gap-4">
                                <button
                                    onClick={() => setConfirmScraper(null)}
                                    className="rounded-2xl border border-white/5 bg-white/5 py-4 text-xs font-black text-white/40 hover:bg-white/10 transition-all uppercase tracking-widest"
                                >
                                    Abortar
                                </button>
                                <button
                                    onClick={() => {
                                        if (confirmScraper) runScrapersMutation.mutate(confirmScraper);
                                        setConfirmScraper(null);
                                    }}
                                    className="rounded-2xl bg-orange-500 py-4 text-xs font-black text-white hover:bg-orange-600 transition-all uppercase tracking-widest shadow-lg shadow-orange-500/20"
                                >
                                    Desplegar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Reset Modal */}
            {confirmReset && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in zoom-in-95 duration-300">
                    <div className="relative w-full max-w-md overflow-hidden rounded-3xl border border-red-500/30 bg-black/80 p-8 shadow-2xl">
                        <div className="flex flex-col items-center gap-6 text-center">
                            <div className="h-16 w-16 rounded-full bg-red-500/20 flex items-center justify-center border border-red-500/50 animate-pulse">
                                <ShieldAlert className="h-8 w-8 text-red-500" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="text-3xl font-black text-white uppercase tracking-tighter">EL GRAN REAJUSTE</h3>
                                <p className="text-sm text-white/50 leading-relaxed">
                                    Esta maniobra desvinculará **todos** los items creados por el algoritmo (SmartMatch) y los devolverá al Purgatorio. <span className="text-red-400 font-bold">Tus capturas manuales no se verán afectadas.</span>
                                </p>
                            </div>
                            <div className="grid w-full grid-cols-2 gap-4">
                                <button
                                    onClick={() => setConfirmReset(false)}
                                    className="rounded-2xl border border-white/5 bg-white/5 py-4 text-xs font-black text-white/40 hover:bg-white/10 transition-all uppercase tracking-widest"
                                >
                                    Abortar
                                </button>
                                <button
                                    onClick={() => resetSmartMatchesMutation.mutate()}
                                    disabled={resetSmartMatchesMutation.isPending}
                                    className="rounded-2xl bg-red-500 py-4 text-xs font-black text-white hover:bg-red-600 transition-all uppercase tracking-widest shadow-lg shadow-red-500/20 disabled:opacity-50"
                                >
                                    {resetSmartMatchesMutation.isPending ? 'PURIFICANDO...' : 'EJECUTAR RESET'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

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
                    pendingItems?.map((item: any) => (
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
                                        <span className={`rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-widest border ${item.shop_name === 'kidinn' ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' : 'bg-white/5 border-white/10 text-white/40'}`}>
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
                                            setSearchTerm('');
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
                                        {item.suggestions && item.suggestions.length > 0 && !searchTerm && (
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
                                                    {item.suggestions.map((s: any) => (
                                                        <button
                                                            key={s.product_id}
                                                            onClick={() => matchMutation.mutate({ pendingId: item.id, productId: s.product_id })}
                                                            className="group/btn relative flex items-center gap-4 overflow-hidden rounded-2xl border border-brand-primary/20 bg-brand-primary/5 p-4 text-left transition-all hover:border-brand-primary hover:bg-brand-primary/10 hover:shadow-[0_0_30px_rgba(var(--brand-primary-rgb),0.15)]"
                                                        >
                                                            {/* Score Ring */}
                                                            <div className="relative h-14 w-14 shrink-0 flex items-center justify-center rounded-full bg-black border-2 border-brand-primary/30 group-hover/btn:border-brand-primary transition-colors">
                                                                <span className="text-xs font-black text-brand-primary">{s.match_score}%</span>
                                                            </div>

                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <span className="px-1.5 py-0.5 rounded bg-brand-primary/20 text-[9px] font-black text-brand-primary uppercase tracking-tighter">
                                                                        {s.reason.toUpperCase()}
                                                                    </span>
                                                                    <span className="text-[9px] font-bold text-white/30 uppercase tracking-widest truncate">{s.sub_category}</span>
                                                                </div>
                                                                <h5 className="text-sm font-bold text-white leading-tight truncate">{s.name}</h5>
                                                                <p className="text-[10px] text-white/40 font-mono mt-0.5">{s.figure_id}</p>
                                                            </div>

                                                            <div className="opacity-0 group-hover/btn:opacity-100 absolute right-4 transition-all transform translate-x-4 group-hover/btn:translate-x-0">
                                                                <CheckCircle2 className="h-6 w-6 text-brand-primary" />
                                                            </div>
                                                        </button>
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
                                                    value={searchTerm}
                                                    onChange={(e) => setSearchTerm(e.target.value)}
                                                />
                                            </div>

                                            {/* Results List */}
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto custom-scrollbar pr-2">
                                                {(searchTerm ? filteredProducts : []).map((p: any) => (
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
                                                {searchTerm && filteredProducts?.length === 0 && (
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
                )}
            </div>

            {/* Bulk Action Bar */}
            {selectedIds.length > 0 && (
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
            )}
        </div>
    );
};

export default Purgatory;
