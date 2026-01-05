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
    CheckCircle2
} from 'lucide-react';
import { getPurgatory, matchItem, discardItem, getScrapersStatus, runScrapers } from '../api/purgatory';
import axios from 'axios';

const Purgatory: React.FC = () => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);

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

    const { data: products } = useQuery({
        queryKey: ['products-purgatory'],
        queryFn: async () => {
            const response = await axios.get('http://localhost:8000/api/products');
            return response.data;
        }
    });

    // Mutations
    const runScrapersMutation = useMutation({
        mutationFn: runScrapers,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
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
            setSelectedPendingId(null);
        }
    });

    const isRunning = scrapersStatus?.some(s => s.status === 'running');

    const filteredProducts = products?.filter((p: any) =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.figure_id?.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 10);

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Header / Scraper Control */}
            <div className="relative overflow-hidden rounded-3xl border border-red-500/20 bg-gradient-to-br from-red-500/5 to-black p-8 backdrop-blur-xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-red-500/5 blur-3xl"></div>

                <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-red-500">
                            <Flame className="h-5 w-5" />
                            <span className="text-xs font-black uppercase tracking-widest opacity-70">El Espejo de Eternia</span>
                        </div>
                        <h2 className="text-4xl font-black tracking-tight text-white lg:text-5xl">Purgatorio</h2>
                        <p className="max-w-md text-sm leading-relaxed text-white/50">
                            Reliquias que el SmartMatcher no pudo purificar. Vincula manualmente estos hallazgos al Gran Catálogo.
                        </p>
                    </div>

                    <div className="flex flex-col gap-3">
                        <button
                            onClick={() => runScrapersMutation.mutate()}
                            disabled={isRunning || runScrapersMutation.isPending}
                            className={`flex items-center justify-center gap-3 rounded-2xl px-8 py-4 text-sm font-black transition-all shadow-lg ${isRunning
                                    ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30 animate-pulse'
                                    : 'bg-red-500 text-white hover:bg-red-600 hover:shadow-red-500/20 border border-red-400/50'
                                }`}
                        >
                            {isRunning ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
                            {isRunning ? 'COSECHANDO...' : 'DESPLEGAR RECOLECTORES'}
                        </button>
                        <div className="flex items-center gap-2 px-2">
                            <div className={`h-2 w-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-white/20'}`}></div>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">
                                {isRunning ? 'Sistemas Activos' : 'Sistemas en Reposo'}
                            </span>
                        </div>
                    </div>
                </div>
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
                                        title="Descartar permanentemente"
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
                                    <div className="space-y-4">
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
                                            {filteredProducts?.map((p: any) => (
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
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Purgatory;
