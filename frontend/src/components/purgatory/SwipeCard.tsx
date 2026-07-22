import React, { useState } from 'react';
import { motion, useMotionValue, useTransform, useDragControls } from 'framer-motion';
import { Trash2, ExternalLink, Search, History, ArrowDown, Check } from 'lucide-react';

interface SwipeCardProps {
    item: any;
    isTop: boolean;
    originalIndex: number;
    handleApproveCard: (item: any) => void;
    handleDiscardCard: (item: any) => void;
    handleSwipeDown: (item: any) => void;
    openClassifyModal: (itemId: number, name: string) => void;
    isSearchingAssociation: boolean;
    setIsSearchingAssociation: (search: boolean) => void;
    associatedProductId: number | null;
    setAssociatedProductId: (id: number | null) => void;
    manualSearchTerm: string;
    setManualSearchTerm: (term: string) => void;
    filteredProducts: any[];
    allProducts: any[];
}

const SwipeCard: React.FC<SwipeCardProps> = ({
    item,
    isTop,
    originalIndex,
    handleApproveCard,
    handleDiscardCard,
    handleSwipeDown,
    openClassifyModal,
    isSearchingAssociation,
    setIsSearchingAssociation,
    associatedProductId,
    setAssociatedProductId,
    manualSearchTerm,
    setManualSearchTerm,
    filteredProducts,
    allProducts
}) => {
    const x = useMotionValue(0);
    const y = useMotionValue(0);
    const [showAllSuggestions, setShowAllSuggestions] = useState(false);
    const dragControls = useDragControls();

    // Dynamic rotation and overlay opacities based on translation
    const rotate = useTransform(x, [-200, 200], [-15, 15]);
    const opacityRight = useTransform(x, [20, 120], [0, 1]);
    const opacityLeft = useTransform(x, [-120, -20], [1, 0]);
    const opacityUp = useTransform(y, [-120, -20], [1, 0]);
    const opacityDown = useTransform(y, [20, 120], [0, 1]);

    // Position offset for stack depth effect
    const stackY = originalIndex * 12;
    const stackScale = 1 - originalIndex * 0.04;
    const stackZ = 50 - originalIndex;

    const handleDragEnd = (_event: any, info: any) => {
        if (!isTop) return;
        const threshold = 120;
        const swipeX = info.offset.x;
        const swipeY = info.offset.y;

        if (Math.abs(swipeX) > Math.abs(swipeY)) {
            if (swipeX > threshold) {
                handleApproveCard(item);
            } else if (swipeX < -threshold) {
                handleDiscardCard(item);
            }
        } else {
            if (swipeY > threshold) {
                handleSwipeDown(item);
            } else if (swipeY < -threshold) {
                openClassifyModal(item.id, item.scraped_name);
            }
        }
    };

    // Find details of the selected associated product to show it in the card
    const selectedProduct = allProducts?.find((p: any) => p.id === associatedProductId);
    const associatedProductName = selectedProduct ? selectedProduct.name : 'Producto personalizado';

    return (
        <motion.div
            style={isTop ? { x, y, rotate, zIndex: stackZ } : { y: stackY, scale: stackScale, zIndex: stackZ, opacity: 1 - originalIndex * 0.25 }}
            drag={isTop}
            dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
            dragElastic={0.6}
            dragControls={dragControls}
            dragListener={false}
            onDragEnd={handleDragEnd}
            animate={isTop ? { x: 0, y: 0, rotate: 0, scale: 1 } : { y: stackY, scale: stackScale }}
            transition={isTop ? { type: 'spring', stiffness: 300, damping: 20 } : { duration: 0.3 }}
            exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.2 } }}
            className={`absolute w-full h-[530px] rounded-[2.5rem] border bg-gradient-to-br from-black/85 via-black/90 to-white/[0.04] p-6 shadow-2xl backdrop-blur-xl flex flex-col justify-between ${isTop ? 'border-brand-primary/30 cursor-default shadow-brand-primary/10' : 'border-white/5 shadow-black/80 pointer-events-none'}`}
        >
            {/* Swiping Indicator Overlays */}
            {isTop && (
                <>
                    <motion.div style={{ opacity: opacityRight }} className="absolute inset-0 bg-green-500/20 border border-green-500/50 rounded-[2.5rem] flex items-center justify-center pointer-events-none z-50">
                        <span className="text-xl font-black text-green-400 uppercase tracking-widest bg-black/90 border border-green-500/30 px-6 py-3 rounded-full shadow-lg">VINCULAR/APROBAR</span>
                    </motion.div>
                    <motion.div style={{ opacity: opacityLeft }} className="absolute inset-0 bg-red-500/20 border border-red-500/50 rounded-[2.5rem] flex items-center justify-center pointer-events-none z-50">
                        <span className="text-xl font-black text-red-400 uppercase tracking-widest bg-black/90 border border-red-500/30 px-6 py-3 rounded-full shadow-lg">DESCARTAR</span>
                    </motion.div>
                    <motion.div style={{ opacity: opacityUp }} className="absolute inset-0 bg-amber-500/20 border border-amber-500/50 rounded-[2.5rem] flex items-center justify-center pointer-events-none z-50">
                        <span className="text-xl font-black text-amber-400 uppercase tracking-widest bg-black/90 border border-amber-500/30 px-6 py-3 rounded-full shadow-lg">NUEVO PRODUCTO</span>
                    </motion.div>
                    <motion.div style={{ opacity: opacityDown }} className="absolute inset-0 bg-blue-500/20 border border-blue-500/50 rounded-[2.5rem] flex items-center justify-center pointer-events-none z-50">
                        <span className="text-xl font-black text-blue-400 uppercase tracking-widest bg-black/90 border border-blue-500/30 px-6 py-3 rounded-full shadow-lg">RE-ENCOLAR</span>
                    </motion.div>
                </>
            )}

            {/* Top Details (Image + Scraped Info) - Serve as drag handle */}
            <div
                onPointerDown={(e) => isTop && dragControls.start(e)}
                className={`flex gap-4 items-start select-none relative pr-8 ${isTop ? 'cursor-grab active:cursor-grabbing touch-none' : ''}`}
            >
                <div className="relative h-24 w-24 rounded-2xl bg-black border border-white/10 overflow-hidden shrink-0 shadow-lg">
                    {item.image_url ? (
                        <img src={item.image_url} alt={item.scraped_name} className="h-full w-full object-cover p-0.5" />
                    ) : (
                        <div className="flex h-full w-full items-center justify-center text-[9px] text-white/20 uppercase font-black">No IMG</div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/85 text-[8px] font-black uppercase text-center text-white/60 tracking-widest py-0.5 border-t border-white/5">{item.shop_name}</div>
                </div>

                <div className="flex-1 min-w-0 space-y-1">
                    <span className="text-[9px] font-bold text-white/30 uppercase tracking-widest">ID: #{item.id} <span className="text-white/10">|</span> {new Date(item.found_at || item.scraped_at).toLocaleDateString()}</span>
                    <h3 className="text-sm font-bold text-white leading-tight line-clamp-2" title={item.scraped_name}>{item.scraped_name}</h3>
                    <div className="flex items-baseline gap-1">
                        <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Precio:</span>
                        <span className="text-lg font-black text-brand-primary">{item.price} <span className="text-xs text-brand-primary/80">{item.currency}</span></span>
                    </div>
                </div>

                {item.url && isTop && (
                    <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        onPointerDown={(e) => e.stopPropagation()}
                        className="absolute right-0 top-0 p-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-brand-primary/20 hover:border-brand-primary/30 text-white/50 hover:text-white transition-all shadow-md cursor-pointer z-10"
                        title="Abrir enlace original"
                    >
                        <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                )}
            </div>

            {/* Middle Section (Linking Panel / Quick Association) */}
            <div className="flex-1 my-4 flex flex-col justify-end min-h-0">
                {isSearchingAssociation ? (
                    /* BÚSQUEDA MANUAL */
                    <div className="space-y-2 bg-black/40 border border-white/5 p-3 rounded-2xl flex flex-col h-[230px]">
                        <div className="flex items-center justify-between">
                            <span className="text-[9px] font-black uppercase tracking-widest text-brand-primary">Buscador Manual [Esc para salir]</span>
                            <button onClick={() => setIsSearchingAssociation(false)} className="text-[9px] font-black uppercase tracking-widest text-white/45 hover:text-white">Cerrar</button>
                        </div>
                        <div className="relative shrink-0">
                            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-white/40" />
                            <input
                                id={`assoc-search-${item.id}`}
                                type="text"
                                placeholder="Buscar figura en catálogo..."
                                className="w-full rounded-xl bg-black/60 border border-white/10 py-2 pl-9 pr-3 text-xs font-bold text-white placeholder:text-white/20 outline-none focus:border-brand-primary/50 transition-all"
                                value={manualSearchTerm}
                                onChange={(e) => setManualSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="flex-1 overflow-y-auto custom-scrollbar space-y-1">
                            {manualSearchTerm ? (
                                filteredProducts.map((p: any) => (
                                    <button
                                        key={p.id}
                                        onClick={() => {
                                            setAssociatedProductId(p.id);
                                            setIsSearchingAssociation(false);
                                            setManualSearchTerm('');
                                        }}
                                        className="w-full flex items-center justify-between rounded-lg bg-white/5 p-2 text-left hover:bg-white/10 border border-transparent hover:border-white/10 transition-all text-xs font-bold"
                                    >
                                        <div className="truncate pr-2">
                                            <div className="text-white truncate">{p.name}</div>
                                            <div className="flex flex-wrap items-center gap-1 mt-0.5 text-[8px] uppercase font-black tracking-wider text-white/45">
                                                <span className="text-brand-primary bg-brand-primary/10 px-1.5 py-0.5 rounded border border-brand-primary/20">
                                                    {p.sub_category}
                                                </span>
                                                {p.release_year && (
                                                    <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                                                        {p.release_year}
                                                    </span>
                                                )}
                                                {selectedProduct?.variant_name && selectedProduct.variant_name !== 'NAN' && selectedProduct.variant_name !== 'nan' && (
                                                    <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5 truncate max-w-[80px]">
                                                        {p.variant_name}
                                                    </span>
                                                )}
                                                {p.figure_id && (
                                                    <span className="text-white/30 font-mono">#{p.figure_id}</span>
                                                )}
                                            </div>
                                        </div>
                                        <Check className="h-3.5 w-3.5 text-brand-primary shrink-0" />
                                    </button>
                                ))
                            ) : (
                                <div className="h-full flex items-center justify-center text-center text-white/20 text-[9px] uppercase tracking-widest font-black">Escriba para buscar</div>
                            )}
                            {manualSearchTerm && filteredProducts.length === 0 && (
                                <div className="text-center text-white/30 text-[9px] py-4 uppercase font-black tracking-widest">No se encontraron figuras</div>
                            )}
                        </div>
                    </div>
                ) : (
                    /* PANEL DE VINCULACIÓN ACTIVA Y SUGERENCIAS */
                    <div className="space-y-3 flex flex-col justify-end h-[230px]">
                        {/* 1. Asociación Activa */}
                        <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-3">
                            <div className="flex items-center justify-between mb-1.5">
                                <span className="text-[9px] font-black uppercase tracking-widest text-white/40">Vincular con</span>
                                <button
                                    onClick={() => setIsSearchingAssociation(true)}
                                    className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:underline flex items-center gap-1"
                                >
                                    <Search className="h-2.5 w-2.5" /> Cambiar [E]
                                </button>
                            </div>
                            {associatedProductId ? (
                                <div className="flex items-center justify-between bg-brand-primary/10 border border-brand-primary/30 rounded-xl p-2.5">
                                    <div className="min-w-0 pr-2">
                                        <div className="text-xs font-black text-white truncate">{associatedProductName}</div>
                                        <div className="flex flex-wrap items-center gap-1 mt-1 text-[8px] uppercase font-black tracking-wider text-white/50">
                                            {selectedProduct?.sub_category && (
                                                <span className="text-brand-primary bg-brand-primary/10 px-1.5 py-0.5 rounded border border-brand-primary/20">
                                                    {selectedProduct.sub_category}
                                                </span>
                                            )}
                                            {selectedProduct?.release_year && (
                                                <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                                                    {selectedProduct.release_year}
                                                </span>
                                            )}
                                            {selectedProduct?.variant_name && selectedProduct.variant_name !== 'NAN' && selectedProduct.variant_name !== 'nan' && (
                                                <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5 truncate max-w-[80px]">
                                                    {selectedProduct.variant_name}
                                                </span>
                                            )}
                                            <span className="text-white/40 font-mono">ID: #{associatedProductId}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setAssociatedProductId(null)}
                                        className="text-[8px] font-black text-red-400 hover:text-red-300 uppercase tracking-widest hover:bg-red-500/10 px-2 py-1 rounded-md transition-colors"
                                    >
                                        Quitar
                                    </button>
                                </div>
                            ) : (
                                <div className="text-center py-2.5 border border-dashed border-white/10 rounded-xl text-[10px] text-white/40 font-bold uppercase tracking-wider">
                                    ⚠️ Ningún item vinculado
                                </div>
                            )}
                        </div>

                        {/* 2. Sugerencias rápidas del Oráculo */}
                        <div className="space-y-1.5">
                            <span className="text-[9px] font-black uppercase tracking-widest text-white/40 block">Coincidencias Sugeridas</span>
                            <div className="flex flex-col gap-1.5 max-h-[135px] overflow-y-auto custom-scrollbar pr-1">
                                {(() => {
                                    const filtered = item.suggestions ? item.suggestions.filter((s: any) => !s.is_vintage) : [];
                                    const visible = showAllSuggestions ? filtered : filtered.slice(0, 4);
                                    return visible.map((sug: any) => {
                                        const isSelected = associatedProductId === sug.product_id;
                                        return (
                                            <button
                                                key={sug.product_id}
                                                onClick={() => setAssociatedProductId(sug.product_id)}
                                                className={`w-full flex items-center justify-between rounded-xl p-2.5 text-left transition-all border text-xs ${isSelected ? 'bg-brand-primary/20 border-brand-primary/60 text-white' : 'bg-white/5 border-white/5 text-white/70 hover:bg-white/10 hover:border-white/10'}`}
                                            >
                                                <div className="min-w-0 pr-2">
                                                    <div className="font-bold truncate text-white">{sug.name}</div>
                                                    <div className="flex flex-wrap items-center gap-1 mt-0.5 text-[8px] uppercase font-black tracking-wider text-white/50">
                                                        <span className="text-brand-primary bg-brand-primary/10 px-1.5 py-0.5 rounded border border-brand-primary/25">
                                                            {sug.sub_category}
                                                        </span>
                                                        {sug.release_year && (
                                                            <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                                                                {sug.release_year}
                                                            </span>
                                                        )}
                                                        {sug.variant_name && sug.variant_name !== 'NAN' && sug.variant_name !== 'nan' && (
                                                            <span className="bg-white/5 px-1.5 py-0.5 rounded border border-white/5 truncate max-w-[80px]">
                                                                {sug.variant_name}
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2 shrink-0">
                                                    <span className={`text-[8px] font-black px-1.5 py-0.5 rounded ${sug.match_score >= 80 ? 'bg-green-500/20 text-green-400' : sug.match_score >= 50 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                                                        {sug.match_score}%
                                                    </span>
                                                </div>
                                            </button>
                                        );
                                    });
                                })()}
                                {item.suggestions && item.suggestions.filter((s: any) => !s.is_vintage).length > 4 && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setShowAllSuggestions(prev => !prev);
                                        }}
                                        className="w-full text-center py-1.5 rounded-lg border border-dashed border-white/10 hover:border-white/20 text-[8px] font-black uppercase tracking-widest text-brand-primary hover:text-brand-primary/80 transition-colors cursor-pointer mt-1 bg-white/[0.01]"
                                    >
                                        {showAllSuggestions ? 'Contraer' : `Ver más (+${item.suggestions.filter((s: any) => !s.is_vintage).length - 4})`}
                                    </button>
                                )}
                                {(!item.suggestions || item.suggestions.filter((s: any) => !s.is_vintage).length === 0) && (
                                    <div className="text-center text-[9px] font-bold text-white/30 uppercase tracking-widest py-3 bg-white/[0.01] rounded-xl border border-white/5">Sin sugerencias del oráculo</div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Bottom Actions (Buttons for classic clicking) */}
            <div className="flex gap-2.5 pt-4 border-t border-white/5 select-none shrink-0 text-white">
                <button
                    onClick={() => handleDiscardCard(item)}
                    className="flex-1 py-2 px-1 rounded-xl bg-red-500/5 hover:bg-red-500 text-red-500 hover:text-white border border-red-500/10 hover:border-red-500 flex flex-col items-center justify-center gap-1 transition-all duration-200"
                    title="Descartar Item [A]"
                >
                    <Trash2 className="h-4 w-4 text-red-500 hover:text-white shrink-0" />
                    <span className="text-[8px] font-black uppercase tracking-widest text-center">Descartar</span>
                </button>
                <button
                    onClick={() => handleSwipeDown(item)}
                    className="flex-1 py-2 px-1 rounded-xl bg-blue-500/5 hover:bg-blue-500 text-blue-500 hover:text-white border border-blue-500/10 hover:border-blue-500 flex flex-col items-center justify-center gap-1 transition-all duration-200"
                    title="Re-encolar para después [S]"
                >
                    <ArrowDown className="h-4 w-4 text-blue-500 hover:text-white shrink-0" />
                    <span className="text-[8px] font-black uppercase tracking-widest text-center">Re-encolar</span>
                </button>
                <button
                    onClick={() => openClassifyModal(item.id, item.scraped_name)}
                    className="flex-1 py-2 px-1 rounded-xl bg-amber-500/5 hover:bg-amber-500 text-amber-500 hover:text-black border border-amber-500/10 hover:border-amber-500 flex flex-col items-center justify-center gap-1 transition-all duration-200"
                    title="Clasificar en catálogo [N]"
                >
                    <History className="h-4 w-4 text-amber-500 hover:text-black shrink-0" />
                    <span className="text-[8px] font-black uppercase tracking-widest text-center">Clasificar [N]</span>
                </button>
                <button
                    onClick={() => handleApproveCard(item)}
                    disabled={!associatedProductId}
                    className={`flex-1 py-2 px-1 rounded-xl flex flex-col items-center justify-center gap-1 transition-all duration-200 ${associatedProductId ? 'bg-brand-primary text-white hover:brightness-110 shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/35 border border-white/5 cursor-not-allowed'}`}
                    title="Aprobar vinculación [D]"
                >
                    <Check className="h-4 w-4 shrink-0" />
                    <span className="text-[8px] font-black uppercase tracking-widest text-center">Aprobar [D]</span>
                </button>
            </div>
        </motion.div>
    );
};

export default SwipeCard;
