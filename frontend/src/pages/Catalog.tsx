import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Package, AlertCircle, Loader2, Info, Plus, Check, ShoppingCart } from 'lucide-react';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

// Para desarrollo, usamos el ID de David
const DAVID_USER_ID = 2;

const Catalog: React.FC = () => {
    const queryClient = useQueryClient();
    const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);

    // 1. Fetch de todos los productos
    const { data: products, isLoading: isLoadingProducts, isError: isErrorProducts } = useQuery<Product[]>({
        queryKey: ['products'],
        queryFn: async () => {
            const response = await axios.get('/api/products');
            return response.data;
        }
    });

    // 2. Fetch de la colección de David
    const { data: collection, isLoading: isLoadingCollection } = useQuery<Product[]>({
        queryKey: ['collection', DAVID_USER_ID],
        queryFn: () => getCollection(DAVID_USER_ID)
    });

    // 3. Fetch de ofertas del producto seleccionado
    const { data: productOffers, isLoading: isLoadingOffers } = useQuery<any[]>({
        queryKey: ['product-offers', selectedProduct?.id],
        queryFn: async () => {
            if (!selectedProduct) return [];
            const response = await axios.get(`/api/products/${selectedProduct.id}/offers`);
            return response.data;
        },
        enabled: !!selectedProduct
    });

    // 4. Fetch de IDs de productos con ofertas activas (inteligencia de mercado)
    const { data: productsWithOffers } = useQuery<number[]>({
        queryKey: ['products-with-offers'],
        queryFn: async () => {
            const response = await axios.get('/api/products/with-offers');
            return response.data;
        }
    });

    const hasMarketIntel = (productId: number) => productsWithOffers?.includes(productId);

    // 4. Mutación para alternar estado (Optimistic Updates)
    const toggleMutation = useMutation({
        mutationFn: (productId: number) => toggleCollection(productId, DAVID_USER_ID),
        onMutate: async (productId) => {
            await queryClient.cancelQueries({ queryKey: ['collection', DAVID_USER_ID] });
            const previousCollection = queryClient.getQueryData<Product[]>(['collection', DAVID_USER_ID]);

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
            if (context?.previousCollection) {
                queryClient.setQueryData(['collection', DAVID_USER_ID], context.previousCollection);
            }
        },
        onSettled: () => {
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
        <div className="space-y-10 animate-in fade-in duration-1000">
            {/* Header / Search Area */}
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1">
                    <h2 className="text-4xl font-black tracking-tighter text-white">Eternia</h2>
                    <p className="text-sm font-bold text-white/30 uppercase tracking-widest">Almacén Sagrado de Reliquias</p>
                </div>
                <div className="flex items-center gap-3 rounded-2xl bg-white/[0.03] px-6 py-3 border border-white/5 backdrop-blur-3xl">
                    <Package className="h-5 w-5 text-brand-primary" />
                    <span className="text-2xl font-black text-white">{products?.length}</span>
                    <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] pt-1">Modelos Purificados</span>
                </div>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-2 gap-3 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {products?.map((product) => {
                    const owned = isOwned(product.id);
                    const hasIntel = hasMarketIntel(product.id);
                    return (
                        <div
                            key={product.id}
                            className={`group relative flex flex-col gap-2 sm:gap-5 rounded-3xl sm:rounded-[2.5rem] border p-2.5 sm:p-5 transition-all duration-500 hover:translate-y-[-8px] ${hasIntel
                                ? 'border-brand-primary/30 bg-brand-primary/[0.03] shadow-[0_0_20px_-5px_rgba(14,165,233,0.15)] hover:shadow-[0_40px_80px_-20px_rgba(14,165,233,0.2)]'
                                : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.05] hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.5)]'
                                }`}
                        >
                            {/* Market Intel Badge */}
                            {hasIntel && (
                                <div className="absolute top-2 right-2 sm:top-4 sm:right-4 z-20 flex items-center gap-1 rounded-lg sm:rounded-xl bg-brand-primary/10 px-1.5 py-0.5 sm:px-2.5 sm:py-1 border border-brand-primary/20 backdrop-blur-md">
                                    <span className="h-1 w-1 sm:h-1.5 sm:w-1.5 rounded-full bg-brand-primary animate-pulse"></span>
                                    <span className="text-[6px] sm:text-[8px] font-black uppercase tracking-widest text-brand-primary">Live</span>
                                </div>
                            )}

                            {/* Owned Badge (Small Corner indicator) */}
                            {owned && (
                                <div className="absolute top-0 left-0 w-12 h-12 sm:w-16 sm:h-16 overflow-hidden z-20">
                                    <div className="bg-green-500 text-white text-[7px] sm:text-[9px] font-black uppercase text-center w-[80px] sm:w-[100px] py-0.5 sm:py-1 absolute rotate-[-45deg] left-[-25px] sm:left-[-30px] top-[10px] sm:top-[15px] shadow-[0_5px_15px_rgba(34,197,94,0.4)] border-b border-white/20">
                                        Cautivo
                                    </div>
                                </div>
                            )}

                            {/* Image Container */}
                            <div className="relative aspect-square w-full overflow-hidden rounded-2xl sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner group/img">
                                {product.image_url ? (
                                    <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="h-full w-full object-cover transition-all duration-700 group-hover/img:scale-110 group-hover/img:rotate-1"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center italic text-white/20 text-[10px] sm:text-xs font-black uppercase tracking-widest">
                                        Sin Imagen
                                    </div>
                                )}
                                <div className="absolute top-2 right-2 sm:top-4 sm:right-4 rounded-lg sm:rounded-xl bg-black/70 px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black text-brand-primary backdrop-blur-md border border-brand-primary/20 shadow-2xl opacity-0 group-hover:opacity-100 transition-all transform translate-y-[-10px] group-hover:translate-y-0 uppercase tracking-widest">
                                    #{product.figure_id}
                                </div>
                            </div>

                            {/* Content */}
                            <div className="flex flex-1 flex-col gap-2 sm:gap-3 px-1">
                                <div className="space-y-0.5 sm:space-y-1">
                                    <span className="text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-white/20 group-hover:text-brand-primary/50 transition-colors line-clamp-1">
                                        {product.sub_category}
                                    </span>
                                    <h3 className="line-clamp-2 min-h-[2rem] sm:min-h-[2.5rem] text-xs sm:text-lg font-black leading-tight text-white group-hover:text-brand-primary transition-colors">
                                        {product.name}
                                    </h3>
                                </div>

                                <div className="mt-auto flex items-center justify-between pt-2 sm:pt-4 gap-2 sm:gap-3">
                                    {/* Action Button: Detail View */}
                                    <button
                                        onClick={() => setSelectedProduct(product)}
                                        className="flex flex-1 items-center justify-center gap-1.5 sm:gap-2 rounded-xl sm:rounded-2xl bg-white/5 py-2 sm:py-2.5 text-[10px] sm:text-xs font-black uppercase tracking-widest text-white/40 border border-white/5 transition-all hover:bg-brand-primary/20 hover:text-brand-primary hover:border-brand-primary/40 group/btn"
                                    >
                                        <Info className="h-3 w-3 sm:h-4 sm:w-4 transition-transform group-hover/btn:scale-120" />
                                        <span className="hidden sm:inline">Mercado</span>
                                        <span className="sm:hidden">Ver</span>
                                    </button>

                                    {/* Action: Toggle Collection */}
                                    <button
                                        onClick={() => toggleMutation.mutate(product.id)}
                                        disabled={toggleMutation.isPending}
                                        className={`flex h-8 w-8 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl transition-all border shadow-lg ${owned
                                            ? 'bg-green-500/20 text-green-400 border-green-500/30 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30'
                                            : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20 hover:bg-brand-primary/20 hover:shadow-[0_0_20px_rgba(14,165,233,0.3)]'
                                            } ${toggleMutation.isPending ? 'opacity-50 cursor-wait' : ''}`}
                                        title={owned ? 'Liberar del Catálogo' : 'Asegurar en la Fortaleza'}
                                    >
                                        {owned ? <Check className="h-3 w-3 sm:h-5 sm:w-5" /> : <Plus className="h-3 w-3 sm:h-5 sm:w-5" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* PRODUCT DETAIL MODAL (OFFERS) */}
            {selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in fade-in duration-300">
                    <div
                        className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-[3rem] border border-white/10 bg-[#0A0A0B] shadow-[0_50px_100px_-20px_rgba(0,0,0,1)] flex flex-col"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Modal Header */}
                        <div className="p-8 pb-4 flex items-start justify-between">
                            <div className="flex gap-6 items-center">
                                <div className="h-24 w-24 shrink-0 overflow-hidden rounded-3xl border border-white/10 bg-black/40">
                                    <img src={selectedProduct.image_url || ''} className="h-full w-full object-cover" />
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-3xl font-black tracking-tighter text-white leading-none">
                                        Analítica de <span className="text-brand-primary">Precios</span>
                                    </h4>
                                    <p className="text-sm font-bold text-white/30 uppercase tracking-widest">{selectedProduct.name}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedProduct(null)}
                                className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:bg-red-500/20 hover:text-red-400 transition-all"
                            >
                                <span className="text-2xl">&times;</span>
                            </button>
                        </div>

                        {/* Modal Body: Price List */}
                        <div className="flex-1 overflow-y-auto p-8 pt-4 custom-scrollbar">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between px-4">
                                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">La Verdad del Mercado</h5>
                                    <span className="text-[10px] font-black text-brand-primary uppercase">Mejor Oferta Disponible</span>
                                </div>

                                {isLoadingOffers ? (
                                    <div className="flex h-40 items-center justify-center gap-3">
                                        <Loader2 className="h-6 w-6 animate-spin text-brand-primary" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-white/20">Consultando Mercaderes...</span>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {productOffers?.map((offer) => (
                                            <div
                                                key={offer.id}
                                                className={`group flex items-center justify-between gap-4 rounded-3xl p-5 transition-all border ${offer.is_best ? 'bg-brand-primary/5 border-brand-primary/30 shadow-[0_0_30px_rgba(14,165,233,0.1)]' : 'bg-white/[0.03] border-white/5 hover:bg-white/[0.05]'}`}
                                            >
                                                <div className="flex items-center gap-6 flex-1">
                                                    <div className="space-y-1">
                                                        <div className="flex items-center gap-3">
                                                            <span className="text-xs font-black uppercase tracking-widest text-white/80">{offer.shop_name}</span>
                                                            {offer.is_best && (
                                                                <span className="rounded-full bg-brand-primary/20 px-2 py-0.5 text-[8px] font-black uppercase text-brand-primary border border-brand-primary/20">
                                                                    Mejor Precio
                                                                </span>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-4 text-[9px] font-bold uppercase text-white/20">
                                                            <span>Visto por última vez: {formatDistanceToNow(new Date(offer.last_seen), { addSuffix: true, locale: es })}</span>
                                                            <span className="flex items-center gap-1">
                                                                <span className="h-1 w-1 rounded-full bg-green-500"></span> STOCK OK
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-8">
                                                    <div className="text-right space-y-0.5">
                                                        <div className={`text-2xl font-black ${offer.is_best ? 'text-brand-primary' : 'text-white'}`}>{offer.price} €</div>
                                                        <div className="text-[9px] font-black uppercase tracking-tighter text-white/10">Mín. Histórico: {offer.min_historical}€</div>
                                                    </div>

                                                    <a
                                                        href={offer.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className={`flex h-12 w-12 items-center justify-center rounded-2xl transition-all border ${offer.is_best ? 'bg-brand-primary text-white border-brand-primary shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10 hover:text-white'}`}
                                                    >
                                                        <ShoppingCart className="h-5 w-5" />
                                                    </a>
                                                </div>
                                            </div>
                                        ))}

                                        {(!productOffers || productOffers.length === 0) && (
                                            <div className="flex h-40 flex-col items-center justify-center rounded-[2rem] border border-dashed border-white/5 text-white/10">
                                                <Package className="mb-3 h-8 w-8" />
                                                <p className="text-[10px] font-black uppercase tracking-widest">Aún no hay ofertas registradas para este item</p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="p-8 pt-4 border-t border-white/5 bg-white/[0.02]">
                            <p className="text-[9px] font-bold text-white/20 uppercase text-center tracking-[0.3em]">
                                Datos procesados por la Red de Inteligencia del Oráculo — Actualización en Tiempo Real
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Catalog;
