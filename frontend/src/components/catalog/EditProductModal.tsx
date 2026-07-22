import React from 'react';
import type { UseMutationResult } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Settings, X, RefreshCw, Save } from 'lucide-react';
import type { Product } from '../../api/collection';

interface EditProductModalProps {
    isAdmin: boolean;
    editingProduct: Product | null;
    setEditingProduct: (product: Product | null) => void;
    handleSaveEdit: (e: React.FormEvent) => void;
    isIncognito: boolean;
    updateMutation: UseMutationResult<any, any, { id: number, data: any }, any>;
}

const EditProductModal: React.FC<EditProductModalProps> = ({
    isAdmin,
    editingProduct,
    setEditingProduct,
    handleSaveEdit,
    isIncognito,
    updateMutation
}) => {
    if (!isAdmin || !editingProduct) return null;

    return (
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
    );
};

export default EditProductModal;
