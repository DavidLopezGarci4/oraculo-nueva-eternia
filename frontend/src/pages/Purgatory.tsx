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
    AlertCircle
} from 'lucide-react';
import { getPurgatory, matchItem, discardItem, getScrapersStatus, runScrapers, getScraperLogs, resetSmartMatches } from '../api/purgatory';
import axios from 'axios';

const Purgatory: React.FC = () => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);
    const [confirmScraper, setConfirmScraper] = useState<string | null>(null);
    const [confirmReset, setConfirmReset] = useState(false);

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
            const response = await axios.get('http://localhost:8000/api/products');
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
        }
    });

    const matchMutation = useMutation({
        mutationFn: ({ pendingId, productId }: { pendingId: number, productId: number }) =>
            matchItem(pendingId, productId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedPendingId(null);
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
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Header / Scraper Control Panel */}
            <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.05] to-black p-8 backdrop-blur-xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/5 blur-3xl"></div>

                <div className="relative space-y-8">
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-brand-primary">
                                <Flame className="h-5 w-5" />
                                <span className="text-xs font-black uppercase tracking-widest opacity-70">El Espejo de Eternia</span>
                            </div>
                            <h2 className="text-4xl font-black tracking-tight text-white lg:text-5xl">Purgatorio</h2>
                            <p className="max-w-md text-sm leading-relaxed text-white/50">
                                Gestiona las reliquias que necesitan vinculación manual y despliega incursiones a las tierras lejanas.
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

                    {/* Scraper Grid */}
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
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

                        {/* Individual Spiders */}
                        {['actiontoys', 'fantasia', 'frikiverso', 'electropolis', 'pixelatoy', 'amazon', 'dvdstorespain', 'kidinn'].map(shop => {
                            const status = scrapersStatus?.find((s: any) => s.spider_name === shop)?.status;
                            const isActive = status === 'running';
                            return (
                                <button
                                    key={shop}
                                    onClick={() => setConfirmScraper(shop)}
                                    disabled={isRunning}
                                    className="group relative flex flex-col gap-3 rounded-2xl border border-white/5 bg-white/[0.02] p-4 transition-all hover:bg-white/5 disabled:opacity-50"
                                >
                                    <div className="flex items-center justify-between">
                                        <Search className={`h-4 w-4 ${isActive ? 'text-brand-primary' : 'text-white/20'}`} />
                                        <div className={`h-1.5 w-1.5 rounded-full ${isActive ? 'bg-brand-primary animate-pulse' : status === 'completed' ? 'bg-green-500/50' : 'bg-white/5'}`}></div>
                                    </div>
                                    <div className="space-y-1 text-left">
                                        <p className="text-[10px] font-black uppercase tracking-tighter text-white/20">Background Spider</p>
                                        <p className="text-xs font-bold text-white/70 uppercase truncate">{shop}</p>
                                    </div>
                                </button>
                            );
                        })}
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
                                <thead className="sticky top-0 z-10 border-b border-white/5 bg-black/80 backdrop-blur-md">
                                    <tr>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Registro</th>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Hallazgos</th>
                                        <th className="px-4 py-3 text-[9px] font-black uppercase tracking-widest text-white/20">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {scrapersLogs?.map((log) => (
                                        <tr key={log.id} className="group hover:bg-white/[0.01] transition-colors">
                                            <td className="px-4 py-3">
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-black text-white/80 uppercase tracking-tight">{log.spider_name}</span>
                                                    <span className="text-[9px] text-white/20 font-bold">{new Date(log.start_time).toLocaleTimeString()}</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <Database className="h-3 w-3 text-brand-primary/40" />
                                                    <span className="text-[10px] font-bold text-white/60">{log.items_found} items</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
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
                        <div key={item.id} className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/[0.02] p-4 transition-all hover:bg-white/[0.04] hover:border-white/10">
                            <div className="flex flex-col gap-6 md:flex-row md:items-center">
                                {/* Thumbnail */}
                                <div className="h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-black/40 border border-white/5">
                                    {item.image_url ? (
                                        <img src={item.image_url} alt={item.scraped_name} className="h-full w-full object-cover p-1" />
                                    ) : (
                                        <div className="flex h-full w-full items-center justify-center text-[10px] text-white/10 uppercase font-black">No img</div>
                                    )}
                                </div>

                                {/* Info */}
                                <div className="flex-1 space-y-2">
                                    <div className="flex items-center gap-2">
                                        <span className="rounded bg-white/5 px-2 py-0.5 text-[10px] font-black text-white/40 uppercase tracking-tighter border border-white/10">
                                            {item.shop_name}
                                        </span>
                                        <span className="text-[10px] text-white/20 font-bold">
                                            {new Date(item.found_at).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <h3 className="text-sm font-bold text-white/90 leading-tight">{item.scraped_name}</h3>
                                    <div className="flex items-center gap-4">
                                        <span className="text-lg font-black text-white">{item.price} {item.currency}</span>
                                        <a href={item.url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[10px] font-bold text-brand-primary hover:underline">
                                            Ver Original <ExternalLink className="h-3 w-3" />
                                        </a>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex shrink-0 items-center gap-3">
                                    <button
                                        onClick={() => discardMutation.mutate(item.id)}
                                        className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all transition-all"
                                    >
                                        <Trash2 className="h-5 w-5" />
                                    </button>
                                    <button
                                        onClick={() => setSelectedPendingId(selectedPendingId === item.id ? null : item.id)}
                                        className={`flex items-center gap-2 rounded-xl px-6 py-2.5 text-xs font-black transition-all ${selectedPendingId === item.id
                                            ? 'bg-brand-primary text-white'
                                            : 'bg-brand-primary/10 text-brand-primary border border-brand-primary/20 hover:bg-brand-primary/20'
                                            }`}
                                    >
                                        <Link className="h-4 w-4" />
                                        {selectedPendingId === item.id ? 'CANCELAR' : 'VINCULAR'}
                                    </button>
                                </div>
                            </div>

                            {/* Matcher Drawer (condicional) */}
                            {selectedPendingId === item.id && (
                                <div className="mt-4 animate-in slide-in-from-top-4 duration-300 border-t border-white/5 pt-4">
                                    <div className="space-y-6">
                                        {/* Sugerencias del Oráculo */}
                                        {item.suggestions && item.suggestions.length > 0 && !searchTerm && (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-2 text-brand-primary">
                                                    <Zap className="h-4 w-4" />
                                                    <span className="text-[10px] font-black uppercase tracking-widest">Sugerencias del Oráculo</span>
                                                </div>
                                                <div className="grid grid-cols-1 gap-2">
                                                    {item.suggestions.map((s: any) => (
                                                        <button
                                                            key={s.product_id}
                                                            onClick={() => matchMutation.mutate({ pendingId: item.id, productId: s.product_id })}
                                                            className="flex items-center justify-between rounded-xl bg-brand-primary/5 border border-brand-primary/20 p-4 text-left hover:bg-brand-primary/10 transition-all group/suggestion"
                                                        >
                                                            <div className="flex items-center gap-4">
                                                                <div className="flex flex-col items-center justify-center h-10 w-12 rounded-lg bg-brand-primary/20 border border-brand-primary/30">
                                                                    <span className="text-[14px] font-black text-brand-primary leading-none">{s.match_score}%</span>
                                                                    <span className="text-[8px] font-black text-brand-primary/60 uppercase">Score</span>
                                                                </div>
                                                                <div>
                                                                    <div className="text-xs font-black text-white group-hover/suggestion:text-brand-primary transition-colors">{s.name}</div>
                                                                    <div className="text-[10px] text-white/30 uppercase font-bold">{s.sub_category} • {s.figure_id}</div>
                                                                </div>
                                                            </div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-[9px] font-black text-white/10 uppercase tracking-widest mr-2">{s.reason}</span>
                                                                <div className="flex h-8 items-center gap-2 rounded-lg bg-brand-primary px-3 text-[10px] font-black text-white shadow-lg shadow-brand-primary/20 opacity-0 group-hover/suggestion:opacity-100 transition-all translate-x-1 group-hover/suggestion:translate-x-0">
                                                                    CONFIRMAR VÍNCULO <CheckCircle2 className="h-3 w-3" />
                                                                </div>
                                                            </div>
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Buscador Manual */}
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2 text-white/20">
                                                <Search className="h-4 w-4" />
                                                <span className="text-[10px] font-black uppercase tracking-widest">Búsqueda Manual</span>
                                            </div>
                                            <div className="relative">
                                                <Search className="absolute left-3 top-2.5 h-4 w-4 text-white/20" />
                                                <input
                                                    type="text"
                                                    placeholder="Buscar producto en el Gran Catálogo..."
                                                    className="w-full rounded-xl bg-black/40 border border-white/10 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-white/20 outline-none focus:border-brand-primary/50"
                                                    autoFocus
                                                    value={searchTerm}
                                                    onChange={(e) => setSearchTerm(e.target.value)}
                                                />
                                            </div>

                                            <div className="grid grid-cols-1 gap-2 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                                                {(searchTerm ? filteredProducts : []).map((p: any) => (
                                                    <button
                                                        key={p.id}
                                                        onClick={() => matchMutation.mutate({ pendingId: item.id, productId: p.id })}
                                                        className="flex items-center justify-between rounded-lg bg-white/5 p-3 text-left hover:bg-brand-primary/10 border border-transparent hover:border-brand-primary/20 transition-all group/match"
                                                    >
                                                        <div className="flex items-center gap-3">
                                                            <div className="h-8 w-8 rounded bg-white/10 flex items-center justify-center text-[10px] font-black text-white/40">
                                                                {p.figure_id}
                                                            </div>
                                                            <div>
                                                                <div className="text-xs font-bold text-white/90">{p.name}</div>
                                                                <div className="text-[10px] text-white/30 uppercase">{p.sub_category}</div>
                                                            </div>
                                                        </div>
                                                        <div className="hidden group-hover/match:flex items-center gap-1.5 text-[10px] font-black text-brand-primary">
                                                            CONFIRMAR <CheckCircle2 className="h-3.5 w-3.5" />
                                                        </div>
                                                    </button>
                                                ))}
                                                {searchTerm && filteredProducts?.length === 0 && (
                                                    <div className="py-8 text-center text-xs text-white/20">
                                                        No se encontraron reliquias con ese nombre.
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
        </div>
    );
};

export default Purgatory;
