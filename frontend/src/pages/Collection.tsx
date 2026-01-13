import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Box, AlertCircle, Loader2, Info, Check, Database, Trophy, TrendingUp, Euro } from 'lucide-react';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';

const DAVID_USER_ID = 2;

const Collection: React.FC = () => {
    const queryClient = useQueryClient();

    // 1. Fetch de la colección de David
    const { data: collection, isLoading, isError } = useQuery<Product[]>({
        queryKey: ['collection', DAVID_USER_ID],
        queryFn: () => getCollection(DAVID_USER_ID)
    });

    // 2. Mutación para quitar de la colección
    const toggleMutation = useMutation({
        mutationFn: (productId: number) => toggleCollection(productId, DAVID_USER_ID),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', DAVID_USER_ID] });
        }
    });

    if (isLoading) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/50">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-medium animate-pulse text-brand-primary/80">Abriendo las puertas de la Fortaleza...</p>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium italic">La conexión con la Fortaleza se ha perdido...</p>
                {/* Debug info - Remove in prod */}
                <p className="text-xs opacity-50 font-mono bg-black/20 p-2 rounded">
                    {(isError as any)?.message || "Error desconocido"}
                </p>
            </div>
        );
    }

    if (!collection || collection.length === 0) {
        return (
            <div className="flex min-h-[400px] flex-col items-center justify-center gap-6 rounded-3xl border-2 border-dashed border-white/5 bg-white/[0.02] p-12 text-center backdrop-blur-sm">
                <div className="relative">
                    <div className="absolute inset-0 animate-ping rounded-full bg-brand-primary/20"></div>
                    <Box className="relative h-16 w-16 text-white/20" />
                </div>
                <div className="max-w-xs space-y-2">
                    <p className="text-xl font-bold text-white/80">Tu Fortaleza está desolada</p>
                    <p className="text-sm text-white/40 leading-relaxed">
                        Aún no has reclamado ninguna reliquia de Eternia. Ve al Catálogo Maestro y comienza tu colección hoy mismo.
                    </p>
                </div>
                <button
                    onClick={() => window.location.reload()} // Simplified way to "go back" if App.tsx uses state
                    className="mt-4 rounded-xl bg-brand-primary/10 px-6 py-2.5 text-sm font-bold text-brand-primary border border-brand-primary/20 hover:bg-brand-primary/20 transition-all shadow-[0_0_20px_rgba(14,165,233,0.15)]"
                >
                    Explorar el Catálogo
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Stats Header */}
            <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.03] to-white/[0.01] p-8 backdrop-blur-xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/5 blur-3xl"></div>

                <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Box className="h-5 w-5" />
                            <span className="text-xs font-black uppercase tracking-widest opacity-70">Sanctum Sanctorum</span>
                        </div>
                        <h2 className="text-4xl font-black tracking-tight text-white lg:text-5xl">Mi Fortaleza</h2>
                        <p className="max-w-md text-sm leading-relaxed text-white/50">
                            Custodiando las reliquias más valiosas de Nueva Eternia. Cada pieza cuenta una historia de conquista.
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col items-center justify-center rounded-2xl bg-white/5 p-4 border border-white/5 backdrop-blur-md">
                            <span className="text-2xl font-black text-white">{collection.length}</span>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-white/40">Reliquias</span>
                        </div>
                        <div className="flex flex-col items-center justify-center rounded-2xl bg-green-500/10 p-4 border border-green-500/20 backdrop-blur-md">
                            <span className="text-2xl font-black text-green-400">100%</span>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-green-400/60">Purificadas</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-2 gap-3 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {collection.map((product) => {
                    const isGrail = product.is_grail;
                    const roi = product.grail_score || 0;

                    return (
                        <div key={product.id} className={`glass-card group flex flex-col gap-2 sm:gap-4 relative overflow-hidden transition-all hover:translate-y-[-4px] rounded-2xl sm:rounded-3xl p-3 sm:p-5 ${isGrail ? 'border-yellow-500/50 shadow-[0_0_20px_rgba(234,179,8,0.2)]' : ''}`}>
                            {/* Grail Shine Effect */}
                            {isGrail && (
                                <div className="absolute inset-0 bg-gradient-to-tr from-yellow-500/10 via-transparent to-transparent pointer-events-none animate-pulse"></div>
                            )}

                            {/* Status Glow */}
                            <div className="absolute inset-0 bg-gradient-to-t from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

                            {/* Image */}
                            <div className="aspect-square w-full overflow-hidden rounded-xl sm:rounded-2xl bg-white/5 border border-white/10 relative">
                                {product.image_url ? (
                                    <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center bg-white/5 italic text-white/10 text-[10px] sm:text-xs text-center p-2 sm:p-4">
                                        {product.name}
                                    </div>
                                )}
                                <div className="absolute top-2 right-2 sm:top-3 sm:right-3 rounded-md sm:rounded-lg bg-black/60 px-1.5 py-0.5 sm:px-2.5 sm:py-1 text-[8px] sm:text-[10px] font-black text-white/90 backdrop-blur-md border border-white/20 shadow-xl z-10">
                                    #{product.figure_id}
                                </div>

                                {/* Grail Badge */}
                                {isGrail && (
                                    <div className="absolute top-2 left-2 sm:top-3 sm:left-3 rounded-md sm:rounded-lg bg-gradient-to-r from-yellow-600 to-yellow-500 px-1.5 py-0.5 sm:px-2.5 sm:py-1 text-[8px] sm:text-[10px] font-black text-black backdrop-blur-md border border-yellow-400 shadow-[0_0_10px_rgba(234,179,8,0.4)] z-10 flex items-center gap-1 animate-in zoom-in duration-300">
                                        <Trophy className="h-2 w-2 sm:h-3 sm:w-3" />
                                        GRIAL
                                    </div>
                                )}

                                {/* Ownership pulse */}
                                <div className="absolute bottom-2 left-2 sm:bottom-3 sm:left-3 flex h-1.5 w-1.5 sm:h-2 sm:w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-full w-full bg-green-500"></span>
                                </div>
                            </div>

                            {/* Info */}
                            <div className="space-y-1 sm:space-y-3">
                                <h3 className="line-clamp-2 text-xs sm:text-sm font-bold text-white/95 leading-tight group-hover:text-green-400 transition-colors min-h-[2.5em]">
                                    {product.name}
                                </h3>
                                <div className="flex flex-wrap gap-1 sm:gap-2">
                                    <span className="flex items-center gap-1 rounded-md bg-white/5 px-1.5 py-0.5 sm:px-2 sm:py-1 text-[9px] sm:text-[10px] font-bold text-white/40 border border-white/5">
                                        <Database className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                                        {product.sub_category}
                                    </span>

                                    {/* Market Value Badge */}
                                    {product.market_value && product.market_value > 0 && (
                                        <span className={`flex items-center gap-1 rounded-md px-1.5 py-0.5 sm:px-2 sm:py-1 text-[9px] sm:text-[10px] font-bold border ${isGrail ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'}`}>
                                            <Euro className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                                            {product.market_value}
                                        </span>
                                    )}

                                    {/* ROI Badge */}
                                    {roi > 0 && (
                                        <span className="flex items-center gap-1 rounded-md bg-green-500/10 px-1.5 py-0.5 sm:px-2 sm:py-1 text-[9px] sm:text-[10px] font-bold text-green-400 border border-green-500/20">
                                            <TrendingUp className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                                            +{roi}%
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                                <button className="flex-1 flex items-center justify-center gap-1 sm:gap-2 rounded-lg sm:rounded-xl bg-white/5 px-2 py-1.5 sm:px-3 sm:py-2 text-[10px] sm:text-xs font-bold text-white/60 hover:bg-white/10 hover:text-white transition-all border border-white/5">
                                    <Info className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
                                    <span className="hidden sm:inline">Detalles</span>
                                </button>

                                <button
                                    onClick={() => toggleMutation.mutate(product.id)}
                                    disabled={toggleMutation.isPending}
                                    className="flex-1 flex items-center justify-center gap-1 sm:gap-2 rounded-lg sm:rounded-xl px-2 py-1.5 sm:px-3 sm:py-2 text-[10px] sm:text-xs font-black transition-all border shadow-[0_0_15px_rgba(34,197,94,0)] bg-green-500/10 text-green-400 border-green-500/20 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30 hover:shadow-[0_0_15px_rgba(239,68,68,0.2)] group/btn"
                                >
                                    <span className="group-hover/btn:hidden transition-all flex items-center gap-1.5 sm:gap-2">
                                        <Check className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
                                        <span className="hidden sm:inline">Cautivo</span>
                                    </span>
                                    <span className="hidden group-hover/btn:flex items-center gap-1.5 sm:gap-2">
                                        <Box className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
                                        <span className="hidden sm:inline">Liberar</span>
                                    </span>
                                </button>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    );
};

export default Collection;
