import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Gavel, AlertCircle, Loader2, Info, Plus, Check, ShoppingCart, ShoppingBasket, RefreshCw, Star, TrendingUp, History, Package, X, ExternalLink } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { motion } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getProductPriceHistory } from '../api/products';
import PriceHistoryChart from '../components/products/PriceHistoryChart';

const MarketStatCard: React.FC<{ title: string, value: number, type: 'retail' | 'p2p' }> = ({ title, value, type }) => {
    const { data: analytics, isLoading } = useQuery({
        queryKey: ['market-analytics', value],
        queryFn: async () => {
            const response = await axios.get(`/api/market/analytics/${value}`);
            return response.data;
        },
        enabled: !!value
    });

    if (isLoading) return (
        <div className="glass p-4 rounded-2xl animate-pulse flex flex-col gap-1">
            <div className="h-2 w-16 bg-white/5 rounded" />
            <div className="h-6 w-24 bg-white/5 rounded" />
        </div>
    );

    const stats = type === 'retail' ? analytics?.retail : analytics?.p2p;

    return (
        <div className="glass p-4 rounded-2xl border border-white/5 hover:bg-white/5 transition-all">
            <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">{title}</p>
            <div className="flex items-baseline gap-2">
                <span className="text-xl font-black text-white">{stats?.avg || 0} €</span>
                <span className="text-[10px] font-bold text-white/30">Avg</span>
            </div>
            <div className="flex items-center gap-2 mt-1">
                <span className="text-[8px] font-bold text-green-500/60 uppercase">Min: {stats?.min || 0} €</span>
                <span className="text-[8px] font-bold text-red-500/60 uppercase">Max: {stats?.max || 0} €</span>
            </div>
        </div>
    );
};

const Auctions: React.FC = () => {
    const queryClient = useQueryClient();
    const { addToCart } = useCart();
    const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);
    const [historyProductId, setHistoryProductId] = React.useState<number | null>(null);
    const [expandedImage, setExpandedImage] = React.useState<string | null>(null);

    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');

    // 1. Fetch de productos con subastas activas
    const { data: products, isLoading: isLoadingProducts, isError: isErrorProducts } = useQuery<Product[]>({
        queryKey: ['auction-products'],
        queryFn: async () => {
            const response = await axios.get('/api/auctions/products');
            return response.data;
        }
    });

    // 2. Fetch de la colección
    const { data: collection, isLoading: isLoadingCollection } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId],
        queryFn: () => getCollection(activeUserId)
    });

    // 3. Fetch de ofertas de subasta del producto seleccionado
    const { data: productOffers, isLoading: isLoadingOffers } = useQuery<any[]>({
        queryKey: ['product-auction-offers', selectedProduct?.id],
        queryFn: async () => {
            if (!selectedProduct) return [];
            const response = await axios.get(`/api/products/${selectedProduct.id}/offers`);
            // Filtrar solo las de tipo P2P para esta vista
            return response.data.filter((o: any) => o.source_type === 'Peer-to-Peer');
        },
        enabled: !!selectedProduct
    });

    // 4. Histórico de precios
    const { data: priceHistory, isLoading: isLoadingHistory } = useQuery({
        queryKey: ['price-history', historyProductId],
        queryFn: () => historyProductId ? getProductPriceHistory(historyProductId) : null,
        enabled: !!historyProductId
    });

    const toggleMutation = useMutation({
        mutationFn: ({ productId, wish }: { productId: number, wish: boolean }) => toggleCollection(productId, activeUserId, wish),
        onMutate: async ({ productId, wish }) => {
            await queryClient.cancelQueries({ queryKey: ['collection', activeUserId] });
            const previousCollection = queryClient.getQueryData<Product[]>(['collection', activeUserId]);
            queryClient.setQueryData<Product[]>(['collection', activeUserId], (old) => {
                const item = old?.find(p => p.id === productId);
                if (item) {
                    if (item.is_wish && !wish) return old?.map(p => p.id === productId ? { ...p, is_wish: false } : p);
                    else if (item.is_wish === wish) return old?.filter(p => p.id !== productId);
                    return old;
                } else {
                    const productToAdd = products?.find(p => p.id === productId);
                    if (productToAdd) return old ? [...old, { ...productToAdd, is_wish: wish }] : [{ ...productToAdd, is_wish: wish }];
                    return old;
                }
            });
            return { previousCollection };
        },
        onError: (_, __, context) => {
            if (context?.previousCollection) queryClient.setQueryData(['collection', activeUserId], context.previousCollection);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', activeUserId] });
        }
    });

    const isOwned = (productId: number) => {
        const item = collection?.find(p => p.id === productId);
        return item && !item.is_wish;
    };

    const isWished = (productId: number) => {
        const item = collection?.find(p => p.id === productId);
        return item && item.is_wish;
    };

    if (isLoadingProducts || isLoadingCollection) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/50">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-medium animate-pulse">Infiltrándonos en Wallapop & eBay...</p>
            </div>
        );
    }

    if (isErrorProducts) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al conectar con la Red de Subastas</p>
            </div>
        );
    }

    return (
        <div className="space-y-10 animate-in fade-in duration-1000">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1">
                    <h2 className="text-4xl font-black tracking-tighter text-white">El Pabellón</h2>
                    <p className="text-sm font-bold text-white/30 uppercase tracking-widest">Subastas & Mercado de Segunda Mano</p>
                </div>
                <div className="flex items-center gap-3 rounded-2xl bg-white/[0.03] px-6 py-3 border border-white/5 backdrop-blur-3xl">
                    <Gavel className="h-5 w-5 text-brand-primary" />
                    <span className="text-2xl font-black text-white">{products?.length}</span>
                    <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] pt-1">Otras Reliquias Libres</span>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {products?.map((product) => {
                    const owned = isOwned(product.id);
                    const wished = isWished(product.id);
                    return (
                        <div
                            key={product.id}
                            className="group relative flex flex-col gap-2 sm:gap-5 rounded-3xl sm:rounded-[2.5rem] border border-white/5 bg-white/[0.02] p-2.5 sm:p-5 hover:bg-white/[0.05] transition-all duration-500 hover:translate-y-[-8px] hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.5)]"
                        >
                            <div
                                className="relative aspect-square w-full overflow-hidden rounded-2xl sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner group/img cursor-pointer"
                                onClick={() => setSelectedProduct(product)}
                            >
                                {product.image_url ? (
                                    <img src={product.image_url} alt={product.name} className="h-full w-full object-cover transition-all duration-700 group-hover/img:scale-110" />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center italic text-white/20 text-[10px] sm:text-xs font-black uppercase tracking-widest">Sin Imagen</div>
                                )}

                                {/* Auction Badge (Inside container for proper layering) */}
                                <div className="absolute top-2 right-2 sm:top-4 sm:right-4 z-40 flex items-center gap-1 rounded-lg sm:rounded-xl bg-orange-500/10 px-1.5 py-0.5 sm:px-2.5 sm:py-1 border border-orange-500/20 backdrop-blur-md">
                                    <span className="h-1 w-1 sm:h-1.5 sm:w-1.5 rounded-full bg-orange-500 animate-pulse"></span>
                                    <span className="text-[6px] sm:text-[8px] font-black uppercase tracking-widest text-orange-500">Subasta</span>
                                </div>

                                {/* Captivo Ribbon (Inside container) */}
                                {owned && (
                                    <div className="absolute top-0 left-0 w-12 h-12 sm:w-16 sm:h-16 overflow-hidden z-40 pointer-events-none">
                                        <div className="bg-green-500 text-white text-[7px] sm:text-[9px] font-black uppercase text-center w-[80px] sm:w-[100px] py-0.5 sm:py-1 absolute rotate-[-45deg] left-[-25px] sm:left-[-30px] top-[10px] sm:top-[15px] shadow-[0_5px_15px_rgba(34,197,94,0.4)] border-b border-white/20">Captivo</div>
                                    </div>
                                )}

                                {/* Right Strip Action (Collection Toggle) */}
                                <div
                                    className={`absolute top-0 right-0 h-full w-8 sm:w-12 flex flex-col items-center justify-center transition-all duration-300 z-30 border-l border-white/10 backdrop-blur-md hover:w-10 sm:hover:w-14 ${owned
                                        ? 'bg-green-500/20 text-green-400 hover:bg-red-500/40 hover:text-white'
                                        : wished
                                            ? 'bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white'
                                            : 'bg-white/5 text-white/10 hover:bg-brand-primary/20 hover:text-white'
                                        }`}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleMutation.mutate({ productId: product.id, wish: false });
                                    }}
                                    title={owned ? 'Liberar del Catálogo (Presionar Lateral)' : wished ? 'Reclamar Reliquia (Presionar Lateral)' : 'Asegurar en la Fortaleza (Presionar Lateral)'}
                                >
                                    {toggleMutation.isPending ? (
                                        <Loader2 className="h-4 w-4 sm:h-6 sm:w-6 animate-spin text-brand-primary" />
                                    ) : owned ? (
                                        <div className="flex flex-col items-center gap-1 group/btn">
                                            <Check className="h-4 w-4 sm:h-6 sm:w-6 group-hover/btn:hidden" />
                                            <X className="h-4 w-4 sm:h-6 sm:w-6 hidden group-hover/btn:block" />
                                            <span className="text-[6px] font-black uppercase vertical-text tracking-widest mt-2 hidden sm:block">BAJA</span>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center gap-1">
                                            {wished ? <ShoppingCart className="h-4 w-4 sm:h-6 sm:w-6" /> : <Plus className="h-4 w-4 sm:h-6 sm:w-6" />}
                                            <span className="text-[6px] font-black uppercase vertical-text tracking-widest mt-2 hidden sm:block">{wished ? 'CAPTURAR' : 'AÑADIR'}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-40 rounded-lg sm:rounded-xl bg-black/70 px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black text-brand-primary backdrop-blur-md border border-brand-primary/20 opacity-0 group-hover:opacity-100 transition-all uppercase tracking-widest">#{product.figure_id}</div>
                            </div>

                            <div className="flex flex-1 flex-col gap-2 sm:gap-3 px-1">
                                <div className="space-y-0.5 sm:space-y-1">
                                    <span className="text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-white/20 group-hover:text-brand-primary/50 transition-colors line-clamp-1">{product.sub_category}</span>
                                    <h3 className="line-clamp-2 min-h-[2rem] text-xs sm:text-lg font-black leading-tight text-white group-hover:text-brand-primary transition-colors">{product.name}</h3>
                                </div>

                                <div className="mt-auto flex items-center justify-between pt-2 sm:pt-4 gap-2 sm:gap-3">
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => setHistoryProductId(historyProductId === product.id ? null : product.id)} className={`flex h-8 w-8 sm:h-11 sm:w-11 items-center justify-center rounded-xl sm:rounded-2xl transition-all border ${historyProductId === product.id ? 'bg-purple-500/20 text-purple-400 border-purple-500/50' : 'bg-white/5 text-white/30 border-white/5 hover:bg-white/10 hover:text-white'}`}><History className="h-3 w-3 sm:h-5 sm:w-5" /></button>
                                        <button onClick={() => setSelectedProduct(product)} className="flex h-8 w-8 sm:h-11 sm:w-11 items-center justify-center rounded-xl sm:rounded-2xl bg-white/5 text-white/40 border border-white/5 hover:bg-brand-primary/20 hover:text-brand-primary transition-all"><Info className="h-3 w-3 sm:h-5 sm:w-5" /></button>
                                    </div>
                                    <button onClick={() => toggleMutation.mutate({ productId: product.id, wish: true })} disabled={toggleMutation.isPending || owned} className={`flex h-8 w-8 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl transition-all border ${wished ? 'bg-brand-primary/20 text-brand-primary border-brand-primary/30' : 'bg-white/5 text-white/20 border-white/10 hover:bg-brand-primary/10 hover:text-brand-primary'} ${owned ? 'opacity-20' : ''}`}><Star className={`h-3 w-3 sm:h-5 sm:w-5 ${wished ? 'fill-current' : ''}`} /></button>
                                </div>

                                {historyProductId === product.id && (
                                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="overflow-hidden space-y-3">
                                        <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-purple-400 pt-2 px-1"><span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> Evolución Subastas</span></div>
                                        {isLoadingHistory ? <div className="h-20 flex items-center justify-center"><RefreshCw className="h-4 w-4 animate-spin text-purple-500/50" /></div> : priceHistory && priceHistory.length > 0 ? <PriceHistoryChart data={priceHistory} /> : <div className="p-4 text-[10px] font-bold text-center text-white/10 uppercase italic">Sin datos históricos</div>}
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl" onClick={() => setSelectedProduct(null)}>
                    <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-[3rem] border border-white/10 bg-[#0A0A0B] shadow-[0_50px_100px_-20px_rgba(0,0,0,1)] flex flex-col" onClick={(e) => e.stopPropagation()}>
                        <div className="p-8 pb-4 flex items-start justify-between">
                            <div className="flex gap-6 items-center">
                                <div
                                    className="h-24 w-24 shrink-0 overflow-hidden rounded-3xl border border-white/10 bg-black/40 cursor-zoom-in hover:scale-105 transition-transform"
                                    onClick={() => setExpandedImage(selectedProduct.image_url)}
                                    title="Expandir Reliquia"
                                >
                                    <img src={selectedProduct.image_url || ''} className="h-full w-full object-cover" />
                                </div>
                                <div className="space-y-1"><h4 className="text-3xl font-black tracking-tighter text-white">Lote de <span className="text-orange-500">Subastas</span></h4><p className="text-sm font-bold text-white/30 uppercase tracking-widest">{selectedProduct.name}</p></div>
                            </div>
                            <button onClick={() => setSelectedProduct(null)} className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:bg-red-500/20 hover:text-red-400">&times;</button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 pt-4 custom-scrollbar">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between px-4"><h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">Mercado Secundario (Wallapop/eBay)</h5></div>
                                {isLoadingOffers ? (
                                    <div className="flex h-40 items-center justify-center gap-3"><Loader2 className="h-6 w-6 animate-spin text-brand-primary" /><span className="text-xs font-bold uppercase tracking-widest text-white/20">Escudriñando el Abismo...</span></div>
                                ) : (
                                    <div className="space-y-6">
                                        {/* PHASE 40: MARKET ANALYTICS SECTION */}
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-4">
                                            <MarketStatCard
                                                title="Media Retail"
                                                value={selectedProduct.id}
                                                type="retail"
                                            />
                                            <MarketStatCard
                                                title="Media P2P/Subasta"
                                                value={selectedProduct.id}
                                                type="p2p"
                                            />
                                            <div className="rounded-2xl bg-brand-primary/10 border border-brand-primary/20 p-4 flex flex-col justify-center items-center">
                                                <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Estado Mercado</span>
                                                <span className="text-lg font-black text-white">Saludable</span>
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            {productOffers?.map((offer) => (
                                                <div key={offer.id} className="group flex items-center justify-between gap-4 rounded-3xl p-5 bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all">
                                                    <div className="flex items-center gap-6 flex-1">
                                                        <div className="space-y-1">
                                                            <div className="flex items-center gap-3">
                                                                <span className="text-xs font-black uppercase tracking-widest text-white/80">{offer.shop_name}</span>
                                                                {offer.sale_type === 'Auction' ? (
                                                                    <span className="rounded-full bg-orange-500/20 px-2 py-0.5 text-[8px] font-black uppercase text-orange-500 border border-orange-500/20">
                                                                        Subasta ({offer.bids_count} pujas)
                                                                    </span>
                                                                ) : (
                                                                    <span className="rounded-full bg-blue-500/20 px-2 py-0.5 text-[8px] font-black uppercase text-blue-400 border border-blue-500/20">
                                                                        Venta Directa
                                                                    </span>
                                                                )}
                                                            </div>
                                                            <div className="flex flex-col gap-0.5">
                                                                <div className="text-[9px] font-bold uppercase text-white/20">Visto hace: {formatDistanceToNow(new Date(offer.last_seen), { addSuffix: true, locale: es })}</div>
                                                                {offer.expiry_at && (
                                                                    <div className="text-[9px] font-black uppercase text-orange-400">
                                                                        Expira: {formatDistanceToNow(new Date(offer.expiry_at), { addSuffix: true, locale: es })}
                                                                    </div>
                                                                )}
                                                                {offer.time_left_raw && !offer.expiry_at && (
                                                                    <div className="text-[9px] font-black uppercase text-orange-400/60">
                                                                        Quedan: {offer.time_left_raw}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-8">
                                                        <div className="text-right space-y-0.5">
                                                            <div className="text-2xl font-black text-white">{offer.price} €</div>
                                                            {offer.landing_price && offer.landing_price !== offer.price && (
                                                                <div className="text-[10px] font-black text-orange-500/80 flex flex-col items-end">
                                                                    <span className="flex items-center gap-1">
                                                                        <Package className="h-2.5 w-2.5" />
                                                                        {offer.landing_price} € (Landed)
                                                                    </span>
                                                                </div>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <button
                                                                onClick={() => addToCart({
                                                                    id: offer.id.toString(),
                                                                    product_name: selectedProduct?.name || 'Reliquia',
                                                                    shop_name: offer.shop_name,
                                                                    price: offer.price,
                                                                    image_url: selectedProduct?.image_url || undefined
                                                                })}
                                                                className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-white/40 border border-white/10 hover:bg-brand-primary/20 hover:text-brand-primary transition-all"
                                                                title="Simular en Oracle Cart"
                                                            >
                                                                <ShoppingBasket className="h-5 w-5" />
                                                            </button>
                                                            <a
                                                                href={offer.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-white/40 border border-white/10 hover:bg-orange-500 hover:text-white transition-all"
                                                                title="Ver en Tienda"
                                                            >
                                                                <ExternalLink className="h-5 w-5" />
                                                            </a>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* FULLSCREEN IMAGE EXPANSION */}
            {expandedImage && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-20 bg-black/95 backdrop-blur-3xl animate-in zoom-in duration-300 shadow-2xl"
                    onClick={() => setExpandedImage(null)}
                >
                    <div className="relative max-w-full max-h-full group">
                        <img
                            src={expandedImage}
                            alt="Expanded Relic"
                            className="max-w-full max-h-[90vh] rounded-[2rem] sm:rounded-[3rem] border border-white/10 shadow-[0_0_100px_rgba(0,0,0,0.8)] object-contain"
                            onClick={(e) => e.stopPropagation()}
                        />
                        <button
                            onClick={() => setExpandedImage(null)}
                            className="absolute -top-4 -right-4 sm:-top-8 sm:-right-8 h-10 w-10 sm:h-14 sm:w-14 flex items-center justify-center rounded-2xl bg-white/10 text-white hover:bg-red-500 hover:scale-110 transition-all border border-white/10 backdrop-blur-md shadow-2xl z-50"
                        >
                            <X className="h-6 w-6 sm:h-8 sm:w-8" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Auctions;
