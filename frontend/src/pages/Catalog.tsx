import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Package, AlertCircle, Loader2, Info, Plus, Check } from 'lucide-react';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';

// Para desarrollo, usamos el ID de David
const DAVID_USER_ID = 2;

const Catalog: React.FC = () => {
    const queryClient = useQueryClient();

    // 1. Fetch de todos los productos
    const { data: products, isLoading: isLoadingProducts, isError: isErrorProducts } = useQuery<Product[]>({
        queryKey: ['products'],
        queryFn: async () => {
            const response = await axios.get('http://localhost:8000/api/products');
            return response.data;
        }
    });

    // 2. Fetch de la colección de David
    const { data: collection, isLoading: isLoadingCollection } = useQuery<Product[]>({
        queryKey: ['collection', DAVID_USER_ID],
        queryFn: () => getCollection(DAVID_USER_ID)
    });

    // 3. Mutación para alternar estado (Optimistic Updates)
    const toggleMutation = useMutation({
        mutationFn: (productId: number) => toggleCollection(productId, DAVID_USER_ID),
        onMutate: async (productId) => {
            // Cancelar refetches salientes
            await queryClient.cancelQueries({ queryKey: ['collection', DAVID_USER_ID] });

            // Snapshot del estado previo
            const previousCollection = queryClient.getQueryData<Product[]>(['collection', DAVID_USER_ID]);

            // Actualizar el cache de forma optimista
            queryClient.setQueryData<Product[]>(['collection', DAVID_USER_ID], (old) => {
                const alreadyOwned = old?.some(p => p.id === productId);
                if (alreadyOwned) {
                    return old?.filter(p => p.id !== productId);
                } else {
                    const productToAdd = products?.find(p => p.id === productId);
                    return old ? [...old, productToAdd!] : [productToAdd!];
                }
            });

            return { previousCollection };
        },
        onError: (_, __, context) => {
            // Revertir si hay error
            if (context?.previousCollection) {
                queryClient.setQueryData(['collection', DAVID_USER_ID], context.previousCollection);
            }
        },
        onSettled: () => {
            // Refrescar al final para sincronizar con la verdad del servidor
            queryClient.invalidateQueries({ queryKey: ['collection', DAVID_USER_ID] });
        }
    });

    const isOwned = (productId: number) => {
        return collection?.some(p => p.id === productId);
    };

    if (isLoadingProducts || isLoadingCollection) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/50">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-medium animate-pulse">Sincronizando con Eternia...</p>
            </div>
        );
    }

    if (isErrorProducts) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al conectar con la API Broker</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="space-y-1">
                    <h2 className="text-3xl font-bold tracking-tight text-white">Eternia</h2>
                    <p className="text-sm text-white/50">Visualización de los {products?.length} productos purificados en Supabase.</p>
                </div>
                <div className="flex items-center gap-2 rounded-full bg-brand-primary/10 px-4 py-2 border border-brand-primary/20">
                    <Package className="h-4 w-4 text-brand-primary" />
                    <span className="text-xs font-bold text-brand-primary">{products?.length} Items</span>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {products?.map((product) => {
                    const owned = isOwned(product.id);
                    return (
                        <div key={product.id} className="glass-card group flex flex-col gap-4 relative overflow-hidden transition-all duration-300 hover:translate-y-[-4px] hover:shadow-[0_20px_40px_rgba(0,0,0,0.3)]">
                            {/* Owned Badge (Small Corner indicator) */}
                            {owned && (
                                <div className="absolute top-0 left-0 w-12 h-12 overflow-hidden z-10 transition-transform group-hover:scale-110">
                                    <div className="bg-green-500 text-white text-[8px] font-black uppercase text-center w-[60px] py-0.5 absolute rotate-[-45deg] left-[-20px] top-[10px] shadow-lg">
                                        Cautivo
                                    </div>
                                </div>
                            )}

                            {/* Image Placeholder / Actual Image */}
                            <div className="aspect-square w-full overflow-hidden rounded-xl bg-white/5 border border-white/10 relative">
                                {product.image_url ? (
                                    <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center italic text-white/20 text-xs">
                                        Sin imagen
                                    </div>
                                )}
                                <div className="absolute top-3 right-3 rounded-lg bg-black/60 px-2.5 py-1 text-[10px] font-black text-white/90 backdrop-blur-md border border-white/20 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity">
                                    #{product.figure_id}
                                </div>
                            </div>

                            {/* Info */}
                            <div className="space-y-2">
                                <div className="flex items-start justify-between gap-2">
                                    <h3 className="line-clamp-2 text-sm font-bold text-white/90 group-hover:text-brand-primary transition-colors leading-tight">
                                        {product.name}
                                    </h3>
                                </div>
                                <div className="flex flex-wrap gap-1.5">
                                    <span className="rounded-md bg-white/5 px-2 py-0.5 text-[10px] font-bold text-white/40 border border-white/5 group-hover:border-brand-primary/20 transition-colors">
                                        {product.sub_category}
                                    </span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                                <button className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium text-white/60 hover:bg-white/10 hover:text-white transition-all border border-white/5">
                                    <Info className="h-3.5 w-3.5" />
                                    Detalles
                                </button>

                                <button
                                    onClick={() => toggleMutation.mutate(product.id)}
                                    disabled={toggleMutation.isPending}
                                    className={`flex items-center gap-2 rounded-xl px-4 py-1.5 text-xs font-black transition-all border shadow-lg ${owned
                                        ? 'bg-green-500/20 text-green-400 border-green-500/30 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30'
                                        : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20 hover:bg-brand-primary/20 hover:shadow-[0_0_15px_rgba(14,165,233,0.3)]'
                                        } ${toggleMutation.isPending ? 'opacity-50 cursor-wait' : ''}`}
                                >
                                    {owned ? <Check className={`h-3.5 w-3.5 ${toggleMutation.isPending ? 'animate-spin' : ''}`} /> : <Plus className={`h-3.5 w-3.5 ${toggleMutation.isPending ? 'animate-bounce' : ''}`} />}
                                    {owned ? 'Cautivo' : 'Capturar'}
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Catalog;
