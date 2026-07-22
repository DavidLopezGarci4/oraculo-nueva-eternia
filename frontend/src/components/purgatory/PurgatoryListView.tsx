import React from 'react';
import type { UseMutationResult } from '@tanstack/react-query';
import { CheckCircle2, ChevronLeft, ChevronRight, Database, ExternalLink, History, Link, Search, Trash2, X, Zap } from 'lucide-react';

interface PurgatoryListViewProps {
    paginatedItems: any[];
    selectedIds: number[];
    setSelectedIds: React.Dispatch<React.SetStateAction<number[]>>;
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    totalPages: number;
    startIndex: number;
    totalItems: number;
    itemsPerPage: number;
    discardMutation: UseMutationResult<any, any, number, any>;
    selectedPendingId: number | null;
    setSelectedPendingId: (id: number | null) => void;
    manualSearchTerm: string;
    setManualSearchTerm: (term: string) => void;
    filteredProducts: any[];
    matchMutation: UseMutationResult<any, any, { pendingId: number, productId: number }, any>;
    openClassifyModal: (itemId: number, name: string) => void;
    matchVintageMutation: UseMutationResult<any, any, any, any>;
}

const PurgatoryListView: React.FC<PurgatoryListViewProps> = ({
    paginatedItems,
    selectedIds,
    setSelectedIds,
    currentPage,
    setCurrentPage,
    totalPages,
    startIndex,
    totalItems,
    itemsPerPage,
    discardMutation,
    selectedPendingId,
    setSelectedPendingId,
    manualSearchTerm,
    setManualSearchTerm,
    filteredProducts,
    matchMutation,
    openClassifyModal,
    matchVintageMutation
}) => {
    return (
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
            ))}

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
    );
};

export default PurgatoryListView;
