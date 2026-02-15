import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    Zap,
    Euro,
    RotateCcw,
    ShoppingBag,
    Loader2,
    Trash2,
    Link,
    ShoppingCart
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import OracleCart from '../components/cart/OracleCart';
import { getDashboardStats, getTopDeals, getDashboardHistory, getDashboardMatchStats, revertDashboardAction, getHallOfFame } from '../api/dashboard';
import { unlinkOffer, relinkOffer, type Hero } from '../api/admin';
import axios from 'axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import masterRoleImg from '../assets/role-master.png';
import guardianRoleImg from '../assets/role-guardian.png';

interface DashboardProps {
    user: Hero | null;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
    const { addToCart } = useCart();
    const isAdmin = user?.role === 'admin';

    const queryClient = useQueryClient();
    const [selectedRelinkId, setSelectedRelinkId] = React.useState<number | null>(null);
    const [manualSearchTerm, setManualSearchTerm] = React.useState('');
    const [searchResults, setSearchResults] = React.useState<any[]>([]);

    // Mutations
    const revertMutation = useMutation({
        mutationFn: (id: number) => revertDashboardAction(id),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-history'] });
            queryClient.invalidateQueries({ queryKey: ['match-stats'] });
            queryClient.invalidateQueries({ queryKey: ['top-deals'] });
            alert(data.message);
        }
    });

    const unlinkMutation = useMutation({
        mutationFn: (id: number) => unlinkOffer(id),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['top-deals'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-history'] });
            alert(data.message);
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
        }
    });

    // Queries
    const { data: stats, isLoading: isLoadingStats } = useQuery({
        queryKey: ['dashboard-stats', user?.id],
        queryFn: () => getDashboardStats(user?.id || 2),
        refetchInterval: 60000
    });

    const { data: topDeals } = useQuery({
        queryKey: ['top-deals', user?.id],
        queryFn: () => getTopDeals(user?.id || 2),
        refetchInterval: 300000 // 5 min
    });

    const { data: history } = useQuery({
        queryKey: ['dashboard-history', user?.id],
        queryFn: () => getDashboardHistory(user?.id || 2),
        refetchInterval: 60000 // 1 min
    });

    const { data: matchStats } = useQuery({
        queryKey: ['match-stats', user?.id],
        queryFn: () => getDashboardMatchStats(user?.id || 2),
        refetchInterval: 60000
    });

    const { data: hallOfFame } = useQuery({
        queryKey: ['hall-of-fame', user?.id],
        queryFn: () => getHallOfFame(user?.id || 2),
        refetchInterval: 60000
    });

    // Search Logic
    React.useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (manualSearchTerm.length >= 2) {
                try {
                    const response = await axios.get(`/api/products/search?q=${manualSearchTerm}`);
                    setSearchResults(response.data);
                } catch (error) {
                    console.error("Search failed", error);
                }
            } else {
                setSearchResults([]);
            }
        }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [manualSearchTerm]);

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
        <div className="space-y-2 md:space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            {/* Hero Section */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.08] to-transparent py-2 px-3 md:p-6 backdrop-blur-3xl">
                <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
                    <img
                        src={!isAdmin ? guardianRoleImg : masterRoleImg}
                        alt=""
                        className="w-full h-full object-cover blur-2xl scale-125"
                    />
                </div>
                <div className="relative flex flex-col gap-1">
                    <div className="flex items-center gap-2 text-brand-primary">
                        <Zap className="h-3 w-3 fill-brand-primary" />
                        <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                            Tablero de <span className="text-brand-primary">Poder</span>
                        </h2>
                    </div>
                    <p className="max-w-xl text-[11px] md:text-sm text-white/40 font-medium">
                        Bienvenido al Mando Central, <span className="text-white font-bold">{user?.username || (isAdmin ? 'Maestro' : 'Guardián')}</span>. La inteligencia de Nueva Eternia converge.
                    </p>
                </div>
            </div>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-2 gap-3 md:gap-6 md:grid-cols-3">
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-white/[0.03] p-4 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-brand-primary/10 border border-brand-primary/20 shrink-0">
                            <Zap className="h-4 w-4 md:h-5 md:w-5 text-brand-primary" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[7px] md:text-[10px] font-black uppercase tracking-widest text-white/30 mb-1">Vínculos Activos</p>
                            <h3 className="text-sm md:text-3xl font-black text-white">{stats?.total_products || 0}</h3>
                        </div>
                    </div>
                </div>
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-white/[0.03] p-4 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-green-500/10 border border-green-500/20 shrink-0">
                            <ShoppingBag className="h-4 w-4 md:h-5 md:w-5 text-green-500" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[7px] md:text-[10px] font-black uppercase tracking-widest text-white/30 mb-1">Fortaleza</p>
                            <h3 className="text-sm md:text-3xl font-black text-white">{stats?.owned_count || 0}</h3>
                        </div>
                    </div>
                </div>
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-white/[0.03] p-4 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-orange-500/10 border border-orange-500/20 shrink-0">
                            <Euro className="h-4 w-4 md:h-5 md:w-5 text-orange-500" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[7px] md:text-[10px] font-black uppercase tracking-widest text-white/30 mb-1">Valor Venta</p>
                            <h3 className="text-sm md:text-3xl font-black text-white">{(stats?.financial?.market_value || 0).toLocaleString('es-ES')}€</h3>
                        </div>
                    </div>
                </div>
            </div>

            {/* Conditional Content Based on Role */}
            {!isAdmin ? (
                // GUARDIAN VIEW: Custom Order (Oportunidades -> Hall of Fame)
                <div className="space-y-10">
                    <OracleCart />

                    {/* Top Deals Section (Oportunidades de Captura) */}
                    <div className="space-y-4">
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
                                <div className="grid grid-cols-1 md:grid-cols-2 text-white">
                                    {topDeals?.map((deal) => (
                                        <div key={deal.id} className="border-b border-white/[0.03] last:border-0">
                                            <div className={`group flex flex-col transition-all`}>
                                                <div className="flex items-center gap-2 md:gap-3 p-2 md:p-4 hover:bg-white/[0.04]">
                                                    <a href={deal.url} target="_blank" rel="noopener noreferrer" className="relative h-10 w-10 md:h-12 md:w-12 shrink-0 overflow-hidden rounded-xl bg-black/40 border border-white/5">
                                                        {deal.image_url ? (
                                                            <img src={deal.image_url || undefined} alt="" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                                                        ) : (
                                                            <div className="flex h-full w-full items-center justify-center bg-brand-primary/5">
                                                                <ShoppingBag className="h-4 w-4 md:h-5 md:w-5 text-brand-primary/20" />
                                                            </div>
                                                        )}
                                                    </a>

                                                    <div className="flex flex-1 items-center justify-between gap-4 overflow-hidden">
                                                        <div className="min-w-0 flex-1 space-y-0.5">
                                                            <a href={deal.url} target="_blank" rel="noopener noreferrer" className="truncate text-sm font-bold text-white/90 group-hover:text-brand-primary transition-colors block">
                                                                {deal.product_name}
                                                            </a>
                                                            <span className="text-[10px] font-black uppercase tracking-widest text-white/20 group-hover:text-white/40">{deal.shop_name}</span>
                                                        </div>

                                                        <div className="flex items-center gap-3 shrink-0">
                                                            <div className="text-right">
                                                                <div className="text-xs font-black text-brand-primary">{deal.landing_price} € <span className="text-[8px] opacity-40">LANDED</span></div>
                                                                <div className="text-[10px] font-bold text-white/30">{deal.price} € <span className="text-[8px] opacity-50">LIST</span></div>
                                                            </div>
                                                            <button
                                                                onClick={() => addToCart({
                                                                    id: deal.id.toString(),
                                                                    product_name: deal.product_name,
                                                                    shop_name: deal.shop_name,
                                                                    price: deal.price,
                                                                    image_url: deal.image_url
                                                                })}
                                                                className="p-2 rounded-xl bg-white/5 hover:bg-brand-primary/20 text-white/20 hover:text-brand-primary transition-all"
                                                                title="Simular en Oracle Cart"
                                                            >
                                                                <ShoppingCart className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!topDeals || topDeals.length === 0) && (
                                        <div className="col-span-2 py-20 text-center text-white/10 uppercase font-black text-[10px] tracking-widest">Nada en el radar local</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                        {/* Kingdom's Grails */}
                        <div className="relative overflow-hidden rounded-[2.5rem] border border-yellow-500/20 bg-gradient-to-br from-yellow-900/10 to-transparent p-6">
                            <h4 className="text-white font-black text-lg mb-4">Griales del Reino</h4>
                            <div className="space-y-3">
                                {hallOfFame?.top_value?.map((item) => (
                                    <div key={item.id} className="flex items-center gap-3 rounded-xl bg-black/20 p-2 border border-white/5">
                                        <div className="h-10 w-10 shrink-0 overflow-hidden rounded-lg">
                                            <img src={item.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h5 className="truncate text-xs font-bold text-white">{item.name}</h5>
                                            <p className="text-[10px] text-white/40 font-black">{item.market_value}€</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Potencial Oculto */}
                        <div className="relative overflow-hidden rounded-[2.5rem] border border-green-500/20 bg-gradient-to-br from-green-900/10 to-transparent p-6">
                            <h4 className="text-white font-black text-lg mb-4">Potencial Oculto</h4>
                            <div className="space-y-3">
                                {hallOfFame?.top_roi?.map((item) => (
                                    <div key={item.id} className="flex items-center gap-3 rounded-xl bg-black/20 p-2 border border-white/5">
                                        <div className="h-10 w-10 shrink-0 overflow-hidden rounded-lg">
                                            <img src={item.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h5 className="truncate text-xs font-bold text-white">{item.name}</h5>
                                            <p className="text-[10px] text-green-500 font-black">+{item.roi_percentage}%</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                // ADMIN VIEW: Exclusive Operational Sections (Top Deals & Activity)
                <div className="space-y-10">
                    <OracleCart />
                    {/* Admin Horizontal Sections: Conquistas & Actividad */}
                    <div className="space-y-4">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Conquistas de Mercado</h4>
                        <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.02] p-4 md:p-8">
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3 md:gap-4">
                                {matchStats?.map((item) => (
                                    <div key={item.shop} className="flex flex-col gap-1 rounded-2xl bg-white/[0.03] p-3 md:p-4 border border-white/5">
                                        <span className="text-[8px] md:text-[9px] font-black uppercase text-white/30 tracking-widest truncate">{item.shop}</span>
                                        <span className="text-xl md:text-2xl font-black text-white">{item.count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Actividad Logística</h4>
                        <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.02] p-4 md:p-6 h-[300px] overflow-y-auto custom-scrollbar">
                            <div className="space-y-2">
                                {history?.map((entry) => (
                                    <div key={entry.id} className="flex flex-col gap-1.5 rounded-xl border border-white/5 bg-white/[0.01] p-3 text-xs">
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-2">
                                                <div className={`h-1.5 w-1.5 rounded-full ${entry.action_type === 'LINKED_MANUAL' ? 'bg-brand-primary' : 'bg-green-500'}`}></div>
                                                <span className="font-bold text-white/90 truncate max-w-[150px] md:max-w-none">{entry.product_name}</span>
                                            </div>
                                            <button onClick={() => revertMutation.mutate(entry.id)} className="p-1 rounded bg-white/5 hover:bg-white/10 text-white/40">
                                                <RotateCcw className="h-3 w-3" />
                                            </button>
                                        </div>
                                        <div className="flex items-center justify-between text-[8px] font-black text-white/20 uppercase">
                                            <span>{entry.shop_name}</span>
                                            <span>{formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true, locale: es })}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Admin Top Deals (Interactive) - Now at the bottom */}
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Oportunidades Bajo Seguimiento</h4>
                            <span className="text-[10px] font-bold text-brand-primary">MÓDULO DE ACCIÓN</span>
                        </div>
                        <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.01] overflow-hidden">
                            <div className="grid grid-cols-1 md:grid-cols-2">
                                {topDeals?.map((deal, idx) => (
                                    <div key={deal.id} className={`p-4 border-white/[0.03] ${(idx < topDeals.length - 1) ? 'border-b' : ''} ${(idx % 2 === 0 && idx < topDeals.length - 1) ? 'md:border-r' : ''} hover:bg-white/[0.02] transition-all`}>
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-3 min-w-0">
                                                <div className="h-10 w-10 shrink-0 rounded-lg bg-white/5 overflow-hidden">
                                                    <img src={deal.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="truncate text-xs font-bold text-white">{deal.product_name}</p>
                                                    <p className="text-[10px] font-black text-white/20 uppercase">{deal.shop_name} - {deal.price}€</p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => addToCart({
                                                        id: deal.id.toString(),
                                                        product_name: deal.product_name,
                                                        shop_name: deal.shop_name,
                                                        price: deal.price,
                                                        image_url: deal.image_url
                                                    })}
                                                    className="p-2 rounded-lg bg-white/5 text-white/40 hover:bg-brand-primary/20 hover:text-brand-primary transition-all"
                                                    title="Simular en Oracle Cart"
                                                >
                                                    <ShoppingCart className="h-3.5 w-3.5" />
                                                </button>
                                                <button onClick={() => unlinkMutation.mutate(deal.id)} className="p-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all">
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </button>
                                                <button onClick={() => setSelectedRelinkId(selectedRelinkId === deal.id ? null : deal.id)} className="p-2 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white transition-all">
                                                    <Link className="h-3.5 w-3.5" />
                                                </button>
                                            </div>
                                        </div>

                                        {/* Relink Drawer */}
                                        {selectedRelinkId === deal.id && (
                                            <div className="mt-4 space-y-3 bg-black/40 p-3 rounded-xl border border-white/5 animate-in slide-in-from-top-2">
                                                <input
                                                    type="text"
                                                    placeholder="Buscar reliquia para vincular..."
                                                    className="w-full rounded-lg bg-white/5 border border-white/10 p-2 text-xs text-white"
                                                    value={manualSearchTerm}
                                                    onChange={(e) => setManualSearchTerm(e.target.value)}
                                                />
                                                <div className="max-h-32 overflow-y-auto space-y-1">
                                                    {searchResults?.map((p) => (
                                                        <button key={p.id} onClick={() => relinkMutation.mutate({ offerId: deal.id, productId: p.id })} className="w-full text-left p-2 text-[10px] text-white/60 hover:text-white hover:bg-white/5 rounded transition-colors">
                                                            {p.name}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
