import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    ShoppingCart,
    Coins,
    ShoppingBag,
    Loader2,
    Zap,
    RotateCcw,
    Trophy,
    TrendingUp,
    Euro,
    ExternalLink,
    Copy,
    Trash2,
    Link,
    Search,
    CheckCircle2
} from 'lucide-react';
import { getDashboardStats, getTopDeals, getDashboardHistory, getDashboardMatchStats, revertDashboardAction, getHallOfFame } from '../api/dashboard';
import { unlinkOffer, relinkOffer } from '../api/admin';
import axios from 'axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import masterRoleImg from '../assets/role-master.png';
import guardianRoleImg from '../assets/role-guardian.png';

const Dashboard: React.FC = () => {
    const queryClient = useQueryClient();
    const [selectedRelinkId, setSelectedRelinkId] = React.useState<number | null>(null);
    const [manualSearchTerm, setManualSearchTerm] = React.useState('');

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

    const unlinkMutation = useMutation({
        mutationFn: (id: number) => unlinkOffer(id),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['top-deals'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-history'] });
            alert(data.message);
        },
        onError: (error: any) => {
            alert(error.response?.data?.detail || "Error al desvincular reliquia");
        }
    });

    const relinkMutation = useMutation({
        mutationFn: ({ offerId, productId }: { offerId: number, productId: number }) => relinkOffer(offerId, productId),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['top-deals'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-history'] });
            setSelectedRelinkId(null);
            setManualSearchTerm('');
            alert(data.message);
        },
        onError: (error: any) => {
            alert(error.response?.data?.detail || "Error al reasignar reliquia");
        }
    });

    // Queries
    const { data: stats, isLoading: isLoadingStats } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: getDashboardStats,
        refetchInterval: 60000 // Refresh every 60s (Relaxed)
    });

    const { data: topDeals } = useQuery({
        queryKey: ['top-deals'],
        queryFn: () => getTopDeals(),
        refetchInterval: 120000 // Refresh every 2 mins
    });

    const { data: history } = useQuery({
        queryKey: ['dashboard-history'],
        queryFn: getDashboardHistory,
        refetchInterval: 30000 // Refresh every 30s
    });

    const { data: matchStats } = useQuery({
        queryKey: ['match-stats'],
        queryFn: getDashboardMatchStats,
        refetchInterval: 60000 // Refresh every 60s
    });

    const { data: hallOfFame } = useQuery({
        queryKey: ['hall-of-fame'],
        queryFn: getHallOfFame,
        refetchInterval: 60000
    });

    const [searchResults, setSearchResults] = React.useState<any[]>([]);
    const [isSearching, setIsSearching] = React.useState(false);

    // Búsqueda Atómica Reactiva (Fase 34)
    React.useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (manualSearchTerm.length >= 2) {
                setIsSearching(true);
                try {
                    const response = await axios.get(`/api/products/search?q=${manualSearchTerm}`);
                    setSearchResults(response.data);
                } catch (error) {
                    console.error("Search failed", error);
                } finally {
                    setIsSearching(false);
                }
            } else {
                setSearchResults([]);
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [manualSearchTerm]);

    const isAdmin = true; // Hardcoded for now, could be dynamic

    if (isLoadingStats) {
        return (
            <div className="flex h-[60vh] flex-col items-center justify-center gap-4 text-white/30">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <div className="space-y-1 text-center">
                    <p className="text-sm font-bold uppercase tracking-widest animate-pulse">Sincronizando Oráculo...</p>
                    <p className="text-[10px] text-white/10 uppercase font-black">Conjugando fuerzas del mercado</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            {/* Hero Section / Welcome */}
            <div className="relative overflow-hidden rounded-[2rem] md:rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.08] to-transparent p-6 md:p-10 backdrop-blur-3xl">
                {/* Role Background Layer */}
                <div className="absolute inset-0 z-0 opacity-20 pointer-events-none overflow-hidden mt-[-10%] ml-[-5%] w-[110%] h-[120%]">
                    <img
                        src={localStorage.getItem('active_user_id') === '2' ? guardianRoleImg : masterRoleImg}
                        alt=""
                        className="w-full h-full object-cover blur-2xl scale-125 transition-transform duration-1000"
                    />
                </div>

                <div className="absolute -right-20 -top-20 h-64 w-64 md:h-96 md:w-96 rounded-full bg-brand-primary/10 blur-[100px]"></div>
                <div className="absolute -left-20 -bottom-20 h-64 w-64 md:h-96 md:w-96 rounded-full bg-brand-primary/5 blur-[100px]"></div>

                <div className="relative space-y-2">
                    <div className="flex items-center gap-2 text-brand-primary">
                        <Zap className="h-3 w-3 md:h-4 md:w-4 fill-brand-primary" />
                        <span className="text-[8px] md:text-[10px] font-black uppercase tracking-[0.3em]">Estado de la Fortaleza</span>
                    </div>
                    <h2 className="text-3xl md:text-5xl lg:text-6xl font-black tracking-tighter text-white">
                        Tablero de <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary to-blue-400">Poder</span>
                    </h2>
                    <p className="max-w-xl text-sm md:text-lg text-white/40 font-medium leading-relaxed">
                        Bienvenido, Maestro. La inteligencia de mercaderes converge con tu gloria personal.
                    </p>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {/* Total Manual Matches (Vínculos) */}
                <div className="group relative overflow-hidden rounded-3xl md:rounded-[2rem] border border-white/5 bg-white/[0.03] p-5 md:p-8 transition-all hover:bg-white/[0.05] hover:border-brand-primary/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <Zap className="h-24 w-24 md:h-32 md:w-32 text-brand-primary" />
                    </div>
                    <div className="relative space-y-3 md:space-y-4">
                        <div className="flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-2xl bg-brand-primary/10 border border-brand-primary/20">
                            <Zap className="h-5 w-5 md:h-6 md:w-6 text-brand-primary" />
                        </div>
                        <div>
                            <p className="text-[10px] md:text-xs font-black uppercase tracking-widest text-white/30">Vínculos Sagrados</p>
                            <h3 className="text-3xl md:text-4xl font-black text-white">{stats?.match_count || 0}</h3>
                            <p className="text-[10px] md:text-xs text-white/20 font-bold">Items asimilados</p>
                        </div>
                    </div>
                </div>

                {/* My Fortress */}
                <div className="group relative overflow-hidden rounded-3xl md:rounded-[2rem] border border-white/5 bg-white/[0.03] p-5 md:p-8 transition-all hover:bg-white/[0.05] hover:border-green-500/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <ShoppingBag className="h-24 w-24 md:h-32 md:w-32 text-green-500" />
                    </div>
                    <div className="relative space-y-3 md:space-y-4">
                        <div className="flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-2xl bg-green-500/10 border border-green-500/20">
                            <ShoppingCart className="h-5 w-5 md:h-6 md:w-6 text-green-500" />
                        </div>
                        <div>
                            <p className="text-[10px] md:text-xs font-black uppercase tracking-widest text-white/30">Mi Fortaleza</p>
                            <h3 className="text-3xl md:text-4xl font-black text-white">{stats?.owned_count}</h3>
                            <p className="text-[10px] md:text-xs text-white/20 font-bold">Items asegurados</p>
                        </div>
                    </div>
                </div>

                {/* Financial Performance (ROI Engine) */}
                <div className="group relative overflow-hidden rounded-3xl md:rounded-[2rem] border border-white/5 bg-white/[0.03] p-5 md:p-8 transition-all hover:bg-white/[0.05] hover:border-orange-500/20">
                    <div className="absolute -right-4 -top-4 opacity-10 transition-transform group-hover:scale-110">
                        <Coins className="h-24 w-24 md:h-32 md:w-32 text-orange-500" />
                    </div>
                    <div className="relative space-y-3 md:space-y-4">
                        <div className="flex items-start justify-between">
                            <div className="flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-2xl bg-orange-500/10 border border-orange-500/20">
                                <Zap className="h-5 w-5 md:h-6 md:w-6 text-orange-500" />
                            </div>
                            <div className={`flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-black border ${(stats?.financial?.profit_loss || 0) >= 0
                                ? 'bg-green-500/10 text-green-500 border-green-500/20'
                                : 'bg-red-500/10 text-red-500 border-red-500/20'
                                }`}>
                                {(stats?.financial?.profit_loss || 0) >= 0 ? '+' : ''}{stats?.financial?.roi}% ROI
                            </div>
                        </div>

                        <div>
                            <p className="text-[10px] md:text-xs font-black uppercase tracking-widest text-white/30">Valor de Mercado</p>
                            <h3 className="text-3xl md:text-4xl font-black text-white">
                                {stats?.financial?.market_value} <span className="text-lg md:text-xl opacity-30">€</span>
                            </h3>

                            <div className="mt-2 flex flex-col md:flex-row md:items-center gap-1 md:gap-4 text-[10px] md:text-xs font-medium">
                                <div className="text-white/40">
                                    Inv: <span className="text-white/60">{stats?.financial?.total_invested} €</span>
                                </div>
                                <div className={`${(stats?.financial?.profit_loss || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                    {(stats?.financial?.profit_loss || 0) >= 0 ? 'Ganancia: ' : 'Pérdida: '}
                                    <span className="font-bold">{(stats?.financial?.profit_loss || 0) >= 0 ? '+' : ''}{stats?.financial?.profit_loss} €</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Visionary Section: Hall of Fame */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                {/* Kingdom's Grails (Top Value) */}
                <div className="relative overflow-hidden rounded-[2.5rem] border border-yellow-500/20 bg-gradient-to-br from-yellow-900/10 to-transparent p-8">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-yellow-500/10 border border-yellow-500/20">
                                <Trophy className="h-5 w-5 text-yellow-500" />
                            </div>
                            <div>
                                <h4 className="text-white font-black text-lg leading-none">Griales del Reino</h4>
                                <p className="text-[10px] font-bold text-yellow-500/60 uppercase tracking-widest mt-1">Activos más valiosos</p>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {hallOfFame?.top_value?.map((item, idx: number) => (
                            <div key={item.id} className="group flex items-center gap-4 rounded-2xl bg-black/20 p-3 border border-white/5 transition-all hover:bg-yellow-500/5 hover:border-yellow-500/20">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-yellow-500/20 font-black text-yellow-500 text-sm border border-yellow-500/10">
                                    {idx + 1}
                                </div>
                                <div className="h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-white/5">
                                    {item.image_url && <img src={item.image_url} alt={item.name} className="h-full w-full object-cover" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h5 className="truncate text-sm font-bold text-white group-hover:text-yellow-400 transition-colors">{item.name}</h5>
                                    <div className="flex items-center gap-2 mt-0.5">
                                        <div className="flex items-center gap-1 text-xs font-black text-white/40">
                                            <span>Inv: {item.invested_value}€</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="flex items-center justify-end gap-1 text-yellow-500 font-black text-lg">
                                        <Euro className="h-4 w-4" />
                                        {item.market_value}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {(!hallOfFame?.top_value?.length) && (
                            <div className="text-center py-8 text-white/20 text-xs italic">
                                La Sala del Trono está vacía...
                            </div>
                        )}
                    </div>
                </div>

                {/* Hidden Potential (Top ROI) */}
                <div className="relative overflow-hidden rounded-[2.5rem] border border-green-500/20 bg-gradient-to-br from-green-900/10 to-transparent p-8">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-500/10 border border-green-500/20">
                                <TrendingUp className="h-5 w-5 text-green-500" />
                            </div>
                            <div>
                                <h4 className="text-white font-black text-lg leading-none">Potencial Oculto</h4>
                                <p className="text-[10px] font-bold text-green-500/60 uppercase tracking-widest mt-1">Mayor crecimiento</p>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {hallOfFame?.top_roi?.map((item) => (
                            <div key={item.id} className="group flex items-center gap-4 rounded-2xl bg-black/20 p-3 border border-white/5 transition-all hover:bg-green-500/5 hover:border-green-500/20">
                                <div className="h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-white/5">
                                    {item.image_url && <img src={item.image_url} alt={item.name} className="h-full w-full object-cover" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h5 className="truncate text-sm font-bold text-white group-hover:text-green-400 transition-colors">{item.name}</h5>
                                    <div className="flex items-center gap-1 mt-0.5 text-[10px] font-bold uppercase text-white/30">
                                        Mercado: {item.market_value}€
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="inline-flex items-center gap-1 rounded-lg bg-green-500/10 px-2.5 py-1 text-sm font-black text-green-500 border border-green-500/20">
                                        +{item.roi_percentage}%
                                    </div>
                                </div>
                            </div>
                        ))}
                        {(!hallOfFame?.top_roi?.length) && (
                            <div className="text-center py-8 text-white/20 text-xs italic">
                                El potencial aún duerme...
                            </div>
                        )}
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
                                        <div className="flex items-center gap-2">
                                            {/* Link to Source */}
                                            {entry.offer_url?.toLowerCase().includes('wallapop.com') ? (
                                                <button
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(entry.offer_url);
                                                        alert("URL de Wallapop copiada al portapapeles");
                                                    }}
                                                    className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
                                                    title="Copiar URL (Wallapop)"
                                                >
                                                    <Copy className="h-3 w-3" />
                                                </button>
                                            ) : (
                                                <a
                                                    href={entry.offer_url}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
                                                    title="Ver Fuente Original"
                                                >
                                                    <ExternalLink className="h-3 w-3" />
                                                </a>
                                            )}

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
                                <div
                                    key={deal.id}
                                    className={`group flex flex-col transition-all border-white/[0.03] ${
                                        // Lógica de bordes para rejilla de 2 columnas
                                        (idx < topDeals.length - 1) ? 'border-b' : ''
                                        } ${(idx % 2 === 0 && idx < topDeals.length - 1) ? 'md:border-r' : ''}`}
                                >
                                    <div className="flex items-center gap-4 p-4 hover:bg-white/[0.04]">
                                        <a
                                            href={deal.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="relative h-12 w-12 shrink-0 overflow-hidden rounded-xl bg-black/40 border border-white/5"
                                        >
                                            {deal.image_url ? (
                                                <img src={deal.image_url} alt={deal.product_name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                                            ) : (
                                                <div className="flex h-full w-full items-center justify-center bg-brand-primary/5">
                                                    <ShoppingBag className="h-5 w-5 text-brand-primary/20" />
                                                </div>
                                            )}
                                        </a>

                                        {/* Info Grid */}
                                        <div className="flex flex-1 items-center justify-between gap-4 overflow-hidden">
                                            <div className="min-w-0 flex-1 space-y-0.5">
                                                <a
                                                    href={deal.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="truncate text-sm font-bold text-white/90 group-hover:text-brand-primary transition-colors block"
                                                >
                                                    {deal.product_name}
                                                </a>
                                                <span className="text-[10px] font-black uppercase tracking-widest text-white/20 group-hover:text-white/40">{deal.shop_name}</span>
                                            </div>

                                            <div className="flex items-center gap-3 shrink-0">
                                                <div className="text-right">
                                                    <div className="text-sm font-black text-brand-primary">{deal.price} €</div>
                                                </div>

                                                {isAdmin && (
                                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all">
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                e.preventDefault();
                                                                if (confirm(`¿Devolver '${deal.product_name}' al Purgatorio?`)) {
                                                                    unlinkMutation.mutate(deal.id);
                                                                }
                                                            }}
                                                            disabled={unlinkMutation.isPending}
                                                            className="h-7 w-7 flex items-center justify-center rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition-all relative z-20"
                                                            title="Devolver al Purgatorio"
                                                        >
                                                            <Trash2 className="h-3 w-3" />
                                                        </button>
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                e.preventDefault();
                                                                setSelectedRelinkId(selectedRelinkId === deal.id ? null : deal.id);
                                                                setManualSearchTerm('');
                                                            }}
                                                            className={`h-7 w-7 flex items-center justify-center rounded-lg border transition-all relative z-20 ${selectedRelinkId === deal.id ? 'bg-white text-black border-white' : 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary hover:bg-brand-primary hover:text-white'}`}
                                                            title="Vincular a otro producto"
                                                        >
                                                            <Link className="h-3 w-3" />
                                                        </button>
                                                    </div>
                                                )}

                                                <div className="hidden sm:flex h-7 w-7 items-center justify-center rounded-lg border border-white/5 bg-white/5 opacity-0 group-hover:opacity-100 transition-all transform translate-x-1 group-hover:translate-x-0">
                                                    <Zap className="h-2.5 w-2.5 text-brand-primary fill-current" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Relink Drawer */}
                                    {selectedRelinkId === deal.id && (
                                        <div className="border-t border-white/10 bg-brand-primary/[0.03] p-4 space-y-4 animate-in slide-in-from-top-2">
                                            <div className="flex items-center gap-2">
                                                <div className="h-6 w-6 rounded-full bg-white/10 flex items-center justify-center">
                                                    <Search className="h-3 w-3 text-white/50" />
                                                </div>
                                                <h6 className="text-[10px] font-black text-white uppercase tracking-widest">Reasignar Reliquia</h6>
                                            </div>

                                            <input
                                                type="text"
                                                placeholder="Buscar nuevo producto..."
                                                className="w-full rounded-xl bg-black/40 border border-white/10 py-2.5 px-4 text-xs font-bold text-white outline-none focus:border-brand-primary/50 transition-all"
                                                value={manualSearchTerm}
                                                autoFocus
                                                onChange={(e) => setManualSearchTerm(e.target.value)}
                                            />

                                            <div className="grid grid-cols-1 gap-1 max-h-40 overflow-y-auto custom-scrollbar-thin">
                                                {isSearching && (
                                                    <div className="py-4 text-center">
                                                        <Loader2 className="h-4 w-4 animate-spin text-brand-primary mx-auto" />
                                                    </div>
                                                )}
                                                {searchResults?.map((p: any) => (
                                                    <button
                                                        key={p.id}
                                                        onClick={() => relinkMutation.mutate({ offerId: deal.id, productId: p.id })}
                                                        className="flex items-center justify-between gap-3 rounded-lg bg-white/5 p-2.5 text-left hover:bg-brand-primary/10 hover:border-brand-primary/30 border border-transparent transition-all group/res"
                                                    >
                                                        <div className="min-w-0 flex-1">
                                                            <div className="text-[11px] font-bold text-white truncate">{p.name}</div>
                                                            <div className="text-[8px] font-black text-white/20 uppercase tracking-tighter">{p.figure_id}</div>
                                                        </div>
                                                        <CheckCircle2 className="h-3.5 w-3.5 text-brand-primary opacity-0 group-hover/res:opacity-100 transition-opacity" />
                                                    </button>
                                                ))}
                                                {manualSearchTerm.length >= 2 && !isSearching && searchResults?.length === 0 && (
                                                    <div className="py-4 text-center text-[10px] font-bold text-white/20">Sin resultados</div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                        {(!topDeals || topDeals.length === 0) && (
                            <div className="flex min-h-[400px] flex-col items-center justify-center text-white/10 uppercase tracking-[0.2em] font-black text-[10px]">
                                <ShoppingBag className="mb-4 h-10 w-10 opacity-20" />
                                <span className="opacity-50">Nada en el radar, Maestro.</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
