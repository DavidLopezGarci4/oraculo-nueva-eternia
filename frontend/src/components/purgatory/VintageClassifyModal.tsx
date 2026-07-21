import React from 'react';
import type { UseMutationResult } from '@tanstack/react-query';
import { History, Database, Search, Link, RefreshCcw } from 'lucide-react';

interface VintageClassifyModalProps {
    isVintageModalOpen: boolean;
    vintageModalRef: React.RefObject<HTMLDivElement | null>;
    setIsVintageModalOpen: (open: boolean) => void;
    selectedDivision: 'vintage' | 'modern';
    setSelectedDivision: (division: 'vintage' | 'modern') => void;
    vintageModalItemName: string;
    vintageCustomName: string;
    setVintageCustomName: (name: string) => void;
    handleInputChange: (val: string) => void;
    showCustomSubCategoryInput: boolean;
    setShowCustomSubCategoryInput: (show: boolean) => void;
    customSubCategory: string;
    setCustomSubCategory: (value: string) => void;
    matchMiscMutation: UseMutationResult<any, any, number, any>;
    vintageModalItemId: number | null;
    vintageModalSuggestionsToDisplay: any[];
    selectedVintageProductId: number | null;
    setSelectedVintageProductId: (id: number | null) => void;
    matchVintageMutation: UseMutationResult<any, any, { pendingId: number, customName?: string, productId?: number, isVintage: boolean, subCategory?: string }, any>;
}

const VintageClassifyModal: React.FC<VintageClassifyModalProps> = ({
    isVintageModalOpen,
    vintageModalRef,
    setIsVintageModalOpen,
    selectedDivision,
    setSelectedDivision,
    vintageModalItemName,
    vintageCustomName,
    setVintageCustomName,
    handleInputChange,
    showCustomSubCategoryInput,
    setShowCustomSubCategoryInput,
    customSubCategory,
    setCustomSubCategory,
    matchMiscMutation,
    vintageModalItemId,
    vintageModalSuggestionsToDisplay,
    selectedVintageProductId,
    setSelectedVintageProductId,
    matchVintageMutation
}) => {
    if (!isVintageModalOpen) return null;

    const isVintageStyle = selectedDivision === 'vintage';
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl animate-in fade-in duration-300" onClick={() => setIsVintageModalOpen(false)}>
            <div
                ref={vintageModalRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby="vintage-classify-modal-title"
                tabIndex={-1}
                className={`relative w-full max-w-lg overflow-hidden rounded-[2.5rem] border bg-gradient-to-b flex flex-col animate-in zoom-in-95 duration-300 transition-all duration-500 outline-none ${
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
                            <h4 id="vintage-classify-modal-title" className="text-lg font-black tracking-tighter text-white uppercase transition-all duration-500">
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
                    <button onClick={() => setIsVintageModalOpen(false)} aria-label="Cerrar" className={`h-8 w-8 flex items-center justify-center rounded-xl bg-white/5 text-white/65 transition-all font-black ${
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
                            <label htmlFor="purgatory-subcategory-select" className="text-[10px] font-black text-brand-primary uppercase tracking-widest block">Línea del Artículo / Subcategoría:</label>
                            <div className="flex gap-2">
                                {!showCustomSubCategoryInput ? (
                                    <select
                                        id="purgatory-subcategory-select"
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
};

export default VintageClassifyModal;
