import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Box, AlertCircle, Loader2, Info, Check, Trophy, TrendingUp, Euro, Star, ShoppingCart, Sparkles, Download, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';

interface CollectionProps {
    searchQuery?: string;
}

const Collection: React.FC<CollectionProps> = ({ searchQuery = "" }) => {
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState<'owned' | 'wish'>('owned');

    // Contexto de Autenticación (Fase 8.2)
    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');

    // 1. Fetch de la colección (basada en el ID activo)
    const { data: collection, isLoading, isError } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId],
        queryFn: () => getCollection(activeUserId)
    });

    // 2. Mutación para alternar estado
    const toggleMutation = useMutation({
        mutationFn: ({ productId, wish }: { productId: number, wish: boolean }) => toggleCollection(productId, activeUserId, wish),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', activeUserId] });
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
        return (
            <div className="flex h-[60vh] flex-col items-center justify-center gap-4 text-white/50">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-medium animate-pulse text-brand-primary/80 uppercase tracking-widest">Sincronizando con la Fortaleza...</p>
            </div>
        );
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
        <div className="space-y-10 animate-in fade-in duration-700 pb-20">
            {/* Header & Stats Banner */}
            <div className="relative overflow-hidden rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.04] to-black p-8 md:p-10 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-3xl"></div>
                <div className="absolute -left-20 -bottom-20 h-48 w-48 rounded-full bg-purple-500/10 blur-3xl"></div>

                <div className="relative flex flex-col gap-10 lg:flex-row lg:items-center lg:justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-brand-primary">
                            <Box className="h-6 w-6" />
                            <span className="text-xs font-black uppercase tracking-[0.3em] opacity-80">Archivos de Nueva Eternia</span>
                        </div>
                        <h2 className="text-5xl font-black tracking-tighter text-white lg:text-7xl">
                            Mi <span className="text-brand-primary">Legado</span>
                        </h2>
                        <p className="max-w-md text-sm leading-relaxed text-white/40 font-medium">
                            Coleccionando no solo figuras, sino fragmentos de historia y valor en el tiempo.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        {/* Bóveda Digital Buttons (Prominent) */}
                        <div className="flex flex-col gap-2 justify-center">
                            <button
                                onClick={async () => {
                                    try {
                                        const { exportCollectionExcel } = await import('../api/admin');
                                        await exportCollectionExcel(activeUserId);
                                        alert('📊 Excel: Tu colección ha sido exportada con éxito.');
                                    } catch (error) {
                                        console.error('Export error:', error);
                                        alert('❌ Error al exportar Excel.');
                                    }
                                }}
                                className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-green-500/10 text-green-400 border border-green-500/20 text-[10px] font-black uppercase tracking-widest hover:bg-green-500 hover:text-white transition-all shadow-lg shadow-green-500/0 hover:shadow-green-500/20 group/vault"
                            >
                                <Download className="h-4 w-4 group-hover/vault:scale-125 transition-transform" />
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
                                className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-black uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all shadow-lg shadow-indigo-500/0 hover:shadow-indigo-500/20 group/vault"
                            >
                                <Database className="h-4 w-4 group-hover/vault:scale-125 transition-transform" />
                                Bóveda SQLite
                            </button>
                        </div>

                        <div className="flex flex-col gap-1 rounded-[2rem] bg-white/5 p-6 border border-white/10 backdrop-blur-xl min-w-[160px] group hover:bg-white/10 transition-all">
                            <div className="flex items-center justify-between text-white/40 group-hover:text-brand-primary">
                                <span className="text-[10px] font-black uppercase tracking-widest">Fortaleza</span>
                                <Box className="h-4 w-4" />
                            </div>
                            <span className="text-4xl font-black text-white">{totalOwned}</span>
                            <span className="text-[9px] font-bold text-white/20 uppercase">Items Poseídos</span>
                        </div>

                        <div className="flex flex-col gap-1 rounded-[2rem] bg-brand-primary/5 p-6 border border-brand-primary/20 backdrop-blur-xl min-w-[160px] group hover:bg-brand-primary/10 transition-all">
                            <div className="flex items-center justify-between text-brand-primary/40 group-hover:text-brand-primary">
                                <span className="text-[10px] font-black uppercase tracking-widest">Deseos</span>
                                <Star className="h-4 w-4" />
                            </div>
                            <span className="text-4xl font-black text-brand-primary">{totalWish}</span>
                            <span className="text-[9px] font-bold text-brand-primary/30 uppercase">En el Radar</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex bg-white/5 p-1.5 rounded-[2rem] border border-white/10 backdrop-blur-3xl w-fit">
                <button
                    onClick={() => setActiveTab('owned')}
                    className={`flex items-center gap-3 px-8 py-3.5 rounded-full text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'owned' ? 'bg-brand-primary text-white shadow-xl shadow-brand-primary/20 scale-105' : 'text-white/30 hover:text-white'}`}
                >
                    <Box className="h-4 w-4" />
                    La Fortaleza
                </button>
                <button
                    onClick={() => setActiveTab('wish')}
                    className={`flex items-center gap-3 px-8 py-3.5 rounded-full text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'wish' ? 'bg-brand-primary text-white shadow-xl shadow-brand-primary/20 scale-105' : 'text-white/30 hover:text-white'}`}
                >
                    <Star className="h-4 w-4" />
                    Lista de Deseos
                    {totalWish > 0 && (
                        <span className="bg-white/10 text-brand-primary text-[10px] px-2 py-0.5 rounded-full ml-1">
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
                            <Sparkles className="absolute -top-2 -right-2 h-6 w-6 text-brand-primary opacity-30 animate-pulse" />
                        </div>
                        <div className="max-w-xs space-y-3">
                            <p className="text-2xl font-black text-white/80 uppercase tracking-tighter">
                                {searchQuery ? 'Sin Resultados' : 'Sector Vacío'}
                            </p>
                            <p className="text-sm text-white/40 leading-relaxed font-medium">
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
                        className="grid grid-cols-2 gap-4 sm:gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
                    >
                        {(activeTab === 'owned' ? ownedItems : wishItems).map((product) => {
                            const isGrail = product.is_grail;
                            const roi = product.grail_score || 0;

                            return (
                                <div
                                    key={product.id}
                                    className={`group flex flex-col gap-4 relative overflow-hidden transition-all duration-500 hover:translate-y-[-8px] rounded-[2rem] sm:rounded-[2.5rem] p-4 sm:p-6 border ${isGrail ? 'border-yellow-500/30 bg-yellow-500/[0.03] shadow-[0_30px_60px_-15px_rgba(234,179,8,0.2)]' : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.04]'}`}
                                >
                                    {/* Image Container */}
                                    <div className="relative aspect-square w-full overflow-hidden rounded-[1.5rem] sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner">
                                        {product.image_url ? (
                                            <img src={product.image_url} className="h-full w-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1" />
                                        ) : (
                                            <div className="flex h-full w-full items-center justify-center text-[10px] text-white/10 font-black uppercase tracking-widest">No Image</div>
                                        )}

                                        {/* Corner Badges */}
                                        <div className="absolute top-3 right-3 sm:top-4 sm:right-4 z-10 flex flex-col gap-2">
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
                                            <div className={`h-2 w-2 rounded-full ${activeTab === 'owned' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]' : 'bg-brand-primary shadow-[0_0_10px_rgba(14,165,233,0.8)] animate-pulse'}`}></div>
                                            <span className="text-[9px] font-black text-white uppercase tracking-widest opacity-80 backdrop-blur-sm bg-black/20 px-2 py-0.5 rounded-full">
                                                {activeTab === 'owned' ? 'Poseída' : 'Prioridad'}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Info */}
                                    <div className="space-y-3 flex-1">
                                        <div className="space-y-1">
                                            <span className="text-[9px] font-black text-white/20 uppercase tracking-widest group-hover:text-brand-primary/60 transition-colors">
                                                {product.sub_category}
                                            </span>
                                            <h3 className="line-clamp-2 text-sm sm:text-lg font-black text-white leading-tight group-hover:text-white group-hover:translate-x-1 transition-all">
                                                {product.name}
                                            </h3>
                                        </div>

                                        <div className="flex flex-wrap gap-2 pt-1">
                                            {product.market_value && product.market_value > 0 && (
                                                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border font-black text-[10px] ${isGrail ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20'}`}>
                                                    <Euro className="h-3 w-3" />
                                                    {product.market_value}
                                                </div>
                                            )}
                                            {roi > 0 && activeTab === 'owned' && (
                                                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-green-500/10 text-green-400 border border-green-500/20 font-black text-[10px]">
                                                    <TrendingUp className="h-3 w-3" />
                                                    +{roi}%
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Multi-Actions Bar */}
                                    <div className="mt-auto flex items-center gap-2">
                                        <button className="h-12 flex-1 flex items-center justify-center rounded-2xl bg-white/5 border border-white/5 text-white/30 hover:bg-white/10 hover:text-white transition-all group/info">
                                            <Info className="h-5 w-5 group-hover:scale-110 transition-transform" />
                                        </button>

                                        {activeTab === 'wish' ? (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: false })}
                                                disabled={toggleMutation.isPending}
                                                className="h-12 px-6 flex items-center gap-3 rounded-2xl bg-brand-primary text-white font-black text-xs uppercase tracking-widest shadow-lg shadow-brand-primary/20 hover:brightness-110 transition-all border border-brand-primary/50"
                                            >
                                                {toggleMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShoppingCart className="h-4 w-4" />}
                                                Reclamar
                                            </button>
                                        ) : (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: false })}
                                                disabled={toggleMutation.isPending}
                                                className="h-12 px-6 flex items-center gap-3 rounded-2xl bg-green-500/10 text-green-400 font-black text-xs uppercase tracking-widest border border-green-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30 transition-all group/action"
                                            >
                                                {toggleMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : (
                                                    <>
                                                        <Check className="h-4 w-4 group-hover/action:hidden" />
                                                        <Box className="h-4 w-4 hidden group-hover/action:block" />
                                                    </>
                                                )}
                                                <span className="group-hover/action:hidden">En Sanctum</span>
                                                <span className="hidden group-hover/action:block">Liberar</span>
                                            </button>
                                        )}

                                        {activeTab === 'wish' && (
                                            <button
                                                onClick={() => toggleMutation.mutate({ productId: product.id, wish: true })}
                                                disabled={toggleMutation.isPending}
                                                className="h-12 px-4 flex items-center justify-center rounded-2xl bg-red-500/5 text-red-500/30 border border-red-500/10 hover:bg-red-500 hover:text-white transition-all"
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
        </div>
    );
};

export default Collection;
