import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    ShoppingCart,
    Coins,
    ShoppingBag,
    Loader2,
    Zap,
    RotateCcw
} from 'lucide-react';
import { getDashboardStats, getTopDeals, getDashboardHistory, getDashboardMatchStats, revertDashboardAction } from '../api/dashboard';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

const Dashboard: React.FC = () => {
    const queryClient = useQueryClient();

    // Mutations
    const revertMutation = useMutation({
        mutationFn: (id: number) => revertDashboardAction(id),
        onSuccess: (data) => {
            // Invalidate queries to refresh data
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-history'] });
            queryClient.invalidateQueries({ queryKey: ['match-stats'] });
            queryClient.invalidateQueries({ queryKey: ['top-deals'] });
            queryClient.invalidateQueries({ queryKey: ['purgatory-matches'] });
            alert(data.message);
        },
        onError: (error: any) => {
            alert(error.response?.data?.detail || "Error al restaurar justicia");
        }
    });

    // Queries
    const { data: stats, isLoading: isLoadingStats } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: getDashboardStats,
        refetchInterval: 30000 // Refresh every 30s
    });

    const { data: topDeals, isLoading: isLoadingDeals } = useQuery({
        queryKey: ['top-deals'],
        queryFn: () => getTopDeals(2),
        refetchInterval: 60000 // Refresh every minute
    });

    const { data: history, isLoading: isLoadingHistory } = useQuery({
        queryKey: ['dashboard-history'],
        queryFn: getDashboardHistory,
        refetchInterval: 15000 // Refresh every 15s for high reactivity
    });

    const { data: matchStats, isLoading: isLoadingMatchStats } = useQuery({
        queryKey: ['match-stats'],
        queryFn: getDashboardMatchStats,
        refetchInterval: 30000
    });

    if (isLoadingStats || isLoadingDeals || isLoadingHistory || isLoadingMatchStats) {
        return (
            <div className="flex h-[60vh] flex-col items-center justify-center gap-4 text-white/30">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-bold uppercase tracking-widest animate-pulse">Sincronizando Oráculo...</p>
            </div>
        );
    }

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            {/* Hero Section / Welcome */}
            <div className="relative overflow-hidden rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.08] to-transparent p-10 backdrop-blur-3xl">
                <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-brand-primary/10 blur-[100px]"></div>
                <div className="absolute -left-20 -bottom-20 h-96 w-96 rounded-full bg-brand-primary/5 blur-[100px]"></div>

                <div className="relative space-y-2">
                    <div className="flex items-center gap-2 text-brand-primary">
                        <Zap className="h-4 w-4 fill-brand-primary" />
                        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Estado de la Fortaleza</span>
                    </div>
                    <h2 className="text-5xl font-black tracking-tighter text-white lg:text-6xl">
                        Tablero de <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary to-blue-400">Poder</span>
                    </h2>
                    <p className="max-w-xl text-lg text-white/40 font-medium">
                        Bienvenido, Maestro de Armas. Aquí converge la inteligencia de mercaderes lejanos con la gloria de tu colección personal.
                    </p>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {/* Total Manual Matches (Vínculos) */}
                <div className="group relative overflow-hidden rounded-[2rem] border border-white/5 bg-white/[0.03] p-8 transition-all hover:bg-white/[0.05] hover:border-brand-primary/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <Zap className="h-32 w-32 text-brand-primary" />
                    </div>
                    <div className="relative space-y-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-primary/10 border border-brand-primary/20">
                            <Zap className="h-6 w-6 text-brand-primary" />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-white/30">Vínculos Sagrados</p>
                            <h3 className="text-4xl font-black text-white">{stats?.match_count || 0}</h3>
                            <p className="text-xs text-white/20 font-bold">Items asimilados</p>
                        </div>
                    </div>
                </div>

                {/* My Fortress */}
                <div className="group relative overflow-hidden rounded-[2rem] border border-white/5 bg-white/[0.03] p-8 transition-all hover:bg-white/[0.05] hover:border-green-500/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <ShoppingBag className="h-32 w-32 text-green-500" />
                    </div>
                    <div className="relative space-y-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-green-500/10 border border-green-500/20">
                            <ShoppingCart className="h-6 w-6 text-green-500" />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-white/30">Mi Fortaleza</p>
                            <h3 className="text-4xl font-black text-white">{stats?.owned_count}</h3>
                            <p className="text-xs text-white/20 font-bold">Items asegurados</p>
                        </div>
                    </div>
                </div>

                {/* Total Value */}
                <div className="group relative overflow-hidden rounded-[2rem] border border-white/5 bg-white/[0.03] p-8 transition-all hover:bg-white/[0.05] hover:border-orange-500/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <Coins className="h-32 w-32 text-orange-500" />
                    </div>
                    <div className="relative space-y-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-500/10 border border-orange-500/20">
                            <Coins className="h-6 w-6 text-orange-500" />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest text-white/30">Valor Estimado</p>
                            <h3 className="text-4xl font-black text-white">{stats?.total_value} <span className="text-xl opacity-30">€</span></h3>
                            <p className="text-xs text-white/20 font-bold">Patrimonio en reliquias</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Activities & Distribution Section */}
            <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
                {/* Shop Match Counts (Conquistas) */}
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Conquistas por Mercado</h4>
                        <span className="text-[10px] font-bold text-brand-primary">ÉXITO POR TIENDA</span>
                    </div>
                    <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.02] p-8 min-h-[400px]">
                        <div className="grid grid-cols-2 gap-4">
                            {matchStats?.map((item) => (
                                <div key={item.shop} className="flex flex-col gap-1 rounded-2xl bg-white/[0.03] p-4 border border-white/5 group hover:border-brand-primary/20 transition-all">
                                    <span className="text-[9px] font-black uppercase text-white/30 tracking-widest">{item.shop}</span>
                                    <span className="text-2xl font-black text-white group-hover:text-brand-primary transition-colors">{item.count}</span>
                                </div>
                            ))}
                            {(!matchStats || matchStats.length === 0) && (
                                <div className="col-span-2 py-10 text-center text-[10px] font-black uppercase text-white/10 tracking-widest">
                                    Aún no hay conquistas registradas
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Activities Column */}
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Actividad del Oráculo</h4>
                        <span className="text-[10px] font-bold text-white/20">RECIENTE</span>
                    </div>
                    <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.02] p-6 h-[400px] flex flex-col">
                        <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar flex-1">
                            {history?.map((entry) => (
                                <div key={entry.id} className="flex flex-col gap-1.5 rounded-2xl border border-white/5 bg-white/[0.01] p-3 text-xs transition-colors hover:bg-white/[0.03]">
                                    <div className="flex items-center justify-between gap-4">
                                        <div className="flex items-center gap-2">
                                            <div className={`h-1.5 w-1.5 rounded-full ${entry.action_type === 'LINKED_MANUAL' ? 'bg-brand-primary shadow-[0_0_8px_rgba(0,163,255,0.5)]' :
                                                entry.action_type === 'SMART_MATCH' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' :
                                                    entry.action_type === 'UPDATE' ? 'bg-yellow-500' :
                                                        'bg-red-500'
                                                }`}></div>
                                            <div className="space-y-0">
                                                <p className="font-bold text-white/90">
                                                    {entry.action_type === 'LINKED_MANUAL' ? 'Manual: ' :
                                                        entry.action_type === 'SMART_MATCH' ? 'SmartMatch: ' :
                                                            entry.action_type === 'UPDATE' ? 'Update: ' :
                                                                entry.action_type === 'PURGATORY' ? 'A Purgatorio: ' :
                                                                    'Discard: '}
                                                    <span className="text-brand-primary truncate max-w-[120px] inline-block align-bottom">{entry.product_name}</span>
                                                </p>
                                            </div>
                                        </div>
                                        {entry.action_type !== 'PURGATORY' && (
                                            <button
                                                onClick={() => revertMutation.mutate(entry.id)}
                                                disabled={revertMutation.isPending}
                                                className="group/btn relative flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border border-white/5 bg-white/[0.05] transition-all hover:bg-brand-primary/20 hover:border-brand-primary/40 disabled:opacity-30"
                                                title="Revertir"
                                            >
                                                <RotateCcw className={`h-2.5 w-2.5 text-white/40 group-hover/btn:text-brand-primary transition-colors ${revertMutation.isPending ? 'animate-spin' : ''}`} />
                                            </button>
                                        )}
                                    </div>
                                    <div className="flex items-center justify-between text-[8px] font-bold text-white/20 uppercase tracking-tighter">
                                        <span>{entry.shop_name}</span>
                                        <span>{formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true, locale: es })}</span>
                                    </div>
                                </div>
                            ))}
                            {(!history || history.length === 0) && (
                                <div className="flex h-full items-center justify-center py-10 text-center text-[10px] font-black uppercase text-white/10 tracking-widest">
                                    Sin actividad reciente
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Top Deals List Column (Compact - Two Columns) */}
            <div className="lg:col-span-2 space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Oportunidades de Captura</h4>
                        <div className="flex items-center gap-1.5 rounded-full bg-brand-primary/10 px-2 py-0.5 border border-brand-primary/20">
                            <div className="h-1 w-1 rounded-full bg-brand-primary animate-pulse"></div>
                            <span className="text-[8px] font-black text-brand-primary uppercase tracking-tighter">Sin Capturar</span>
                        </div>
                    </div>
                    <span className="text-[10px] font-black text-white/20 uppercase tracking-widest">Top 20 Reliquias</span>
                </div>

                <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.01] overflow-hidden">
                    <div className="max-h-[600px] overflow-y-auto custom-scrollbar-thin">
                        {/* Grid de 2 columnas para el listado */}
                        <div className="grid grid-cols-1 md:grid-cols-2">
                            {topDeals?.map((deal, idx) => (
                                <a
                                    key={deal.id}
                                    href={deal.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={`group flex items-center gap-4 p-4 transition-all hover:bg-white/[0.04] border-white/[0.03] ${
                                        // Lógica de bordes para rejilla de 2 columnas
                                        (idx < topDeals.length - 1) ? 'border-b' : ''
                                        } ${(idx % 2 === 0 && idx < topDeals.length - 1) ? 'md:border-r' : ''}`}
                                >
                                    {/* Mini Thumbnail */}
                                    <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-xl bg-black/40 border border-white/5">
                                        {deal.image_url ? (
                                            <img src={deal.image_url} alt={deal.product_name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                                        ) : (
                                            <div className="flex h-full w-full items-center justify-center bg-brand-primary/5">
                                                <ShoppingBag className="h-5 w-5 text-brand-primary/20" />
                                            </div>
                                        )}
                                    </div>

                                    {/* Info Grid */}
                                    <div className="flex flex-1 items-center justify-between gap-4 overflow-hidden">
                                        <div className="min-w-0 flex-1 space-y-0.5">
                                            <h5 className="truncate text-sm font-bold text-white/90 group-hover:text-brand-primary transition-colors">{deal.product_name}</h5>
                                            <span className="text-[10px] font-black uppercase tracking-widest text-white/20 group-hover:text-white/40">{deal.shop_name}</span>
                                        </div>

                                        <div className="flex items-center gap-4 shrink-0">
                                            <div className="text-right">
                                                <div className="text-sm font-black text-brand-primary">{deal.price} €</div>
                                            </div>
                                            <div className="hidden sm:flex h-7 w-7 items-center justify-center rounded-lg border border-white/5 bg-white/5 opacity-0 group-hover:opacity-100 transition-all transform translate-x-1 group-hover:translate-x-0">
                                                <Zap className="h-2.5 w-2.5 text-brand-primary fill-current" />
                                            </div>
                                        </div>
                                    </div>
                                </a>
                            ))}
                        </div>
                        {(!topDeals || topDeals.length === 0) && (
                            <div className="flex min-h-[400px] flex-col items-center justify-center text-white/10 uppercase tracking-[0.2em] font-black text-[10px]">
                                <ShoppingBag className="mb-4 h-10 w-10 opacity-20" />
                                Nada en el radar, Maestro.
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
