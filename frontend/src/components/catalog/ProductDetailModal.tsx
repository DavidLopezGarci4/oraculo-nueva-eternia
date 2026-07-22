import React from 'react';
import type { UseMutationResult, QueryClient } from '@tanstack/react-query';
import { RefreshCw, Trash2, GitMerge, Package, ShoppingBasket, ExternalLink } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getOptimizedImageUrl } from '../../utils/imageUtils';
import { MOTUImage } from '../ui/MOTUImage';
import { parseUtcDate } from '../../utils/dateUtils';
import { mergeProducts } from '../../api/admin';
import type { Product } from '../../api/collection';

interface ProductDetailModalProps {
    selectedProduct: Product | null;
    setSelectedProduct: (product: Product | null) => void;
    isVintageOnly: boolean;
    setExpandedImage: (url: string | null) => void;
    isAdmin: boolean;
    deleteProductMutation: UseMutationResult<any, any, number, any>;
    showMergePanel: boolean;
    setShowMergePanel: (show: boolean) => void;
    mergeSearchQuery: string;
    setMergeSearchQuery: (query: string) => void;
    mergeTargetProduct: Product | null;
    setMergeTargetProduct: (product: Product | null) => void;
    products: Product[] | undefined;
    isMerging: boolean;
    setIsMerging: (merging: boolean) => void;
    queryClient: QueryClient;
    isLoadingOffers: boolean;
    productOffers: any[] | undefined;
    unlinkMutation: UseMutationResult<any, any, number, any>;
    addToCart: (item: { id: string, product_name: string, shop_name: string, price: number, image_url?: string }) => void;
}

const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
    selectedProduct,
    setSelectedProduct,
    isVintageOnly,
    setExpandedImage,
    isAdmin,
    deleteProductMutation,
    showMergePanel,
    setShowMergePanel,
    mergeSearchQuery,
    setMergeSearchQuery,
    mergeTargetProduct,
    setMergeTargetProduct,
    products,
    isMerging,
    setIsMerging,
    queryClient,
    isLoadingOffers,
    productOffers,
    unlinkMutation,
    addToCart
}) => {
    if (!selectedProduct) return null;

    return (
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
    );
};

export default ProductDetailModal;
