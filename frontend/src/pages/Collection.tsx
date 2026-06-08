import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Box,
    AlertCircle,
    Info,
    Check,
    Trophy,
    TrendingUp,
    TrendingDown,
    Euro,
    Star,
    ShoppingCart,
    Sparkles,
    Download,
    Database,
    RefreshCw,
    Settings,
    Trash2,
    X,
    Save,
    ArrowUp,
    ArrowDown
} from 'lucide-react';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { motion, AnimatePresence } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { getOptimizedImageUrl } from '../utils/imageUtils';
import CollectionItemDetailModal from '../components/CollectionItemDetailModal';
import { updateProduct, deleteProduct } from '../api/admin';
import type { Hero } from '../api/admin';

const getAdjustedStats = (product: Product, isOwned: boolean) => {
    const baseValue = product.market_value || 0;
    if (!isOwned) {
        const msrp = product.retail_price || 0;
        const roi = msrp > 0 ? ((baseValue - msrp) / msrp) * 100 : 0;
        return {
            adjustedValue: baseValue,
            roi: roi,
            condition: '',
            grading: 0
        };
    }

    const cond = product.condition || 'New';
    const grad = product.grading !== undefined ? product.grading : 10.0;
    
    let condMult = 0.75;
    if (cond.toUpperCase() === 'MOC') condMult = 1.0;
    else if (cond.toUpperCase() === 'LOOSE') condMult = 0.5;

    const gradFactor = Math.max(0.10, 1.0 - ((10.0 - grad) * 0.04));
    const adjustedValue = baseValue * condMult * gradFactor;

    let roi = 0;
    if (product.purchase_price && product.purchase_price > 0) {
        roi = ((adjustedValue - product.purchase_price) / product.purchase_price) * 100;
    } else {
        const msrp = product.retail_price || 0;
        roi = msrp > 0 ? ((adjustedValue - msrp) / msrp) * 100 : 0;
    }

    return {
        adjustedValue,
        roi,
        condition: cond,
        grading: grad
    };
};

interface CollectionProps {
    searchQuery?: string;
    isVintageOnly?: boolean;
    user?: Hero | null;
}

const Collection: React.FC<CollectionProps> = ({ searchQuery = "", isVintageOnly = false, user }) => {
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState<'owned' | 'wish'>('owned');
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);
    const [sortBy, setSortBy] = useState<'name' | 'id'>('name');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    // Contexto de Autenticación (Fase 8.2)
    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');
    const isAdmin = user?.role === 'admin' || user?.username === 'David';

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number, data: any }) => updateProduct(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection'] });
            setEditingProduct(null);
        }
    });

    const deleteProductMutation = useMutation({
        mutationFn: (productId: number) => deleteProduct(productId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection'] });
            queryClient.invalidateQueries({ queryKey: ['vintage-products'] });
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedProduct(null);
            alert('Reliquia eliminada y devuelta al Purgatorio con éxito.');
        },
        onError: (err) => {
            console.error('Error al eliminar producto:', err);
            alert('No se pudo eliminar el producto. Inténtelo de nuevo.');
        }
    });

    const handleSaveEdit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingProduct) return;
        updateMutation.mutate({
            id: editingProduct.id,
            data: {
                name: editingProduct.name,
                ean: editingProduct.ean,
                image_url: editingProduct.image_url,
                sub_category: editingProduct.sub_category,
                retail_price: editingProduct.retail_price,
                is_vintage: editingProduct.is_vintage
            }
        });
    };

    const handleDeleteProduct = (product: Product) => {
        if (confirm(`¿Estás completamente seguro de que deseas eliminar permanentemente '${product.name}' de los catálogos y colecciones? Todas sus ofertas vinculadas volverán al Purgatorio.`)) {
            deleteProductMutation.mutate(product.id);
        }
    };

    // 1. Fetch de la colección (basada en el ID activo)
    const { data: collection, isLoading, isError } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId, isVintageOnly],
        queryFn: () => getCollection(activeUserId, isVintageOnly)
    });

    // 2. Mutación para alternar estado
    const toggleMutation = useMutation({
        mutationFn: ({ productId, wish }: { productId: number, wish: boolean }) => toggleCollection(productId, activeUserId, wish),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', activeUserId, isVintageOnly] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats', activeUserId] });
        }
    });

    const sortedFilteredItems = React.useMemo(() => {
        if (!collection) return [];
        
        const filtered = collection.filter(product => {
            const query = searchQuery.toLowerCase();
            return (
                product.name.toLowerCase().includes(query) ||
                product.figure_id.toLowerCase().includes(query) ||
                product.sub_category?.toLowerCase().includes(query)
            );
        });

        return [...filtered].sort((a, b) => {
            let comparison = 0;
            if (sortBy === 'name') {
                comparison = a.name.localeCompare(b.name);
            } else if (sortBy === 'id') {
                comparison = a.id - b.id;
            }

            return sortOrder === 'asc' ? comparison : -comparison;
        });
    }, [collection, searchQuery, sortBy, sortOrder]);

    const ownedItems = sortedFilteredItems.filter(p => !p.is_wish);
    const wishItems = sortedFilteredItems.filter(p => p.is_wish);

    // Total count for stats (unfiltered)
    const totalOwned = collection?.filter(p => !p.is_wish).length || 0;
    const totalWish = collection?.filter(p => p.is_wish).length || 0;

    if (isLoading) {
        return <PowerSwordLoader variant="fullScreen" text="Sincronizando con la Fortaleza..." isVintage={isVintageOnly} />;
    }

    if (isError) {
        return (
            <div className="flex h-[60vh] flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium italic">La conexión con los archivos de Eternia ha fallado.</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 md:space-y-3 animate-in fade-in duration-700 pb-20">
            {/* Header & Stats Banner */}
            {/* Header & Stats Banner */}
            <div className="relative overflow-hidden flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl pointer-events-none ${isVintageOnly ? 'bg-amber-500/10' : 'bg-brand-primary/10'}`}></div>

                <div className="relative z-10 flex flex-col gap-2">
                    <div className="flex flex-col gap-1">
                        <div className={`flex items-center gap-2 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>
                            <Box className={`h-3 w-3 md:h-4 md:w-4 ${isVintageOnly ? 'fill-amber-500' : 'fill-brand-primary'}`} />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                {isVintageOnly ? (
                                    <>
                                        Mi Fortaleza <span className="text-amber-500">Vintage</span>
                                    </>
                                ) : (
                                    <>
                                        Mi <span className="text-brand-primary">Legado</span>
                                    </>
                                )}
                            </h2>
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/40 font-medium uppercase tracking-[0.1em]">
                            {isVintageOnly 
                                ? 'Coleccionando no solo figuras retro, sino reliquias históricas y valor del pasado.'
                                : 'Coleccionando no solo figuras, sino fragmentos de historia y valor en el tiempo.'
                            }
                        </p>
                    </div>

                    {/* Export Buttons Dock */}
                    <div className="flex flex-row gap-2 mt-1">
                        <button
                            onClick={async () => {
                                try {
                                    const { exportCollectionExcel, exportCollectionExcelVintage } = await import('../api/admin');
                                    if (isVintageOnly) {
                                        await exportCollectionExcelVintage(activeUserId);
                                    } else {
                                        await exportCollectionExcel(activeUserId);
                                    }
                                    alert('📊 Excel: Tu colección ha sido exportada con éxito.');
                                } catch (error) {
                                    console.error('Export error:', error);
                                    alert('❌ Error al exportar Excel.');
                                }
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-green-500/10 text-green-400 border border-green-500/20 text-[9px] font-black uppercase tracking-widest hover:bg-green-500 hover:text-white transition-all shadow-md cursor-pointer"
                        >
                            <Download className="h-3 w-3" />
                            <span>Excel</span>
                        </button>
                        <button
                            onClick={async () => {
                                try {
                                    const { exportCollectionSqlite } = await import('../api/admin');
                                    await exportCollectionSqlite(activeUserId);
                                    alert('🗄️ SQLite: Bóveda portátil generada con éxito.');
                                } catch (error) {
                                    console.error('Export error:', error);
                                    alert('❌ Error al exportar SQLite.');
                                }
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[9px] font-black uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all shadow-md cursor-pointer"
                        >
                            <Database className="h-3 w-3" />
                            <span>SQLite</span>
                        </button>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full lg:w-auto relative z-10">
                    <div className="flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
                        <div className="grid grid-cols-2 gap-1 sm:gap-2 p-1 rounded-xl bg-white/[0.03] border border-white/5 flex-1 sm:flex-initial">
                            <button
                                onClick={() => setSortBy('name')}
                                className={`py-1.5 px-4 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] transition-all ${
                                    sortBy === 'name' 
                                        ? (isVintageOnly ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'bg-brand-primary text-white shadow-[0_0_15px_rgba(14,165,233,0.3)]') 
                                        : 'text-white/20 hover:text-white/40'
                                }`}
                            >
                                Nombre
                            </button>
                            <button
                                onClick={() => setSortBy('id')}
                                className={`py-1.5 px-4 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] transition-all ${
                                    sortBy === 'id' 
                                        ? (isVintageOnly ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'bg-brand-primary text-white shadow-[0_0_15px_rgba(14,165,233,0.3)]') 
                                        : 'text-white/20 hover:text-white/40'
                                }`}
                            >
                                ID
                            </button>
                        </div>

                        <button
                            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                            className={`h-[38px] w-[38px] sm:h-[42px] sm:w-[42px] flex items-center justify-center rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/10 transition-all shrink-0 shadow-md ${
                                isVintageOnly ? 'text-amber-500 hover:text-amber-400' : 'text-brand-primary hover:text-brand-primary/80'
                            }`}
                            title={sortOrder === 'asc' ? 'Orden Ascendente' : 'Orden Descendente'}
                        >
                            {sortOrder === 'asc' ? <ArrowUp className="h-4 w-4 sm:h-5 sm:w-5" /> : <ArrowDown className="h-4 w-4 sm:h-5 sm:w-5" />}
                        </button>
                    </div>

                    <div className="flex items-center justify-between sm:justify-start gap-3 rounded-xl sm:rounded-2xl bg-white/[0.03] px-4 py-2 sm:py-2.5 border border-white/5 backdrop-blur-3xl w-full sm:w-auto h-[38px] sm:h-[42px]">
                        <div className="flex items-center gap-2">
                            <Box className={`h-4 w-4 sm:h-5 sm:w-5 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`} />
                            <span className="text-lg sm:text-xl font-black text-white leading-none">{activeTab === 'owned' ? totalOwned : totalWish}</span>
                        </div>
                        <span className="text-[8px] sm:text-[9px] font-black text-white/20 uppercase tracking-[0.15em] pt-0.5 leading-tight text-right sm:text-left">
                            {activeTab === 'owned' ? 'Fortaleza' : 'Radar'}<br className="sm:hidden" /> Coleccionados
                        </span>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex bg-black/50 p-1 rounded-2xl md:rounded-3xl border border-white/10 backdrop-blur-3xl w-fit">
                <button
                    onClick={() => setActiveTab('owned')}
                    className={`flex items-center justify-center gap-1.5 px-4 md:px-6 py-1.5 md:py-2 rounded-xl md:rounded-2xl text-[10px] md:text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'owned' ? (isVintageOnly ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/20 scale-105' : 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20 scale-105') : 'text-white/60 hover:text-white'}`}
                >
                    <Box className="h-3 w-3 md:h-4 md:w-4" />
                    La Fortaleza
                </button>
                <button
                    onClick={() => setActiveTab('wish')}
                    className={`flex items-center justify-center gap-1.5 px-4 md:px-6 py-1.5 md:py-2 rounded-xl md:rounded-2xl text-[10px] md:text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'wish' ? (isVintageOnly ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/20 scale-105' : 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20 scale-105') : 'text-white/60 hover:text-white'}`}
                >
                    <Star className="h-3 w-3 md:h-4 md:w-4" />
                    Lista de Deseos
                    {totalWish > 0 && (
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-md ml-1 ${isVintageOnly ? 'bg-black/20 text-amber-600 font-extrabold' : 'bg-white/10 text-brand-primary'}`}>
                            {totalWish}
                        </span>
                    )}
                </button>
            </div>

            {/* Grid Area */}
            <AnimatePresence mode="wait">
                {(activeTab === 'owned' ? ownedItems : wishItems).length === 0 ? (
                    <motion.div
                        key="empty"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="flex min-h-[400px] flex-col items-center justify-center gap-8 rounded-[3rem] border-2 border-dashed border-white/5 bg-white/[0.01] p-12 text-center"
                    >
                        <div className="h-24 w-24 rounded-full bg-white/5 flex items-center justify-center border border-white/10 relative">
                            {activeTab === 'owned' ? <Box className="h-10 w-10 text-white/20" /> : <Star className="h-10 w-10 text-white/20" />}
                            <Sparkles className={`absolute -top-2 -right-2 h-6 w-6 opacity-30 animate-pulse ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`} />
                        </div>
                        <div className="max-w-xs space-y-3">
                            <p className="text-2xl font-black text-white/80 uppercase tracking-tighter">
                                {searchQuery ? 'Sin Resultados' : 'Sector Vacío'}
                            </p>
                            <p className="text-sm text-white/65 leading-relaxed font-medium">
                                {searchQuery
                                    ? `Ninguna reliquia en tu ${activeTab === 'owned' ? 'fortaleza' : 'lista'} coincide con "${searchQuery}".`
                                    : activeTab === 'owned'
                                        ? 'Aún no has reclamado ninguna reliquia. El catálogo maestro te espera para forjar tu leyenda.'
                                        : 'No tienes objetivos marcados. Encuentra tu próxima obsesión en el catálogo.'}
                            </p>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="grid grid-cols-2 gap-1.5 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4 landscape:grid-cols-3"
                    >
                        {(activeTab === 'owned' ? ownedItems : wishItems).map((product) => {
                            const isGrail = product.is_grail;
                            const { adjustedValue, roi, condition, grading } = getAdjustedStats(product, activeTab === 'owned');

                            return (
                                <div
                                    key={product.id}
                                    className={`group flex flex-col gap-1 sm:gap-1.5 md:gap-3 relative overflow-hidden transition-all duration-500 hover:translate-y-[-8px] rounded-2xl sm:rounded-3xl p-1.5 sm:p-2 md:p-3.5 border ${isGrail ? 'border-yellow-500/30 bg-yellow-500/10 backdrop-blur-md shadow-[0_30px_60px_-15px_rgba(234,179,8,0.2)]' : 'border-white/5 bg-black/25 backdrop-blur-md hover:bg-black/20'}`}
                                >
                                    {/* Image Container */}
                                    <div 
                                        className="relative aspect-square w-full overflow-hidden rounded-[1.2rem] sm:rounded-[1.5rem] bg-black/40 border border-white/10 shadow-inner cursor-pointer"
                                        onClick={() => {
                                            setSelectedProduct(product);
                                            setIsDetailOpen(true);
                                        }}
                                    >
                                        {product.image_url ? (
                                            <img 
                                                src={getOptimizedImageUrl(product.image_url, 300)} 
                                                className="h-full w-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1" 
                                                loading="lazy"
                                                alt={product.name}
                                            />
                                        ) : (
                                            <div className="flex h-full w-full items-center justify-center text-[10px] text-white/10 font-black uppercase tracking-widest">No Image</div>
                                        )}

                                        {/* Corner Badges */}
                                        <div className="absolute top-2 left-2 sm:top-3 sm:left-3 z-40 flex items-center gap-1">
                                            <div className="rounded-lg bg-black/70 px-2 py-0.5 text-[8px] sm:text-[9px] font-black text-white/90 backdrop-blur-md border border-white/20 shadow-2xl uppercase tracking-widest">
                                                #{product.figure_id}
                                            </div>
                                            {isGrail && (
                                                <div className="rounded-lg bg-yellow-500 text-black px-2 py-0.5 text-[8px] sm:text-[9px] font-black backdrop-blur-md border border-yellow-400 shadow-[0_0_20px_rgba(234,179,8,0.5)] flex items-center gap-1">
                                                    <Trophy className="h-2.5 w-2.5" />
                                                    GRIAL
                                                </div>
                                            )}
                                        </div>

                                        {/* Status indicator */}
                                        <div className="absolute bottom-2 left-2 flex items-center gap-1.5">
                                            <div className={`h-1.5 w-1.5 rounded-full ${activeTab === 'owned' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]' : (isVintageOnly ? 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)] animate-pulse' : 'bg-brand-primary shadow-[0_0_10px_rgba(14,165,233,0.8)] animate-pulse')}`}></div>
                                            <span className="text-[8px] font-black text-white uppercase tracking-widest opacity-80 backdrop-blur-sm bg-black/20 px-1.5 py-0.5 rounded-full">
                                                {activeTab === 'owned' ? 'Poseída' : 'Prioridad'}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Info */}
                                    <div className="space-y-1 flex-1 px-0.5">
                                        <div className="space-y-0.5">
                                            <span className={`text-[8px] sm:text-[9px] font-black uppercase tracking-widest transition-colors ${isVintageOnly ? 'text-amber-500 group-hover:text-amber-500/80' : 'text-brand-primary group-hover:text-brand-primary/80'}`}>
                                                {product.sub_category}
                                            </span>
                                            <h3 className={`line-clamp-2 text-[10px] sm:text-xs md:text-sm lg:text-base font-black leading-tight text-white transition-all ${isVintageOnly ? 'group-hover:text-amber-500' : 'group-hover:text-brand-primary'}`}>
                                                {product.name}
                                            </h3>
                                        </div>

                                        <div className="flex flex-wrap items-center gap-1 pt-0.5">
                                            {adjustedValue > 0 && (
                                                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded-lg border font-black text-[8px] sm:text-[9px] whitespace-nowrap ${isGrail ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : (isVintageOnly ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20')}`}>
                                                    <Euro className="h-2 w-2 sm:h-2.5 sm:w-2.5" />
                                                    {adjustedValue.toFixed(2)}€
                                                </div>
                                            )}
                                            {roi !== 0 && (
                                                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded-lg border font-black text-[8px] sm:text-[9px] whitespace-nowrap ${roi >= 0 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                                                    {roi >= 0 ? <TrendingUp className="h-2 w-2 sm:h-2.5 sm:w-2.5" /> : <TrendingDown className="h-2 w-2 sm:h-2.5 sm:w-2.5" />}
                                                    {roi >= 0 ? '+' : ''}{roi.toFixed(1)}%
                                                </div>
                                            )}
                                            {activeTab === 'owned' && (
                                                <div className="flex items-center gap-1">
                                                    <span className="px-1 py-0.5 rounded-md bg-white/5 border border-white/10 text-white/60 text-[6px] sm:text-[7px] font-black uppercase tracking-wider">
                                                        {condition}
                                                    </span>
                                                    <span className={`px-1 py-0.5 rounded-md text-[6px] sm:text-[7px] font-black uppercase tracking-wider ${grading >= 9 ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20'}`}>
                                                        {grading.toFixed(1)}
                                                    </span>
                                                    {product.purchase_price && product.purchase_price > 0 ? (
                                                        <span className={`px-1 py-0.5 rounded-md text-[6px] sm:text-[7px] font-black uppercase tracking-wider flex items-center gap-0.5 border ${isVintageOnly ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20'}`} title={`Inversión manual: ${product.purchase_price}€`}>
                                                            <ShoppingCart className="h-2 w-2" />
                                                            {product.purchase_price.toFixed(0)}€
                                                        </span>
                                                    ) : (
                                                        <span className="px-1 py-0.5 rounded-md bg-white/5 border border-white/10 text-white/20 text-[6px] sm:text-[7px] font-black uppercase tracking-wider flex items-center gap-0.5" title="Inversión por defecto (0€)">
                                                            <ShoppingCart className="h-2 w-2 opacity-30" />
                                                            --
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Multi-Actions Bar */}
                                    <div className="mt-auto flex items-center gap-1 sm:gap-1.5 pt-1">
                                        <button
                                            onClick={() => {
                                                setSelectedProduct(product);
                                                setIsDetailOpen(true);
                                            }}
                                            className="h-7 w-7 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-white/10 hover:text-white transition-all group/info"
                                        >
                                            <Info className="h-3.5 w-3.5 group-hover:scale-110 transition-transform" />
                                        </button>

                                        {isAdmin && (
                                            <>
                                                <button
                                                    onClick={() => setEditingProduct(product)}
                                                    className="h-7 w-7 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-white/10 hover:text-white transition-all"
                                                    title="Editar metadatos"
                                                >
                                                    <Settings className="h-3.5 w-3.5" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteProduct(product)}
                                                    className="h-7 w-7 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-red-500/20 hover:text-red-400 transition-all"
                                                    title="Eliminar y devolver al Purgatorio"
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </button>
                                            </>
                                        )}

                                        {activeTab === 'wish' ? (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: false })}
                                                disabled={toggleMutation.isPending}
                                                className={`h-7 px-2.5 flex items-center justify-center gap-1 rounded-xl font-black text-[9px] uppercase tracking-widest shadow-lg transition-all flex-1 ${isVintageOnly ? 'bg-amber-500 text-black border border-amber-500/50 shadow-amber-500/20 hover:brightness-110' : 'bg-brand-primary text-white border border-brand-primary/50 shadow-brand-primary/20 hover:brightness-110'}`}
                                            >
                                                {toggleMutation.isPending ? <RefreshCw className="h-3 w-3 animate-spin text-white/50" /> : <ShoppingCart className={`h-3 w-3 ${isVintageOnly ? 'text-black' : 'text-white'}`} />}
                                                <span className="hidden sm:inline">Reclamar</span>
                                            </button>
                                        ) : (
                                            <button
                                                onClick={() => {
                                                    const message = isVintageOnly
                                                        ? `¿Seguro de desvincular '${product.name}' de tu colección? Volverá a aparecer en Eternia (el producto, sus ofertas y estadísticas se conservarán intactos).`
                                                        : `¿Seguro de liberar '${product.name}' de tu colección? Volverá a aparecer en Nueva Eternia.`;
                                                    if (confirm(message)) {
                                                        toggleMutation.mutate({ productId: product.id, wish: false });
                                                    }
                                                }}
                                                disabled={toggleMutation.isPending}
                                                className={`h-7 px-2.5 flex items-center justify-center gap-1 rounded-xl font-black text-[9px] uppercase tracking-widest border transition-all group/action flex-1 ${
                                                    isVintageOnly 
                                                        ? 'bg-amber-500/10 text-amber-500 border-amber-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30' 
                                                        : 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30'
                                                }`}
                                            >
                                                {toggleMutation.isPending ? <RefreshCw className="h-3 w-3 animate-spin text-white/50" /> : (
                                                    <>
                                                        <Check className="h-3 w-3 group-hover/action:hidden" />
                                                        <Box className="h-3 w-3 hidden group-hover/action:block" />
                                                    </>
                                                )}
                                                <span className="hidden sm:inline group-hover/action:hidden">
                                                    {isVintageOnly ? 'En Fortaleza' : 'En Sanctum'}
                                                </span>
                                                <span className="hidden sm:group-hover/action:block">
                                                    {isVintageOnly ? 'Desvincular' : 'Liberar'}
                                                </span>
                                            </button>
                                        )}

                                        {activeTab === 'wish' && (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: true })}
                                                disabled={toggleMutation.isPending}
                                                className="h-7 w-7 flex items-center justify-center rounded-xl bg-red-500/5 text-red-500/30 border border-red-500/10 hover:bg-red-500 hover:text-white transition-all shrink-0"
                                                title="Eliminar de Deseos"
                                            >
                                                <Star className="h-3.5 w-3.5 fill-current" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Detail Modal Integration (Legado Bridge) */}
            {isDetailOpen && selectedProduct && (
                <CollectionItemDetailModal
                    product={selectedProduct}
                    userId={activeUserId}
                    onClose={() => {
                        setIsDetailOpen(false);
                        setSelectedProduct(null);
                    }}
                />
            )}

            {/* EDIT PRODUCT MODAL (ADMIN ONLY) */}
            {isAdmin && editingProduct && (
                <div className="fixed inset-0 z-[130] flex items-center justify-center p-4 bg-black/90 backdrop-blur-2xl animate-in fade-in duration-300">
                    <motion.div
                                                        initial={{ scale: 0.9, opacity: 0 }}
                                                        animate={{ scale: 1, opacity: 1 }}
                                                        className={`relative w-full max-w-2xl overflow-hidden rounded-[2.5rem] border bg-[#0A0A0B] flex flex-col transition-all ${editingProduct.is_vintage ? 'border-amber-500/30 shadow-[0_0_50px_rgba(245,158,11,0.2)]' : 'border-brand-primary/30 shadow-[0_0_50px_rgba(14,165,233,0.2)]'}`}
                                                        onClick={(e) => e.stopPropagation()}
                                                    >
                                                        <form onSubmit={handleSaveEdit}>
                                                            <div className="p-8 pb-4 flex items-center justify-between border-b border-white/5">
                                                                <div className="flex items-center gap-4">
                                                                    <div className={`p-3 rounded-xl ${editingProduct.is_vintage ? 'bg-amber-500/10' : 'bg-brand-primary/10'}`}>
                                                                        <Settings className={`h-6 w-6 ${editingProduct.is_vintage ? 'text-amber-500' : 'text-brand-primary'}`} />
                                                                    </div>
                                                                    <h4 className="text-2xl font-black text-white">Editor de <span className={editingProduct.is_vintage ? 'text-amber-500' : 'text-brand-primary'}>La Verdad</span></h4>
                                                                </div>
                                <button
                                    type="button"
                                    onClick={() => setEditingProduct(null)}
                                    className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/65 hover:bg-red-500/20 hover:text-red-400 transition-all"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="p-8 space-y-6 overflow-y-auto max-h-[60vh] custom-scrollbar">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Name */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Nombre de la Reliquia</label>
                                        <input
                                            value={editingProduct.name}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none transition-all ${editingProduct.is_vintage ? 'focus:border-amber-500/50' : 'focus:border-brand-primary/50'}`}
                                        />
                                    </div>

                                    {/* EAN */}
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">EAN (Código Sagrado)</label>
                                        <input
                                            value={editingProduct.ean || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, ean: e.target.value })}
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none transition-all ${editingProduct.is_vintage ? 'focus:border-amber-500/50' : 'focus:border-brand-primary/50'}`}
                                            placeholder="Desconocido"
                                        />
                                    </div>

                                    {/* Retail Price */}
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Precio de Lanzamiento (€)</label>
                                        <input
                                            type="number"
                                            value={editingProduct.retail_price || 0}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, retail_price: parseFloat(e.target.value) })}
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none transition-all ${editingProduct.is_vintage ? 'focus:border-amber-500/50' : 'focus:border-brand-primary/50'}`}
                                        />
                                    </div>

                                    {/* Subcategory */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Línea temporal (Subcategoría)</label>
                                        <input
                                            value={editingProduct.sub_category || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, sub_category: e.target.value })}
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none transition-all ${editingProduct.is_vintage ? 'focus:border-amber-500/50' : 'focus:border-brand-primary/50'}`}
                                        />
                                    </div>

                                    {/* Image URL */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Pocion Visual (URL Imagen)</label>
                                        <input
                                            value={editingProduct.image_url || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, image_url: e.target.value })}
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white/50 text-xs focus:outline-none transition-all ${editingProduct.is_vintage ? 'focus:border-amber-500/50' : 'focus:border-brand-primary/50'}`}
                                        />
                                    </div>

                                    {/* Linea Vintage (is_vintage) toggle */}
                                    <div className="col-span-1 md:col-span-2 flex items-center justify-between p-4 rounded-2xl bg-white/[0.02] border border-white/5 mt-2">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-black uppercase tracking-widest text-white/80 block">Línea Vintage (Eternia)</label>
                                            <span className="text-[8px] text-white/60 font-bold uppercase tracking-wider block">Activar para transferir este producto a la línea retro vintage</span>
                                        </div>
                                        <label className="relative inline-flex items-center cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={!!editingProduct.is_vintage}
                                                onChange={(e) => setEditingProduct({ ...editingProduct, is_vintage: e.target.checked })}
                                                className="sr-only peer"
                                            />
                                            <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white/40 peer-checked:after:bg-amber-500 after:border-none after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500/20 border border-white/10 peer-checked:border-amber-500/30"></div>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 border-t border-white/5 bg-white/[0.02] flex items-center justify-end gap-4">
                                <button
                                    type="button"
                                    onClick={() => setEditingProduct(null)}
                                    className="px-6 py-3 rounded-2xl text-sm font-black uppercase tracking-widest text-white/60 hover:text-white transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={updateMutation.isPending}
                                    className={`px-8 py-3 rounded-2xl font-black uppercase tracking-widest transition-all flex items-center gap-2 disabled:opacity-50 text-white ${editingProduct.is_vintage ? 'bg-amber-500 hover:bg-amber-600 text-black shadow-[0_0_30px_rgba(245,158,11,0.3)]' : 'bg-brand-primary hover:bg-brand-secondary shadow-[0_0_30px_rgba(14,165,233,0.3)]'}`}
                                >
                                    {updateMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                                    Preservar Cambios
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default Collection;
