import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    Zap,
    Euro,
    RotateCcw,
    ShoppingBag,
    Trash2,
    Link,
    ShoppingCart,
    Target,
    Award,
    X,
    Layers,
    Shield
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import OracleCart from '../components/cart/OracleCart';
import { getDashboardStats, getTopDeals, getDashboardHistory, revertDashboardAction, getHallOfFame } from '../api/dashboard';
import { unlinkOffer, relinkOffer, type Hero } from '../api/admin';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import axios from 'axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { parseUtcDate } from '../utils/dateUtils';
import masterRoleImg from '../assets/role-master.webp';
import guardianRoleImg from '../assets/role-guardian.webp';
import { MOTUImage } from '../components/ui/MOTUImage';

// Recharts & Collection API Imports for Arsenal Analytics & Completitud
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip as RechartsTooltip
} from 'recharts';
import { getCollection, type Product } from '../api/collection';

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
    const [showOpportunitiesModal, setShowOpportunitiesModal] = React.useState(false);

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
        refetchInterval: 300000 // 5 min
    });

    const { data: topDeals } = useQuery({
        queryKey: ['top-deals', user?.id],
        queryFn: () => getTopDeals(user?.id || 2),
        refetchInterval: 600000 // 10 min
    });

    const { data: history } = useQuery({
        queryKey: ['dashboard-history', user?.id],
        queryFn: () => getDashboardHistory(user?.id || 2),
        refetchInterval: 300000 // 5 min
    });

    const { data: hallOfFame } = useQuery({
        queryKey: ['hall-of-fame', user?.id],
        queryFn: () => getHallOfFame(user?.id || 2),
        refetchInterval: 300000 // 5 min
    });

    const activeUserId = user?.id || 2;

    // Queries to support Pareto features (Completitud + Arsenal Analytics)
    const { data: modernProducts } = useQuery<Product[]>({
        queryKey: ['products', false],
        queryFn: async () => {
            const response = await axios.get('/api/products?is_vintage=false');
            return response.data;
        }
    });

    const { data: vintageProducts } = useQuery<Product[]>({
        queryKey: ['products', true],
        queryFn: async () => {
            const response = await axios.get('/api/products?is_vintage=true');
            return response.data;
        }
    });

    const { data: modernCollection } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId, false],
        queryFn: () => getCollection(activeUserId, false)
    });

    const { data: vintageCollection } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId, true],
        queryFn: () => getCollection(activeUserId, true)
    });

    // Memos for calculations
    const groups = useMemo(() => {
        if (!modernProducts && !vintageProducts) return [];
        const prodList = [...(modernProducts || []), ...(vintageProducts || [])];
        const collList = [...(modernCollection || []), ...(vintageCollection || [])];
        const ownedIds = new Set(collList.filter(c => !c.is_wish).map(c => c.id));

        const map: Record<string, { total: number; owned: number; missing: Product[]; isVintage: boolean }> = {};
        prodList.forEach(p => {
            const sub = p.sub_category || 'Otros';
            if (!map[sub]) {
                map[sub] = { total: 0, owned: 0, missing: [], isVintage: !!p.is_vintage };
            }
            map[sub].total++;
            if (ownedIds.has(p.id)) {
                map[sub].owned++;
            } else {
                map[sub].missing.push(p);
            }
            if (p.is_vintage) {
                map[sub].isVintage = true;
            }
        });

        return Object.entries(map)
            .map(([name, data]) => ({
                name,
                total: data.total,
                owned: data.owned,
                percentage: data.total > 0 ? (data.owned / data.total) * 100 : 0,
                missing: data.missing,
                isVintage: data.isVintage
            }))
            .filter(g => g.total > 0)
            .sort((a, b) => b.percentage - a.percentage);
    }, [modernProducts, vintageProducts, modernCollection, vintageCollection]);

    const conditionData = useMemo(() => {
        const collList = [...(modernCollection || []), ...(vintageCollection || [])].filter(c => !c.is_wish);
        const counts: Record<string, { count: number; value: number }> = {
            MOC: { count: 0, value: 0 },
            Loose: { count: 0, value: 0 },
            New: { count: 0, value: 0 }
        };

        collList.forEach(item => {
            let cond = (item.condition || 'MOC').trim();
            if (cond.toUpperCase() === 'NEW') cond = 'New';
            else if (cond.toUpperCase() === 'LOOSE') cond = 'Loose';
            else cond = 'MOC';

            const basePrice = item.market_value || item.avg_market_price || 0;
            let condMult = 1.0;
            if (cond === 'New') condMult = 0.75;
            else if (cond === 'Loose') condMult = 0.5;

            const grad = item.grading !== undefined ? item.grading : 10.0;
            const gradFactor = Math.max(0.10, 1.0 - ((10.0 - grad) * 0.04));
            const adjustedPrice = basePrice * condMult * gradFactor;

            counts[cond].count++;
            counts[cond].value += adjustedPrice;
        });

        return Object.entries(counts)
            .map(([name, data]) => ({
                name,
                value: data.count,
                estimatedValue: data.value
            }))
            .filter(d => d.value > 0);
    }, [modernCollection, vintageCollection]);

    const COLORS = {
        MOC: '#10b981',   // Emerald
        New: '#0ea5e9',   // Cyan
        Loose: '#a8a29e'  // Slate Gray
    };

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
        return <PowerSwordLoader variant="fullScreen" text="Sintonizando el Orbe de Grayskull..." />;
    }

    return (
        <div className="space-y-2 md:space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            {/* Hero Section */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/50 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
                    <img
                        src={!isAdmin ? guardianRoleImg : masterRoleImg}
                        alt=""
                        className="w-full h-full object-cover blur-2xl scale-125"
                    />
                </div>
                <div className="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Zap className="h-3 w-3" />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                Orbe de <span className="text-brand-primary">Grayskull</span>
                            </h2>
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium">
                            Bienvenido al Orbe de Grayskull, <span className="text-white font-bold">{user?.username || (isAdmin ? 'Maestro' : 'Guardián')}</span>. La inteligencia de Nueva Eternia converge.
                        </p>
                    </div>
                </div>
            </div>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-3 gap-1.5 md:gap-6">
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-black/50 backdrop-blur-md p-2 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-brand-primary/10 border border-brand-primary/20 shrink-0">
                            <Zap className="h-3.5 w-3.5 md:h-5 md:w-5 text-brand-primary" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-white/60 mb-0.5 md:mb-1">Vínculos Activos</p>
                            <h3 className="text-xs xs:text-sm md:text-3xl font-black text-white">{stats?.total_products || 0}</h3>
                        </div>
                    </div>
                </div>
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-black/50 backdrop-blur-md p-2 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-green-500/10 border border-green-500/20 shrink-0">
                            <ShoppingBag className="h-3.5 w-3.5 md:h-5 md:w-5 text-green-500" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-white/60 mb-0.5 md:mb-1">Fortaleza</p>
                            <h3 className="text-xs xs:text-sm md:text-3xl font-black text-white blur-incognito">{stats?.owned_count || 0}</h3>
                        </div>
                    </div>
                </div>
                <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-white/5 bg-black/50 backdrop-blur-md p-2 md:p-5">
                    <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                        <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-orange-500/10 border border-orange-500/20 shrink-0">
                            <Euro className="h-3.5 w-3.5 md:h-5 md:w-5 text-orange-500" />
                        </div>
                        <div className="text-center md:text-left">
                            <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-white/60 mb-0.5 md:mb-1">Valor Venta</p>
                            <h3 className="text-xs xs:text-sm md:text-3xl font-black text-white blur-incognito">{(stats?.financial?.market_value || 0).toLocaleString('es-ES')}€</h3>
                        </div>
                    </div>
                </div>
            </div>

            {/* Vintage Metrics Ribbon (Gold/Amber Theme) */}
            {stats && (stats.total_products_vintage > 0 || stats.owned_count_vintage > 0) && (
                <div className="grid grid-cols-3 gap-1.5 md:gap-6 mt-4">
                    {/* Vínculos Activos Vintage */}
                    <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-amber-500/15 bg-amber-950/10 backdrop-blur-md p-2 md:p-5 shadow-[0_0_15px_-5px_rgba(245,158,11,0.1)]">
                        <div className={`absolute -right-10 -top-10 h-24 w-24 rounded-full bg-amber-500/5 blur-2xl pointer-events-none`}></div>
                        <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                            <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-amber-500/10 border border-amber-500/20 shrink-0">
                                <Zap className="h-3.5 w-3.5 md:h-5 md:w-5 text-amber-500 fill-amber-500" />
                            </div>
                            <div className="text-center md:text-left">
                                <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-amber-500/60 mb-0.5 md:mb-1">Vínculos Vintage</p>
                                <h3 className="text-xs xs:text-sm md:text-3xl font-black text-amber-500">{stats?.total_products_vintage || 0}</h3>
                            </div>
                        </div>
                    </div>
                    {/* Fortaleza Vintage */}
                    {stats.owned_count_vintage > 0 && (
                        <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-amber-500/15 bg-amber-950/10 backdrop-blur-md p-2 md:p-5 shadow-[0_0_15px_-5px_rgba(245,158,11,0.1)]">
                            <div className={`absolute -right-10 -top-10 h-24 w-24 rounded-full bg-amber-500/5 blur-2xl pointer-events-none`}></div>
                            <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                                <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-amber-500/10 border border-amber-500/20 shrink-0">
                                    <ShoppingBag className="h-3.5 w-3.5 md:h-5 md:w-5 text-amber-500" />
                                </div>
                                <div className="text-center md:text-left">
                                    <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-amber-500/60 mb-0.5 md:mb-1">Fortaleza Vintage</p>
                                    <h3 className="text-xs xs:text-sm md:text-3xl font-black text-amber-500 blur-incognito">{stats?.owned_count_vintage || 0}</h3>
                                </div>
                            </div>
                        </div>
                    )}
                    {/* Valor Venta Vintage */}
                    {stats.owned_count_vintage > 0 && (
                        <div className="group relative overflow-hidden rounded-xl md:rounded-2xl border border-amber-500/15 bg-amber-950/10 backdrop-blur-md p-2 md:p-5 shadow-[0_0_15px_-5px_rgba(245,158,11,0.1)]">
                            <div className={`absolute -right-10 -top-10 h-24 w-24 rounded-full bg-amber-500/5 blur-2xl pointer-events-none`}></div>
                            <div className="relative flex flex-col items-center md:items-start gap-1 md:gap-3">
                                <div className="flex h-7 w-7 md:h-10 md:w-10 items-center justify-center rounded-lg md:rounded-xl bg-amber-500/10 border border-amber-500/20 shrink-0">
                                    <Euro className="h-3.5 w-3.5 md:h-5 md:w-5 text-amber-500" />
                                </div>
                                <div className="text-center md:text-left">
                                    <p className="text-[6px] xs:text-[8px] md:text-[10px] font-black uppercase tracking-widest text-amber-500/60 mb-0.5 md:mb-1">Valor Vintage</p>
                                    <h3 className="text-xs xs:text-sm md:text-3xl font-black text-amber-500 blur-incognito">{(stats?.financial_vintage?.market_value || 0).toLocaleString('es-ES')}€</h3>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Salón de la Fama (Griales) - Renderizado Inline */}
            <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-brand-primary animate-pulse" />
                    <h4 className="text-xs font-black uppercase tracking-widest text-white/65">Salón de la Fama (Joyas de la Corona)</h4>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* CATEGORÍA ORIGINS (MODERNO) */}
                    <div className="relative overflow-hidden rounded-2xl md:rounded-[2.5rem] border border-brand-primary/10 bg-black/60 backdrop-blur-md p-5 md:p-6 shadow-[0_0_20px_-5px_rgba(0,163,255,0.05)] animate-in fade-in duration-500">
                        <div className="absolute top-0 right-0 h-24 w-24 rounded-full bg-brand-primary/5 blur-2xl pointer-events-none"></div>
                        
                        <div className="flex items-center gap-2 mb-4">
                            <span className="flex h-6 w-6 items-center justify-center rounded bg-brand-primary/10 text-brand-primary">
                                <Zap className="h-3.5 w-3.5 fill-current" />
                            </span>
                            <h4 className="text-white font-black text-xs md:text-sm uppercase tracking-wider">Colección Origins <span className="text-brand-primary text-[10px]">(Moderna)</span></h4>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Top Valor Origins */}
                            <div className="space-y-2">
                                <h5 className="text-[9px] font-black uppercase tracking-widest text-white/60">Mayores Reliquias (Valor)</h5>
                                <div className="space-y-2">
                                    {hallOfFame?.origins?.top_value?.map((item) => (
                                        <div key={item.id} className="group flex items-center gap-2.5 rounded-xl bg-white/[0.02] p-2 border border-white/5 hover:border-brand-primary/20 hover:bg-white/[0.04] transition-all duration-300">
                                            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-lg bg-black/40">
                                                <MOTUImage productId={item.id} src={item.image_url || undefined} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h5 className="truncate text-[11px] font-bold text-white/95 group-hover:text-brand-primary transition-colors">{item.name}</h5>
                                                <div className="flex items-center justify-between text-[9px] font-black text-white/60">
                                                    <span>PVP: <span className="blur-incognito">{item.invested_value || item.purchase_price || 0}€</span></span>
                                                    <span className="text-white font-black blur-incognito">{item.market_value}€</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!hallOfFame?.origins?.top_value || hallOfFame.origins.top_value.length === 0) && (
                                        <div className="py-8 text-center text-white/60 uppercase font-black text-[8px] tracking-widest bg-white/[0.01] rounded-xl border border-white/5">Sin griales en colección</div>
                                    )}
                                </div>
                            </div>

                            {/* Top ROI Origins */}
                            <div className="space-y-2">
                                <h5 className="text-[9px] font-black uppercase tracking-widest text-white/60">Mayor Retorno (ROI)</h5>
                                <div className="space-y-2">
                                    {hallOfFame?.origins?.top_roi?.map((item) => (
                                        <div key={item.id} className="group flex items-center gap-2.5 rounded-xl bg-white/[0.02] p-2 border border-white/5 hover:border-brand-primary/20 hover:bg-white/[0.04] transition-all duration-300">
                                            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-lg bg-black/40">
                                                <MOTUImage productId={item.id} src={item.image_url || undefined} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h5 className="truncate text-[11px] font-bold text-white/95 group-hover:text-brand-primary transition-colors">{item.name}</h5>
                                                <div className="flex items-center justify-between text-[9px] font-black text-white/60">
                                                    <span>ROI: <span className="text-green-500 font-black blur-incognito">+{item.roi_percentage || item.roi || 0}%</span></span>
                                                    <span className="text-white font-black blur-incognito">{item.market_value}€</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!hallOfFame?.origins?.top_roi || hallOfFame.origins.top_roi.length === 0) && (
                                        <div className="py-8 text-center text-white/60 uppercase font-black text-[8px] tracking-widest bg-white/[0.01] rounded-xl border border-white/5">Sin revalorizaciones</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* CATEGORÍA VINTAGE (RETRO) */}
                    <div className="relative overflow-hidden rounded-2xl md:rounded-[2.5rem] border border-amber-500/10 bg-black/60 backdrop-blur-md p-5 md:p-6 shadow-[0_0_20px_-5px_rgba(245,158,11,0.05)] animate-in fade-in duration-500">
                        <div className="absolute top-0 right-0 h-24 w-24 rounded-full bg-amber-500/5 blur-2xl pointer-events-none"></div>
                        
                        <div className="flex items-center gap-2 mb-4">
                            <span className="flex h-6 w-6 items-center justify-center rounded bg-amber-500/10 text-amber-500">
                                <Zap className="h-3.5 w-3.5 fill-amber-500" />
                            </span>
                            <h4 className="text-white font-black text-xs md:text-sm uppercase tracking-wider">Colección Vintage <span className="text-amber-500 text-[10px]">(Retro 80s)</span></h4>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Top Valor Vintage */}
                            <div className="space-y-2">
                                <h5 className="text-[9px] font-black uppercase tracking-widest text-amber-500/60">Mayores Reliquias (Valor)</h5>
                                <div className="space-y-2">
                                    {hallOfFame?.vintage?.top_value?.map((item) => (
                                        <div key={item.id} className="group flex items-center gap-2.5 rounded-xl bg-white/[0.02] p-2 border border-white/5 hover:border-amber-500/20 hover:bg-white/[0.04] transition-all duration-300">
                                            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-lg bg-black/40">
                                                <MOTUImage productId={item.id} src={item.image_url || undefined} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h5 className="truncate text-[11px] font-bold text-white/95 group-hover:text-amber-500 transition-colors">{item.name}</h5>
                                                <div className="flex items-center justify-between text-[9px] font-black text-white/60">
                                                    <span>Original: <span className="blur-incognito">{item.invested_value || item.purchase_price || 0}€</span></span>
                                                    <span className="text-amber-500 font-extrabold blur-incognito">{item.market_value}€</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!hallOfFame?.vintage?.top_value || hallOfFame.vintage.top_value.length === 0) && (
                                        <div className="py-8 text-center text-white/60 uppercase font-black text-[8px] tracking-widest bg-white/[0.01] rounded-xl border border-white/5">Sin griales en colección</div>
                                    )}
                                </div>
                            </div>

                            {/* Top ROI Vintage */}
                            <div className="space-y-2">
                                <h5 className="text-[9px] font-black uppercase tracking-widest text-amber-500/60">Mayor Retorno (ROI)</h5>
                                <div className="space-y-2">
                                    {hallOfFame?.vintage?.top_roi?.map((item) => (
                                        <div key={item.id} className="group flex items-center gap-2.5 rounded-xl bg-white/[0.02] p-2 border border-white/5 hover:border-amber-500/20 hover:bg-white/[0.04] transition-all duration-300">
                                            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-lg bg-black/40">
                                                <MOTUImage productId={item.id} src={item.image_url || undefined} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h5 className="truncate text-[11px] font-bold text-white/95 group-hover:text-amber-500 transition-colors">{item.name}</h5>
                                                <div className="flex items-center justify-between text-[9px] font-black text-white/60">
                                                    <span>ROI: <span className="text-green-500 font-black blur-incognito">+{item.roi_percentage || item.roi || 0}%</span></span>
                                                    <span className="text-amber-500 font-extrabold blur-incognito">{(item.market_value)}€</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {(!hallOfFame?.vintage?.top_roi || hallOfFame.vintage.top_roi.length === 0) && (
                                        <div className="py-8 text-center text-white/60 uppercase font-black text-[8px] tracking-widest bg-white/[0.01] rounded-xl border border-white/5">Sin revalorizaciones</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Pareto features: Completitud and Donut Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                {/* Arsenal Analytics: Donut Chart */}
                <div className="relative overflow-hidden rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/60 backdrop-blur-md p-5 md:p-6 shadow-2xl flex flex-col justify-between">
                    <div className="absolute top-0 right-0 h-24 w-24 rounded-full bg-brand-primary/5 blur-2xl pointer-events-none"></div>
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="flex h-6 w-6 items-center justify-center rounded bg-brand-primary/10 text-brand-primary">
                                <Shield className="h-3.5 w-3.5 fill-current" />
                            </span>
                            <h4 className="text-white font-black text-xs md:text-sm uppercase tracking-wider">Estado de la Fortaleza</h4>
                        </div>
                        
                        {conditionData.length === 0 ? (
                            <div className="py-12 text-center text-white/45 uppercase font-bold text-[10px] tracking-widest bg-white/[0.01] rounded-2xl border border-white/5">
                                Registra figuras en tu colección para ver analíticas de conservación
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
                                {/* Pie Chart */}
                                <div className="h-44 w-full relative flex items-center justify-center">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={conditionData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={50}
                                                outerRadius={75}
                                                paddingAngle={4}
                                                dataKey="value"
                                            >
                                                {conditionData.map((entry) => (
                                                    <Cell 
                                                        key={`cell-${entry.name}`} 
                                                        fill={COLORS[entry.name as keyof typeof COLORS] || '#fff'} 
                                                    />
                                                ))}
                                            </Pie>
                                            <RechartsTooltip
                                                content={({ active, payload }) => {
                                                    if (active && payload && payload.length) {
                                                        const data = payload[0].payload;
                                                        return (
                                                            <div className="glass p-2.5 rounded-xl border border-white/10 text-[10px] bg-black/95">
                                                                <p className="font-black text-white uppercase tracking-wider mb-1">{data.name}</p>
                                                                <p className="text-white/60">Cantidad: <span className="font-black text-brand-primary blur-incognito">{data.value}</span></p>
                                                                <p className="text-white/60">Valor Est.: <span className="font-black text-emerald-400 blur-incognito">{data.estimatedValue.toFixed(2)}€</span></p>
                                                            </div>
                                                        );
                                                    }
                                                    return null;
                                                }}
                                            />
                                        </PieChart>
                                    </ResponsiveContainer>
                                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                        <span className="text-[9px] font-black uppercase text-white/35 tracking-wider leading-none">Total</span>
                                        <span className="text-xl font-black text-white blur-incognito">
                                            {conditionData.reduce((acc, curr) => acc + curr.value, 0)}
                                        </span>
                                    </div>
                                </div>

                                {/* Custom Legend */}
                                <div className="space-y-2">
                                    {conditionData.map((entry) => {
                                        const totalCount = conditionData.reduce((acc, curr) => acc + curr.value, 0);
                                        const pct = totalCount > 0 ? (entry.value / totalCount) * 100 : 0;
                                        const color = COLORS[entry.name as keyof typeof COLORS] || '#fff';
                                        
                                        return (
                                            <div key={entry.name} className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.02] border border-white/5">
                                                <div className="flex items-center gap-2">
                                                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }}></span>
                                                    <span className="text-[10px] font-black uppercase tracking-wider text-white/70">{entry.name}</span>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-[10px] font-black text-white blur-incognito">{entry.value} uds. ({pct.toFixed(0)}%)</div>
                                                    <div className="text-[9px] font-medium text-emerald-400 blur-incognito">{entry.estimatedValue.toFixed(2)}€</div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Hordas de Completitud: Wave Progress */}
                <div className="relative overflow-hidden rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/60 backdrop-blur-md p-5 md:p-6 shadow-2xl flex flex-col justify-between">
                    <div className="absolute top-0 right-0 h-24 w-24 rounded-full bg-brand-primary/5 blur-2xl pointer-events-none"></div>
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="flex h-6 w-6 items-center justify-center rounded bg-brand-primary/10 text-brand-primary">
                                <Layers className="h-3.5 w-3.5 fill-current" />
                            </span>
                            <h4 className="text-white font-black text-xs md:text-sm uppercase tracking-wider">Regimientos del Destino (Completitud)</h4>
                        </div>
                        
                        {groups.length === 0 ? (
                            <div className="py-12 text-center text-white/45 uppercase font-bold text-[10px] tracking-widest bg-white/[0.01] rounded-2xl border border-white/5">
                                Sincronizando catálogo para calcular las hordas...
                            </div>
                        ) : (
                            <div className="space-y-4 max-h-[175px] overflow-y-auto pr-1 custom-scrollbar">
                                {groups.map(group => (
                                    <div key={group.name} className="space-y-1.5">
                                        <div className="flex justify-between items-baseline">
                                            <span className="text-[10px] font-black uppercase tracking-wider text-white/80">
                                                {group.name}
                                            </span>
                                            <span className={`text-[9px] font-black uppercase tracking-widest blur-incognito ${group.isVintage ? 'text-amber-500' : 'text-brand-primary'}`}>
                                                {group.owned} / {group.total} ({group.percentage.toFixed(0)}%)
                                            </span>
                                        </div>
                                        
                                        {/* Progress Bar Container */}
                                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/[0.03]">
                                            <div 
                                                className={`h-full rounded-full transition-all duration-500 bg-gradient-to-r ${
                                                    group.isVintage
                                                        ? 'from-amber-500 to-amber-300'
                                                        : 'from-brand-primary to-cyan-400'
                                                }`}
                                                style={{ width: `${group.percentage}%` }}
                                            />
                                        </div>

                                        {/* Missing Figures List (Inline Pareto suggestion) */}
                                        {group.missing.length > 0 && (
                                            <div className="text-[8px] text-white/40 leading-normal font-bold uppercase tracking-wider truncate">
                                                Falta: {group.missing.slice(0, 3).map(m => m.name).join(', ')}
                                                {group.missing.length > 3 && ` y ${group.missing.length - 3} más...`}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Dashboard Workspace */}
            <div className="space-y-4 md:space-y-6 mt-6">
                {/* Botón Destacado: Radar de Oportunidades */}
                <button
                    onClick={() => setShowOpportunitiesModal(true)}
                    className="w-full flex items-center justify-center gap-3 rounded-2xl border border-brand-primary/20 bg-brand-primary/10 hover:bg-brand-primary/20 p-6 text-brand-primary transition-all duration-300 shadow-lg hover:scale-[1.01] active:scale-[0.99]"
                >
                    <Target className="h-7 w-7 text-brand-primary animate-pulse" />
                    <div className="text-left">
                        <span className="block text-[10px] font-black uppercase tracking-widest text-brand-primary/70">Radar de Capturas y Simulaciones</span>
                        <span className="text-sm font-bold text-white">Radar de Oportunidades</span>
                    </div>
                </button>

                {/* Logistics Console (Only for Admin) - Rendered at the absolute bottom */}
                {isAdmin && (
                    <div className="space-y-4 pt-4 border-t border-white/5">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/65">Actividad Logística</h4>
                        <div className="rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/25 backdrop-blur-md p-4 md:p-6 h-[300px] overflow-y-auto custom-scrollbar">
                            <div className="space-y-2">
                                {history?.map((entry) => (
                                    <div key={entry.id} className="flex flex-col gap-1.5 rounded-xl border border-white/5 bg-white/[0.01] p-3 text-xs">
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-2">
                                                <div className={`h-1.5 w-1.5 rounded-full ${entry.action_type === 'LINKED_MANUAL' ? 'bg-brand-primary' : 'bg-green-500'}`}></div>
                                                <span className="font-bold text-white/90 truncate max-w-[150px] md:max-w-none">{entry.product_name}</span>
                                            </div>
                                            <button 
                                                onClick={() => {
                                                    if (confirm("⚠️ ¿Estás seguro de que deseas revertir esta acción logística? Esta operación restaurará la oferta al Purgatorio.")) {
                                                        revertMutation.mutate(entry.id);
                                                    }
                                                }} 
                                                className="p-1 rounded bg-white/5 hover:bg-white/10 text-white/65"
                                            >
                                                <RotateCcw className="h-3 w-3" />
                                            </button>
                                        </div>
                                        <div className="flex items-center justify-between text-[8px] font-black text-white/60 uppercase">
                                            <span>{entry.shop_name}</span>
                                            <span>{formatDistanceToNow(parseUtcDate(entry.timestamp), { addSuffix: true, locale: es })}</span>
                                        </div>
                                    </div>
                                ))}
                                {(!history || history.length === 0) && (
                                    <div className="py-20 text-center text-white/60 uppercase font-black text-[10px] tracking-widest">Sin actividad registrada</div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* OVERLAY MODAL: Oportunidades */}
            {showOpportunitiesModal && (
                <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/90 backdrop-blur-xl p-2 md:p-10 animate-in fade-in duration-300">
                    <div className="relative w-full max-w-7xl rounded-[3rem] border border-white/10 bg-gradient-to-br from-white/[0.05] to-transparent overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
                        {/* Header */}
                        <div className="p-6 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Target className="h-6 w-6 text-brand-primary" />
                                <h3 className="text-white font-black text-lg uppercase tracking-wider">
                                    {isAdmin ? 'Oportunidades Bajo Seguimiento' : 'Oportunidades de Captura'}
                                </h3>
                            </div>
                            <button 
                                onClick={() => {
                                    setShowOpportunitiesModal(false);
                                    setSelectedRelinkId(null);
                                }} 
                                className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                <X className="h-5 w-5 text-white/70" />
                            </button>
                        </div>

                        {/* List content */}
                        <div className="flex-1 overflow-y-auto p-4 md:p-6 custom-scrollbar space-y-6">
                            {/* Carrito Ficticio Integrado Verticalmente en la parte superior */}
                            <div className="border-b border-white/10 pb-6 mb-6">
                                <OracleCart />
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-xs font-black uppercase tracking-widest text-brand-primary flex items-center gap-2">
                                    <Target className="h-4 w-4" />
                                    {isAdmin ? 'Oportunidades de Capturas Bajo Seguimiento' : 'Oportunidades de Captura'}
                                </h4>

                                {!isAdmin ? (
                                    // Guardian view
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-white">
                                        {topDeals?.map((deal) => (
                                            <div key={deal.id} className="border-b border-white/[0.03] last:border-0 hover:bg-white/[0.02] p-4 rounded-2xl transition-all">
                                                <div className="flex items-center gap-3">
                                                    <a href={deal.url} target="_blank" rel="noopener noreferrer" className="relative h-12 w-12 shrink-0 overflow-hidden rounded-xl bg-black/40 border border-white/5">
                                                        {deal.image_url ? (
                                                            <MOTUImage productId={deal.product_id} src={deal.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                                        ) : (
                                                            <div className="flex h-full w-full items-center justify-center bg-brand-primary/5">
                                                                <ShoppingBag className="h-5 w-5 text-brand-primary/20" />
                                                            </div>
                                                        )}
                                                    </a>

                                                    <div className="flex flex-1 items-center justify-between gap-4 overflow-hidden">
                                                        <div className="min-w-0 flex-1 space-y-0.5">
                                                            <a href={deal.url} target="_blank" rel="noopener noreferrer" className="truncate text-sm font-bold text-white/95 hover:text-brand-primary transition-colors block">
                                                                {deal.product_name}
                                                            </a>
                                                            <span className="text-[10px] font-black uppercase tracking-widest text-white/60">{deal.shop_name}</span>
                                                        </div>

                                                        <div className="flex items-center gap-3 shrink-0">
                                                            <div className="text-right">
                                                                <div className="text-xs font-black text-brand-primary">{deal.landing_price} € <span className="text-[8px] opacity-40">LANDED</span></div>
                                                                <div className="text-[10px] font-bold text-white/60">{deal.price} € <span className="text-[8px] opacity-50">LIST</span></div>
                                                            </div>
                                                            <button
                                                                onClick={() => addToCart({
                                                                    id: deal.id.toString(),
                                                                    product_name: deal.product_name,
                                                                    shop_name: deal.shop_name,
                                                                    price: deal.price,
                                                                    image_url: deal.image_url
                                                                })}
                                                                className="p-2 rounded-xl bg-white/5 hover:bg-brand-primary/20 text-white/70 hover:text-brand-primary transition-all"
                                                                title="Simular en Oracle Cart"
                                                            >
                                                                <ShoppingCart className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                        {(!topDeals || topDeals.length === 0) && (
                                            <div className="col-span-2 py-20 text-center text-white/60 uppercase font-black text-[10px] tracking-widest">Nada en el radar local</div>
                                        )}
                                    </div>
                                ) : (
                                    // Admin view
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {topDeals?.map((deal) => (
                                            <div key={deal.id} className="p-4 border border-white/5 bg-white/[0.01] hover:bg-white/[0.02] rounded-2xl transition-all">
                                                <div className="flex items-center justify-between gap-4">
                                                    <div className="flex items-center gap-3 min-w-0">
                                                        <a href={deal.url} target="_blank" rel="noopener noreferrer" className="h-10 w-10 shrink-0 rounded-lg bg-white/5 overflow-hidden block">
                                                            <MOTUImage productId={deal.product_id} src={deal.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                                        </a>
                                                        <div className="min-w-0">
                                                            <a href={deal.url} target="_blank" rel="noopener noreferrer" className="truncate text-xs font-bold text-white block hover:text-brand-primary transition-colors">{deal.product_name}</a>
                                                            <p className="text-[10px] font-black text-white/60 uppercase">{deal.shop_name} - {deal.price}€</p>
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
                                                            className="p-2 rounded-lg bg-white/5 text-white/70 hover:bg-brand-primary/20 hover:text-brand-primary transition-all"
                                                            title="Simular en Oracle Cart"
                                                        >
                                                            <ShoppingCart className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button 
                                                            onClick={() => {
                                                                if (confirm("⚠️ ¿Estás seguro de que deseas desvincular esta oferta del seguimiento? Volverá al estado sin procesar en el Purgatorio.")) {
                                                                    unlinkMutation.mutate(deal.id);
                                                                }
                                                            }} 
                                                            className="p-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                                                            title="Desvincular"
                                                        >
                                                            <Trash2 className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button 
                                                            onClick={() => setSelectedRelinkId(selectedRelinkId === deal.id ? null : deal.id)} 
                                                            className="p-2 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white transition-all"
                                                            title="Re-vincular"
                                                        >
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
                                                                <button 
                                                                    key={p.id} 
                                                                    onClick={() => relinkMutation.mutate({ offerId: deal.id, productId: p.id })} 
                                                                    className="w-full text-left p-2 text-[10px] text-white/70 hover:text-white hover:bg-white/5 rounded transition-colors"
                                                                >
                                                                    {p.name}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                        {(!topDeals || topDeals.length === 0) && (
                                            <div className="col-span-2 py-20 text-center text-white/60 uppercase font-black text-[10px] tracking-widest">Nada en el radar local</div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
