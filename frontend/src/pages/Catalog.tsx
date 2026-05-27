import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import {
    Package,
    AlertCircle,
    Info,
    Plus,
    Check,
    ShoppingCart,
    ShoppingBasket,
    Settings,
    Save,
    X,
    RefreshCw,
    Star,
    ExternalLink,
    TrendingUp,
    History,
    Flame,
    ArrowUpRight,
    Gem,
    Search,
    Box,
    Trash2
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { motion } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { updateProduct, unlinkOffer, deleteProduct } from '../api/admin';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getProductPriceHistory } from '../api/products';
import PriceHistoryChart from '../components/products/PriceHistoryChart';
import type { Hero } from '../api/admin';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';


// Para desarrollo, usamos el ID de David
interface CatalogProps {
    searchQuery?: string;
    isVintageOnly?: boolean;
    user?: Hero | null;
}

const Catalog: React.FC<CatalogProps> = React.memo(({ searchQuery = "", isVintageOnly = false, user }) => {
    const queryClient = useQueryClient();
    const { addToCart } = useCart();
    const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);
    const [editingProduct, setEditingProduct] = React.useState<Product | null>(null);
    const [historyProductId, setHistoryProductId] = React.useState<number | null>(null);
    const [expandedImage, setExpandedImage] = React.useState<string | null>(null);

    // Vintage Sync Telemetry states
    const [showVintageSyncModal, setShowVintageSyncModal] = React.useState(false);
    const [vintageSyncLogs, setVintageSyncLogs] = React.useState<string>("");
    const [vintageSyncStatus, setVintageSyncStatus] = React.useState<string>("idle");

    // Contexto de Autenticación (Fase 8.2)
    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');
    const isAdmin = user?.role?.toLowerCase() === 'admin' || user?.username?.toLowerCase() === 'david';

    const handleTriggerVintageSync = async () => {
        setShowVintageSyncModal(true);
        setVintageSyncStatus("running");
        setVintageSyncLogs("🚀 Iniciando conexión con el Oráculo Vintage...\n⌛ Esperando respuesta del servidor...");
        try {
            const { syncNexusVintage } = await import('../api/admin');
            await syncNexusVintage();
        } catch (err: any) {
            console.error(err);
            setVintageSyncLogs(prev => prev + `\n❌ Error al iniciar sincronización: ${err.message || err}`);
            setVintageSyncStatus("error");
        }
    };

    React.useEffect(() => {
        if (!showVintageSyncModal || vintageSyncStatus !== "running") return;

        let intervalId = setInterval(async () => {
            try {
                const { getScrapersLogs } = await import('../api/admin');
                const logs = await getScrapersLogs() as any[];
                const vintageLog = logs.find(log => log.spider_name === "NexusVintage");
                if (vintageLog) {
                    setVintageSyncLogs(vintageLog.logs || "Procesando...");
                    if (vintageLog.status === "success") {
                        setVintageSyncStatus("completed");
                        clearInterval(intervalId);
                        queryClient.invalidateQueries({ queryKey: ['products', isVintageOnly] });
                    } else if (vintageLog.status === "error") {
                        setVintageSyncStatus("error");
                        clearInterval(intervalId);
                    }
                }
            } catch (err) {
                console.error("Error fetching live vintage logs:", err);
            }
        }, 2000);

        return () => clearInterval(intervalId);
    }, [showVintageSyncModal, vintageSyncStatus, queryClient, isVintageOnly]);


    // 1. Fetch de todos los productos
    const { data: products, isLoading: isLoadingProducts, isError: isErrorProducts } = useQuery<Product[]>({
        queryKey: ['products', isVintageOnly],
        queryFn: async () => {
            const response = await axios.get(`/api/products${isVintageOnly ? '?is_vintage=true' : ''}`);
            return response.data;
        }
    });

    // 2. Fetch de la colección (basada en el ID activo)
    const { data: collection, isLoading: isLoadingCollection } = useQuery<Product[]>({
        queryKey: ['collection', activeUserId, isVintageOnly],
        queryFn: () => getCollection(activeUserId, isVintageOnly)
    });

    // 2.5 Fetch de productos con ofertas activas (para el badge Live)
    const { data: productsWithOffers } = useQuery<number[]>({
        queryKey: ['products-with-offers'],
        queryFn: async () => {
            const response = await axios.get('/api/products/with-offers');
            return response.data;
        }
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

    // 5. Fetch de Histórico de Precios (Fase 8.3 Cronos)
    const { data: priceHistory, isLoading: isLoadingHistory } = useQuery({
        queryKey: ['price-history', historyProductId],
        queryFn: () => historyProductId ? getProductPriceHistory(historyProductId) : null,
        enabled: !!historyProductId
    });

    const hasMarketIntel = (productId: number) => productsWithOffers?.includes(productId);

    // 4. Mutación para alternar estado (Optimistic Updates)
    const toggleMutation = useMutation({
        mutationFn: ({ productId, wish }: { productId: number, wish: boolean }) => toggleCollection(productId, activeUserId, wish),
        onMutate: async ({ productId, wish }) => {
            await queryClient.cancelQueries({ queryKey: ['collection', activeUserId, isVintageOnly] });
            const previousCollection = queryClient.getQueryData<Product[]>(['collection', activeUserId, isVintageOnly]);

            queryClient.setQueryData<Product[]>(['collection', activeUserId, isVintageOnly], (old) => {
                const item = old?.find(p => p.id === productId);

                if (item) {
                    // Si ya existe y pulsas "wish" cuando ya estaba en "wish", lo quitas
                    // Si ya existe y pulsas "owned" cuando ya estaba en "owned", lo quitas
                    // Si estaba en "wish" y pulsas "owned", lo pasas a "owned" (upgrade)
                    if (item.is_wish && !wish) {
                        return old?.map(p => p.id === productId ? { ...p, is_wish: false } : p);
                    } else if (item.is_wish === wish) {
                        return old?.filter(p => p.id !== productId);
                    }
                    return old;
                } else {
                    const productToAdd = products?.find(p => p.id === productId);
                    if (productToAdd) {
                        return old ? [...old, { ...productToAdd, is_wish: wish }] : [{ ...productToAdd, is_wish: wish }];
                    }
                    return old;
                }
            });

            return { previousCollection };
        },
        onError: (_, __, context) => {
            if (context?.previousCollection) {
                queryClient.setQueryData(['collection', activeUserId, isVintageOnly], context.previousCollection);
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', activeUserId, isVintageOnly] });
        }
    });

    // 6. Mapa de Búsqueda Rápida (Optimización O(1) para Zero-Lag)
    const collectionMap = React.useMemo(() => {
        const map = new Map<number, Product>();
        collection?.forEach(p => map.set(p.id, p));
        return map;
    }, [collection]);

    const getCollectionItem = React.useCallback((productId: number) => {
        return collectionMap.get(productId);
    }, [collectionMap]);

    const isOwned = React.useCallback((productId: number): boolean => {
        const item = getCollectionItem(productId);
        return !!(item && !item.is_wish);
    }, [getCollectionItem]);

    const isWished = React.useCallback((productId: number): boolean => {
        const item = getCollectionItem(productId);
        return !!(item && item.is_wish);
    }, [getCollectionItem]);

    const isGrail = React.useCallback((productId: number): boolean => {
        const item = getCollectionItem(productId);
        return !!(item && item.is_grail);
    }, [getCollectionItem]);

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number, data: any }) => updateProduct(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            setEditingProduct(null);
        }
    });

    const unlinkMutation = useMutation({
        mutationFn: (offerId: number) => unlinkOffer(offerId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['product-offers', selectedProduct?.id] });
            queryClient.invalidateQueries({ queryKey: ['products-with-offers'] });
        }
    });

    const deleteProductMutation = useMutation({
        mutationFn: (productId: number) => deleteProduct(productId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products', isVintageOnly] });
            queryClient.invalidateQueries({ queryKey: ['vintage-products'] });
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedProduct(null);
        },
        onError: (err) => {
            console.error('Error al eliminar de Eternia:', err);
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

    // 7. Estadísticas de Sub-categoría (Cierre de Sets)
    const subCatStats = React.useMemo(() => {
        if (!products) return {};
        const stats: Record<string, { total: number, owned: number }> = {};
        products.forEach(p => {
            const sub = p.sub_category || 'Desconocida';
            if (!stats[sub]) stats[sub] = { total: 0, owned: 0 };
            stats[sub].total++;
            if (isOwned(p.id)) stats[sub].owned++;
        });
        return stats;
    }, [products, collectionMap]);
    // 8. Lógica de Ordenación Híbrida (VEC3/Hunting List)
    const sortedProducts = React.useMemo(() => {
        if (!products) return [];

        return [...products]
            .filter(product => {
                const query = searchQuery.toLowerCase();
                const owned = isOwned(product.id);

                // EXCLUSIÓN TOTAL: Si ya es propiedad del usuario, no aparece en Nueva Eternia
                if (owned) return false;

                return (
                    product.name.toLowerCase().includes(query) ||
                    product.figure_id?.toLowerCase().includes(query) ||
                    product.sub_category?.toLowerCase().includes(query)
                );
            })
            .sort((a, b) => {
                if (isVintageOnly) {
                    const countA = a.purgatory_match_count || 0;
                    const countB = b.purgatory_match_count || 0;
                    if (countA !== countB) {
                        return countB - countA;
                    }
                    return a.id - b.id;
                }

                const aWished = isWished(a.id);
                const bWished = isWished(b.id);
                const aGrail = isGrail(a.id);
                const bGrail = isGrail(b.id);

                const getTacticalWeight = (p: Product, wished: boolean, grail: boolean) => {
                    if (grail) return 10000; // Prioridad Sagrada

                    const idNum = parseInt(p.figure_id?.replace(/[^0-9]/g, '') || '0');
                    const isOld = idNum > 0 && idNum < 4500;
                    const isMid = idNum >= 4500 && idNum <= 9500;
                    const isNew = idNum > 9500;

                    // Indicadores de estudio de mercado (Simulados/Derivados)
                    const marketVal = p.market_value || 0;
                    const retailPrice = p.retail_price || 0;
                    const p25 = p.p25_price || p.p25_retail_price || retailPrice;

                    const isPriceFloor = marketVal > 0 && marketVal <= p25 * 1.1; // Suelo detectado (dentro del 10%)
                    const isRising = marketVal > 0 && retailPrice > 0 && marketVal > retailPrice * 1.4;

                    // Boost por completitud de set (Fuerza del Cierre)
                    const stats = subCatStats[p.sub_category || 'Desconocida'];
                    const completionBoost = stats ? Math.floor((stats.owned / stats.total) * 500) : 0;
                    const wishBoost = wished ? 1000 : 0;

                    // 1. ZONA DE RIESGO: Antiguo/Descontinuado + Subiendo Precio
                    if (isOld && isRising) return 8000 + wishBoost + completionBoost;

                    // 2. PUNTO DULCE: Lanzamiento de maduración + Suelo encontrado
                    if (isMid && isPriceFloor) return 7000 + wishBoost + completionBoost;

                    // 3. EXPLORACIÓN ACTIVA: Nuevo que ha tocado suelo (Alerta de compra)
                    if (isNew && isPriceFloor) return 6000 + wishBoost + completionBoost;

                    // 4. TRANSICIÓN: Items de edad media
                    if (isMid) return 5000 + wishBoost + completionBoost;

                    // 5. SEGUIMIENTO PASIVO: Nuevos sin suelo detectado (Enfriamiento)
                    if (isNew) return 3000 + wishBoost + completionBoost;

                    // 6. FONDO DE CAZA: Antiguos estables
                    return 2000 + wishBoost + completionBoost;
                };

                const weightA = getTacticalWeight(a, aWished, aGrail);
                const weightB = getTacticalWeight(b, bWished, bGrail);

                if (weightA !== weightB) return weightB - weightA;

                // Orden secundario por ID (más antiguos primero dentro del mismo peso)
                const idA = parseInt(a.figure_id?.replace(/[^0-9]/g, '') || '99999');
                const idB = parseInt(b.figure_id?.replace(/[^0-9]/g, '') || '99999');
                return idA - idB;
            });
    }, [products, searchQuery, subCatStats, isOwned, isWished, isGrail, isVintageOnly]);

    if (isLoadingProducts || isLoadingCollection) {
        return <PowerSwordLoader variant="fullScreen" text="Invocando el Catálogo Maestro..." />;
    }

    const getSentimentBadge = (product: Product) => {
        const momentum = product.market_momentum || 1.0;
        const popularity = product.popularity_score || 0;

        const badges = [];

        if (popularity > 1500) {
            badges.push(
                <div key="hot" className="flex items-center gap-1 rounded-full bg-orange-500/10 px-2 py-0.5 border border-orange-500/20 text-orange-400">
                    <Flame className="h-2.5 w-2.5 animate-pulse" />
                    <span className="text-[7px] font-black uppercase tracking-tighter">Codiciada</span>
                </div>
            );
        }

        if (momentum > 1.3) {
            badges.push(
                <div key="up" className="flex items-center gap-1 rounded-full bg-green-500/10 px-2 py-0.5 border border-green-500/20 text-green-400">
                    <ArrowUpRight className="h-2.5 w-2.5" />
                    <span className="text-[7px] font-black uppercase tracking-tighter">Al Alza</span>
                </div>
            );
        } else if (momentum < 0.85) {
            badges.push(
                <div key="opp" className="flex items-center gap-1 rounded-full bg-brand-primary/10 px-2 py-0.5 border border-brand-primary/20 text-brand-primary">
                    <Gem className="h-2.5 w-2.5" />
                    <span className="text-[7px] font-black uppercase tracking-tighter">Oportunidad</span>
                </div>
            );
        }

        return badges;
    };



    if (isErrorProducts) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al conectar con la API Broker</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 md:space-y-3 animate-in fade-in duration-1000">
            {/* Header / Search Area */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl pointer-events-none ${isVintageOnly ? 'bg-amber-500/10' : 'bg-brand-primary/10'}`}></div>

                <div className="relative flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                    <div className="flex flex-col gap-1">
                        <div className={`flex items-center gap-2 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>
                            <Box className={`h-3 w-3 md:h-4 md:w-4 ${isVintageOnly ? 'fill-amber-500' : 'fill-brand-primary'}`} />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                {isVintageOnly ? (
                                    <>
                                        Eternia <span className="text-amber-500">Vintage</span>
                                    </>
                                ) : (
                                    <>
                                        Nueva <span className="text-brand-primary">Eternia</span>
                                    </>
                                )}
                            </h2>
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/40 font-medium uppercase tracking-[0.1em]">
                            {isVintageOnly ? 'Almacén Sagrado de Reliquias Vintage' : 'Almacén Sagrado de Reliquias'}
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        {isVintageOnly && isAdmin && (
                            <button
                                onClick={handleTriggerVintageSync}
                                className="flex items-center gap-2 rounded-xl md:rounded-2xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 font-bold uppercase tracking-wider text-[10px] md:text-xs px-4 py-2.5 border border-amber-500/30 transition-all duration-300 shadow-[0_0_15px_-5px_rgba(245,158,11,0.3)] hover:shadow-[0_0_20px_-2px_rgba(245,158,11,0.5)] cursor-pointer"
                            >
                                <RefreshCw className={`h-3.5 w-3.5 ${vintageSyncStatus === 'running' ? 'animate-spin' : ''}`} />
                                <span>Sincronizar Catálogo Vintage</span>
                            </button>
                        )}
                        
                        <div className="flex items-center gap-2 md:gap-3 rounded-xl md:rounded-2xl bg-white/5 px-4 py-2 border border-white/10 backdrop-blur-xl w-fit xl:w-auto">
                            <Package className={`h-4 w-4 md:h-5 md:w-5 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`} />
                            <span className="text-xl md:text-2xl font-black text-white">{products?.length}</span>
                            <span className="text-[8px] md:text-[10px] font-black text-white/20 uppercase tracking-[0.2em] pt-1">Modelos Purificados</span>
                        </div>
                    </div>

                </div>
            </div>

            {/* Grid / Empty State */}
            {!products || products.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-20 text-white/20 space-y-4 rounded-[2.5rem] border border-white/5 bg-black/20 backdrop-blur-md">
                    <Package className="h-16 w-16 opacity-20" />
                    <p className="text-xl font-black uppercase tracking-widest text-white/60">El Oráculo está vacío...</p>
                    <p className="text-[10px] font-bold uppercase tracking-widest opacity-40">
                        {isVintageOnly 
                            ? "No hay reliquias registradas en Eternia todavía." 
                            : "No hay reliquias registradas en Nueva Eternia todavía."
                        }
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-2 gap-2 sm:gap-6 lg:grid-cols-3 xl:grid-cols-4 landscape:grid-cols-3">
                {sortedProducts?.map((product) => {
                    const owned = isOwned(product.id);
                    const wished = isWished(product.id);
                    const hasIntel = hasMarketIntel(product.id);
                    return (
                        <div
                            key={product.id}
                            className={`group relative flex flex-col gap-1 sm:gap-2 md:gap-5 rounded-2xl sm:rounded-[1.5rem] md:rounded-[2.5rem] border p-1.5 sm:p-2 md:p-5 transition-all duration-500 hover:translate-y-[-8px] ${hasIntel
                                ? 'border-brand-primary/30 bg-brand-primary/[0.03] shadow-[0_0_20px_-5px_rgba(14,165,233,0.15)] hover:shadow-[0_40px_80px_-20px_rgba(14,165,233,0.2)]'
                                : 'border-white/5 bg-black/25 backdrop-blur-md hover:bg-black/20 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.5)]'
                                }`}
                        >


                            {/* Owned/Wish Badge */}
                            {owned && (
                                <div className="absolute top-0 left-0 w-12 h-12 sm:w-16 sm:h-16 overflow-hidden z-20">
                                    <div className="bg-green-500 text-white text-[7px] sm:text-[9px] font-black uppercase text-center w-[80px] sm:w-[100px] py-0.5 sm:py-1 absolute rotate-[-45deg] left-[-25px] sm:left-[-30px] top-[10px] sm:top-[15px] shadow-[0_5px_15px_rgba(34,197,94,0.4)] border-b border-white/20">
                                        Captivo
                                    </div>
                                </div>
                            )}
                            {!owned && wished && (
                                <div className="absolute top-0 left-0 w-12 h-12 sm:w-16 sm:h-16 overflow-hidden z-20">
                                    <div className="bg-brand-primary text-white text-[7px] sm:text-[9px] font-black uppercase text-center w-[80px] sm:w-[100px] py-0.5 sm:py-1 absolute rotate-[-45deg] left-[-25px] sm:left-[-30px] top-[10px] sm:top-[15px] shadow-[0_5px_15px_rgba(14,165,233,0.4)] border-b border-white/20">
                                        Deseado
                                    </div>
                                </div>
                            )}

                            {/* Image Container */}
                            <div
                                className="relative aspect-square w-full overflow-hidden rounded-2xl sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner group/img cursor-pointer"
                                onClick={() => setSelectedProduct(product)}
                            >
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

                                {/* Right Strip Action (Collection Toggle) */}
                                <div
                                    className={`absolute top-0 right-0 h-full w-6 sm:w-12 flex flex-col items-center justify-center transition-all duration-300 z-30 border-l border-white/10 backdrop-blur-md hover:w-8 sm:hover:w-14 ${owned
                                        ? 'bg-green-500/20 text-green-400 hover:bg-red-500/40 hover:text-white'
                                        : wished
                                            ? 'bg-brand-primary/20 text-brand-primary hover:brightness-150'
                                            : 'bg-white/5 text-white/10 hover:bg-brand-primary/20 hover:text-white'
                                        }`}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleMutation.mutate({ productId: product.id, wish: false });
                                    }}
                                    title={owned ? 'Liberar del Catálogo (Presionar Lateral)' : wished ? 'Reclamar Reliquia (Presionar Lateral)' : 'Asegurar en la Fortaleza (Presionar Lateral)'}
                                >
                                    {toggleMutation.isPending ? (
                                        <RefreshCw className="h-6 w-6 animate-spin text-white/50" />
                                    ) : owned ? (
                                        <div className="flex flex-col items-center gap-1 group/btn">
                                            <Check className="h-4 w-4 sm:h-6 sm:w-6 group-hover/btn:hidden" />
                                            <X className="h-4 w-4 sm:h-6 sm:w-6 hidden group-hover/btn:block" />
                                            <span className="text-[6px] font-black uppercase vertical-text tracking-widest mt-2 hidden sm:block">BAJA</span>
                                        </div>
                                    ) : wished ? (
                                        <div className="flex flex-col items-center gap-1">
                                            <ShoppingCart className="h-4 w-4 sm:h-6 sm:w-6" />
                                            <span className="text-[6px] font-black uppercase vertical-text tracking-widest mt-2 hidden sm:block">CAPTURAR</span>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center gap-1">
                                            <Plus className="h-4 w-4 sm:h-6 sm:w-6" />
                                            <span className="text-[6px] font-black uppercase vertical-text tracking-widest mt-2 hidden sm:block">AÑADIR</span>
                                        </div>
                                    )}
                                </div>

                                {(() => {
                                    const idNum = parseInt(product.figure_id?.replace(/[^0-9]/g, '') || '0');
                                    let colorClass = 'text-blue-400 border-blue-400/20 bg-blue-400/10'; // Recent/Blue
                                    if (idNum > 0 && idNum < 4500) colorClass = 'text-amber-500 border-amber-500/20 bg-amber-500/10'; // Vintage/Amber
                                    if (idNum >= 4500 && idNum <= 9500) colorClass = 'text-slate-300 border-slate-300/20 bg-slate-300/10'; // Mid/Silver

                                    // Valuation Priority Logic
                                    const displayPrice = product.best_p2p_price || product.avg_market_price || 0;
                                    const isMaster = !product.best_p2p_price && product.avg_market_price;

                                    return (
                                        <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-40 flex items-center gap-1 sm:gap-1.5">
                                            <div className={`rounded-lg sm:rounded-xl px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black backdrop-blur-md border shadow-2xl transition-all transform uppercase tracking-widest ${colorClass}`}>
                                                #{product.figure_id}
                                            </div>
                                            <div className={`rounded-lg sm:rounded-xl px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black backdrop-blur-md border shadow-2xl transition-all transform uppercase tracking-widest flex items-center gap-1.5 ${isMaster ? 'border-purple-500/30 bg-purple-500/20 text-purple-300' : 'border-brand-primary/30 bg-brand-primary/20 text-white'}`}>
                                                <Gem className={`h-2 w-2 sm:h-3 sm:w-3 ${isMaster ? 'text-purple-400' : 'text-brand-primary'}`} />
                                                <span>{displayPrice}€</span>
                                                {product.best_p2p_source && (
                                                    <span className="opacity-40 text-[6px] sm:text-[7px] border-l border-white/20 pl-1.5 ml-0.5">{product.best_p2p_source}</span>
                                                )}
                                                {isMaster && !product.best_p2p_source && (
                                                    <span className="opacity-40 text-[6px] sm:text-[7px] border-l border-white/20 pl-1.5 ml-0.5 whitespace-nowrap">Master Ref</span>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })()}
                            </div>

                            {/* Content */}
                            <div className="flex flex-1 flex-col gap-1 sm:gap-4 px-0.5 pb-1">
                                <div className="space-y-0.5 sm:space-y-1">
                                    <div className="flex flex-wrap gap-1 mb-1">
                                        <span className="text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-brand-primary group-hover:text-brand-primary/80 transition-colors line-clamp-1">
                                            {product.sub_category}
                                        </span>
                                        {getSentimentBadge(product)}
                                    </div>
                                    <h3 className="line-clamp-2 min-h-[1.2rem] sm:min-h-[1.5rem] md:min-h-[2.5rem] text-[10px] sm:text-xs md:text-lg font-black leading-tight text-white group-hover:text-brand-primary transition-colors">
                                        {product.name}
                                    </h3>

                                    {/* Set Completion Mini-Progress (3OX Motivation) */}
                                    {(() => {
                                        const stats = subCatStats[product.sub_category || 'Desconocida'];
                                        if (!stats || stats.total <= 1) return null;
                                        const progress = (stats.owned / stats.total) * 100;
                                        return (
                                            <div className="mt-1 space-y-1">
                                                <div className="flex items-center justify-between text-[6px] sm:text-[8px] font-black uppercase tracking-tighter">
                                                    <span className={`${progress > 80 ? 'text-brand-primary' : 'text-white/30'}`}>Set Completion</span>
                                                    <span className="text-white/40">{Math.round(progress)}%</span>
                                                </div>
                                                <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full transition-all duration-1000 ${progress > 80 ? 'bg-brand-primary shadow-[0_0_5px_rgba(14,165,233,0.5)]' : 'bg-white/20'}`}
                                                        style={{ width: `${progress}%` }}
                                                    ></div>
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>

                                <div className="mt-auto flex flex-col gap-2">
                                    {/* Action Buttons Row - Symmetrical Center Dock */}
                                    <div className="flex items-center justify-center gap-2 rounded-2xl bg-white/[0.03] p-1.5 border border-white/10 group-hover:border-brand-primary/20 transition-all backdrop-blur-sm w-full">
                                        {/* Action: Toggle Price History */}
                                        <button
                                            onClick={() => setHistoryProductId(historyProductId === product.id ? null : product.id)}
                                            className={`flex h-8 w-8 items-center justify-center rounded-xl transition-all border hover:scale-110 active:scale-95 duration-300 shadow-md ${historyProductId === product.id ? 'bg-purple-500/20 text-purple-400 border-purple-500/50' : 'bg-white/5 text-white/30 border-white/10 hover:bg-white/10 hover:text-white'}`}
                                            title="Ver Evolución de Precios"
                                        >
                                            <History className="h-4 w-4" />
                                        </button>

                                        {/* Action Button: Detail View */}
                                        <button
                                            onClick={() => setSelectedProduct(product)}
                                            className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-white/40 border border-white/10 transition-all hover:bg-brand-primary/20 hover:text-brand-primary hover:border-brand-primary/45 hover:scale-110 active:scale-95 duration-300 shadow-md"
                                            title="Ver Mercado Live"
                                        >
                                            <Info className="h-4 w-4" />
                                        </button>

                                        {/* Action: Toggle Wishlist */}
                                        <button
                                            onClick={() => toggleMutation.mutate({ productId: product.id, wish: true })}
                                            disabled={toggleMutation.isPending || owned}
                                            className={`flex h-8 w-8 items-center justify-center rounded-xl transition-all border shadow-md hover:scale-110 active:scale-95 duration-300 ${wished
                                                ? 'bg-brand-primary/20 text-brand-primary border-brand-primary/30 hover:bg-red-500/20 hover:text-red-400'
                                                : 'bg-white/5 text-white/20 border-white/10 hover:bg-brand-primary/10 hover:text-brand-primary'
                                                } ${owned ? 'opacity-20 cursor-not-allowed' : ''} ${toggleMutation.isPending ? 'opacity-50 cursor-wait' : ''}`}
                                            title={wished ? 'Quitar de Deseos' : 'Añadir a Deseos'}
                                        >
                                            <Star className={`h-4 w-4 ${wished ? 'fill-current' : ''}`} />
                                        </button>

                                        {/* Action: Universal Search (EAN/ASIN) */}
                                        <a
                                            href={product.asin ? `https://www.amazon.es/s?k=${product.asin}` : `https://www.google.com/search?q=${encodeURIComponent(product.name + ' masters of the universe origins')}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-white/20 border border-white/10 hover:bg-brand-secondary/20 hover:text-brand-secondary transition-all hover:scale-110 active:scale-95 duration-300 shadow-md"
                                            title={product.asin ? "Buscar en Amazon.es por ASIN" : "Buscar en Google"}
                                        >
                                            <Search className="h-4 w-4" />
                                        </a>

                                        {/* Admin Action: Edit */}
                                        {isAdmin && (
                                            <button
                                                onClick={() => setEditingProduct(product)}
                                                className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-white/40 border border-white/10 transition-all hover:bg-brand-primary/20 hover:text-brand-primary hover:scale-110 active:scale-95 duration-300 shadow-md"
                                                title="Editar Metadatos (Arquitecto)"
                                            >
                                                <Settings className="h-4 w-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Inline Price History Chart (Cronos) */}
                                {historyProductId === product.id && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        className="overflow-hidden space-y-3"
                                    >
                                        <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-purple-400 pt-2 px-1">
                                            <span className="flex items-center gap-1">
                                                <TrendingUp className="h-3 w-3" />
                                                Evolución Cronos
                                            </span>
                                            <button onClick={() => setSelectedProduct(product)} className="hover:text-white transition-colors">
                                                Ver Detalles
                                            </button>
                                        </div>
                                        {isLoadingHistory ? (
                                            <div className="h-20 flex items-center justify-center">
                                                <RefreshCw className="h-8 w-8 animate-spin text-purple-400/50" />
                                            </div>
                                        ) : priceHistory && priceHistory.length > 0 ? (
                                            <PriceHistoryChart data={priceHistory} />
                                        ) : (
                                            <div className="p-4 text-[10px] font-bold text-center text-white/10 uppercase italic">
                                                Sin datos históricos suficientes
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
            )}

            {/* PRODUCT DETAIL MODAL (OFFERS) */}
            {selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in fade-in duration-300">
                    <div
                        className={`relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-[3rem] border bg-[#0A0A0B] shadow-[0_50px_100px_-20px_rgba(0,0,0,1)] flex flex-col ${isVintageOnly ? 'border-amber-500/20' : 'border-white/10'}`}
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Glow background for vintage */}
                        {isVintageOnly && (
                            <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-amber-500/5 blur-[100px] pointer-events-none"></div>
                        )}

                        {/* Modal Header */}
                        <div className="p-8 pb-4 flex items-start justify-between relative z-10">
                            <div className="flex gap-6 items-center">
                                <div
                                    className={`h-24 w-24 shrink-0 overflow-hidden rounded-3xl bg-black/40 cursor-zoom-in hover:scale-105 transition-transform border ${isVintageOnly ? 'border-amber-500/25' : 'border-white/10'}`}
                                    onClick={() => setExpandedImage(selectedProduct.image_url)}
                                    title="Expandir Reliquia"
                                >
                                    <img src={selectedProduct.image_url || ''} className="h-full w-full object-cover" />
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-3xl font-black tracking-tighter text-white leading-none">
                                        Analítica de <span className={isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}>Precios</span>
                                    </h4>
                                    <p className="text-sm font-bold text-white/30 uppercase tracking-widest">{selectedProduct.name}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {isAdmin && (
                                    <button
                                        onClick={() => {
                                            if (confirm(`¿Arquitecto, está seguro de ELIMINAR por completo el producto genérico '${selectedProduct.name}' de Eternia? Todas las ofertas vinculadas serán devueltas de inmediato al Purgatorio.`)) {
                                                deleteProductMutation.mutate(selectedProduct.id);
                                            }
                                        }}
                                        disabled={deleteProductMutation.isPending}
                                        className={`h-10 px-4 flex items-center justify-center gap-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all text-xs font-black uppercase tracking-widest shadow-lg`}
                                        title="Eliminar producto de Eternia (Devolver ofertas al Purgatorio)"
                                    >
                                        {deleteProductMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                        <span className="hidden sm:inline">Eliminar de Eternia</span>
                                    </button>
                                )}
                                <button
                                    onClick={() => setSelectedProduct(null)}
                                    className={`h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:text-white transition-all ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-red-500/20 hover:text-red-400'}`}
                                >
                                    <span className="text-2xl">&times;</span>
                                </button>
                            </div>
                        </div>

                        {/* Modal Body: Price List */}
                        <div className="flex-1 overflow-y-auto p-8 pt-4 custom-scrollbar relative z-10">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between px-4">
                                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">La Verdad del Mercado</h5>
                                    <span className={`text-[10px] font-black uppercase ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>Mejor Oferta Disponible</span>
                                </div>

                                {isLoadingOffers ? (
                                    <div className="flex h-40 flex-col items-center justify-center gap-3">
                                        <RefreshCw className={`h-10 w-10 animate-spin ${isVintageOnly ? 'text-amber-500/50' : 'text-brand-primary/50'}`} />
                                        <span className={`text-xs font-black uppercase tracking-widest ${isVintageOnly ? 'text-amber-500/50' : 'text-brand-primary/50'}`}>Escudriñando el Abismo...</span>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {productOffers?.map((offer) => (
                                            <div
                                                key={offer.id}
                                                className={`group flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-3xl p-5 transition-all border ${
                                                    offer.is_best 
                                                        ? (isVintageOnly 
                                                            ? 'bg-amber-500/5 border-amber-500/35 shadow-[0_0_30px_rgba(245,158,11,0.15)]'
                                                            : 'bg-brand-primary/5 border-brand-primary/30 shadow-[0_0_30px_rgba(14,165,233,0.1)]')
                                                        : 'bg-white/[0.03] border-white/5 hover:bg-white/[0.05]'
                                                }`}
                                            >
                                                <div className="flex items-center gap-4 flex-1">
                                                    <div className="space-y-1">
                                                        <div className="flex items-center flex-wrap gap-2">
                                                            <span className="text-xs font-black uppercase tracking-widest text-white/80">{offer.shop_name}</span>
                                                            {offer.is_best && (
                                                                <span className={`rounded-full px-2 py-0.5 text-[8px] font-black uppercase border ${isVintageOnly ? 'bg-amber-500/20 text-amber-400 border-amber-500/20' : 'bg-brand-primary/20 text-brand-primary border-brand-primary/20'}`}>
                                                                    Mejor Precio
                                                                </span>
                                                            )}
                                                        </div>
                                                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 text-[9px] font-bold uppercase text-white/20">
                                                            <span>Última vez: {formatDistanceToNow(new Date(offer.last_seen), { locale: es })}</span>
                                                            <span className="flex items-center gap-1">
                                                                <span className={`h-1.5 w-1.5 rounded-full ${offer.is_available ? 'bg-green-500' : 'bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.5)]'}`}></span>
                                                                <span className={offer.is_available ? '' : 'text-red-400 font-black'}>
                                                                    {offer.is_available ? 'STOCK OK' : 'SIN STOCK'}
                                                                </span>
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex flex-row items-center justify-between w-full md:w-auto md:justify-end gap-5">
                                                    <div className="text-left md:text-right space-y-0.5">
                                                        <div className={`text-xl font-black ${offer.is_best ? (isVintageOnly ? 'text-amber-500' : 'text-brand-primary') : 'text-white'}`}>{offer.price} €</div>
                                                        {offer.landing_price && offer.landing_price !== offer.price && (
                                                            <div className="text-[10px] font-black text-brand-secondary/80 flex flex-col items-start md:items-end">
                                                                <span className="flex items-center gap-1">
                                                                    <Package className="h-2.5 w-2.5" />
                                                                    {offer.landing_price} €
                                                                </span>
                                                            </div>
                                                        )}
                                                        <div className="text-[9px] font-black uppercase tracking-tighter text-white/10">Mín: {offer.min_historical}€</div>
                                                    </div>

                                                    <div className="flex items-center gap-2 shrinks-0">
                                                        {isAdmin && (
                                                            <button
                                                                onClick={() => {
                                                                    if (confirm(`¿Arquitecto, está seguro de desterrar esta oferta de '${selectedProduct?.name}' al Purgatorio?`)) {
                                                                        unlinkMutation.mutate(offer.id);
                                                                    }
                                                                }}
                                                                disabled={unlinkMutation.isPending}
                                                                className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-all shadow-lg"
                                                                title="Desvincular y enviar al Purgatorio"
                                                            >
                                                                {unlinkMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                                            </button>
                                                        )}

                                                        <div className="flex items-center gap-2">
                                                            <button
                                                                onClick={() => addToCart({
                                                                    id: offer.id.toString(),
                                                                    product_name: selectedProduct?.name || 'Reliquia',
                                                                    shop_name: offer.shop_name,
                                                                    price: offer.price,
                                                                    image_url: selectedProduct?.image_url || undefined
                                                                })}
                                                                className={`flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-white/40 border border-white/10 transition-all shadow-lg ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-brand-primary/20 hover:text-brand-primary'}`}
                                                                title="Simular en Oracle Cart"
                                                            >
                                                                <ShoppingBasket className="h-4 w-4" />
                                                            </button>
                                                            <a
                                                                href={offer.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className={`flex h-10 w-10 items-center justify-center rounded-xl transition-all border shadow-lg ${offer.is_best ? 'bg-orange-500 text-white border-orange-500 shadow-orange-500/20' : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10 hover:text-white'}`}
                                                                title="Ver en Tienda"
                                                            >
                                                                <ExternalLink className="h-4 w-4" />
                                                            </a>
                                                        </div>
                                                    </div>
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
            {/* EDIT PRODUCT MODAL (ADMIN ONLY) */}
            {isAdmin && editingProduct && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-2xl animate-in fade-in duration-300">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="relative w-full max-w-2xl overflow-hidden rounded-[2.5rem] border border-brand-primary/30 bg-[#0A0A0B] shadow-[0_0_50px_rgba(14,165,233,0.2)] flex flex-col"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <form onSubmit={handleSaveEdit}>
                            <div className="p-8 pb-4 flex items-center justify-between border-b border-white/5">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-brand-primary/10 rounded-xl">
                                        <Settings className="h-6 w-6 text-brand-primary" />
                                    </div>
                                    <h4 className="text-2xl font-black text-white">Editor de <span className="text-brand-primary">La Verdad</span></h4>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setEditingProduct(null)}
                                    className="h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:bg-red-500/20 hover:text-red-400 transition-all"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="p-8 space-y-6 overflow-y-auto max-h-[60vh] custom-scrollbar">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Name */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">Nombre de la Reliquia</label>
                                        <input
                                            value={editingProduct.name}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* EAN */}
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">EAN (Código Sagrado)</label>
                                        <input
                                            value={editingProduct.ean || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, ean: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                            placeholder="Desconocido"
                                        />
                                    </div>

                                    {/* Retail Price */}
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">Precio de Lanzamiento (€)</label>
                                        <input
                                            type="number"
                                            value={editingProduct.retail_price || 0}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, retail_price: parseFloat(e.target.value) })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* Subcategory */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">Línea temporal (Subcategoría)</label>
                                        <input
                                            value={editingProduct.sub_category || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, sub_category: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* Image URL */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">Pocion Visual (URL Imagen)</label>
                                        <input
                                            value={editingProduct.image_url || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, image_url: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white/50 text-xs focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* Linea Vintage (is_vintage) toggle */}
                                    <div className="col-span-1 md:col-span-2 flex items-center justify-between p-4 rounded-2xl bg-white/[0.02] border border-white/5 mt-2">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-black uppercase tracking-widest text-white/80 block">Línea Vintage (Eternia)</label>
                                            <span className="text-[8px] text-white/30 font-bold uppercase tracking-wider block">Activar para transferir este producto a la línea retro vintage</span>
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
                                    className="px-6 py-3 rounded-2xl text-sm font-black uppercase tracking-widest text-white/30 hover:text-white transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={updateMutation.isPending}
                                    className="bg-brand-primary hover:bg-brand-secondary text-white px-8 py-3 rounded-2xl font-black uppercase tracking-widest transition-all shadow-[0_0_30px_rgba(14,165,233,0.3)] flex items-center gap-2 disabled:opacity-50"
                                >
                                    {updateMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                                    Preservar Cambios
                                </button>
                            </div>
                        </form>
                    </motion.div>
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

            {/* VINTAGE SYNC TELEMETRY MODAL */}
            {showVintageSyncModal && (
                <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        className="w-full max-w-2xl overflow-hidden rounded-3xl border border-amber-500/25 bg-[#0f0e0c]/95 backdrop-blur-2xl shadow-[0_0_50px_rgba(245,158,11,0.2)]"
                    >
                        <div className="p-6 border-b border-white/5 bg-gradient-to-r from-amber-500/10 to-transparent flex items-center justify-between">
                            <div className="flex items-center gap-2 text-amber-500">
                                <RefreshCw className={`h-5 w-5 ${vintageSyncStatus === 'running' ? 'animate-spin' : ''}`} />
                                <h3 className="font-black uppercase tracking-widest text-white text-sm md:text-base">
                                    Nexo Maestro Vintage: Telemetría
                                </h3>
                            </div>
                            {vintageSyncStatus !== 'running' && (
                                <button
                                    onClick={() => setShowVintageSyncModal(false)}
                                    className="rounded-xl bg-white/5 p-2 text-white/50 hover:bg-white/10 hover:text-white transition-all border border-white/5 cursor-pointer"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            )}
                        </div>

                        <div className="p-6 space-y-4">
                            <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-white/40">
                                <span>Estado de la Incursión</span>
                                <span className={`px-2.5 py-0.5 rounded-full border text-[8px] font-black uppercase tracking-widest ${
                                    vintageSyncStatus === 'running' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400 animate-pulse' :
                                    vintageSyncStatus === 'completed' ? 'bg-green-500/10 border-green-500/20 text-green-400' :
                                    vintageSyncStatus === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                                    'bg-white/5 border-white/10 text-white/50'
                                }`}>
                                    {vintageSyncStatus === 'running' ? 'Sincronizando...' :
                                     vintageSyncStatus === 'completed' ? 'Completado' :
                                     vintageSyncStatus === 'error' ? 'Fallo Crítico' :
                                     'Inactivo'}
                                </span>
                            </div>

                            {/* Terminal window */}
                            <div className="h-64 overflow-y-auto rounded-2xl bg-black/80 p-5 border border-white/5 font-mono text-[10px] md:text-xs text-amber-400/90 space-y-1.5 shadow-inner scrollbar-thin">
                                {vintageSyncLogs.split('\n').map((line, i) => (
                                    <div key={i} className={line.startsWith('❌') ? 'text-red-400' : line.startsWith('✅') ? 'text-green-400' : ''}>
                                        {line}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="p-6 border-t border-white/5 bg-white/[0.01] flex items-center justify-end gap-3">
                            {vintageSyncStatus !== 'running' ? (
                                <button
                                    onClick={() => setShowVintageSyncModal(false)}
                                    className="bg-amber-500 hover:bg-amber-600 text-black px-6 py-2.5 rounded-xl font-black uppercase tracking-widest text-xs transition-all shadow-[0_0_20px_rgba(245,158,11,0.2)] cursor-pointer"
                                >
                                    Cerrar Telemetría
                                </button>
                            ) : (
                                <span className="text-[10px] font-bold uppercase tracking-wider text-white/30 animate-pulse">
                                    Ejecutando Secuencia en Segundo Plano...
                                </span>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </div>

    );
});

export default Catalog;
