import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Box,
    AlertCircle,
    Info,
    Check,
    Trophy,
    TrendingUp,
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
    Save
} from 'lucide-react';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { motion, AnimatePresence } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { getOptimizedImageUrl } from '../utils/imageUtils';
import CollectionItemDetailModal from '../components/CollectionItemDetailModal';
import { updateProduct, deleteProduct } from '../api/admin';
import type { Hero } from '../api/admin';

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

    const filteredItems = collection?.filter(product => {
        const query = searchQuery.toLowerCase();
        return (
            product.name.toLowerCase().includes(query) ||
            product.figure_id.toLowerCase().includes(query) ||
            product.sub_category?.toLowerCase().includes(query)
        );
    }) || [];

    const ownedItems = filteredItems.filter(p => !p.is_wish);
    const wishItems = filteredItems.filter(p => p.is_wish);

    // Total count for stats (unfiltered)
    const totalOwned = collection?.filter(p => !p.is_wish).length || 0;
    const totalWish = collection?.filter(p => p.is_wish).length || 0;

    if (isLoading) {
        return <PowerSwordLoader variant="fullScreen" text="Sincronizando con la Fortaleza..." />;
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
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/50 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl pointer-events-none ${isVintageOnly ? 'bg-amber-500/10' : 'bg-brand-primary/10'}`}></div>
                <div className="absolute -left-20 -bottom-20 h-48 w-48 rounded-full bg-purple-500/10 blur-3xl pointer-events-none"></div>

                <div className="relative flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
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
                        <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium">
                            {isVintageOnly 
                                ? 'Coleccionando no solo figuras retro, sino reliquias históricas y valor del pasado.'
                                : 'Coleccionando no solo figuras, sino fragmentos de historia y valor en el tiempo.'
                            }
                        </p>
                    </div>

                    <div className="flex flex-col gap-4">
                        {/* Bóveda Digital Buttons (Prominent) */}
                        <div className="flex flex-row gap-2 md:gap-4 justify-start lg:justify-end">
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
                                className="flex-1 lg:flex-none flex items-center justify-center gap-1 md:gap-2 px-3 py-2 md:px-6 md:py-3 rounded-xl md:rounded-2xl bg-green-500/10 text-green-400 border border-green-500/20 text-[8px] md:text-[10px] font-black uppercase tracking-widest hover:bg-green-500 hover:text-white transition-all shadow-lg shadow-green-500/0 hover:shadow-green-500/20 group/vault"
                            >
                                <Download className="h-3 w-3 md:h-4 md:w-4 group-hover/vault:scale-125 transition-transform" />
                                Bóveda Excel
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
                                className="flex-1 lg:flex-none flex items-center justify-center gap-1 md:gap-2 px-3 py-2 md:px-6 md:py-3 rounded-xl md:rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[8px] md:text-[10px] font-black uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all shadow-lg shadow-indigo-500/0 hover:shadow-indigo-500/20 group/vault"
                            >
                                <Database className="h-3 w-3 md:h-4 md:w-4 group-hover/vault:scale-125 transition-transform" />
                                Bóveda SQLite
                            </button>
                        </div>

                        {/* Fortaleza and Deseos stats */}
                        <div className="flex flex-row gap-2 md:gap-4">
                            <div className={`flex-1 flex flex-col gap-0.5 rounded-xl md:rounded-2xl bg-white/5 p-2 md:p-4 border border-white/10 backdrop-blur-xl group transition-all ${isVintageOnly ? 'hover:bg-amber-500/5 hover:border-amber-500/20' : 'hover:bg-white/10'}`}>
                                <div className={`flex items-center justify-between text-white/65 ${isVintageOnly ? 'group-hover:text-amber-500' : 'group-hover:text-brand-primary'}`}>
                                    <span className="text-[8px] md:text-[10px] font-black uppercase tracking-widest">Fortaleza</span>
                                    <Box className="h-3 w-3 md:h-4 md:w-4" />
                                </div>
                                <span className="text-2xl md:text-4xl font-black text-white">{totalOwned}</span>
                                <span className="text-[7px] md:text-[9px] font-bold text-white/20 uppercase">Items Poseídos</span>
                            </div>

                            <div className={`flex-1 flex flex-col gap-0.5 rounded-xl md:rounded-2xl p-2 md:p-4 border backdrop-blur-xl group transition-all ${isVintageOnly ? 'bg-amber-500/5 border-amber-500/20 hover:bg-amber-500/10' : 'bg-brand-primary/5 border-brand-primary/20 hover:bg-brand-primary/10'}`}>
                                <div className={`flex items-center justify-between ${isVintageOnly ? 'text-amber-500/40 group-hover:text-amber-500' : 'text-brand-primary/40 group-hover:text-brand-primary'}`}>
                                    <span className="text-[8px] md:text-[10px] font-black uppercase tracking-widest">Deseos</span>
                                    <Star className="h-3 w-3 md:h-4 md:w-4" />
                                </div>
                                <span className={`text-2xl md:text-4xl font-black ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>{totalWish}</span>
                                <span className={`text-[7px] md:text-[9px] font-bold uppercase ${isVintageOnly ? 'text-amber-500/30' : 'text-brand-primary/30'}`}>En el Radar</span>
                            </div>
                        </div>
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
                        className="grid grid-cols-2 gap-2 sm:gap-8 lg:grid-cols-3 xl:grid-cols-4 landscape:grid-cols-3"
                    >
                        {(activeTab === 'owned' ? ownedItems : wishItems).map((product) => {
                            const isGrail = product.is_grail;
                            const roi = product.grail_score || 0;

                            return (
                                <div
                                    key={product.id}
                                    className={`group flex flex-col gap-2 sm:gap-4 relative overflow-hidden transition-all duration-500 hover:translate-y-[-8px] rounded-2xl sm:rounded-[2.5rem] p-3 sm:p-6 border ${isGrail ? 'border-yellow-500/30 bg-yellow-500/10 backdrop-blur-md shadow-[0_30px_60px_-15px_rgba(234,179,8,0.2)]' : 'border-white/5 bg-black/25 backdrop-blur-md hover:bg-black/20'}`}
                                >
                                    {/* Image Container */}
                                    <div 
                                        className="relative aspect-square w-full overflow-hidden rounded-[1.5rem] sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner cursor-pointer"
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
                                        <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-40 flex items-center gap-1 sm:gap-1.5">
                                            <div className="rounded-lg sm:rounded-xl bg-black/70 px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black text-white/90 backdrop-blur-md border border-white/20 shadow-2xl uppercase tracking-widest">
                                                #{product.figure_id}
                                            </div>
                                            {isGrail && (
                                                <div className="rounded-lg sm:rounded-xl bg-yellow-500 text-black px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black backdrop-blur-md border border-yellow-400 shadow-[0_0_20px_rgba(234,179,8,0.5)] flex items-center gap-1.5">
                                                    <Trophy className="h-3 w-3" />
                                                    GRIAL
                                                </div>
                                            )}
                                        </div>

                                        {/* Status indicator */}
                                        <div className="absolute bottom-4 left-4 flex items-center gap-2">
                                            <div className={`h-2 w-2 rounded-full ${activeTab === 'owned' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]' : (isVintageOnly ? 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)] animate-pulse' : 'bg-brand-primary shadow-[0_0_10px_rgba(14,165,233,0.8)] animate-pulse')}`}></div>
                                            <span className="text-[9px] font-black text-white uppercase tracking-widest opacity-80 backdrop-blur-sm bg-black/20 px-2 py-0.5 rounded-full">
                                                {activeTab === 'owned' ? 'Poseída' : 'Prioridad'}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Info */}
                                    <div className="space-y-3 flex-1">
                                        <div className="space-y-1">
                                            <span className={`text-[9px] font-black uppercase tracking-widest transition-colors ${isVintageOnly ? 'text-amber-500 group-hover:text-amber-500/80' : 'text-brand-primary group-hover:text-brand-primary/80'}`}>
                                                {product.sub_category}
                                            </span>
                                            <h3 className="line-clamp-2 text-sm sm:text-lg font-black text-white leading-tight group-hover:text-white group-hover:translate-x-1 transition-all">
                                                {product.name}
                                            </h3>
                                        </div>

                                        <div className="flex items-center gap-1 sm:gap-1.5 pt-1 flex-nowrap overflow-hidden">
                                            {product.market_value && product.market_value > 0 && (
                                                <div className={`flex items-center gap-1 px-2 py-1 sm:px-3 sm:py-1.5 rounded-lg sm:rounded-xl border font-black text-[8px] sm:text-[10px] whitespace-nowrap ${isGrail ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : (isVintageOnly ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20')}`}>
                                                    <Euro className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                                                    {product.market_value}€
                                                </div>
                                            )}
                                            {roi > 0 && activeTab === 'owned' && (
                                                <div className="flex items-center gap-1 px-2 py-1 sm:px-3 sm:py-1.5 rounded-lg sm:rounded-xl bg-green-500/10 text-green-400 border border-green-500/20 font-black text-[8px] sm:text-[10px] whitespace-nowrap">
                                        <TrendingUp className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                                                    +{roi}%
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Multi-Actions Bar */}
                                    <div className="mt-auto flex items-center gap-1 sm:gap-2">
                                        <button
                                            onClick={() => {
                                                setSelectedProduct(product);
                                                setIsDetailOpen(true);
                                            }}
                                            className="h-6 sm:h-8 flex-1 flex items-center justify-center rounded-lg sm:rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-white/10 hover:text-white transition-all group/info"
                                        >
                                            <Info className="h-5 w-5 group-hover:scale-110 transition-transform" />
                                        </button>

                                        {isAdmin && (
                                            <>
                                                <button
                                                    onClick={() => setEditingProduct(product)}
                                                    className="h-6 sm:h-8 px-2 flex items-center justify-center rounded-lg sm:rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-white/10 hover:text-white transition-all"
                                                    title="Editar metadatos"
                                                >
                                                    <Settings className="h-4 w-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteProduct(product)}
                                                    className="h-6 sm:h-8 px-2 flex items-center justify-center rounded-lg sm:rounded-xl bg-white/5 border border-white/5 text-white/60 hover:bg-red-500/20 hover:text-red-400 transition-all"
                                                    title="Eliminar y devolver al Purgatorio"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </>
                                        )}

                                        {activeTab === 'wish' ? (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: false })}
                                                disabled={toggleMutation.isPending}
                                                className={`h-6 sm:h-8 px-3 sm:px-6 flex items-center justify-center gap-1.5 sm:gap-3 rounded-lg sm:rounded-xl font-black text-[10px] sm:text-xs uppercase tracking-widest shadow-lg transition-all ${isVintageOnly ? 'bg-amber-500 text-black border border-amber-500/50 shadow-amber-500/20 hover:brightness-110' : 'bg-brand-primary text-white border border-brand-primary/50 shadow-brand-primary/20 hover:brightness-110'}`}
                                            >
                                                {toggleMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin text-white/50" /> : <ShoppingCart className={`h-4 w-4 ${isVintageOnly ? 'text-black' : 'text-white'}`} />}
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
                                                className={`h-6 sm:h-8 px-3 sm:px-6 flex items-center justify-center gap-1.5 sm:gap-3 rounded-lg sm:rounded-xl font-black text-[10px] sm:text-xs uppercase tracking-widest border transition-all group/action flex-1 ${
                                                    isVintageOnly 
                                                        ? 'bg-amber-500/10 text-amber-500 border-amber-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30' 
                                                        : 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30'
                                                }`}
                                            >
                                                {toggleMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin text-white/50" /> : (
                                                    <>
                                                        <Check className="h-4 w-4 group-hover/action:hidden" />
                                                        <Box className="h-4 w-4 hidden group-hover/action:block" />
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
                                                className="h-6 sm:h-8 px-3 flex items-center justify-center rounded-lg sm:rounded-xl bg-red-500/5 text-red-500/30 border border-red-500/10 hover:bg-red-500 hover:text-white transition-all"
                                                title="Eliminar de Deseos"
                                            >
                                                <Star className="h-4 w-4 fill-current" />
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
