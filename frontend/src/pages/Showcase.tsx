import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    Globe,
    Award,
    Compass,
    Lock,
    Search,
    TrendingUp
} from 'lucide-react';
import { getPublicShowcase } from '../api/admin';
import { getOptimizedImageUrl } from '../utils/imageUtils';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';

interface ShowcaseProps {
    username: string;
}

const getAdjustedValue = (item: any) => {
    const baseValue = item.product.avg_market_price || item.product.p25_price || 0;
    const cond = item.condition || 'New';
    const grad = item.grading !== undefined ? item.grading : 10.0;
    
    let condMult = 0.75;
    if (cond.toUpperCase() === 'MOC') condMult = 1.0;
    else if (cond.toUpperCase() === 'LOOSE') condMult = 0.5;

    const gradFactor = Math.max(0.10, 1.0 - ((10.0 - grad) * 0.04));
    return baseValue * condMult * gradFactor;
};

const Showcase: React.FC<ShowcaseProps> = ({ username }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [categoryFilter, setCategoryFilter] = useState<'all' | 'modern' | 'vintage'>('all');
    const [subCategoryFilter, setSubCategoryFilter] = useState<string>('all');

    const { data: showcaseData, isLoading, isError, error } = useQuery({
        queryKey: ['publicShowcase', username],
        queryFn: () => getPublicShowcase(username),
        retry: 1
    });

    const items = showcaseData?.items || [];

    // Extract unique subcategories
    const subCategories = useMemo(() => {
        const subs = new Set<string>();
        items.forEach((item: any) => {
            if (item.product.sub_category) {
                subs.add(item.product.sub_category);
            }
        });
        return Array.from(subs).sort();
    }, [items]);

    // Filtered items
    const filteredItems = useMemo(() => {
        return items.filter((item: any) => {
            const query = searchQuery.toLowerCase();
            const matchesSearch = 
                item.product.name.toLowerCase().includes(query) ||
                (item.product.variant_name && item.product.variant_name.toLowerCase().includes(query)) ||
                (item.product.sub_category && item.product.sub_category.toLowerCase().includes(query));
            
            const isVintage = !!item.product.is_vintage;
            const matchesCategory = 
                categoryFilter === 'all' ||
                (categoryFilter === 'modern' && !isVintage) ||
                (categoryFilter === 'vintage' && isVintage);

            const matchesSub = 
                subCategoryFilter === 'all' ||
                item.product.sub_category === subCategoryFilter;

            return matchesSearch && matchesCategory && matchesSub;
        });
    }, [items, searchQuery, categoryFilter, subCategoryFilter]);

    // Statistics
    const stats = useMemo(() => {
        let totalValue = 0;
        let vintageCount = 0;
        let modernCount = 0;

        items.forEach((item: any) => {
            totalValue += getAdjustedValue(item);
            if (item.product.is_vintage) {
                vintageCount++;
            } else {
                modernCount++;
            }
        });

        return {
            totalValue,
            vintageCount,
            modernCount,
            totalCount: items.length
        };
    }, [items]);

    if (isLoading) {
        return <PowerSwordLoader variant="fullScreen" text={`Invocando el Santuario de ${username}...`} />;
    }

    if (isError) {
        const status = (error as any)?.response?.status;
        
        return (
            <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-[#08080c] text-white">
                <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
                    <div className="absolute top-[20%] left-[20%] h-[50%] w-[50%] rounded-full bg-red-950/15 blur-[120px]" />
                </div>
                
                <div className="relative z-10 glass border border-red-500/20 p-8 rounded-3xl max-w-md w-full text-center space-y-6 bg-red-950/5">
                    <div className="inline-flex p-4 bg-red-500/10 rounded-full text-red-500 border border-red-500/20">
                        <Lock className="h-10 w-10 animate-pulse" />
                    </div>
                    <div className="space-y-2">
                        <h2 className="text-xl font-black uppercase tracking-widest text-white">Santuario Restringido</h2>
                        <p className="text-xs text-white/50 uppercase leading-relaxed font-bold">
                            {status === 403 
                                ? `El Guardián '${username}' ha decidido mantener su Santuario en modo privado.` 
                                : `El Santuario de '${username}' no se encuentra en los archivos de Eternia.`}
                        </p>
                    </div>
                    <a
                        href="/"
                        className="inline-flex w-full justify-center bg-white/5 hover:bg-white/10 text-white border border-white/10 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all"
                    >
                        Volver al Oráculo
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#08080c] text-white font-inter pb-20 p-4 md:p-8 relative overflow-hidden">
            {/* Ambient Lighting Background */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
                <div className="absolute top-[-10%] right-[-5%] h-[60%] w-[60%] rounded-full bg-brand-primary/5 blur-[120px]" />
                <div className="absolute bottom-[-10%] left-[-5%] h-[60%] w-[60%] rounded-full bg-amber-500/5 blur-[120px]" />
                <div className="absolute inset-0 bg-gradient-to-b from-black/0 via-black/10 to-black/40" />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto space-y-6">
                
                {/* Header Showcase Banner */}
                <div className="relative overflow-hidden flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between rounded-3xl border border-white/5 bg-black/25 p-6 md:p-8 backdrop-blur-2xl shadow-2xl">
                    <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-3xl pointer-events-none"></div>

                    <div className="relative z-10 flex flex-col gap-3">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Globe className="h-4 w-4 animate-spin-slow" />
                            <h2 className="text-xs font-black uppercase tracking-[0.25em]">Santuario Público</h2>
                        </div>
                        <div className="flex items-baseline gap-2.5 flex-wrap">
                            <h1 className="text-2xl md:text-3xl font-black uppercase tracking-tight text-white">
                                Colección de <span className="text-brand-primary">{showcaseData.username}</span>
                            </h1>
                            {showcaseData.location && (
                                <span className="text-[10px] font-black tracking-widest uppercase px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/50">
                                    Guardián en {showcaseData.location}
                                </span>
                            )}
                        </div>
                        <p className="max-w-xl text-[10px] md:text-xs text-white/45 font-bold uppercase tracking-wider leading-relaxed">
                            Contempla las reliquias custodiadas en la fortaleza de {showcaseData.username}. Los datos financieros han sido protegidos por decreto del Consejo de Eternia.
                        </p>
                    </div>

                    {/* Quick Stats Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 relative z-10">
                        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-md">
                            <div className="text-[9px] font-black uppercase tracking-wider text-white/40 mb-1">Total Figuras</div>
                            <div className="text-xl font-black text-brand-primary">{stats.totalCount}</div>
                        </div>
                        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-md">
                            <div className="text-[9px] font-black uppercase tracking-wider text-white/40 mb-1">Colección Retro</div>
                            <div className="text-xl font-black text-amber-500">{stats.vintageCount}</div>
                        </div>
                        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-md">
                            <div className="text-[9px] font-black uppercase tracking-wider text-white/40 mb-1">Colección Moderna</div>
                            <div className="text-xl font-black text-cyan-400">{stats.modernCount}</div>
                        </div>
                        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-md">
                            <div className="text-[9px] font-black uppercase tracking-wider text-white/40 mb-1">Valor Estimado</div>
                            <div className="text-xl font-black text-emerald-400">
                                {stats.totalValue.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}€
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filters Row */}
                <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-black/15 p-4 rounded-2xl border border-white/5 backdrop-blur-lg">
                    {/* Search Input */}
                    <div className="relative w-full md:w-80">
                        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/30" />
                        <input
                            type="text"
                            placeholder="Buscar figura o sub-línea..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-xs placeholder-white/30 text-white focus:outline-none focus:border-brand-primary/50 transition-all font-medium"
                        />
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex flex-wrap gap-2 w-full md:w-auto items-center justify-end">
                        <div className="flex p-0.5 rounded-xl bg-white/[0.03] border border-white/5">
                            <button
                                onClick={() => setCategoryFilter('all')}
                                className={`py-1.5 px-3 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all ${categoryFilter === 'all' ? 'bg-brand-primary text-white' : 'text-white/40 hover:text-white/70'}`}
                            >
                                Todas
                            </button>
                            <button
                                onClick={() => setCategoryFilter('modern')}
                                className={`py-1.5 px-3 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all ${categoryFilter === 'modern' ? 'bg-brand-primary text-white' : 'text-white/40 hover:text-white/70'}`}
                            >
                                Modernas
                            </button>
                            <button
                                onClick={() => setCategoryFilter('vintage')}
                                className={`py-1.5 px-3 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all ${categoryFilter === 'vintage' ? 'bg-amber-500 text-white' : 'text-white/40 hover:text-white/70'}`}
                            >
                                Vintage
                            </button>
                        </div>

                        {/* Subcategory Select Dropdown */}
                        <select
                            value={subCategoryFilter}
                            onChange={(e) => setSubCategoryFilter(e.target.value)}
                            className="bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-[9px] font-black uppercase tracking-widest text-white/70 focus:outline-none cursor-pointer"
                        >
                            <option value="all" className="bg-[#121214]">Sub-líneas (Todas)</option>
                            {subCategories.map(sub => (
                                <option key={sub} value={sub} className="bg-[#121214]">{sub}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Showcase Cards Grid */}
                {filteredItems.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                        <Compass className="h-12 w-12 text-white/20 animate-pulse" />
                        <p className="text-xs text-white/40 uppercase tracking-widest font-black">No se encontraron reliquias en este Santuario</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                        {filteredItems.map((item: any) => {
                            const adjustedValue = getAdjustedValue(item);
                            const hasGrading = item.grading && item.grading > 0;
                            
                            return (
                                <div
                                    key={item.id}
                                    className="group relative flex flex-col rounded-3xl border border-white/5 bg-black/20 overflow-hidden hover:border-brand-primary/30 hover:bg-brand-primary/[0.02] transition-all duration-300 shadow-lg hover:shadow-2xl"
                                >
                                    {/* Image Container with Badges */}
                                    <div className="relative aspect-square w-full overflow-hidden bg-white/5 flex items-center justify-center">
                                        <img
                                            src={getOptimizedImageUrl(item.product.image_url)}
                                            alt={item.product.name}
                                            className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
                                            loading="lazy"
                                        />

                                        {/* Vintage/Modern Badge */}
                                        <span className={`absolute top-3 left-3 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest backdrop-blur-md ${item.product.is_vintage ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-brand-primary/10 text-brand-primary border border-brand-primary/20'}`}>
                                            {item.product.is_vintage ? 'Vintage' : 'Modern'}
                                        </span>

                                        {/* Condition Badge */}
                                        <span className={`absolute top-3 right-3 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest backdrop-blur-md ${
                                            item.condition?.toUpperCase() === 'MOC' 
                                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                                                : item.condition?.toUpperCase() === 'LOOSE'
                                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                                        }`}>
                                            {item.condition || 'NEW'}
                                        </span>
                                    </div>

                                    {/* Info Block */}
                                    <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                                        <div className="space-y-1">
                                            {item.product.sub_category && (
                                                <div className="text-[8px] font-black uppercase tracking-widest text-white/35">
                                                    {item.product.sub_category}
                                                </div>
                                            )}
                                            <h3 className="text-xs font-black uppercase text-white tracking-wide line-clamp-2 group-hover:text-brand-primary transition-colors">
                                                {item.product.name}
                                            </h3>
                                            {item.product.variant_name && (
                                                <div className="text-[9px] font-bold text-brand-primary uppercase tracking-wider">
                                                    {item.product.variant_name}
                                                </div>
                                            )}
                                        </div>

                                        {/* Value & Grading */}
                                        <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                                            <div>
                                                <div className="text-[8px] font-bold uppercase tracking-wider text-white/30">Valor Estimado</div>
                                                <div className="text-xs font-black text-emerald-400 flex items-center gap-1">
                                                    <TrendingUp className="h-3 w-3" />
                                                    {adjustedValue.toFixed(2)}€
                                                </div>
                                            </div>

                                            {hasGrading && (
                                                <div className="text-right">
                                                    <div className="text-[8px] font-bold uppercase tracking-wider text-white/30">Grading</div>
                                                    <div className="text-xs font-black text-yellow-400 flex items-center gap-0.5 justify-end">
                                                        <Award className="h-3 w-3 fill-yellow-400/10" />
                                                        {item.grading?.toFixed(1)}
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {/* Notes */}
                                        {item.notes && (
                                            <p className="text-[9px] text-white/45 italic font-medium leading-normal bg-white/5 p-2 rounded-xl border border-white/5 line-clamp-2">
                                                "{item.notes}"
                                            </p>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Showcase;
