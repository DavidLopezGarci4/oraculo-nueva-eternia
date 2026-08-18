import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Copy, Check, X, Award, Calendar, Tag } from 'lucide-react';
import { MOTUImage } from '../ui/MOTUImage';

interface TradingCardModalProps {
    isOpen: boolean;
    onClose: () => void;
    item: {
        id: number;
        product_name?: string;
        name?: string;
        image_url?: string;
        condition?: string;
        grading?: number;
        purchase_price?: number;
        current_value?: number;
        sub_category?: string;
        release_year?: number;
        sku?: string;
        shelf_wear?: string;
    } | null;
}

export const TradingCardModal: React.FC<TradingCardModalProps> = ({ isOpen, onClose, item }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [copied, setCopied] = useState(false);

    if (!isOpen || !item) return null;

    const name = item.product_name || item.name || 'Figura MOTU';
    const condition = (item.condition || 'MOC').toUpperCase();
    const purchase = item.purchase_price || 0.0;
    const market = item.current_value || purchase || 19.99;
    const profit = market - purchase;
    const roiPct = purchase > 0 ? ((profit / purchase) * 100).toFixed(1) : '0.0';

    const handleCopy = () => {
        const textSummary = `🛡️ [Cromo de Colección: ${name}]\n• Estado: ${condition}\n• Inversión: ${purchase.toFixed(2)}€\n• Valor Mercado: ${market.toFixed(2)}€ (${profit >= 0 ? '+' : ''}${profit.toFixed(2)}€ | ${roiPct}%)\n🏰 Custodiado en La Fortaleza de Grayskull`;
        navigator.clipboard.writeText(textSummary);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    className="relative w-full max-w-sm sm:max-w-md bg-gradient-to-b from-slate-900 via-slate-950 to-black border-2 border-amber-500/40 rounded-2xl shadow-2xl p-5 overflow-hidden text-white"
                >
                    {/* Botón cerrar */}
                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 p-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition z-10"
                    >
                        <X className="h-5 w-5" />
                    </button>

                    {/* Contenedor del Cromo / Trading Card */}
                    <div
                        ref={cardRef}
                        className="relative rounded-xl border border-amber-500/30 bg-gradient-to-b from-slate-900/90 to-slate-950 p-4 shadow-inner overflow-hidden"
                    >
                        {/* Efecto holográfico de fondo */}
                        <div className="absolute -right-16 -top-16 w-36 h-36 rounded-full bg-cyan-500/10 blur-2xl pointer-events-none" />
                        <div className="absolute -left-16 -bottom-16 w-36 h-36 rounded-full bg-amber-500/10 blur-2xl pointer-events-none" />

                        {/* Cabecera del Cromo */}
                        <div className="flex items-center justify-between border-b border-amber-500/20 pb-2 mb-3">
                            <div className="flex items-center gap-1.5">
                                <Shield className="h-4 w-4 text-amber-400" />
                                <span className="text-[11px] font-black uppercase tracking-wider text-amber-300">
                                    {item.sub_category || 'Origins'}
                                </span>
                            </div>
                            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/30 text-[10px] font-bold text-amber-300">
                                <Award className="h-3 w-3" />
                                <span>{condition}</span>
                            </div>
                        </div>

                        {/* Foto de la Figura */}
                        <div className="relative h-56 sm:h-64 w-full rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden mb-3 group">
                            <MOTUImage
                                src={item.image_url}
                                alt={name}
                                className="max-h-full max-w-full object-contain p-2 transition duration-300 group-hover:scale-105"
                            />
                            {/* Insignia de Grado */}
                            {item.grading && (
                                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 border border-emerald-500/50 text-emerald-400 text-xs font-mono font-bold">
                                    GRADE {item.grading}
                                </div>
                            )}
                        </div>

                        {/* Título de la Figura */}
                        <h3 className="text-base sm:text-lg font-black text-slate-100 tracking-wide text-center truncate mb-1">
                            {name}
                        </h3>
                        <div className="flex items-center justify-center gap-3 text-xs text-slate-400 mb-4">
                            {item.release_year && (
                                <span className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" /> {item.release_year}
                                </span>
                            )}
                            {item.sku && (
                                <span className="flex items-center gap-1 font-mono">
                                    <Tag className="h-3 w-3" /> {item.sku}
                                </span>
                            )}
                        </div>

                        {/* Métricas Financieras del Cromo */}
                        <div className="grid grid-cols-2 gap-2 bg-slate-900/80 border border-slate-800 rounded-lg p-2.5 mb-3 text-xs">
                            <div>
                                <span className="text-slate-400 block text-[10px]">Coste de Entrada:</span>
                                <span className="font-bold text-white text-sm">{purchase.toFixed(2)} €</span>
                            </div>
                            <div className="text-right">
                                <span className="text-slate-400 block text-[10px]">Valoración Actual:</span>
                                <span className="font-bold text-emerald-400 text-sm">{market.toFixed(2)} €</span>
                            </div>
                        </div>

                        {/* Pie Oficial */}
                        <div className="text-center border-t border-slate-800/80 pt-2 text-[10px] text-slate-400 tracking-wider uppercase font-semibold">
                            🏰 La Fortaleza de Grayskull • Nueva Eternia
                        </div>
                    </div>

                    {/* Botones de Acción */}
                    <div className="flex items-center justify-between gap-3 mt-4">
                        <button
                            onClick={handleCopy}
                            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition"
                        >
                            {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
                            {copied ? '¡Copiado!' : 'Copiar Ficha'}
                        </button>
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-brand-primary/20 hover:bg-brand-primary/30 border border-brand-primary/40 text-brand-primary rounded-lg text-xs font-semibold transition"
                        >
                            Aceptar
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TradingCardModal;
