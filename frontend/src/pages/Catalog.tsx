import React from 'react';
import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
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
    History,
    Flame,
    ArrowUpRight,
    Gem,
    Search,
    Box,
    Trash2,
    ArrowUp,
    ArrowDown,
    GitMerge,
    Store
} from 'lucide-react';
import { getOptimizedImageUrl } from '../utils/imageUtils';
import { MOTUImage } from '../components/ui/MOTUImage';
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts';
import { useCart } from '../context/CartContext';
import { motion } from 'framer-motion';
import { getCollection, toggleCollection } from '../api/collection';
import type { Product } from '../api/collection';
import { updateProduct, unlinkOffer, deleteProduct, mergeProducts, syncNexusVintage, getScrapersLogs } from '../api/admin';
import { format, formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getProductPriceHistory, getUniqueShops } from '../api/products';
import type { Hero } from '../api/admin';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { parseUtcDate } from '../utils/dateUtils';
import { FoilTiltCard } from '../components/ui/FoilTiltCard';


const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const valA = payload[0]?.value;
        const valB = payload[1]?.value;

        let deltaStr = '';
        if (typeof valA === 'number' && typeof valB === 'number') {
            const diff = valA - valB;
            const pct = ((valA - valB) / valB) * 100;
            const sign = diff > 0 ? '+' : '';
            deltaStr = `Dif: ${sign}${diff.toFixed(2)}€ (${sign}${pct.toFixed(1)}%)`;
        }

        return (
            <div className="bg-black/90 border border-white/10 rounded-2xl p-4 shadow-2xl backdrop-blur-xl space-y-2">
                <p className="text-[10px] font-black text-white/40 uppercase tracking-widest">{label}</p>
                <div className="space-y-1">
                    {payload.map((item: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-3 text-xs font-bold justify-between">
                            <div className="flex items-center gap-1.5 min-w-0 pr-4">
                                <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: item.color }}></span>
                                <span className="text-white/80 truncate max-w-[150px]">{item.name}</span>
                            </div>
                            <span className="text-white font-black whitespace-nowrap">{item.value.toFixed(2)} €</span>
                        </div>
                    ))}
                </div>
                {deltaStr && (
                    <div className="h-px bg-white/5 my-1.5"></div>
                )}
                {deltaStr && (
                    <p className="text-[10px] font-black text-brand-primary uppercase tracking-widest text-center">
                        {deltaStr}
                    </p>
                )}
            </div>
        );
    }
    return null;
};

// Para desarrollo, usamos el ID de David
interface CatalogProps {
    searchQuery?: string;
    isVintageOnly?: boolean;
    user: Hero | null;
    isIncognito?: boolean;
}

const Catalog: React.FC<CatalogProps> = React.memo(({ searchQuery = "", isVintageOnly = false, user, isIncognito = false }) => {
    void isIncognito;
    const queryClient = useQueryClient();
    const { addToCart } = useCart();
    const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);
    const [editingProduct, setEditingProduct] = React.useState<Product | null>(null);
    const [expandedImage, setExpandedImage] = React.useState<string | null>(null);
    const [sortBy, setSortBy] = React.useState<'name' | 'offers' | 'completion'>('name');
    const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('asc');

    // Cronos Standalone states
    const [viewMode, setViewMode] = React.useState<'grid' | 'cronos' | 'wish'>('grid');
    const [selectedCronosA, setSelectedCronosA] = React.useState<Product | null>(null);
    const [selectedCronosB, setSelectedCronosB] = React.useState<Product | null>(null);
    const [cronosSearchA, setCronosSearchA] = React.useState('');
    const [cronosSearchB, setCronosSearchB] = React.useState('');
    const [activeCronosShops, setActiveCronosShops] = React.useState<string[]>([]);

    // Vintage Sync Telemetry states
    const [showVintageSyncModal, setShowVintageSyncModal] = React.useState(false);
    const [vintageSyncLogs, setVintageSyncLogs] = React.useState<string>("");
    const [vintageSyncStatus, setVintageSyncStatus] = React.useState<string>("idle");

    // Admin Fusion states
    const [showMergePanel, setShowMergePanel] = React.useState(false);
    const [mergeSearchQuery, setMergeSearchQuery] = React.useState('');
    const [mergeTargetProduct, setMergeTargetProduct] = React.useState<Product | null>(null);
    const [isMerging, setIsMerging] = React.useState(false);
    const [selectedChips, setSelectedChips] = React.useState<string[]>([]);
    const [selectedShopFilter, setSelectedShopFilter] = React.useState<string | null>(() => {
        return localStorage.getItem('catalog_shop_filter');
    });

    React.useEffect(() => {
        const handleNavigate = (e: Event) => {
            const customEvent = e as CustomEvent;
            if (customEvent.detail && customEvent.detail.shop) {
                setSelectedShopFilter(customEvent.detail.shop);
            }
        };
        window.addEventListener('navigate-to-catalog', handleNavigate);
        return () => window.removeEventListener('navigate-to-catalog', handleNavigate);
    }, []);

    const clearShopFilter = React.useCallback(() => {
        setSelectedShopFilter(null);
        localStorage.removeItem('catalog_shop_filter');
    }, []);

    React.useEffect(() => {
        setShowMergePanel(false);
        setMergeSearchQuery('');
        setMergeTargetProduct(null);
        setIsMerging(false);
    }, [selectedProduct]);

    // Contexto de Autenticación (Fase 8.2)
    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');
    const isAdmin = user?.role?.toLowerCase() === 'admin' || user?.username?.toLowerCase() === 'david';

    const handleTriggerVintageSync = async () => {
        setShowVintageSyncModal(true);
        setVintageSyncStatus("running");
        setVintageSyncLogs("🚀 Iniciando conexión con el Oráculo Vintage...\n⌛ Esperando respuesta del servidor...");
        try {
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


    // 1. Fetch de todos los productos con scroll infinito (Infinite Scroll)
    const {
        data: infiniteData,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
        isLoading: isLoadingProducts,
        isError: isErrorProducts
    } = useInfiniteQuery<Product[]>({
        queryKey: ['products-infinite', isVintageOnly, selectedShopFilter, searchQuery],
        queryFn: async ({ pageParam = 0 }) => {
            let url = `/api/products?is_vintage=${isVintageOnly ? 'true' : 'false'}&limit=24&offset=${pageParam}`;
            if (selectedShopFilter) {
                url += `&shop=${encodeURIComponent(selectedShopFilter)}`;
            }
            if (searchQuery) {
                url += `&search=${encodeURIComponent(searchQuery)}`;
            }
            const response = await axios.get(url);
            return response.data;
        },
        initialPageParam: 0,
        getNextPageParam: (lastPage, allPages) => {
            if (lastPage.length < 24) return undefined;
            return allPages.length * 24;
        }
    });

    const products = React.useMemo(() => {
        return infiniteData ? infiniteData.pages.flat() : [];
    }, [infiniteData]);

    const loadMoreRef = React.useRef<HTMLDivElement | null>(null);

    React.useEffect(() => {
        if (!hasNextPage || isFetchingNextPage) return;

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) {
                    fetchNextPage();
                }
            },
            { threshold: 0.1 }
        );

        const currentSensor = loadMoreRef.current;
        if (currentSensor) {
            observer.observe(currentSensor);
        }

        return () => {
            if (currentSensor) {
                observer.unobserve(currentSensor);
            }
        };
    }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

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

    // 5. Fetch de Histórico de Precios para Comparador Cronos
    const { data: historyCronosA, isLoading: loadingCronosA } = useQuery({
        queryKey: ['price-history-cronos-a', selectedCronosA?.id],
        queryFn: () => selectedCronosA ? getProductPriceHistory(selectedCronosA.id) : null,
        enabled: !!selectedCronosA && viewMode === 'cronos'
    });

    const { data: historyCronosB, isLoading: loadingCronosB } = useQuery({
        queryKey: ['price-history-cronos-b', selectedCronosB?.id],
        queryFn: () => selectedCronosB ? getProductPriceHistory(selectedCronosB.id) : null,
        enabled: !!selectedCronosB && viewMode === 'cronos'
    });

    const { data: availableShops } = useQuery<string[]>({
        queryKey: ['unique-shops'],
        queryFn: getUniqueShops,
        enabled: viewMode === 'cronos'
    });

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
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats', activeUserId] });
        }
    });

    // 6. Mapa de Búsqueda Rápida (Optimización O(1) para Zero-Lag)
    const collectionMap = React.useMemo(() => {
        const map = new Map<number, Product>();
        collection?.forEach(p => map.set(p.id, p));
        return map;
    }, [collection]);

    const totalWish = React.useMemo(() => {
        return collection?.filter(p => p.is_wish).length || 0;
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
                const wished = isWished(product.id);

                // Quick-Chips filter applications
                if (selectedChips.includes('offers') && !(product.purgatory_match_count && product.purgatory_match_count > 0)) return false;
                if (selectedChips.includes('coleccionado') && !owned) return false;

                // If not explicitly filtering by owned items, maintain standard hunting list logic (hide owned)
                if (!selectedChips.includes('coleccionado')) {
                    if (viewMode === 'wish') {
                        if (!wished) return false;
                    } else {
                        if (owned) return false;
                    }
                }

                return (
                    product.name.toLowerCase().includes(query) ||
                    product.figure_id?.toLowerCase().includes(query) ||
                    product.sub_category?.toLowerCase().includes(query)
                );
            })
            .sort((a, b) => {
                let comparison = 0;
                if (sortBy === 'name') {
                    comparison = a.name.localeCompare(b.name);
                } else if (sortBy === 'offers') {
                    comparison = (a.purgatory_match_count || 0) - (b.purgatory_match_count || 0);
                } else if (sortBy === 'completion') {
                    const statsA = subCatStats[a.sub_category || 'Desconocida'] || { total: 1, owned: 0 };
                    const statsB = subCatStats[b.sub_category || 'Desconocida'] || { total: 1, owned: 0 };
                    const rateA = statsA.total > 0 ? statsA.owned / statsA.total : 0;
                    const rateB = statsB.total > 0 ? statsB.owned / statsB.total : 0;
                    comparison = rateA - rateB;
                }
                
                if (comparison === 0) {
                    comparison = a.id - b.id;
                }
                
                return sortOrder === 'asc' ? comparison : -comparison;
            });
    }, [products, searchQuery, subCatStats, isOwned, isWished, isGrail, isVintageOnly, productsWithOffers, sortBy, sortOrder, viewMode, selectedChips]);

    const chartData = React.useMemo(() => {
        if (!historyCronosA && !historyCronosB) return [];

        const allowedShops = activeCronosShops.length > 0 ? activeCronosShops : (availableShops || []);

        if (selectedCronosA && selectedCronosB) {
            // Comparing both
            const filtA = (historyCronosA || []).filter(s => allowedShops.includes(s.shop_name));
            const filtB = (historyCronosB || []).filter(s => allowedShops.includes(s.shop_name));

            const datesA = filtA.flatMap(s => s.history.map(h => h.date));
            const datesB = filtB.flatMap(s => s.history.map(h => h.date));
            const allDates = Array.from(new Set([...datesA, ...datesB])).sort();

            return allDates.map(date => {
                let bestA: number | null = null;
                filtA.forEach(shop => {
                    const pt = shop.history.find(h => h.date === date);
                    if (pt && (bestA === null || pt.price < bestA)) {
                        bestA = pt.price;
                    }
                });

                let bestB: number | null = null;
                filtB.forEach(shop => {
                    const pt = shop.history.find(h => h.date === date);
                    if (pt && (bestB === null || pt.price < bestB)) {
                        bestB = pt.price;
                    }
                });

                return {
                    name: format(new Date(date), 'dd MMM', { locale: es }),
                    fullDate: date,
                    [selectedCronosA.name]: bestA,
                    [selectedCronosB.name]: bestB
                };
            });
        } else if (selectedCronosA) {
            const filtA = (historyCronosA || []).filter(s => allowedShops.includes(s.shop_name));
            const allDates = Array.from(new Set(filtA.flatMap(s => s.history.map(h => h.date)))).sort();

            return allDates.map(date => {
                const point: any = {
                    name: format(new Date(date), 'dd MMM', { locale: es }),
                    fullDate: date
                };
                filtA.forEach(shop => {
                    const pt = shop.history.find(h => h.date === date);
                    if (pt) {
                        point[shop.shop_name] = pt.price;
                    }
                });
                return point;
            });
        } else if (selectedCronosB) {
            const filtB = (historyCronosB || []).filter(s => allowedShops.includes(s.shop_name));
            const allDates = Array.from(new Set(filtB.flatMap(s => s.history.map(h => h.date)))).sort();

            return allDates.map(date => {
                const point: any = {
                    name: format(new Date(date), 'dd MMM', { locale: es }),
                    fullDate: date
                };
                filtB.forEach(shop => {
                    const pt = shop.history.find(h => h.date === date);
                    if (pt) {
                        point[shop.shop_name] = pt.price;
                    }
                });
                return point;
            });
        }
        return [];
    }, [historyCronosA, historyCronosB, selectedCronosA, selectedCronosB, activeCronosShops, availableShops]);

    const chartLines = React.useMemo(() => {
        if (selectedCronosA && selectedCronosB) {
            return [
                { key: selectedCronosA.name, color: '#0ea5e9' },
                { key: selectedCronosB.name, color: '#8b5cf6' }
            ];
        } else if (selectedCronosA) {
            const allowedShops = activeCronosShops.length > 0 ? activeCronosShops : (availableShops || []);
            const filtA = (historyCronosA || []).filter(s => allowedShops.includes(s.shop_name));
            return filtA.map((shop, idx) => {
                const colors = ['#0ea5e9', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b'];
                return {
                    key: shop.shop_name,
                    color: colors[idx % colors.length]
                };
            });
        } else if (selectedCronosB) {
            const allowedShops = activeCronosShops.length > 0 ? activeCronosShops : (availableShops || []);
            const filtB = (historyCronosB || []).filter(s => allowedShops.includes(s.shop_name));
            return filtB.map((shop, idx) => {
                const colors = ['#0ea5e9', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b'];
                return {
                    key: shop.shop_name,
                    color: colors[idx % colors.length]
                };
            });
        }
        return [];
    }, [selectedCronosA, selectedCronosB, historyCronosA, historyCronosB, activeCronosShops, availableShops]);

    const cronosStats = React.useMemo(() => {
        const stats: { 
            a?: { min: number; max: number; name: string };
            b?: { min: number; max: number; name: string };
        } = {};

        const allowedShops = activeCronosShops.length > 0 ? activeCronosShops : (availableShops || []);

        if (selectedCronosA && historyCronosA) {
            const prices = historyCronosA
                .filter(s => allowedShops.includes(s.shop_name))
                .flatMap(s => s.history.map(h => h.price));
            if (prices.length > 0) {
                stats.a = {
                    min: Math.min(...prices),
                    max: Math.max(...prices),
                    name: selectedCronosA.name
                };
            }
        }
        if (selectedCronosB && historyCronosB) {
            const prices = historyCronosB
                .filter(s => allowedShops.includes(s.shop_name))
                .flatMap(s => s.history.map(h => h.price));
            if (prices.length > 0) {
                stats.b = {
                    min: Math.min(...prices),
                    max: Math.max(...prices),
                    name: selectedCronosB.name
                };
            }
        }
        return stats;
    }, [historyCronosA, historyCronosB, selectedCronosA, selectedCronosB, activeCronosShops, availableShops]);

    if (isLoadingProducts || isLoadingCollection) {
        return <PowerSwordLoader variant="fullScreen" text="Invocando el Catálogo Maestro..." isVintage={isVintageOnly} />;
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
            <div className="relative overflow-hidden flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl pointer-events-none ${isVintageOnly ? 'bg-amber-500/10' : 'bg-brand-primary/10'}`}></div>

                <div className="relative z-10 flex flex-col gap-1">
                    <div className={`flex items-center gap-2 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>
                        <Box className="h-3 w-3 md:h-4 md:w-4" />
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

                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full lg:w-auto relative z-10">
                    {isVintageOnly && isAdmin && (
                        <button
                            onClick={handleTriggerVintageSync}
                            className="flex items-center justify-center gap-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 font-bold uppercase tracking-wider text-[10px] px-3 py-2 border border-amber-500/30 transition-all duration-300 shadow-[0_0_15px_-5px_rgba(245,158,11,0.3)] hover:shadow-[0_0_20px_-2px_rgba(245,158,11,0.5)] cursor-pointer h-[38px] sm:h-[42px]"
                        >
                            <RefreshCw className={`h-3.5 w-3.5 ${vintageSyncStatus === 'running' ? 'animate-spin' : ''}`} />
                            <span className="hidden sm:inline">Sincronizar Vintage</span>
                            <span className="sm:hidden">Sincronizar</span>
                        </button>
                    )}

                    <div className="flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
                        <div className="grid grid-cols-3 gap-1 sm:gap-2 p-1 rounded-xl bg-white/[0.03] border border-white/5 flex-1 sm:flex-initial">
                            <button
                                onClick={() => setSortBy('name')}
                                className={`py-1.5 px-2.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] transition-all ${
                                    sortBy === 'name' 
                                        ? (isVintageOnly ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'bg-brand-primary text-white shadow-[0_0_15px_rgba(14,165,233,0.3)]') 
                                        : 'text-white/20 hover:text-white/40'
                                }`}
                            >
                                Nombre
                            </button>
                            <button
                                onClick={() => setSortBy('offers')}
                                className={`py-1.5 px-2.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] transition-all ${
                                    sortBy === 'offers' 
                                        ? (isVintageOnly ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'bg-brand-primary text-white shadow-[0_0_15px_rgba(14,165,233,0.3)]') 
                                        : 'text-white/20 hover:text-white/40'
                                }`}
                            >
                                Ofertas
                            </button>
                            <button
                                onClick={() => setSortBy('completion')}
                                className={`py-1.5 px-2.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] transition-all ${
                                    sortBy === 'completion' 
                                        ? (isVintageOnly ? 'bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'bg-brand-primary text-white shadow-[0_0_15px_rgba(14,165,233,0.3)]') 
                                        : 'text-white/20 hover:text-white/40'
                                }`}
                            >
                                Set
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
                            {viewMode === 'wish' ? (
                                <Star className={`h-4 w-4 sm:h-5 sm:w-5 fill-current ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`} />
                            ) : (
                                <Package className={`h-4 w-4 sm:h-5 sm:w-5 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`} />
                            )}
                            <span className="text-lg sm:text-xl font-black text-white leading-none">{sortedProducts?.length}</span>
                        </div>
                        <span className="text-[8px] sm:text-[9px] font-black text-white/20 uppercase tracking-[0.15em] pt-0.5 leading-tight text-right sm:text-left">
                            {viewMode === 'wish' ? 'Deseos' : 'Reliquias'}<br className="sm:hidden" /> Filtradas
                        </span>
                    </div>
                </div>
            </div>

            {/* Sub-navigation tabs */}
            <div className="flex border-b border-white/10 gap-6 mt-2 mb-4">
                <button
                    onClick={() => setViewMode('grid')}
                    className={`pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all ${
                        viewMode === 'grid' 
                            ? (isVintageOnly ? 'border-amber-500 text-white' : 'border-brand-primary text-white') 
                            : 'border-transparent text-white/70 hover:text-white'
                    }`}
                >
                    {isVintageOnly ? "Eternia Vintage" : "Nueva Eternia"}
                </button>
                <button
                    onClick={() => setViewMode('wish')}
                    className={`pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all flex items-center gap-1.5 ${
                        viewMode === 'wish' 
                            ? (isVintageOnly ? 'border-amber-500 text-white' : 'border-brand-primary text-white') 
                            : 'border-transparent text-white/70 hover:text-white'
                    }`}
                >
                    <Star className={`h-3.5 w-3.5 ${viewMode === 'wish' ? 'fill-current' : ''}`} />
                    Lista de Deseos
                    {totalWish > 0 && (
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-md ml-1 ${isVintageOnly ? 'bg-amber-500/20 text-amber-400 font-extrabold' : 'bg-brand-primary/20 text-brand-primary font-extrabold'}`}>
                            {totalWish}
                        </span>
                    )}
                </button>
                <button
                    onClick={() => setViewMode('cronos')}
                    className={`pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all ${
                        viewMode === 'cronos' 
                            ? (isVintageOnly ? 'border-amber-500 text-white' : 'border-brand-primary text-white') 
                            : 'border-transparent text-white/70 hover:text-white'
                    }`}
                >
                    Evolución Cronos
                </button>
            </div>

            {viewMode === 'cronos' ? (
                <div className="relative overflow-hidden rounded-[2rem] border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Autocomplete Reliquia A */}
                        <div className="relative space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Reliquia Principal (A)</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Buscar Reliquia A..."
                                    value={selectedCronosA ? selectedCronosA.name : cronosSearchA}
                                    onChange={(e) => {
                                        setCronosSearchA(e.target.value);
                                        if (selectedCronosA) setSelectedCronosA(null);
                                    }}
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white text-xs md:text-sm font-bold focus:outline-none focus:border-brand-primary transition-all"
                                />
                                {selectedCronosA && (
                                    <button 
                                        onClick={() => { setSelectedCronosA(null); setCronosSearchA(''); }} 
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white font-bold"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                            {/* Dropdown Suggestions */}
                            {!selectedCronosA && cronosSearchA.trim().length > 1 && (
                                <div className="absolute z-50 w-full mt-1 bg-black/90 border border-white/10 rounded-2xl max-h-60 overflow-y-auto shadow-2xl custom-scrollbar">
                                    {products?.filter(p => p.name.toLowerCase().includes(cronosSearchA.toLowerCase()))
                                        .map(p => (
                                            <div
                                                key={p.id}
                                                onClick={() => {
                                                    setSelectedCronosA(p);
                                                    setCronosSearchA(p.name);
                                                }}
                                                className="px-4 py-3 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                            >
                                                {p.name} <span className="opacity-40 ml-2">#{p.figure_id}</span>
                                            </div>
                                        ))
                                    }
                                </div>
                            )}
                        </div>

                        {/* Autocomplete Reliquia B */}
                        <div className="relative space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Reliquia a Comparar (B)</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Buscar Reliquia B..."
                                    value={selectedCronosB ? selectedCronosB.name : cronosSearchB}
                                    onChange={(e) => {
                                        setCronosSearchB(e.target.value);
                                        if (selectedCronosB) setSelectedCronosB(null);
                                    }}
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white text-xs md:text-sm font-bold focus:outline-none focus:border-brand-primary transition-all"
                                />
                                {selectedCronosB && (
                                    <button 
                                        onClick={() => { setSelectedCronosB(null); setCronosSearchB(''); }} 
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white font-bold"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                            {/* Dropdown Suggestions */}
                            {!selectedCronosB && cronosSearchB.trim().length > 1 && (
                                <div className="absolute z-50 w-full mt-1 bg-black/90 border border-white/10 rounded-2xl max-h-60 overflow-y-auto shadow-2xl custom-scrollbar">
                                    {products?.filter(p => p.name.toLowerCase().includes(cronosSearchB.toLowerCase()))
                                        .map(p => (
                                            <div
                                                key={p.id}
                                                onClick={() => {
                                                    setSelectedCronosB(p);
                                                    setCronosSearchB(p.name);
                                                }}
                                                className="px-4 py-3 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                            >
                                                {p.name} <span className="opacity-40 ml-2">#{p.figure_id}</span>
                                            </div>
                                        ))
                                    }
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Shop Selection Checkboxes */}
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Filtrar por Tienda</label>
                        <div className="flex flex-wrap gap-3 bg-white/[0.02] border border-white/5 p-4 rounded-3xl">
                            {availableShops?.map(shop => {
                                const isChecked = activeCronosShops.includes(shop);
                                return (
                                    <label key={shop} className="flex items-center gap-2 cursor-pointer bg-white/5 px-3 py-1.5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                                        <input
                                            type="checkbox"
                                            checked={isChecked}
                                            onChange={() => {
                                                if (isChecked) {
                                                    setActiveCronosShops(activeCronosShops.filter(s => s !== shop));
                                                } else {
                                                    setActiveCronosShops([...activeCronosShops, shop]);
                                                }
                                            }}
                                            className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                        />
                                        <span className="text-[10px] font-black uppercase tracking-wider text-white/80">{shop}</span>
                                    </label>
                                );
                            })}
                            {(!availableShops || availableShops.length === 0) && (
                                <div className="text-[10px] font-bold text-white/60 uppercase tracking-widest py-1">Cargando tiendas...</div>
                            )}
                        </div>
                    </div>

                    {/* Cronos Stats Cards */}
                    {cronosStats && (cronosStats.a || cronosStats.b) && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                            {cronosStats.a && (
                                <div className="rounded-2xl border border-sky-500/20 bg-sky-500/5 p-4 flex items-center justify-between backdrop-blur-md">
                                    <div>
                                        <span className="block text-[8px] font-black uppercase tracking-wider text-sky-400">Rango de Precios - Reliquia A</span>
                                        <span className="text-xs font-bold text-white truncate max-w-[200px] block">{cronosStats.a.name}</span>
                                    </div>
                                    <div className="flex gap-4">
                                        <div className="text-right">
                                            <span className="block text-[8px] font-black uppercase text-white/40">Mínimo</span>
                                            <span className="text-base font-black text-green-400">{cronosStats.a.min.toFixed(2)} €</span>
                                        </div>
                                        <div className="text-right">
                                            <span className="block text-[8px] font-black uppercase text-white/40">Máximo</span>
                                            <span className="text-base font-black text-red-400">{cronosStats.a.max.toFixed(2)} €</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            {cronosStats.b && (
                                <div className="rounded-2xl border border-pink-500/20 bg-pink-500/5 p-4 flex items-center justify-between backdrop-blur-md">
                                    <div>
                                        <span className="block text-[8px] font-black uppercase tracking-wider text-pink-400">Rango de Precios - Reliquia B</span>
                                        <span className="text-xs font-bold text-white truncate max-w-[200px] block">{cronosStats.b.name}</span>
                                    </div>
                                    <div className="flex gap-4">
                                        <div className="text-right">
                                            <span className="block text-[8px] font-black uppercase text-white/40">Mínimo</span>
                                            <span className="text-base font-black text-green-400">{cronosStats.b.min.toFixed(2)} €</span>
                                        </div>
                                        <div className="text-right">
                                            <span className="block text-[8px] font-black uppercase text-white/40">Máximo</span>
                                            <span className="text-base font-black text-red-400">{cronosStats.b.max.toFixed(2)} €</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Chart Container */}
                    <div className="min-h-[400px] w-full bg-black/40 rounded-3xl p-6 border border-white/10 relative flex flex-col justify-center items-center">
                        {(loadingCronosA || loadingCronosB) ? (
                            <div className="flex flex-col items-center justify-center gap-4">
                                <RefreshCw className="h-10 w-10 text-brand-primary animate-spin" />
                                <span className="text-xs font-black uppercase tracking-widest text-white/65">Invocando datos del pasado...</span>
                            </div>
                        ) : chartData.length > 0 ? (
                            <div className="h-[380px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                        <XAxis
                                            dataKey="name"
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                                            dy={5}
                                        />
                                        <YAxis
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                                            unit="€"
                                        />
                                        <Tooltip
                                            cursor={{ stroke: 'rgba(255, 255, 255, 0.15)', strokeWidth: 1.5, strokeDasharray: '4 4' }}
                                            content={<CustomTooltip />}
                                        />
                                        <Legend
                                            iconType="circle"
                                            wrapperStyle={{ paddingTop: '10px', fontSize: '10px', fontWeight: 900, textTransform: 'uppercase' }}
                                        />
                                        {chartLines.map((line) => (
                                            <Line
                                                key={line.key}
                                                type="monotone"
                                                dataKey={line.key}
                                                stroke={line.color}
                                                strokeWidth={3}
                                                dot={{ fill: line.color, stroke: line.color, strokeWidth: 1, r: 4 }}
                                                activeDot={{ r: 8, stroke: '#fff', strokeWidth: 2 }}
                                                animationDuration={1000}
                                                connectNulls
                                            />
                                        ))}
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="text-center text-white/60 space-y-2 uppercase">
                                <History className="h-12 w-12 mx-auto text-white/10 animate-pulse" />
                                <h4 className="text-xs font-black tracking-widest text-white/70">Cronos está inactivo</h4>
                                <p className="text-[9px] font-bold text-white/65 tracking-wider">Selecciona Reliquias para visualizar su evolución de precios</p>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <>
                    {/* Quick-Chips de filtrado rápido */}
                    <div className="flex flex-wrap items-center gap-2 mb-6 bg-white/[0.02] border border-white/5 p-3 rounded-2xl backdrop-blur-md">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2 ml-1">Filtros Rápidos:</span>
                        <button
                            onClick={() => setSelectedChips([])}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all ${selectedChips.length === 0 ? (isVintageOnly ? 'bg-amber-500 text-black shadow-md shadow-amber-500/20' : 'bg-brand-primary text-white shadow-md shadow-brand-primary/20') : 'text-white/60 bg-white/5 hover:bg-white/10 hover:text-white'}`}
                        >
                            Todos
                        </button>
                        <button
                            onClick={() => setSelectedChips(prev => prev.includes('coleccionado') ? prev.filter(c => c !== 'coleccionado') : [...prev, 'coleccionado'])}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${selectedChips.includes('coleccionado') ? (isVintageOnly ? 'bg-amber-500 text-black shadow-md shadow-amber-500/20' : 'bg-brand-primary text-white shadow-md shadow-brand-primary/20') : 'text-white/60 bg-white/5 hover:bg-white/10 hover:text-white'}`}
                        >
                            <Package className="h-3 w-3" />
                            Coleccionado
                        </button>
                        <button
                            onClick={() => setSelectedChips(prev => prev.includes('offers') ? prev.filter(c => c !== 'offers') : [...prev, 'offers'])}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${selectedChips.includes('offers') ? (isVintageOnly ? 'bg-amber-500 text-black shadow-md shadow-amber-500/20' : 'bg-brand-primary text-white shadow-md shadow-brand-primary/20') : 'text-white/60 bg-white/5 hover:bg-white/10 hover:text-white'}`}
                        >
                            <Flame className="h-3 w-3" />
                            En Oferta
                        </button>
                        {selectedShopFilter && (
                            <button
                                onClick={clearShopFilter}
                                className="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/35 hover:text-red-300 flex items-center gap-1.5 shadow-md shadow-red-950/20"
                                title="Quitar filtro de tienda"
                            >
                                <Store className="h-3 w-3" />
                                {selectedShopFilter} <span className="text-white/60 font-black">&times;</span>
                            </button>
                        )}
                    </div>

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
            ) : sortedProducts.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-20 text-white/20 space-y-4 rounded-[2.5rem] border border-white/5 bg-black/20 backdrop-blur-md">
                    {viewMode === 'wish' ? (
                        <Star className="h-16 w-16 opacity-20" />
                    ) : (
                        <Package className="h-16 w-16 opacity-20" />
                    )}
                    <p className="text-xl font-black uppercase tracking-widest text-white/60">
                        {viewMode === 'wish' ? 'Lista de Deseos Vacía' : 'Sin Resultados'}
                    </p>
                    <p className="text-[10px] font-bold uppercase tracking-widest opacity-40">
                        {viewMode === 'wish' 
                            ? (isVintageOnly 
                                ? "Añade reliquias vintage a tu lista de deseos presionando la estrella en el catálogo." 
                                : "Añade reliquias a tu lista de deseos presionando la estrella en el catálogo.")
                            : "Intenta ajustar tus filtros o buscar otro término."
                        }
                    </p>
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-2 gap-2 sm:gap-6 lg:grid-cols-3 xl:grid-cols-4 landscape:grid-cols-3">
                 {sortedProducts?.map((product) => {
                    const owned = isOwned(product.id);
                    const wished = isWished(product.id);
                    
                    const idNum = parseInt(product.figure_id?.replace(/[^0-9]/g, '') || '0');
                    const itemIsGrail = isGrail(product.id);
                    const isOriginsManual = product.figure_id?.startsWith('ORIG-');
                    
                    let cardBorderClass = '';
                    if (isVintageOnly) {
                        if (itemIsGrail) {
                            cardBorderClass = 'border-orange-500/30 bg-orange-500/[0.02] shadow-[0_15px_30px_-10px_rgba(249,115,22,0.15)] hover:shadow-[0_40px_80px_-10px_rgba(249,115,22,0.35)]';
                        } else {
                            cardBorderClass = 'border-yellow-500/25 bg-yellow-500/[0.01] shadow-[0_15px_30px_-10px_rgba(234,179,8,0.1)] hover:shadow-[0_40px_80px_-10px_rgba(234,179,8,0.25)]';
                        }
                    } else {
                        cardBorderClass = 'border-cyan-500/20 bg-black/25 shadow-[0_15px_30px_-10px_rgba(6,182,212,0.08)] hover:shadow-[0_40px_80px_-10px_rgba(6,182,212,0.22)]';
                        if (itemIsGrail) {
                            cardBorderClass = 'border-orange-500/30 bg-orange-500/[0.02] shadow-[0_15px_30px_-10px_rgba(249,115,22,0.15)] hover:shadow-[0_40px_80px_-10px_rgba(249,115,22,0.35)]';
                        } else if (isOriginsManual) {
                            cardBorderClass = 'border-cyan-500/20 bg-cyan-500/[0.02] shadow-[0_15px_30px_-10px_rgba(6,182,212,0.08)] hover:shadow-[0_40px_80px_-10px_rgba(6,182,212,0.22)]';
                        } else if (idNum > 0 && idNum < 4500) {
                            cardBorderClass = 'border-amber-500/25 bg-amber-500/[0.01] shadow-[0_15px_30px_-10px_rgba(245,158,11,0.1)] hover:shadow-[0_40px_80px_-10px_rgba(245,158,11,0.25)]';
                        } else if (idNum >= 4500 && idNum <= 9500) {
                            cardBorderClass = 'border-slate-300/15 bg-black/25 hover:shadow-[0_40px_80px_-10px_rgba(255,255,255,0.08)]';
                        }
                    }
                    
                    const isSpecial = !!product.is_vintage || itemIsGrail || isOriginsManual;

                    return (
                        <FoilTiltCard
                            key={product.id}
                            isSpecial={isSpecial}
                            className={`group relative flex flex-col gap-1 sm:gap-1.5 md:gap-3 rounded-2xl sm:rounded-[1.5rem] md:rounded-3xl border p-1.5 sm:p-2 md:p-3.5 transition-all duration-500 hover:translate-y-[-8px] backdrop-blur-md ${cardBorderClass}`}
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
                                    <MOTUImage
                                        productId={product.id}
                                        src={getOptimizedImageUrl(product.image_url, 300)}
                                        alt={product.name}
                                        loading="lazy"
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
                                            ? (isVintageOnly ? 'bg-amber-500/20 text-amber-500 hover:brightness-150' : 'bg-brand-primary/20 text-brand-primary hover:brightness-150')
                                            : isVintageOnly
                                                ? 'bg-white/5 text-amber-500/60 hover:text-amber-500 hover:bg-amber-500/20'
                                                : 'bg-white/5 text-brand-primary/60 hover:text-brand-primary hover:bg-brand-primary/20'
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
                                    const itemIsGrail = isGrail(product.id);
                                    const isOriginsManual = product.figure_id?.startsWith('ORIG-');
                                    
                                    let colorClass = '';
                                    if (isVintageOnly) {
                                        if (itemIsGrail) {
                                            colorClass = 'text-orange-400 border-orange-500/35 bg-black/65 shadow-[0_0_15px_rgba(249,115,22,0.15)]'; // Grail/Orange
                                        } else {
                                            colorClass = 'text-yellow-400 border-yellow-500/30 bg-black/65'; // Vintage/Yellow
                                        }
                                    } else {
                                        colorClass = 'text-cyan-400 border-cyan-500/30 bg-black/65'; // Recent/Blue
                                        if (itemIsGrail) {
                                            colorClass = 'text-orange-400 border-orange-500/35 bg-black/65 shadow-[0_0_15px_rgba(249,115,22,0.15)]'; // Grail/Orange
                                        } else if (isOriginsManual) {
                                            colorClass = 'text-cyan-400 border-cyan-500/30 bg-black/65'; // Origins Manual/Blue
                                        } else if (idNum > 0 && idNum < 4500) {
                                            colorClass = 'text-amber-400 border-amber-500/30 bg-black/65'; // Vintage/Amber
                                        } else if (idNum >= 4500 && idNum <= 9500) {
                                            colorClass = 'text-slate-300 border-slate-300/30 bg-black/65'; // Mid/Silver
                                        }
                                    }
 
                                    // Valuation Priority Logic
                                    const displayPrice = product.best_p2p_price || product.avg_market_price || 0;
                                    const isMaster = !product.best_p2p_price && product.avg_market_price;

                                    return (
                                        <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-40 flex items-center gap-1 sm:gap-1.5">
                                            <div className={`rounded-lg sm:rounded-xl px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black backdrop-blur-md border shadow-2xl transition-all transform uppercase tracking-widest ${colorClass}`}>
                                                #{product.figure_id}
                                            </div>
                                            <div className={`rounded-lg sm:rounded-xl px-2 py-1 sm:px-3 sm:py-1.5 text-[8px] sm:text-[10px] font-black backdrop-blur-md border shadow-2xl transition-all transform uppercase tracking-widest flex items-center gap-1.5 ${isMaster ? 'border-purple-500/30 bg-purple-500/20 text-purple-300' : (isVintageOnly ? 'border-amber-500/30 bg-amber-500/20 text-white' : 'border-brand-primary/30 bg-brand-primary/20 text-white')}`}>
                                                <Gem className={`h-2 w-2 sm:h-3 sm:w-3 ${isMaster ? 'text-purple-400' : (isVintageOnly ? 'text-amber-500' : 'text-brand-primary')}`} />
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
                                        <span className={`text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] group-hover:text-opacity-80 transition-colors line-clamp-1 ${isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}`}>
                                            {product.sub_category}
                                        </span>
                                        {getSentimentBadge(product)}
                                    </div>
                                    <h3 className={`line-clamp-2 min-h-[1.2rem] sm:min-h-[1.5rem] md:min-h-[2rem] text-[10px] sm:text-xs md:text-sm lg:text-base font-black leading-tight text-white transition-colors ${isVintageOnly ? 'group-hover:text-amber-500' : 'group-hover:text-brand-primary'}`}>
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
                                                    <span className={`${progress > 80 ? (isVintageOnly ? 'text-amber-500' : 'text-brand-primary') : 'text-white/60'}`}>Set Completion</span>
                                                    <span className="text-white/65">{Math.round(progress)}%</span>
                                                </div>
                                                <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full transition-all duration-1000 ${progress > 80 ? (isVintageOnly ? 'bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.5)]' : 'bg-brand-primary shadow-[0_0_5px_rgba(14,165,233,0.5)]') : 'bg-white/20'}`}
                                                        style={{ width: `${progress}%` }}
                                                    ></div>
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>

                                <div className="mt-auto flex flex-col gap-2">
                                    {/* Action Buttons Row - Symmetrical Center Dock */}
                                    <div className={`flex items-center justify-center gap-2 rounded-2xl bg-white/[0.03] p-1.5 border border-white/10 transition-all backdrop-blur-sm w-full ${isVintageOnly ? 'group-hover:border-amber-500/20' : 'group-hover:border-brand-primary/20'}`}>
                                        {/* Action Button: Detail View */}
                                        <button
                                            onClick={() => setSelectedProduct(product)}
                                            className={`flex h-7 w-7 items-center justify-center rounded-xl bg-white/5 text-white/65 border border-white/10 transition-all active:scale-95 duration-300 shadow-md ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-500 hover:border-amber-500/45 hover:scale-110' : 'hover:bg-brand-primary/20 hover:text-brand-primary hover:border-brand-primary/45 hover:scale-110'}`}
                                            title="Ver Mercado Live"
                                        >
                                            <Info className="h-3.5 w-3.5" />
                                        </button>

                                        {/* Action: Toggle Wishlist */}
                                        <button
                                            onClick={() => toggleMutation.mutate({ productId: product.id, wish: true })}
                                            disabled={toggleMutation.isPending || owned}
                                            className={`flex h-7 w-7 items-center justify-center rounded-xl transition-all border shadow-md hover:scale-110 active:scale-95 duration-300 ${wished
                                                ? (isVintageOnly
                                                    ? 'bg-amber-500/20 text-amber-500 border-amber-500/30 hover:bg-red-500/20 hover:text-red-400'
                                                    : 'bg-brand-primary/20 text-brand-primary border-brand-primary/30 hover:bg-red-500/20 hover:text-red-400')
                                                : (isVintageOnly
                                                    ? 'bg-white/5 text-white/20 border-white/10 hover:bg-amber-500/10 hover:text-amber-500'
                                                    : 'bg-white/5 text-white/20 border-white/10 hover:bg-brand-primary/10 hover:text-brand-primary')
                                                } ${owned ? 'opacity-20 cursor-not-allowed' : ''} ${toggleMutation.isPending ? 'opacity-50 cursor-wait' : ''}`}
                                            title={wished ? 'Quitar de Deseos' : 'Añadir a Deseos'}
                                        >
                                            <Star className={`h-3.5 w-3.5 ${wished ? 'fill-current' : ''}`} />
                                        </button>

                                        {/* Action: Universal Search (EAN/ASIN) */}
                                        <a
                                            href={product.asin ? `https://www.amazon.es/s?k=${product.asin}` : `https://www.google.com/search?q=${encodeURIComponent(product.name + ' masters of the universe origins')}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className={`flex h-7 w-7 items-center justify-center rounded-xl bg-white/5 text-white/20 border border-white/10 transition-all hover:scale-110 active:scale-95 duration-300 shadow-md ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-brand-secondary/20 hover:text-brand-secondary'}`}
                                            title={product.asin ? "Buscar en Amazon.es por ASIN" : "Buscar en Google"}
                                        >
                                            <Search className="h-3.5 w-3.5" />
                                        </a>

                                        {/* Admin Action: Edit */}
                                        {isAdmin && (
                                            <button
                                                onClick={() => setEditingProduct(product)}
                                                className={`flex h-7 w-7 items-center justify-center rounded-xl bg-white/5 text-white/65 border border-white/10 transition-all hover:scale-110 active:scale-95 duration-300 shadow-md ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-500' : 'hover:bg-brand-primary/20 hover:text-brand-primary'}`}
                                                title="Editar Metadatos (Arquitecto)"
                                            >
                                                <Settings className="h-3.5 w-3.5" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </FoilTiltCard>
                    );
                })}
            </div>

            {/* Sensor y Spinner de Carga de Scroll Infinito */}
            {hasNextPage && (
                <div ref={loadMoreRef} className="flex justify-center p-8 mt-6 w-full">
                    <PowerSwordLoader size={32} text="Invocando siguientes reliquias..." isVintage={isVintageOnly} />
                </div>
            )}
                </>
            )}
                </>
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
                                    <MOTUImage 
                                        productId={selectedProduct.id}
                                        src={getOptimizedImageUrl(selectedProduct.image_url, 600)} 
                                        className="h-full w-full object-cover" 
                                        loading="lazy"
                                        alt={selectedProduct.name}
                                    />
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-3xl font-black tracking-tighter text-white leading-none">
                                        Analítica de <span className={isVintageOnly ? 'text-amber-500' : 'text-brand-primary'}>Precios</span>
                                    </h4>
                                    <p className="text-sm font-bold text-white/60 uppercase tracking-widest">{selectedProduct.name}</p>
                                </div>
                            </div>
                            <div className="flex flex-col items-center gap-2">
                                <button
                                    onClick={() => setSelectedProduct(null)}
                                    className={`h-10 w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/65 hover:text-white transition-all ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-red-500/20 hover:text-red-400'}`}
                                >
                                    <span className="text-2xl">&times;</span>
                                </button>
                                {isAdmin && (
                                    <button
                                        onClick={() => {
                                            if (confirm(`¿Arquitecto, está seguro de ELIMINAR por completo el producto genérico '${selectedProduct.name}' de Eternia? Todas las ofertas vinculadas serán devueltas de inmediato al Purgatorio.`)) {
                                                deleteProductMutation.mutate(selectedProduct.id);
                                            }
                                        }}
                                        disabled={deleteProductMutation.isPending}
                                        className="h-10 w-10 flex items-center justify-center rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all shadow-lg"
                                        title="Eliminar producto de Eternia (Devolver ofertas al Purgatorio)"
                                    >
                                        {deleteProductMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                    </button>
                                )}
                                {isAdmin && (
                                    <button
                                        onClick={() => setShowMergePanel(!showMergePanel)}
                                        className={`h-10 w-10 flex items-center justify-center rounded-xl transition-all shadow-lg border ${
                                            showMergePanel 
                                                ? 'bg-brand-primary text-white border-brand-primary shadow-brand-primary/20' 
                                                : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20 hover:bg-brand-primary hover:text-white'
                                        }`}
                                        title="Fusionar con otra figura (Arquitecto)"
                                    >
                                        <GitMerge className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 pt-4 custom-scrollbar relative z-10">
                            <div className="space-y-4">
                                {showMergePanel && (
                                    <div className="p-6 bg-white/[0.02] border border-white/5 rounded-3xl space-y-4 mb-4 relative z-50">
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-black uppercase text-brand-primary tracking-wider">Fusionar Reliquia (Arquitecto)</span>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowMergePanel(false);
                                                    setMergeSearchQuery('');
                                                    setMergeTargetProduct(null);
                                                }}
                                                className="text-[10px] font-black uppercase text-white/50 hover:text-white"
                                            >
                                                Cerrar
                                            </button>
                                        </div>
                                        <p className="text-[10px] text-white/60 font-bold uppercase leading-tight">
                                            Transfiere todas las ofertas y vinculaciones de la colección de esta figura '{selectedProduct.name}' a otra figura existente en el catálogo, eliminando el registro duplicado.
                                        </p>

                                        <div className="space-y-2 relative">
                                            <label className="text-[9px] font-black uppercase tracking-wider text-white/40">Buscar Reliquia Destino</label>
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={mergeSearchQuery}
                                                    onChange={(e) => {
                                                        setMergeSearchQuery(e.target.value);
                                                        if (mergeTargetProduct) setMergeTargetProduct(null);
                                                    }}
                                                    placeholder="Escribe el nombre de la figura destino..."
                                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-2.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary transition-all"
                                                />
                                                {mergeTargetProduct && (
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            setMergeTargetProduct(null);
                                                            setMergeSearchQuery('');
                                                        }}
                                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 hover:text-white font-bold"
                                                    >
                                                        &times;
                                                    </button>
                                                )}
                                            </div>
                                            
                                            {/* Dropdown Suggestions */}
                                            {!mergeTargetProduct && mergeSearchQuery.trim().length > 1 && (
                                                <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-2xl max-h-48 overflow-y-auto shadow-2xl custom-scrollbar">
                                                    {products
                                                        ?.filter(p => 
                                                            p.id !== selectedProduct.id && 
                                                            p.name.toLowerCase().includes(mergeSearchQuery.toLowerCase())
                                                        )
                                                        .map(p => (
                                                            <div
                                                                key={p.id}
                                                                onClick={() => {
                                                                    setMergeTargetProduct(p);
                                                                    setMergeSearchQuery(p.name);
                                                                }}
                                                                className="px-4 py-2.5 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                                            >
                                                                {p.name} <span className="opacity-40 ml-2">#{p.figure_id}</span>
                                                            </div>
                                                        ))
                                                    }
                                                    {products?.filter(p => 
                                                        p.id !== selectedProduct.id && 
                                                        p.name.toLowerCase().includes(mergeSearchQuery.toLowerCase())
                                                    ).length === 0 && (
                                                        <div className="px-4 py-3 text-xs text-white/40 uppercase font-black">No se encontraron figuras</div>
                                                    )}
                                                </div>
                                            )}
                                        </div>

                                        {mergeTargetProduct && (
                                            <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/25 space-y-3">
                                                <p className="text-[10px] text-red-400 font-bold uppercase leading-normal">
                                                    ⚠️ ATENCIÓN: Al proceder, todas las ofertas y registros de '{selectedProduct.name}' se transferirán permanentemente a '{mergeTargetProduct.name}' y la figura original será destruida del catálogo.
                                                </p>
                                                <button
                                                    type="button"
                                                    onClick={async () => {
                                                        if (confirm(`¿Confirmar fusión definitiva de '${selectedProduct.name}' dentro de '${mergeTargetProduct.name}'?`)) {
                                                            setIsMerging(true);
                                                            try {
                                                                await mergeProducts(selectedProduct.id, mergeTargetProduct.id);
                                                                alert(`Fusión divina completada. ${selectedProduct.name} absorbida por ${mergeTargetProduct.name}`);
                                                                setShowMergePanel(false);
                                                                setMergeSearchQuery('');
                                                                setMergeTargetProduct(null);
                                                                setSelectedProduct(null);
                                                                queryClient.invalidateQueries({ queryKey: ['products'] });
                                                            } catch (e: any) {
                                                                console.error(e);
                                                                alert("Error al realizar la fusión: " + (e.response?.data?.detail || e.message));
                                                            } finally {
                                                                setIsMerging(false);
                                                            }
                                                        }
                                                    }}
                                                    disabled={isMerging}
                                                    className="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
                                                >
                                                    {isMerging ? <RefreshCw className="h-3 w-3 animate-spin" /> : <GitMerge className="h-3 w-3" />}
                                                    {isMerging ? 'Fusionando...' : 'Confirmar Fusión Divina'}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                )}
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
                                                            <span>Última vez: {formatDistanceToNow(parseUtcDate(offer.last_seen), { locale: es })}</span>
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
                                                                    <span>{offer.landing_price} €</span>
                                                                </span>
                                                            </div>
                                                        )}
                                                        <div className="text-[9px] font-black uppercase tracking-tighter text-white/10">Mín: <span>{offer.min_historical}€</span></div>
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
                                                                className={`flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-white/65 border border-white/10 transition-all shadow-lg ${isVintageOnly ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-brand-primary/20 hover:text-brand-primary'}`}
                                                                title="Simular en Oracle Cart"
                                                            >
                                                                <ShoppingBasket className="h-4 w-4" />
                                                            </button>
                                                            <a
                                                                href={offer.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className={`flex h-10 w-10 items-center justify-center rounded-xl transition-all border shadow-lg ${offer.is_best ? 'bg-orange-500 text-white border-orange-500 shadow-orange-500/20' : 'bg-white/5 text-white/65 border-white/10 hover:bg-white/10 hover:text-white'}`}
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
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* EAN */}
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">EAN (Código Sagrado)</label>
                                        <input
                                            value={editingProduct.ean || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, ean: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
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
                                            className={`w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all ${isIncognito ? 'blur-incognito' : ''}`}
                                            title={isIncognito ? "Precio manual: •••" : undefined}
                                        />
                                    </div>

                                    {/* Subcategory */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Línea temporal (Subcategoría)</label>
                                        <input
                                            value={editingProduct.sub_category || ''}
                                            onChange={(e) => setEditingProduct({ ...editingProduct, sub_category: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white focus:outline-none focus:border-brand-primary/50 transition-all"
                                        />
                                    </div>

                                    {/* Image URL */}
                                    <div className="col-span-1 md:col-span-2 space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Pocion Visual (URL Imagen)</label>
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

                            <div className="p-6 sm:p-8 border-t border-white/5 bg-white/[0.02] flex flex-col sm:flex-row items-center justify-end gap-3 sm:gap-4">
                                <button
                                    type="button"
                                    onClick={() => setEditingProduct(null)}
                                    className="w-full sm:w-auto px-6 h-12 rounded-2xl text-sm font-black uppercase tracking-widest text-white/60 hover:text-white transition-all flex items-center justify-center whitespace-nowrap order-2 sm:order-1"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={updateMutation.isPending}
                                    className="w-full sm:w-auto bg-brand-primary hover:bg-brand-secondary text-white px-8 h-12 rounded-2xl font-black uppercase tracking-widest transition-all shadow-[0_0_30px_rgba(14,165,233,0.3)] flex items-center justify-center gap-2 disabled:opacity-50 whitespace-nowrap order-1 sm:order-2"
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
                        <MOTUImage
                            productId={selectedProduct?.id}
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
                            <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-white/65">
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
                                <span className="text-[10px] font-bold uppercase tracking-wider text-white/60 animate-pulse">
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
