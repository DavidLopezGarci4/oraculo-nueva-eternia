import React from 'react';
import type { UseMutationResult } from '@tanstack/react-query';
import { Info, Star, Search, Settings, Check, X, ShoppingCart, Plus, Gem, Flame, ArrowUpRight, RefreshCw } from 'lucide-react';
import { getOptimizedImageUrl } from '../../utils/imageUtils';
import { MOTUImage } from '../ui/MOTUImage';
import { FoilTiltCard } from '../ui/FoilTiltCard';
import type { Product } from '../../api/collection';
import { buildSearchQuery } from './catalogHelpers';

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

interface ProductCardProps {
    product: Product;
    isVintageOnly: boolean;
    isOwned: (productId: number) => boolean;
    isWished: (productId: number) => boolean;
    isGrail: (productId: number) => boolean;
    setSelectedProduct: (product: Product) => void;
    toggleMutation: UseMutationResult<any, any, { productId: number, wish: boolean }, any>;
    subCatStats: Record<string, { total: number, owned: number }>;
    isAdmin: boolean;
    setEditingProduct: (product: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({
    product,
    isVintageOnly,
    isOwned,
    isWished,
    isGrail,
    setSelectedProduct,
    toggleMutation,
    subCatStats,
    isAdmin,
    setEditingProduct
}) => {
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
                            href={product.asin ? `https://www.amazon.es/s?k=${product.asin}` : buildSearchQuery(product, isVintageOnly)}
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
};

export default ProductCard;
