import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence, useMotionValue, useTransform, useDragControls } from 'framer-motion';
import {
    Flame,
    Zap,
    Trash2,
    Link,
    ExternalLink,
    RefreshCcw,
    Search,
    CheckCircle2,
    ShieldAlert,
    Database,
    ChevronLeft,
    ChevronRight,
    X,
    History,
    ArrowDown,
    Check,
    LayoutGrid,
    LayoutList
} from 'lucide-react';
import { getPurgatory, discardItem, discardItemsBulk, matchVintageItem, matchMiscellaneousItem, matchItemsBulk } from '../api/purgatory';

import QuickPreviewModal from '../components/QuickPreviewModal';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import axios from 'axios';
import { useEffect, useRef, useMemo } from 'react';

const PERSISTENCE_KEY = 'purgatory_offline_actions';

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

const Purgatory: React.FC = React.memo(() => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [manualSearchTerm, setManualSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);
    const [isVintageModalOpen, setIsVintageModalOpen] = useState(false);
    const [selectedDivision, setSelectedDivision] = useState<'vintage' | 'modern'>('vintage');
    const [customSubCategory, setCustomSubCategory] = useState('Origins');
    const [showCustomSubCategoryInput, setShowCustomSubCategoryInput] = useState(false);
    const [vintageModalItemId, setVintageModalItemId] = useState<number | null>(null);
    const [vintageModalItemName, setVintageModalItemName] = useState('');
    const [vintageCustomName, setVintageCustomName] = useState('');
    const [selectedVintageProductId, setSelectedVintageProductId] = useState<number | null>(null);
    const [pendingActions, setPendingActions] = useState<any[]>(() => {
        const saved = localStorage.getItem(PERSISTENCE_KEY);
        return saved ? JSON.parse(saved) : [];
    });

    // Locally processed/synced IDs that should remain hidden until the server refetch completes
    const [locallyProcessedIds, setLocallyProcessedIds] = useState<Set<number>>(new Set());

    // UX/UI Custom States
    const [viewLayout, setViewLayout] = useState<'mazo' | 'lista'>('mazo');
    const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'highest_match' | 'lowest_match'>('highest_match');
    const [shopFilter, setShopFilter] = useState<string>('all');
    const [deckItems, setDeckItems] = useState<any[]>([]);
    const [snoozedIds, setSnoozedIds] = useState<number[]>([]);
    const [associatedProductId, setAssociatedProductId] = useState<number | null>(null);
    const [isSearchingAssociation, setIsSearchingAssociation] = useState(false);

    // Experimental Transit Filter State
    const [enableTransitFilter, setEnableTransitFilter] = useState(false);
    const [transitType, setTransitType] = useState<'all' | 'retail' | 'p2p'>('all');

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 15;
    const [showForensic, setShowForensic] = useState(false);

    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    // Persistence Persistence
    useEffect(() => {
        localStorage.setItem(PERSISTENCE_KEY, JSON.stringify(pendingActions));
    }, [pendingActions]);

    const openClassifyModal = (itemId: number, scrapedName: string) => {
        setVintageModalItemId(itemId);
        setVintageModalItemName(scrapedName);
        setVintageCustomName('');
        setSelectedVintageProductId(null);
        setSelectedDivision('vintage');
        setCustomSubCategory('Origins');
        setShowCustomSubCategoryInput(false);
        setIsVintageModalOpen(true);
    };



    // Mutations
    const discardBulkMutation = useMutation({
        mutationFn: async (ids: number[]) => {
            return ids;
        },
        onMutate: async (ids) => {
            // Find names/urls for forensic context
            const affectedItems = queryClient.getQueryData<any[]>(['purgatory'])?.filter(i => ids.includes(i.id)) || [];

            // Persistence: Add to local buffer immediately
            setPendingActions(prev => {
                if (prev.some(a => a.type === 'bulk-discard' && JSON.stringify(a.pendingIds) === JSON.stringify(ids))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'bulk-discard',
                    pendingIds: ids,
                    items: affectedItems.map(i => ({ id: i.id, name: i.scraped_name, url: i.url })),
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            // Optimistically update the cache
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => !ids.includes(item.id))
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Bulk discard enqueue failed:', err);
        },
        onSuccess: () => {
            // Background worker handles syncing
        },
        onSettled: () => {
            setSelectedIds([]);
        }
    });

    // Queries
    const { data: pendingItems, isLoading: isLoadingPending } = useQuery({
        queryKey: ['purgatory'],
        queryFn: getPurgatory,
        refetchInterval: 300000 // 5 min — evita refrescos constantes que estropean la UX
    });

    // Clean up locallyProcessedIds once the server data updates (confirming deletion/archive)
    useEffect(() => {
        if (pendingItems) {
            const currentItemIds = new Set(pendingItems.map((item: any) => item.id));
            setLocallyProcessedIds(prev => {
                const next = new Set<number>();
                prev.forEach((id: number) => {
                    if (currentItemIds.has(id)) {
                        next.add(id);
                    }
                });
                if (next.size !== prev.size) {
                    return next;
                }
                return prev;
            });
        }
    }, [pendingItems]);

    const { data: products } = useQuery({
        queryKey: ['products-purgatory'],
        queryFn: async () => {
            const response = await axios.get('/api/products');
            return response.data;
        }
    });

    const { data: vintageProducts } = useQuery({
        queryKey: ['vintage-unique-products'],
        queryFn: async () => {
            const response = await axios.get('/api/products?is_vintage=true');
            return response.data;
        }
    });

    useEffect(() => {
        if (vintageCustomName.trim()) {
            const list = selectedDivision === 'vintage' ? vintageProducts : products;
            const match = (list || []).find((p: any) => p.name.toLowerCase() === vintageCustomName.trim().toLowerCase());
            if (match) {
                setSelectedVintageProductId(match.id);
            } else {
                setSelectedVintageProductId(null);
            }
        } else {
            setSelectedVintageProductId(null);
        }
    }, [selectedDivision, vintageCustomName, products, vintageProducts]);


    const discardMutation = useMutation({
        mutationFn: async (id: number) => {
            return id;
        },
        onMutate: async (id) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === id);

            setPendingActions(prev => {
                if (prev.some(a => a.type === 'discard' && a.pendingIds.includes(id))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'discard',
                    pendingIds: [id],
                    scrapedName: item?.scraped_name,
                    action_url: item?.url,
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== id)
            );
            return { previousItems };
        },
        onError: (err, _id, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Discard enqueue failed:', err);
        },
        onSuccess: () => {
            // Background worker handles syncing
        }
    });

    const matchMutation = useMutation({
        mutationFn: async ({ pendingId, productId }: { pendingId: number, productId: number }) => {
            return { pendingId, productId };
        },
        onMutate: async ({ pendingId, productId }) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);

            setPendingActions(prev => {
                if (prev.some(a => a.type === 'match' && a.pendingIds.includes(pendingId))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'match',
                    pendingIds: [pendingId],
                    productId,
                    scrapedName: item?.scraped_name,
                    action_url: item?.url,
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setManualSearchTerm('');
        }
    });

    const matchVintageMutation = useMutation({
        mutationFn: async ({ pendingId, customName, productId, isVintage, subCategory }: { pendingId: number, customName?: string, productId?: number, isVintage: boolean, subCategory?: string }) => {
            return { pendingId, customName, productId, isVintage, subCategory };
        },
        onMutate: async ({ pendingId, customName, productId, isVintage, subCategory }) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);

            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'match-vintage',
                pendingIds: [pendingId],
                customName,
                productId,
                isVintage,
                subCategory,
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Vintage match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setIsVintageModalOpen(false);
        }
    });

    const matchMiscMutation = useMutation({
        mutationFn: async (pendingId: number) => {
            return pendingId;
        },
        onMutate: async (pendingId) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);
            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'match-misc',
                pendingIds: [pendingId],
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);
            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Miscellaneous match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setIsVintageModalOpen(false);
        }
    });

    // Atajo de teclado 'V' para abrir la modal de vinculación Vintage del item seleccionado
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                return;
            }

            if (selectedPendingId !== null && (e.key === 'v' || e.key === 'V')) {
                e.preventDefault();
                const item = (pendingItems || []).find((i: any) => i.id === selectedPendingId);
                if (item) {
                    openClassifyModal(item.id, item.scraped_name);
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedPendingId, pendingItems]);


    // Forensic Failures State
    const [failedActions, setFailedActions] = useState<any[]>(() => {
        const saved = localStorage.getItem('purgatory_sync_failures');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('purgatory_sync_failures', JSON.stringify(failedActions));
    }, [failedActions]);

    // Background Sync Engine (Refined Phase 31 - Non-blocking & Forensic)
    const isSyncing = useRef(false);

    useEffect(() => {
        if (pendingActions.length === 0 || isSyncing.current) return;

        const syncPending = async () => {
            if (isSyncing.current || pendingActions.length === 0) return;
            isSyncing.current = true;

            const failedIds = new Set(failedActions.map(f => f.action.id));
            const actionsToProcess = [...pendingActions].filter(a => !failedIds.has(a.id));

            if (actionsToProcess.length === 0) {
                isSyncing.current = false;
                return;
            }

            // 1. Group 'match' actions to send in bulk
            const matchActions = actionsToProcess.filter(a => a.type === 'match');
            if (matchActions.length > 0) {
                const batch = matchActions.slice(0, 20);
                const batchIds = batch.map(a => a.id);
                try {
                    const matchesPayload = batch.map(a => ({
                        pending_id: a.pendingIds[0],
                        product_id: a.productId
                    }));
                    await matchItemsBulk(matchesPayload);

                    // Add processed IDs to locallyProcessedIds
                    setLocallyProcessedIds(prev => {
                        const next = new Set(prev);
                        batch.flatMap(a => a.pendingIds).forEach((id: number) => next.add(id));
                        return next;
                    });

                    // Remove from pendingActions
                    setPendingActions(prev => prev.filter(a => !batchIds.includes(a.id)));
                    queryClient.invalidateQueries({ queryKey: ['purgatory'] });
                    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
                    queryClient.invalidateQueries({ queryKey: ['products'] });
                } catch (err: any) {
                    console.error('Bulk match sync failed:', err);
                    const errorMessage = err.response?.data?.detail || err.message || 'Unknown Error';
                    // Mark all actions in this batch as failed
                    setFailedActions(prev => {
                        const newFailures = [...prev];
                        for (const action of batch) {
                            if (!newFailures.some(f => f.action.id === action.id)) {
                                newFailures.push({
                                    action,
                                    error: errorMessage,
                                    timestamp: new Date().toISOString(),
                                    url: action.action_url || null,
                                    productId: action.productId || null
                                });
                            }
                        }
                        return newFailures;
                    });
                }
                isSyncing.current = false;
                return;
            }

            // 2. Process non-match actions (e.g. discard, vintage, misc) one by one
            const otherAction = actionsToProcess[0];
            try {
                if (otherAction.type === 'discard') {
                    await discardItem(otherAction.pendingIds[0]);
                } else if (otherAction.type === 'bulk-discard') {
                    await discardItemsBulk(otherAction.pendingIds);
                } else if (otherAction.type === 'match-vintage') {
                    const isV = otherAction.isVintage !== false;
                    await matchVintageItem(otherAction.pendingIds[0], otherAction.customName, otherAction.productId, isV, otherAction.subCategory);
                } else if (otherAction.type === 'match-misc') {
                    await matchMiscellaneousItem(otherAction.pendingIds[0]);
                }

                // Add processed IDs to locallyProcessedIds
                setLocallyProcessedIds(prev => {
                    const next = new Set(prev);
                    otherAction.pendingIds.forEach((id: number) => next.add(id));
                    return next;
                });

                // Remove from pendingActions
                setPendingActions(prev => prev.filter(a => a.id !== otherAction.id));
                queryClient.invalidateQueries({ queryKey: ['purgatory'] });
                if (otherAction.type === 'match-vintage' || otherAction.type === 'match-misc') {
                    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-products'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-unique-products'] });
                    queryClient.invalidateQueries({ queryKey: ['products'] });
                    queryClient.invalidateQueries({ queryKey: ['products-purgatory'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-miscellaneous'] });
                }
            } catch (err: any) {
                console.error(`Sync failed for action type ${otherAction.type}:`, otherAction.id, err);
                const errorMessage = err.response?.data?.detail || err.message || 'Unknown Error';
                setFailedActions(prev => {
                    if (prev.some(f => f.action.id === otherAction.id)) return prev;
                    return [...prev, {
                        action: otherAction,
                        error: errorMessage,
                        timestamp: new Date().toISOString(),
                        url: otherAction.action_url || null,
                        productId: otherAction.productId || null
                    }];
                });
            }

            isSyncing.current = false;
        };

        const interval = setInterval(syncPending, 4000); // Process queue every 4 seconds
        const initialTimeout = setTimeout(syncPending, 1000); // Fast initial run

        return () => {
            clearInterval(interval);
            clearTimeout(initialTimeout);
        };
    }, [pendingActions.length, failedActions.length]); // Re-run mainly to ensure the check continues


    const filteredProducts = (products || [])?.filter((p: any) =>
        !p.is_vintage && (
            (p.name || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase()) ||
            (p.figure_id || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase())
        )
    ).slice(0, 20);

    const handleInputChange = (val: string) => {
        setVintageCustomName(val);
        const list = selectedDivision === 'vintage' ? vintageProducts : products;
        const match = (list || []).find((p: any) => p.name.toLowerCase() === val.trim().toLowerCase());
        if (match) {
            setSelectedVintageProductId(match.id);
        } else {
            setSelectedVintageProductId(null);
        }
    };

    const selectedVintagePendingItem = (pendingItems || []).find((i: any) => i.id === vintageModalItemId);
    const vintageOracleSuggestions = selectedVintagePendingItem?.suggestions?.filter((sug: any) => 
        selectedDivision === 'vintage' ? sug.is_vintage === true : sug.is_vintage !== true
    ) || [];

    const vintageModalSuggestionsToDisplay = vintageCustomName.trim()
        ? (selectedDivision === 'vintage' ? vintageProducts || [] : products || [])
            .filter((p: any) => p.name.toLowerCase().includes(vintageCustomName.toLowerCase()))
            .slice(0, 5)
        : (vintageOracleSuggestions.length > 0
            ? vintageOracleSuggestions.map((sug: any) => ({
                id: sug.product_id,
                name: sug.name,
                figure_id: sug.figure_id,
                sub_category: sug.sub_category,
                reason: sug.reason,
                match_score: sug.match_score
            }))
            : (selectedDivision === 'vintage' ? vintageProducts || [] : products || []).slice(0, 5)
        );

    // Dynamic Filter for Pending Items (Main List)
    const pendingIdsToHide = new Set([
        ...pendingActions.flatMap(a => a.pendingIds),
        ...Array.from(locallyProcessedIds)
    ]);

    const filteredPendingItems = (pendingItems || []).filter((item: any) => {
        // Persistence Ghost Mode: Filter out locally hidden items
        if (pendingIdsToHide.has(item.id)) return false;

        const term = (searchTerm || "").toLowerCase();
        const matchesSearch = !searchTerm || (
            (item.scraped_name || "").toLowerCase().includes(term) ||
            (item.shop_name || "").toLowerCase().includes(term) ||
            (item.ean || "").toLowerCase().includes(term) ||
            item.id.toString().includes(term)
        );

        // ALWAYS keep the selected item visible so they don't lose context while matching
        if (item.id === selectedPendingId) return true;

        let matchesTransit = true;
        if (enableTransitFilter) {
            if (transitType === 'retail') {
                matchesTransit = item.source_type === 'Retail';
            } else if (transitType === 'p2p') {
                matchesTransit = item.source_type === 'Peer-to-Peer';
            }
        }

        return matchesSearch && matchesTransit;
    });

    // --- SORTING AND FILTERING FOR DECK & LIST ---
    const sortedAndFilteredItems = useMemo(() => {
        let items = [...filteredPendingItems];

        // 1. Filtrar por Tienda
        if (shopFilter !== 'all') {
            items = items.filter(i => i.shop_name?.toLowerCase() === shopFilter.toLowerCase());
        }

        // 2. Ordenación
        items.sort((a, b) => {
            const getBestScore = (item: any) => {
                if (!item.suggestions || item.suggestions.length === 0) return 0;
                const scores = item.suggestions.filter((s: any) => !s.is_vintage).map((s: any) => s.match_score || 0);
                return scores.length > 0 ? Math.max(...scores) : 0;
            };

            if (sortBy === 'newest') {
                return new Date(b.found_at).getTime() - new Date(a.found_at).getTime();
            } else if (sortBy === 'oldest') {
                return new Date(a.found_at).getTime() - new Date(b.found_at).getTime();
            } else if (sortBy === 'highest_match') {
                return getBestScore(b) - getBestScore(a);
            } else if (sortBy === 'lowest_match') {
                return getBestScore(a) - getBestScore(b);
            }
            return 0;
        });

        return items;
    }, [filteredPendingItems, sortBy, shopFilter]);

    // Sincronizar deckItems localmente de forma que conserve re-encolados
    const filteredHash = sortedAndFilteredItems.map(i => i.id).join(',');

    useEffect(() => {
        // Ordenar sortedAndFilteredItems de tal manera que los IDs en snoozedIds vayan al final
        const reordered = [...sortedAndFilteredItems].sort((a, b) => {
            const indexA = snoozedIds.indexOf(a.id);
            const indexB = snoozedIds.indexOf(b.id);
            
            if (indexA !== -1 && indexB !== -1) {
                return indexA - indexB; // Ambos snoozed, conservar orden de snooze
            }
            if (indexA !== -1) return 1; // a va al final
            if (indexB !== -1) return -1; // b va al final
            return 0; // Conservar orden relativo original
        });
        setDeckItems(reordered);
    }, [filteredHash, snoozedIds]);

    // Sincronizar la asociación por defecto con el primer item de la pila
    useEffect(() => {
        if (deckItems.length > 0) {
            const currentItem = deckItems[0];
            const firstSug = currentItem.suggestions?.filter((s: any) => !s.is_vintage)?.[0];
            setAssociatedProductId(firstSug ? firstSug.product_id : null);
        } else {
            setAssociatedProductId(null);
        }
        setIsSearchingAssociation(false);
        setManualSearchTerm('');
    }, [deckItems[0]?.id]);

    // Handlers para las Acciones del Mazo
    const handleApproveCard = (item: any) => {
        let prodId = associatedProductId;
        if (!prodId) {
            const sug = item.suggestions?.filter((s: any) => !s.is_vintage)?.[0];
            if (sug) prodId = sug.product_id;
        }

        if (!prodId) {
            alert('Vincule un producto del catálogo antes de aprobar.');
            setIsSearchingAssociation(true);
            setTimeout(() => {
                document.getElementById(`assoc-search-${item.id}`)?.focus();
            }, 50);
            return;
        }

        matchMutation.mutate({ pendingId: item.id, productId: prodId });
        setSnoozedIds(prev => prev.filter(id => id !== item.id));
        setDeckItems(prev => prev.filter(i => i.id !== item.id));
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    const handleDiscardCard = (item: any) => {
        discardMutation.mutate(item.id);
        setSnoozedIds(prev => prev.filter(id => id !== item.id));
        setDeckItems(prev => prev.filter(i => i.id !== item.id));
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    const handleSwipeDown = (item: any) => {
        setSnoozedIds(prev => {
            const filtered = prev.filter(id => id !== item.id);
            return [...filtered, item.id];
        });
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    // Keyboard controls listener for deck curating
    useEffect(() => {
        if (viewLayout !== 'mazo' || deckItems.length === 0) return;
        const currentItem = deckItems[0];

        const handleKeyDown = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                if (e.key === 'Escape') {
                    setIsSearchingAssociation(false);
                    target.blur();
                }
                return;
            }

            if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') {
                e.preventDefault();
                handleApproveCard(currentItem);
            } else if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') {
                e.preventDefault();
                handleDiscardCard(currentItem);
            } else if (e.key === 's' || e.key === 'S' || e.key === 'ArrowDown') {
                e.preventDefault();
                handleSwipeDown(currentItem);
            } else if (e.key === 'n' || e.key === 'N' || e.key === 'ArrowUp') {
                e.preventDefault();
                openClassifyModal(currentItem.id, currentItem.scraped_name);
            } else if (e.key === 'e' || e.key === 'E') {
                e.preventDefault();
                setIsSearchingAssociation(true);
                setTimeout(() => {
                    document.getElementById(`assoc-search-${currentItem.id}`)?.focus();
                }, 50);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [viewLayout, deckItems, associatedProductId]);

    // Dynamic list of unique shops in pending items for filter pills
    const uniqueShopsInPending = useMemo(() => {
        return Array.from(new Set((pendingItems || []).map((i: any) => i.shop_name).filter(Boolean))) as string[];
    }, [pendingItems]);

    // Pagination Logic (Lista tradicional)
    const totalItems = sortedAndFilteredItems.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedItems = sortedAndFilteredItems.slice(startIndex, startIndex + itemsPerPage);

    // Ensure we don't stay on an empty page after items are matched/discarded
    if (currentPage > 1 && paginatedItems.length === 0 && totalItems > 0) {
        setCurrentPage(Math.max(1, totalPages));
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-2 md:space-y-3 animate-in fade-in duration-700">
            {/* Header / Purgatory Status */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px] pointer-events-none"></div>

                <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div className="relative z-10 flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Flame className="h-3 w-3 md:h-4 md:w-4" />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                <span className="text-brand-primary">Purgatorio</span>
                            </h2>
                            {!isLoadingPending && pendingItems && pendingItems.length > 0 && (
                                <div className="ml-2 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-primary/10 border border-brand-primary/20 animate-in zoom-in-95 duration-500">
                                    <div className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-pulse"></div>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary">
                                        {pendingItems.length}
                                    </span>
                                </div>
                            )}
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium uppercase tracking-[0.1em]">
                            Purifica las reliquias para manifestarlas en el catálogo
                        </p>
                    </div>

                    {/* Persistence Sync Indicator (Condensed) */}
                    {pendingActions.length > 0 && (
                        <div className="flex items-center gap-6 px-6 py-4 rounded-3xl bg-brand-primary/10 border border-brand-primary/20 animate-in slide-in-from-right-4 duration-500 backdrop-blur-md">
                            <div className="space-y-1">
                                <p className="text-[10px] font-black uppercase tracking-widest text-brand-primary leading-none">
                                    Sincronización {isSyncing.current ? 'Activa' : 'Pendiente'}
                                </p>
                                <p className="text-[11px] font-bold text-white/50">{pendingActions.length} acciones restantes</p>
                                <div className="flex items-center gap-4">
                                    <button onClick={() => setShowForensic(true)} className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:text-white transition-colors">Forensics</button>
                                    <button
                                        onClick={() => {
                                            if (confirm('¿Limpiar el búfer local? Esto cancelará las acciones no sincronizadas.')) {
                                                setPendingActions([]);
                                                setLocallyProcessedIds(new Set());
                                                setFailedActions([]);
                                                localStorage.removeItem(PERSISTENCE_KEY);
                                                localStorage.removeItem('purgatory_sync_failures');
                                            }
                                        }}
                                        className="text-[9px] font-black uppercase tracking-widest text-red-500/40 hover:text-red-400 transition-colors"
                                    >
                                        Limpiar
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>




            {/* Global Search Bar */}
            <div className={`space-y-6 transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>

                {/* Search Bar */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
                        <Search className={`h-5 w-5 transition-colors ${searchTerm ? 'text-brand-primary' : 'text-white/20'}`} />
                    </div>
                    <input
                        type="text"
                        placeholder="Buscar reliquia en el abismo por nombre, tienda, EAN o ID..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="w-full bg-white/[0.02] border border-white/5 hover:border-white/10 focus:border-brand-primary/50 focus:bg-white/[0.04] rounded-3xl py-6 pl-16 pr-16 text-white placeholder:text-white/20 outline-none transition-all text-sm font-bold shadow-2xl"
                    />
                    {searchTerm && (
                        <button
                            onClick={() => setSearchTerm('')}
                            className="absolute inset-y-0 right-6 flex items-center text-white/20 hover:text-white transition-colors"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    )}
                </div>
                {searchTerm && !selectedPendingId && (
                    <div className="absolute -bottom-6 left-6 animate-in slide-in-from-top-1 flex items-center gap-4">
                        <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary bg-brand-primary/10 px-3 py-1 rounded-full border border-brand-primary/20">
                            Filtrando: {filteredPendingItems.length} resultados
                        </span>
                        {filteredPendingItems.length > 0 && (
                            <button
                                onClick={() => {
                                    const allIds = filteredPendingItems.map(i => i.id);
                                    setSelectedIds(prev => Array.from(new Set([...prev, ...allIds])));
                                }}
                                className="text-[10px] font-black uppercase tracking-widest text-white/65 hover:text-brand-primary transition-colors flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-brand-primary/20"
                            >
                                <CheckCircle2 className="h-3 w-3" /> Seleccionar Todos los Resultados
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Controles y Filtros del Purgatorio */}
            <div className={`space-y-4 bg-white/[0.01] border border-white/5 p-5 rounded-3xl backdrop-blur-md transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* 1. Selector de Diseño / Layout Toggle */}
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Diseño:</span>
                        <button
                            onClick={() => setViewLayout('mazo')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'mazo' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutGrid className="h-3 w-3" />
                            Modo Mazo
                        </button>
                        <button
                            onClick={() => setViewLayout('lista')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'lista' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutList className="h-3 w-3" />
                            Modo Listado
                        </button>
                    </div>

                    {/* 2. Ordenación del Mazo */}
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Ordenar por:</span>
                        <select
                            value={sortBy}
                            onChange={(e: any) => setSortBy(e.target.value)}
                            className="bg-black/60 border border-white/10 rounded-xl px-3 py-1.5 text-[10px] font-black uppercase tracking-widest text-white outline-none focus:border-brand-primary/50 transition-all cursor-pointer"
                        >
                            <option value="highest_match">Mayor Probabilidad</option>
                            <option value="lowest_match">Menor Probabilidad</option>
                            <option value="newest">Más Nuevas Primero</option>
                            <option value="oldest">Más Antiguas Primero</option>
                        </select>
                    </div>
                </div>

                <div className="h-px bg-white/5 my-2"></div>

                <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
                    {/* 3. Filtro de Tiendas (Chips Dinámicos) */}
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Tienda:</span>
                        <button
                            onClick={() => setShopFilter('all')}
                            className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === 'all' ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                        >
                            Todas
                        </button>
                        {uniqueShopsInPending.map(shop => (
                            <button
                                key={shop}
                                onClick={() => setShopFilter(shop)}
                                className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === shop ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                            >
                                {shop}
                            </button>
                        ))}
                    </div>

                    <div className="hidden md:block h-4 w-px bg-white/10"></div>

                    {/* 4. Filtro de Tránsito */}
                    <div className="flex items-center gap-3">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={enableTransitFilter}
                                onChange={(e) => {
                                    setEnableTransitFilter(e.target.checked);
                                    setCurrentPage(1);
                                }}
                                className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary"
                            />
                            <span className="text-[9px] font-black uppercase tracking-widest text-white/65 flex items-center gap-1">
                                <span className="h-1 w-1 rounded-full bg-orange-500 animate-pulse"></span>
                                Tránsito (Expr.)
                            </span>
                        </label>

                        {enableTransitFilter && (
                            <div className="flex items-center gap-1.5 animate-in slide-in-from-left-4 duration-300">
                                <button
                                    onClick={() => { setTransitType('all'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'all' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Todos
                                </button>
                                <button
                                    onClick={() => { setTransitType('retail'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'retail' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Retail
                                </button>
                                <button
                                    onClick={() => { setTransitType('p2p'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'p2p' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    P2P
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>


            {/* Purgatory List */}
            <div className="grid grid-cols-1 gap-6">
                {isLoadingPending ? (
                    <PowerSwordLoader variant="fullScreen" text="Escaneando el abismo..." />
                ) : pendingItems?.length === 0 ? (
                    <div className="flex min-h-[300px] flex-col items-center justify-center gap-6 rounded-3xl border-2 border-dashed border-white/5 bg-white/[0.02] text-center">
                        <CheckCircle2 className="h-12 w-12 text-green-500/40" />
                        <div className="max-w-xs space-y-1">
                            <p className="text-lg font-bold text-white/60">Purgatorio Vacío</p>
                            <p className="text-sm text-white/60">Todas las reliquias han sido purificadas o descartadas.</p>
                        </div>
                    </div>
                                ) : viewLayout === 'mazo' ? (
                    <div className="flex flex-col items-center justify-center py-6 min-h-[600px] relative w-full">
                        {deckItems.length === 0 ? (
                            <div className="flex flex-col items-center justify-center gap-4 text-center py-12 rounded-3xl border border-dashed border-white/10 bg-white/[0.01] w-full max-w-xl">
                                <CheckCircle2 className="h-12 w-12 text-green-500/40 animate-bounce" />
                                <div className="space-y-1">
                                    <p className="text-lg font-black text-white/60 uppercase tracking-widest">Fin del Mazo</p>
                                    <p className="text-xs text-white/65">Has procesado todas las cartas filtradas en esta ronda.</p>
                                </div>
                            </div>
                        ) : (
                            <div className="relative w-full max-w-xl flex flex-col items-center">
                                {/* Instrucciones rápidas en cabecera */}
                                <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 mb-6 text-[9px] font-black uppercase tracking-widest text-white/40 bg-white/[0.02] border border-white/5 px-4 py-2 rounded-full backdrop-blur-md select-none">
                                    <span>⬅️ [A] Descartar</span>
                                    <span>➡️ [D] Vincular</span>
                                    <span>⬇️ [S] Re-encolar</span>
                                    <span>⬆️ [N] Vintage</span>
                                    <span>🔍 [E] Buscar</span>
                                </div>

                                <div className="relative w-full h-[540px] flex items-center justify-center">
                                    <AnimatePresence>
                                        {deckItems.slice(0, 3).reverse().map((item) => {
                                            const originalIndex = deckItems.slice(0, 3).indexOf(item);
                                            const isTop = originalIndex === 0;
                                            return (
                                                <SwipeCard
                                                    key={item.id}
                                                    item={item}
                                                    isTop={isTop}
                                                    originalIndex={originalIndex}
                                                    handleApproveCard={handleApproveCard}
                                                    handleDiscardCard={handleDiscardCard}
                                                    handleSwipeDown={handleSwipeDown}
                                                    openClassifyModal={openClassifyModal}
                                                    isSearchingAssociation={isSearchingAssociation}
                                                    setIsSearchingAssociation={setIsSearchingAssociation}
                                                    associatedProductId={associatedProductId}
                                                    setAssociatedProductId={setAssociatedProductId}
                                                    manualSearchTerm={manualSearchTerm}
                                                    setManualSearchTerm={setManualSearchTerm}
                                                    filteredProducts={filteredProducts}
                                                    allProducts={products || []}
                                                />
                                            );
                                        })}
                                    </AnimatePresence>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <>
                        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-4 px-4 py-3 rounded-2xl bg-white/[0.03] border border-white/5">
                            <div className="flex items-center gap-3 md:gap-4 overflow-hidden">
                                <label className="flex items-center gap-2 cursor-pointer group shrink-0">
                                    <input
                                        type="checkbox"
                                        checked={paginatedItems.length > 0 && paginatedItems.every(item => selectedIds.includes(item.id))}
                                        onChange={(e) => {
                                            const pageIds = paginatedItems.map(i => i.id);
                                            if (e.target.checked) {
                                                setSelectedIds(prev => Array.from(new Set([...prev, ...pageIds])));
                                            } else {
                                                setSelectedIds(prev => prev.filter(id => !pageIds.includes(id)));
                                            }
                                        }}
                                        className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                    />
                                    <span className="text-[10px] font-black uppercase tracking-widest text-white/65 group-hover:text-white/60 transition-colors">
                                        <span className="hidden xs:inline">Seleccionar </span>Página
                                    </span>
                                </label>
                                <div className="h-4 w-px bg-white/10 shrink-0"></div>
                                <div className="text-[9px] md:text-[10px] font-black uppercase tracking-widest text-white/60 italic truncate">
                                    Fragmento {startIndex + 1}-{Math.min(startIndex + itemsPerPage, totalItems)} <span className="text-white/10 mx-0.5">/</span> Total: {totalItems}
                                </div>
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-colors"
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </button>
                                <div className="text-[10px] md:text-xs font-black text-white/60 whitespace-nowrap">Pág {currentPage} / {totalPages}</div>
                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-colors"
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </button>
                            </div>
                        </div>

                        {paginatedItems.map((item: any) => (
                            <div key={item.id} className={`group relative overflow-hidden rounded-3xl border transition-all duration-500 ${selectedPendingId === item.id ? 'bg-brand-primary/[0.03] border-brand-primary/30 shadow-[0_0_30px_rgba(var(--brand-primary-rgb),0.1)]' : 'bg-white/[0.02] border-white/5 hover:border-white/10'}`}>

                                {/* Card Main Body */}
                                <div className="p-5 md:p-6 flex flex-col gap-6 md:flex-row md:items-start">
                                    {/* Selection Checkbox */}
                                    <div className="pt-1">
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.includes(item.id)}
                                            onChange={(e) => {
                                                if (e.target.checked) setSelectedIds([...selectedIds, item.id]);
                                                else setSelectedIds(selectedIds.filter(id => id !== item.id));
                                            }}
                                            className="h-5 w-5 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                        />
                                    </div>

                                    {/* Thumbnail & Mobile Header */}
                                    <div className="flex items-start gap-5 w-full md:w-auto">
                                        <div className="relative h-24 w-24 md:h-32 md:w-32 shrink-0 overflow-hidden rounded-2xl bg-black border border-white/10 shadow-lg">
                                            {item.image_url ? (
                                                <img src={item.image_url} alt={item.scraped_name} className="h-full w-full object-cover p-1 transition-transform duration-700 group-hover:scale-110 opacity-80 group-hover:opacity-100" />
                                            ) : (
                                                <div className="flex h-full w-full items-center justify-center text-[10px] text-white/20 uppercase font-black tracking-widest">No IMG</div>
                                            )}
                                            {/* Shop Badge (Mobile Overlay) */}
                                            <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm py-1 text-center md:hidden">
                                                <span className="text-[9px] font-black text-white/60 uppercase tracking-tighter">{item.shop_name}</span>
                                            </div>
                                        </div>

                                        {/* Mobile Only Info Block */}
                                        <div className="flex-1 md:hidden space-y-2">
                                            <h3 className="text-sm font-bold text-white leading-snug line-clamp-3">{item.scraped_name}</h3>
                                            <div className="flex items-baseline gap-2">
                                                <span className="text-xl font-black text-brand-primary tracking-tight">{item.price} {item.currency}</span>
                                            </div>
                                            <span className="text-[10px] font-bold text-white/60">{new Date(item.found_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>

                                    {/* Desktop Info */}
                                    <div className="hidden md:flex flex-1 flex-col gap-3">
                                        <div className="flex items-center gap-3">
                                            <span className={`rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-widest border ${['kidinn', 'tradeinn', 'diveinn', 'bikeinn', 'motardinn', 'dressinn', 'smashinn', 'trekkinn', 'runnerinn', 'snowinn', 'swiminn', 'waveinn', 'traininn', 'goalinn', 'xtremeinn'].includes(item.shop_name?.toLowerCase()) ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' : 'bg-white/5 border-white/10 text-white/65'}`}>
                                                {item.shop_name}
                                            </span>
                                            <span className="text-[10px] text-white/20 font-bold tracking-wider">
                                                DETECTADO: {new Date(item.found_at).toLocaleString()}
                                            </span>
                                        </div>

                                        <h3 className="text-lg font-bold text-white/90 leading-snug max-w-2xl group-hover:text-white transition-colors">
                                            {item.scraped_name}
                                        </h3>

                                        <div className="flex items-center gap-6 pt-1">
                                            <div className="flex flex-col">
                                                <span className="text-[10px] font-black text-white/60 uppercase tracking-wider">Precio Detectado</span>
                                                <span className="text-2xl font-black text-white tracking-tight">{item.price} <span className="text-sm text-white/65">{item.currency}</span></span>
                                            </div>
                                            {item.ean && (
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-black text-white/60 uppercase tracking-wider">EAN / Ref</span>
                                                    <span className="text-sm font-mono font-bold text-white/60">{item.ean}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Actions Footer */}
                                <div className="border-t border-white/5 bg-black/20 p-4 md:px-6 flex items-center justify-between gap-4">
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-white/20 uppercase tracking-wider">
                                        <Database className="h-3 w-3" /> ID: #{item.id}
                                    </div>
                                    <div className="flex items-center gap-3 w-full md:w-auto">

                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="h-12 md:h-10 w-12 md:w-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white/65 hover:text-white hover:bg-white/10 transition-all"
                                            title="Ver en Tienda"
                                        >
                                            <ExternalLink className="h-5 w-5 md:h-4 md:w-4" />
                                        </a>
                                        <button
                                            onClick={() => discardMutation.mutate(item.id)}
                                            className="h-12 md:h-10 w-12 md:w-auto md:px-5 flex items-center justify-center rounded-xl bg-red-500/5 text-red-500/60 border border-red-500/10 hover:bg-red-500 hover:text-white hover:border-red-500 transition-all"
                                            title="Descartar Item"
                                        >
                                            <Trash2 className="h-5 w-5 md:h-4 md:w-4 md:mr-2" />
                                            <span className="hidden md:inline text-[10px] font-black uppercase tracking-widest">Descartar</span>
                                        </button>
                                        <button
                                            onClick={() => {
                                                setSelectedPendingId(selectedPendingId === item.id ? null : item.id);
                                                setManualSearchTerm('');
                                            }}
                                            className={`h-10 md:h-10 flex-1 md:flex-initial px-3 md:px-6 flex items-center justify-center rounded-xl text-[10px] md:text-xs font-black uppercase tracking-widest transition-all shadow-lg ${selectedPendingId === item.id
                                                ? 'bg-white text-black shadow-white/10 border-2 border-brand-primary'
                                                : 'bg-brand-primary text-white shadow-brand-primary/20 hover:brightness-110'}`}
                                        >
                                            {selectedPendingId === item.id ? 'Cerrar' : 'Vincular'}
                                            {selectedPendingId === item.id ? <X className="ml-1.5 h-3 w-3" /> : <Link className="ml-1.5 h-3.5 w-3.5" />}
                                        </button>
                                    </div>
                                </div>

                                {/* Matcher Drawer (The "Banner" Area) */}
                                {selectedPendingId === item.id && (
                                    <div className="border-t border-white/10 bg-gradient-to-b from-brand-primary/[0.02] to-transparent p-5 md:p-8 animate-in slide-in-from-top-4 duration-500">
                                        <div className="max-w-4xl mx-auto space-y-8">

                                            {/* Section 1: Oracle Suggestions (The Main Banner) */}
                                            {item.suggestions && item.suggestions.filter((sug: any) => !sug.is_vintage).length > 0 && !manualSearchTerm && (
                                                <div className="space-y-4">
                                                    <div className="flex items-center gap-3">
                                                        <div className="h-8 w-8 rounded-full bg-brand-primary/20 flex items-center justify-center animate-pulse">
                                                            <Zap className="h-4 w-4 text-brand-primary" />
                                                        </div>
                                                        <div>
                                                            <h4 className="text-sm font-black text-white uppercase tracking-widest">Sugerencias del Oráculo</h4>
                                                            <p className="text-[10px] font-bold text-white/65">Basado en coincidencia de nombre y metadatos</p>
                                                        </div>
                                                    </div>

                                                    <div className="grid grid-cols-1 gap-3">
                                                        {item.suggestions.filter((sug: any) => !sug.is_vintage).map((sug: any) => (
                                                            <div key={sug.product_id} className="group/btn relative flex items-center gap-4 overflow-hidden rounded-2xl border border-brand-primary/20 bg-brand-primary/5 p-4 text-left transition-all hover:border-brand-primary hover:bg-brand-primary/10">

                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2 mb-1">
                                                                        <span className="px-1.5 py-0.5 rounded bg-brand-primary/20 text-[9px] font-black text-brand-primary uppercase tracking-tighter">
                                                                            {sug.reason?.toUpperCase() || 'MATCH'}
                                                                        </span>
                                                                        <span className="text-[9px] font-bold text-white/60 uppercase tracking-widest">{sug.sub_category}</span>
                                                                    </div>
                                                                    <h5 className="text-base font-black text-white leading-tight">{sug.name}</h5>
                                                                    <p className="text-[10px] text-white/65 font-mono mt-0.5 uppercase tracking-tighter">Vincular con: <span className="text-brand-primary">{item.scraped_name}</span></p>
                                                                </div>

                                                                <div className="flex items-center gap-2">
                                                                    <button
                                                                        onClick={() => matchMutation.mutate({ pendingId: item.id, productId: sug.product_id })}
                                                                        disabled={matchMutation.isPending}
                                                                        className="flex items-center gap-2 rounded-xl bg-brand-primary/20 px-3 py-1.5 text-[9px] font-black uppercase text-brand-primary border border-brand-primary/30 hover:bg-brand-primary hover:text-white transition-all shadow-lg group/match"
                                                                    >
                                                                        <Link className="h-3 w-3" />
                                                                        Vincular
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Section 2: Manual Search */}
                                            <div className="space-y-4 pt-4 border-t border-white/5">
                                                <div className="flex items-center gap-3">
                                                    <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center">
                                                        <Search className="h-4 w-4 text-white/60" />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-sm font-black text-white uppercase tracking-widest">Búsqueda Manual</h4>
                                                        <p className="text-[10px] font-bold text-white/65">Explora el Gran Catálogo de Eternia</p>
                                                    </div>
                                                </div>

                                                <div className="relative group/input">
                                                    <Search className="absolute left-4 top-3.5 h-5 w-5 text-white/60 group-focus-within/input:text-brand-primary transition-colors" />
                                                    <input
                                                        type="text"
                                                        placeholder="Escribe el nombre de la figura..."
                                                        className="w-full rounded-2xl bg-black/40 border border-white/10 py-3.5 pl-12 pr-4 text-sm font-bold text-white placeholder:text-white/20 outline-none focus:border-brand-primary/50 focus:bg-black/60 transition-all focus:ring-1 focus:ring-brand-primary/20"
                                                        value={manualSearchTerm}
                                                        onChange={(e) => setManualSearchTerm(e.target.value)}
                                                    />
                                                </div>

                                                {/* Results List - Expanded height for Phase 32 */}
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-[400px] overflow-y-auto custom-scrollbar pr-2">
                                                    {(manualSearchTerm ? filteredProducts : []).map((p: any) => (
                                                        <button
                                                            key={p.id}
                                                            onClick={() => matchMutation.mutate({ pendingId: item.id, productId: p.id })}
                                                            className="flex items-center gap-3 rounded-xl bg-white/5 p-3 text-left hover:bg-white/10 border border-transparent hover:border-white/20 transition-all group/res"
                                                        >
                                                            <div className="h-10 w-10 shrink-0 rounded-lg bg-black/40 border border-white/5 flex items-center justify-center text-[9px] font-black text-white/60">
                                                                IMG
                                                            </div>
                                                            <div className="flex-1 min-w-0">
                                                                <div className="text-xs font-bold text-white truncate">{p.name}</div>
                                                                <div className="text-[9px] font-black text-white/60 uppercase tracking-widest">{p.figure_id}</div>
                                                            </div>
                                                            <CheckCircle2 className="h-4 w-4 text-brand-primary opacity-0 group-hover/res:opacity-100 transition-opacity" />
                                                        </button>
                                                    ))}
                                                    {manualSearchTerm && filteredProducts?.length === 0 && (
                                                        <div className="col-span-full py-8 text-center">
                                                            <p className="text-xs font-bold text-white/60">El Oráculo no ve nada...</p>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Compact Multidivision Pairing Box ("Fina") */}
                                                <div className="rounded-2xl border border-amber-500/10 bg-amber-500/[0.02] p-3 flex flex-row items-center justify-between gap-4 hover:border-amber-500/20 hover:bg-amber-500/[0.04] transition-all duration-300">
                                                    <div className="flex items-center gap-2.5 min-w-0">
                                                        <div className="h-7 w-7 rounded-lg bg-amber-500/10 flex items-center justify-center border border-amber-500/20 shrink-0">
                                                            <History className="h-3.5 w-3.5 text-amber-500" />
                                                        </div>
                                                        <div className="min-w-0">
                                                            <h5 className="text-[11px] font-black text-amber-500 uppercase tracking-widest leading-none mb-0.5">Clasificación de Catálogo</h5>
                                                            <p className="text-[9px] font-bold text-white/60 truncate max-w-[200px] sm:max-w-md uppercase tracking-tighter">Guardar como artículo independiente en Vintage o Nueva Eternia (Atajo: V)</p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => openClassifyModal(item.id, item.scraped_name)}
                                                        disabled={matchVintageMutation.isPending}
                                                        className="shrink-0 rounded-lg bg-amber-500/10 hover:bg-amber-500 hover:text-black border border-amber-500/30 px-3 py-1.5 text-[9px] font-black uppercase text-amber-400 transition-all hover:scale-105 duration-200"
                                                    >
                                                        Clasificar [V]
                                                    </button>
                                                </div>

                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                        }

                        {/* Bottom Pagination */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-center gap-4 py-8">
                                <button
                                    onClick={() => {
                                        setCurrentPage(p => Math.max(1, p - 1));
                                        window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    disabled={currentPage === 1}
                                    className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-all text-[10px] font-black uppercase tracking-widest text-white"
                                >
                                    Anterior
                                </button>
                                <div className="flex items-center gap-1">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        // Simple sliding window for page numbers
                                        let pageNum = currentPage;
                                        if (currentPage <= 3) pageNum = i + 1;
                                        else if (currentPage >= totalPages - 2) pageNum = totalPages - 4 + i;
                                        else pageNum = currentPage - 2 + i;

                                        if (pageNum <= 0 || pageNum > totalPages) return null;

                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => {
                                                    setCurrentPage(pageNum);
                                                    window.scrollTo({ top: 0, behavior: 'smooth' });
                                                }}
                                                className={`w-10 h-10 rounded-xl text-[10px] font-black transition-all ${currentPage === pageNum ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/65 hover:bg-white/10'}`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}
                                </div>
                                <button
                                    onClick={() => {
                                        setCurrentPage(p => Math.min(totalPages, p + 1));
                                        window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    disabled={currentPage === totalPages}
                                    className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-white/5 border border-white/5 disabled:opacity-20 hover:bg-white/10 transition-all text-[10px] font-black uppercase tracking-widest text-white"
                                >
                                    Siguiente
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Bulk Action Bar */}
            {
                selectedIds.length > 0 && (
                    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-8 duration-500">
                        <div className="bg-black/80 backdrop-blur-2xl border border-brand-primary/30 rounded-full px-8 py-4 flex items-center gap-8 shadow-[0_0_50px_rgba(14,165,233,0.3)]">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Seleccionados</span>
                                <span className="text-xl font-black text-white">{selectedIds.length} <span className="text-sm text-white/65">ITEMS</span></span>
                            </div>
                            <div className="h-8 w-px bg-white/10"></div>
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => setSelectedIds([])}
                                    className="text-xs font-black text-white/65 hover:text-white uppercase tracking-widest transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={() => discardBulkMutation.mutate(selectedIds)}
                                    disabled={discardBulkMutation.isPending}
                                    className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-full text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-red-500/20 flex items-center gap-2 disabled:opacity-50"
                                >
                                    {discardBulkMutation.isPending ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                    Descartar Seleccionados
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Forensic Inspection Modal */}
            {
                showForensic && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/90 backdrop-blur-xl animate-in fade-in duration-300">
                        <div className="relative w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden rounded-[2.5rem] border border-white/10 bg-gradient-to-br from-white/5 to-black shadow-2xl">
                            <div className="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-3">
                                        <ShieldAlert className="h-6 w-6 text-red-400" />
                                        <h3 className="text-2xl font-black text-white uppercase tracking-tight">Sala de Autopsia Forense</h3>
                                    </div>
                                    <p className="text-xs text-white/65 uppercase tracking-widest font-bold">Inspección de acciones estancadas en el búfer ({failedActions.length} items)</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    {failedActions.length > 1 && (
                                        <button
                                            onClick={() => {
                                                setFailedActions([]);
                                                // Removing from failures allows the sync engine to pick them up in the next cycle
                                            }}
                                            className="px-6 py-2.5 rounded-2xl bg-brand-primary/20 border border-brand-primary/30 text-brand-primary text-[10px] font-black uppercase tracking-widest hover:bg-brand-primary hover:text-white transition-all"
                                        >
                                            Reintentar Todo ({failedActions.length})
                                        </button>
                                    )}
                                    <button
                                        onClick={() => setShowForensic(false)}
                                        className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/65 hover:text-white transition-all"
                                    >
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                                {failedActions.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center gap-4 text-white/20">
                                        <CheckCircle2 className="h-12 w-12" />
                                        <p className="text-sm font-bold uppercase tracking-widest">No hay fallos registrados en esta sesión</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {failedActions.map((f, idx) => (
                                            <div key={idx} className="group relative overflow-hidden rounded-2xl border border-red-500/20 bg-red-500/[0.02] p-6 hover:bg-red-500/[0.04] transition-all">
                                                <div className="flex flex-col md:flex-row gap-6 items-start">
                                                    <div className="flex-1 space-y-4 min-w-0">
                                                        <div className="flex items-center gap-3">
                                                            <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter ${f.action.type === 'match' ? 'bg-brand-primary text-white' : 'bg-orange-500 text-white'}`}>
                                                                {f.action.type === 'match' ? 'VINCULACIÓN' : 'DESCARTE'}
                                                            </span>
                                                            <span className="text-[10px] font-bold text-white/20 font-mono">ID ACCIÓN: {f.action.id}</span>
                                                        </div>

                                                        <div className="space-y-1">
                                                            <h4 className="text-lg font-bold text-white leading-tight truncate" title={f.action.scrapedName || f.action.action_url || 'Sin Nombre'}>
                                                                {f.action.scrapedName || (f.action.action_url ? `URL: ${f.action.action_url.substring(0, 50)}...` : 'Ítem sin nombre (Carga previa)')}
                                                            </h4>
                                                            <div className="flex items-center gap-4">
                                                                {(f.action.action_url || f.url) && (
                                                                    <a href={f.action.action_url || f.url} target="_blank" rel="noreferrer" className="text-[10px] font-bold text-brand-primary hover:underline flex items-center gap-1">
                                                                        <ExternalLink className="h-3 w-3" /> Ver Oferta Original
                                                                    </a>
                                                                )}
                                                                {f.action.productId && (
                                                                    <span className="text-[10px] font-bold text-white/60 truncate">
                                                                        Objetivo: Producto #{f.action.productId}
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>

                                                        <div className="p-3 rounded-xl bg-black/40 border border-white/5">
                                                            <p className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-1 opacity-50">Log del Servidor:</p>
                                                            <p className="text-xs font-mono font-bold text-red-300 break-words">{f.error}</p>
                                                        </div>
                                                    </div>

                                                    <div className="flex flex-row md:flex-col gap-2 w-full md:w-auto shrink-0">
                                                        <button
                                                            onClick={() => {
                                                                // Force retry: Remove from failedActions to let the sync engine pick it up again
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                            }}
                                                            className="flex-1 md:w-32 py-2.5 rounded-xl bg-brand-primary text-white text-[10px] font-black uppercase tracking-widest hover:brightness-110 transition-all"
                                                        >
                                                            Reintentar
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                // Forced return to abyss: Remove from failedActions AND pendingActions
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                                setPendingActions(prev => prev.filter(a => a.id !== f.action.id));
                                                                setLocallyProcessedIds(prev => {
                                                                    const next = new Set(prev);
                                                                    f.action.pendingIds.forEach((id: number) => next.delete(id));
                                                                    return next;
                                                                });
                                                            }}
                                                            className="flex-1 md:w-32 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/60 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 hover:text-white transition-all"
                                                        >
                                                            Devolver al Abismo
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                // Remove from failures but keep in ghost mode (uncommon case, but available)
                                                                setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                            }}
                                                            className="p-2.5 rounded-xl bg-red-500/10 text-red-500/60 hover:bg-red-500 hover:text-white transition-all"
                                                            title="Limpiar Log de Error"
                                                        >
                                                            <Trash2 className="h-4 w-4 mx-auto" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="p-6 border-t border-white/5 bg-black/40 flex justify-end">
                                <button
                                    onClick={() => setShowForensic(false)}
                                    className="px-8 py-3 rounded-2xl bg-white/10 text-white text-xs font-black uppercase tracking-widest hover:bg-white/20 transition-all"
                                >
                                    Salir de Autopsia
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }



            {/* Modal de Clasificación Vintage / Nueva Eternia con Nombre Personalizado */}
            {isVintageModalOpen && (() => {
                const isVintageStyle = selectedDivision === 'vintage';
                return (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl animate-in fade-in duration-300" onClick={() => setIsVintageModalOpen(false)}>
                        <div className={`relative w-full max-w-lg overflow-hidden rounded-[2.5rem] border bg-gradient-to-b flex flex-col animate-in zoom-in-95 duration-300 transition-all duration-500 ${
                            isVintageStyle
                                ? 'from-[#1C1405] via-[#0C0903] to-[#050301] border-amber-500/30 shadow-[0_0_80px_rgba(245,158,11,0.15)]'
                                : 'from-[#081824] via-[#040C12] to-[#020609] border-brand-primary/30 shadow-[0_0_80px_rgba(14,165,233,0.15)]'
                        }`} onClick={(e) => e.stopPropagation()}>
                            
                            {/* Glow halo */}
                            <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full blur-[80px] pointer-events-none transition-all duration-500 ${
                                isVintageStyle ? 'bg-amber-500/5' : 'bg-brand-primary/5'
                            }`}></div>

                            {/* Modal Header */}
                            <div className={`p-6 pb-4 flex items-start justify-between border-b relative z-10 ${
                                isVintageStyle ? 'border-amber-500/10' : 'border-brand-primary/10'
                            }`}>
                                <div className="flex items-center gap-3">
                                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center border shrink-0 transition-all duration-500 ${
                                        isVintageStyle ? 'bg-amber-500/10 border-amber-500/20' : 'bg-brand-primary/10 border-brand-primary/20'
                                    }`}>
                                        {isVintageStyle ? (
                                            <History className="h-5 w-5 text-amber-500 transition-all duration-500" />
                                        ) : (
                                            <Database className="h-5 w-5 text-brand-primary transition-all duration-500" />
                                        )}
                                    </div>
                                    <div className="space-y-0.5">
                                        <h4 className="text-lg font-black tracking-tighter text-white uppercase transition-all duration-500">
                                            {isVintageStyle ? (
                                                <>Oráculo <span className="text-amber-500">Vintage</span></>
                                            ) : (
                                                <>Oráculo <span className="text-brand-primary">Nueva Eternia</span></>
                                            )}
                                        </h4>
                                        <p className="text-[9px] font-bold text-white/65 uppercase tracking-widest transition-all duration-500">
                                            {isVintageStyle ? 'Canalización y Vinculación Retro' : 'Vinculación de Reliquias Modernas'}
                                        </p>
                                    </div>
                                </div>
                                <button onClick={() => setIsVintageModalOpen(false)} className={`h-8 w-8 flex items-center justify-center rounded-xl bg-white/5 text-white/65 transition-all font-black ${
                                    isVintageStyle ? 'hover:bg-amber-500/20 hover:text-amber-400' : 'hover:bg-brand-primary/20 hover:text-brand-primary'
                                }`}>&times;</button>
                            </div>

                            {/* Pestañas de Selección de División */}
                            <div className="px-6 pt-4 flex gap-2 border-b border-white/5 relative z-10 bg-black/20 select-none shrink-0">
                                <button
                                    type="button"
                                    onClick={() => setSelectedDivision('vintage')}
                                    className={`flex-1 pb-3 flex items-center justify-center gap-2 border-b-2 text-[10px] font-black uppercase tracking-wider transition-all duration-300 ${
                                        selectedDivision === 'vintage'
                                            ? 'border-amber-500 text-amber-500 drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]'
                                            : 'border-transparent text-white/30 hover:text-white/50'
                                    }`}
                                >
                                    <History className="h-3.5 w-3.5" />
                                    <span>Eternia Vintage</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setSelectedDivision('modern')}
                                    className={`flex-1 pb-3 flex items-center justify-center gap-2 border-b-2 text-[10px] font-black uppercase tracking-wider transition-all duration-300 ${
                                        selectedDivision === 'modern'
                                            ? 'border-brand-primary text-brand-primary drop-shadow-[0_0_8px_rgba(14,165,233,0.4)]'
                                            : 'border-transparent text-white/30 hover:text-white/50'
                                    }`}
                                >
                                    <Database className="h-3.5 w-3.5" />
                                    <span>Nueva Eternia</span>
                                </button>
                            </div>
                            
                            {/* Modal Body */}
                            <div className="p-6 space-y-5 overflow-y-auto max-h-[50vh] custom-scrollbar relative z-10">
                                
                                {/* Scraped Info Card */}
                                <div className={`rounded-2xl border p-4 space-y-1 transition-all duration-500 ${
                                    isVintageStyle ? 'border-amber-500/10 bg-amber-500/[0.03]' : 'border-brand-primary/10 bg-brand-primary/[0.03]'
                                }`}>
                                    <span className={`text-[8px] font-black uppercase tracking-widest block transition-all duration-500 ${
                                        isVintageStyle ? 'text-amber-500/50' : 'text-brand-primary/50'
                                    }`}>Artículo del Purgatorio</span>
                                    <p className="text-xs font-black text-white/90 italic leading-tight">{vintageModalItemName}</p>
                                </div>

                                {/* Search / input field */}
                                <div className="space-y-2">
                                    <label className={`text-[10px] font-black uppercase tracking-widest block transition-all duration-500 ${
                                        isVintageStyle ? 'text-amber-500' : 'text-brand-primary'
                                    }`}>Buscar Figura o Crear Custom:</label>
                                    <div className="relative">
                                        <Search className={`absolute left-4 top-3.5 h-4 w-4 transition-all duration-500 ${
                                            isVintageStyle ? 'text-amber-500/40' : 'text-brand-primary/40'
                                        }`} />
                                        <input
                                            type="text"
                                            value={vintageCustomName}
                                            onChange={(e) => handleInputChange(e.target.value)}
                                            placeholder={isVintageStyle ? "Ej. He-Man, Skeletor, Beast Man..." : "Ej. He-Man Origins, Skeletor Masterverse..."}
                                            className={`w-full border focus:bg-black/35 focus:ring-1 rounded-2xl py-3.5 pl-11 pr-4 text-sm font-bold text-white outline-none transition-all placeholder:text-white/20 ${
                                                isVintageStyle 
                                                    ? 'bg-[#141004]/50 border-amber-500/20 hover:border-amber-500/40 focus:border-amber-500 focus:ring-amber-500/10' 
                                                    : 'bg-[#091016]/50 border-brand-primary/20 hover:border-brand-primary/40 focus:border-brand-primary focus:ring-brand-primary/10'
                                            }`}
                                            autoFocus
                                        />
                                    </div>
                                </div>

                                {/* Subcategory selector for modern items */}
                                {selectedDivision === 'modern' && (
                                    <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-200">
                                        <label className="text-[10px] font-black text-brand-primary uppercase tracking-widest block">Línea del Artículo / Subcategoría:</label>
                                        <div className="flex gap-2">
                                            {!showCustomSubCategoryInput ? (
                                                <select
                                                    value={customSubCategory}
                                                    onChange={(e) => {
                                                        if (e.target.value === 'custom') {
                                                            setShowCustomSubCategoryInput(true);
                                                            setCustomSubCategory('');
                                                        } else {
                                                            setCustomSubCategory(e.target.value);
                                                        }
                                                    }}
                                                    className="flex-1 bg-[#091016]/50 border border-brand-primary/20 hover:border-brand-primary/40 focus:border-brand-primary focus:bg-[#0c161f]/30 focus:ring-1 focus:ring-brand-primary/10 rounded-2xl py-3 px-4 text-xs font-bold text-white outline-none transition-all"
                                                >
                                                    <option value="Origins">Origins (Por defecto)</option>
                                                    <option value="Origins Deluxe">Origins Deluxe</option>
                                                    <option value="Origins Exclusives">Origins Exclusives</option>
                                                    <option value="Turtles of Grayskull">Turtles of Grayskull</option>
                                                    <option value="Masterverse">Masterverse</option>
                                                    <option value="custom">Otro (Especificar manual)...</option>
                                                </select>
                                            ) : (
                                                <div className="flex-1 flex gap-2 items-center">
                                                    <input
                                                        type="text"
                                                        value={customSubCategory}
                                                        onChange={(e) => setCustomSubCategory(e.target.value)}
                                                        placeholder="Ej. Cartoon Collection, Masterverse..."
                                                        className="flex-1 bg-[#091016]/50 border border-brand-primary/30 hover:border-brand-primary/55 focus:border-brand-primary focus:bg-[#0c161f]/30 focus:ring-1 focus:ring-brand-primary/10 rounded-2xl py-2.5 px-4 text-xs font-bold text-white outline-none transition-all"
                                                        autoFocus
                                                    />
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            setShowCustomSubCategoryInput(false);
                                                            setCustomSubCategory('Origins');
                                                        }}
                                                        className="px-3 py-2.5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 text-white/50 hover:text-white transition-all text-[10px] font-black uppercase shrink-0"
                                                        title="Volver a la lista predefinida"
                                                    >
                                                        Listado
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Enviar a Bazar del Oráculo box (Solo en Vintage por defecto, o para Bazar global) */}
                                {isVintageStyle && (
                                    <div className="rounded-2xl border border-dashed border-purple-500/20 bg-purple-500/[0.02] p-4 flex flex-col sm:flex-row items-center justify-between gap-3 hover:border-purple-500/30 hover:bg-purple-500/[0.04] transition-all">
                                        <div className="min-w-0 flex-1">
                                            <span className="text-[8px] font-black text-purple-400 uppercase tracking-widest">Lote o Varios MOTU</span>
                                            <h5 className="text-xs font-black text-white leading-none mt-1">Clasificar en el Bazar del Oráculo</h5>
                                            <p className="text-[9px] text-white/40 uppercase tracking-tighter mt-0.5">Envía este anuncio/lote directamente al Bazar del Oráculo.</p>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                matchMiscMutation.mutate(vintageModalItemId!);
                                            }}
                                            disabled={matchMiscMutation.isPending}
                                            className="w-full sm:w-auto px-4 py-2 rounded-xl bg-purple-600 text-white text-[9px] font-black uppercase tracking-widest hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-1.5 shrink-0 shadow-lg shadow-purple-500/20"
                                        >
                                            {matchMiscMutation.isPending ? <RefreshCcw className="h-3 w-3 animate-spin" /> : <Link className="h-3 w-3" />}
                                            <span>Clasificar en el Bazar</span>
                                        </button>
                                    </div>
                                )}

                                {/* Suggestions and catalog matching */}
                                <div className="space-y-3">
                                    <span className={`text-[9px] font-black uppercase tracking-widest block border-b pb-1 transition-all duration-500 ${
                                        isVintageStyle ? 'text-amber-500/60 border-amber-500/10' : 'text-brand-primary/60 border-brand-primary/10'
                                    }`}>
                                        {vintageCustomName.trim() 
                                            ? isVintageStyle ? 'Resultados en Eternia Vintage:' : 'Resultados en Nueva Eternia:'
                                            : 'Sugerencias de Emparejamiento (Oráculo):'}
                                    </span>

                                    <div className="space-y-2">
                                        {vintageModalSuggestionsToDisplay.length > 0 ? (
                                            vintageModalSuggestionsToDisplay.map((p: any) => (
                                                <div
                                                    key={p.id}
                                                    className={`flex items-center justify-between gap-3 p-3 rounded-xl border transition-all text-left ${
                                                        selectedVintageProductId === p.id 
                                                            ? isVintageStyle 
                                                                ? 'bg-amber-500/10 border-amber-500/45 shadow-[0_0_15px_rgba(245,158,11,0.1)]'
                                                                : 'bg-brand-primary/10 border-brand-primary/45 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                                                            : 'bg-white/[0.02] border-white/5 hover:bg-white/[0.04] hover:border-white/10'
                                                    }`}
                                                >
                                                    <div className="min-w-0 flex-1">
                                                        <span className={`text-[8px] font-bold uppercase tracking-widest block ${
                                                            isVintageStyle ? 'text-amber-500/50' : 'text-brand-primary/50'
                                                        }`}>
                                                            {p.sub_category || (isVintageStyle ? 'Vintage 80s' : 'Origins')}
                                                        </span>
                                                        <h5 className="text-xs font-black text-white truncate leading-tight mt-0.5">{p.name}</h5>
                                                        {p.reason && (
                                                            <span className={`px-1 py-0.5 rounded text-[7px] font-black uppercase tracking-tighter mr-1 ${
                                                                isVintageStyle ? 'bg-amber-500/20 text-amber-400' : 'bg-brand-primary/20 text-brand-primary'
                                                            }`}>
                                                                {p.reason.toUpperCase()}
                                                            </span>
                                                        )}
                                                        <span className="text-[8px] font-mono text-white/60 uppercase">ID: #{p.figure_id}</span>
                                                    </div>
                                                    <div className="flex items-center gap-1.5 shrink-0">
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                setVintageCustomName(p.name);
                                                                setSelectedVintageProductId(p.id);
                                                            }}
                                                            className={`px-2.5 py-1.5 rounded-lg text-[8px] font-black uppercase tracking-wider transition-all border ${
                                                                selectedVintageProductId === p.id 
                                                                    ? isVintageStyle 
                                                                        ? 'bg-amber-500 text-black border-amber-400'
                                                                        : 'bg-brand-primary text-white border-brand-primary/80'
                                                                    : 'bg-white/5 border-white/5 text-white/50 hover:bg-white/10'
                                                            }`}
                                                        >
                                                            {selectedVintageProductId === p.id ? 'Seleccionado' : 'Seleccionar'}
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                matchVintageMutation.mutate({
                                                                    pendingId: vintageModalItemId!,
                                                                    customName: p.name,
                                                                    productId: p.id,
                                                                    isVintage: isVintageStyle,
                                                                    subCategory: isVintageStyle ? undefined : customSubCategory
                                                                });
                                                            }}
                                                            className={`px-2.5 py-1.5 rounded-lg border transition-all text-[8px] font-black uppercase flex items-center gap-1 ${
                                                                isVintageStyle 
                                                                    ? 'bg-amber-500/20 text-amber-400 border-amber-500/30 hover:bg-amber-500 hover:text-black'
                                                                    : 'bg-brand-primary/20 text-brand-primary border-brand-primary/30 hover:bg-brand-primary hover:text-white'
                                                            }`}
                                                        >
                                                            <Link className="h-2.5 w-2.5" />
                                                            Vincular
                                                        </button>
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className={`rounded-xl border border-dashed p-6 text-center space-y-1 ${
                                                isVintageStyle ? 'border-amber-500/20 bg-amber-500/[0.01] text-amber-500/50' : 'border-brand-primary/20 bg-brand-primary/[0.01] text-brand-primary/50'
                                            }`}>
                                                <p className="text-[10px] font-bold uppercase">Sin coincidencia exacta</p>
                                                <p className="text-[9px] font-medium text-white/20 uppercase tracking-tighter">
                                                    {isVintageStyle 
                                                        ? 'Se creará un nuevo artículo vintage independiente en el catálogo.' 
                                                        : 'Se creará un nuevo artículo de Nueva Eternia independiente en el catálogo.'
                                                    }
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Create custom item button option */}
                                {vintageCustomName.trim() && !vintageModalSuggestionsToDisplay.some((p: any) => p.name.toLowerCase() === vintageCustomName.trim().toLowerCase()) && (
                                    <div className={`rounded-2xl border border-dashed p-4 flex flex-col sm:flex-row items-center justify-between gap-3 ${
                                        isVintageStyle ? 'border-amber-500/20 bg-amber-500/[0.02]' : 'border-brand-primary/20 bg-brand-primary/[0.02]'
                                    }`}>
                                        <div className="min-w-0 flex-1">
                                            <span className={`text-[8px] font-black uppercase tracking-widest block ${
                                                isVintageStyle ? 'text-amber-500' : 'text-brand-primary'
                                            }`}>
                                                {isVintageStyle ? 'Nueva Reliquia Vintage' : 'Nuevo Artículo Nueva Eternia'}
                                            </span>
                                            <h5 className="text-xs font-black text-white truncate leading-none mt-1">"{vintageCustomName}"</h5>
                                            {selectedDivision === 'modern' && (
                                                <span className="text-[8px] font-medium text-white/40 uppercase block mt-1">
                                                    Línea: {customSubCategory || 'Origins'}
                                                </span>
                                            )}
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                matchVintageMutation.mutate({
                                                    pendingId: vintageModalItemId!,
                                                    customName: vintageCustomName.trim(),
                                                    productId: undefined,
                                                    isVintage: isVintageStyle,
                                                    subCategory: isVintageStyle ? undefined : customSubCategory
                                                });
                                            }}
                                            className={`w-full sm:w-auto px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest hover:brightness-110 transition-all flex items-center justify-center gap-1 ${
                                                isVintageStyle 
                                                    ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/10' 
                                                    : 'bg-brand-primary text-white shadow-lg shadow-brand-primary/10'
                                            }`}
                                        >
                                            <span>Crear y Vincular</span>
                                        </button>
                                    </div>
                                )}

                            </div>

                            {/* Modal Footer */}
                            <div className={`p-6 border-t bg-black/45 flex items-center justify-end gap-3 relative z-10 ${
                                isVintageStyle ? 'border-amber-500/10' : 'border-brand-primary/10'
                            }`}>
                                <button
                                    onClick={() => setIsVintageModalOpen(false)}
                                    className="px-5 py-2.5 rounded-xl bg-white/5 text-white/50 hover:bg-white/10 hover:text-white text-[10px] font-black uppercase tracking-widest transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={() => {
                                        if (!vintageCustomName.trim()) {
                                            alert('Por favor, ingresa o selecciona un nombre para la figura.');
                                            return;
                                        }
                                        matchVintageMutation.mutate({
                                            pendingId: vintageModalItemId!,
                                            customName: vintageCustomName,
                                            productId: selectedVintageProductId || undefined,
                                            isVintage: isVintageStyle,
                                            subCategory: isVintageStyle ? undefined : customSubCategory
                                        });
                                    }}
                                    disabled={matchVintageMutation.isPending}
                                    className={`px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest hover:brightness-110 disabled:opacity-50 transition-all shadow-lg ${
                                        isVintageStyle 
                                            ? 'bg-amber-500 text-black shadow-amber-500/10' 
                                            : 'bg-brand-primary text-white shadow-brand-primary/10'
                                    }`}
                                >
                                    {matchVintageMutation.isPending 
                                        ? 'Vinculando...' 
                                        : isVintageStyle ? 'Vincular a Eternia' : 'Vincular a Nueva Eternia'
                                    }
                                </button>
                            </div>
                        </div>
                    </div>
                );
            })()}

            {/* Phase 40: Wallapop Oracle Bridge - Quick Preview */}
            {
                previewUrl && (
                    <QuickPreviewModal
                        url={previewUrl}
                        onClose={() => setPreviewUrl(null)}
                    />
                )
            }
        </div >
    );
});

export default Purgatory;
