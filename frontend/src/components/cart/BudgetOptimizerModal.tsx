import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Package, ShoppingBag, X } from 'lucide-react';
import axios from 'axios';

interface BudgetOptimizerModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAddItemsToCart: (items: any[]) => void;
}

export const BudgetOptimizerModal: React.FC<BudgetOptimizerModalProps> = ({
    isOpen,
    onClose,
    onAddItemsToCart
}) => {
    const [budget, setBudget] = useState<number>(80);
    const [loading, setLoading] = useState<boolean>(false);
    const [result, setResult] = useState<any | null>(null);

    if (!isOpen) return null;

    const handleOptimize = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const res = await axios.post(
                '/api/cart/budget-optimize',
                { budget_limit: budget, user_location: 'ES' },
                { headers: token ? { Authorization: `Bearer ${token}` } : {} }
            );
            setResult(res.data);
        } catch (e) {
            console.error('Error optimizing budget:', e);
        } finally {
            setLoading(false);
        }
    };

    const handleApply = () => {
        if (result && result.selected_items) {
            onAddItemsToCart(result.selected_items);
            onClose();
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[200] flex items-center justify-center p-3 sm:p-6 bg-black/90 backdrop-blur-2xl overflow-y-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.93, y: 15 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.93, y: 15 }}
                    className="relative w-full max-w-xl bg-gradient-to-b from-slate-900 via-slate-950 to-black border-2 border-brand-primary/50 rounded-3xl shadow-[0_0_60px_rgba(0,0,0,0.9)] p-5 sm:p-6 text-white my-auto flex flex-col max-h-[88vh] overflow-hidden"
                >
                    {/* Botón cerrar */}
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 p-2 rounded-full bg-slate-800/90 hover:bg-red-500 text-slate-300 hover:text-white transition z-20 shadow-md"
                        title="Cerrar Asistente"
                    >
                        <X className="h-4 w-4" />
                    </button>

                    {/* Header */}
                    <div className="flex items-center gap-3 mb-4 border-b border-white/10 pb-3 pr-10">
                        <div className="p-2.5 bg-brand-primary/20 border border-brand-primary/40 rounded-2xl text-brand-primary shrink-0 shadow-lg">
                            <Sparkles className="h-5 w-5" />
                        </div>
                        <div>
                            <h3 className="text-base sm:text-lg font-black text-white uppercase tracking-wider">
                                Asistente de Presupuesto (Matrix Cart)
                            </h3>
                            <p className="text-[11px] text-slate-400">
                                Maximiza tus compras agrupando envíos y ahorrando el máximo posible
                            </p>
                        </div>
                    </div>

                    {/* Selector de Presupuesto */}
                    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 mb-4">
                        <div className="flex items-center justify-between text-xs text-slate-300 mb-2">
                            <span>¿Cuál es tu presupuesto disponible?</span>
                            <span className="font-bold text-brand-primary text-sm">{budget} €</span>
                        </div>
                        <input
                            type="range"
                            min="30"
                            max="250"
                            step="5"
                            value={budget}
                            onChange={(e) => setBudget(Number(e.target.value))}
                            className="w-full accent-brand-primary cursor-pointer mb-2"
                        />
                        <div className="flex items-center gap-1.5 justify-between">
                            {[40, 60, 80, 100, 150].map((b) => (
                                <button
                                    key={b}
                                    onClick={() => setBudget(b)}
                                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-md border transition ${
                                        budget === b
                                            ? 'bg-brand-primary/20 border-brand-primary text-brand-primary'
                                            : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                                    }`}
                                >
                                    {b} €
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Botón de Cálculo */}
                    {!result && (
                        <button
                            onClick={handleOptimize}
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-brand-primary to-amber-500 hover:from-brand-primary/90 hover:to-amber-500/90 text-black font-bold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-2"
                        >
                            {loading ? 'Calculando combinación óptima...' : '🧙‍♂️ Calcular Cesta Óptima'}
                        </button>
                    )}

                    {/* Resultados de la Optimización */}
                    {result && (
                        <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
                            {/* Tarjeta de Resumen */}
                            <div className="grid grid-cols-3 gap-2 bg-slate-900/90 border border-emerald-500/30 rounded-xl p-3 text-center">
                                <div>
                                    <span className="text-[10px] text-slate-400 block">Total Invertido:</span>
                                    <span className="font-bold text-white text-sm">{result.total_spent} €</span>
                                </div>
                                <div>
                                    <span className="text-[10px] text-slate-400 block">Figuras Conseguidas:</span>
                                    <span className="font-bold text-cyan-400 text-sm">{result.items_count} figuras</span>
                                </div>
                                <div>
                                    <span className="text-[10px] text-slate-400 block">Ahorro Total:</span>
                                    <span className="font-bold text-emerald-400 text-sm">+{result.savings_total} €</span>
                                </div>
                            </div>

                            {/* Lista de Figuras Sugeridas */}
                            <div className="space-y-1.5">
                                <span className="text-slate-400 text-[11px] font-semibold">Cesta Sugerida:</span>
                                {result.selected_items.map((item: any, idx: number) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between p-2.5 bg-slate-950/80 border border-slate-800 rounded-lg"
                                    >
                                        <div className="flex items-center gap-2 truncate">
                                            <Package className="h-4 w-4 text-amber-400 shrink-0" />
                                            <div className="truncate">
                                                <div className="font-bold text-white truncate text-xs">{item.product_name}</div>
                                                <div className="text-[10px] text-slate-400">
                                                    {item.shop_name} • Base: {item.base_price.toFixed(2)}€
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right shrink-0">
                                            <div className="font-bold text-emerald-400 text-xs">
                                                {item.landed_price.toFixed(2)} € <span className="text-[9px] text-slate-400">Landed</span>
                                            </div>
                                            <div className="text-[9px] text-emerald-400 font-semibold">
                                                -{item.savings_pct}% ahorro
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Botones de Acción */}
                            <div className="flex items-center gap-2 pt-2">
                                <button
                                    onClick={() => setResult(null)}
                                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition"
                                >
                                    Recalcular
                                </button>
                                <button
                                    onClick={handleApply}
                                    className="flex-1 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-black font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-500/20"
                                >
                                    <ShoppingBag className="h-4 w-4" />
                                    Añadir {result.items_count} Figuras al Carrito
                                </button>
                            </div>
                        </div>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default BudgetOptimizerModal;
