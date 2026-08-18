import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Shield, Sparkles } from 'lucide-react';

interface GrayskullLightningProps {
    active: boolean;
    onComplete?: () => void;
    color?: 'emerald' | 'gold' | 'cyan';
    productName?: string;
    showToast?: boolean;
}

export const GrayskullLightning: React.FC<GrayskullLightningProps> = ({
    active,
    onComplete,
    color = 'emerald',
    productName,
    showToast = true
}) => {
    const colorGlow = {
        emerald: 'shadow-[0_0_50px_rgba(16,185,129,0.9)] border-emerald-400',
        gold: 'shadow-[0_0_50px_rgba(245,158,11,0.9)] border-amber-400',
        cyan: 'shadow-[0_0_50px_rgba(6,182,212,0.9)] border-cyan-400'
    }[color];

    return (
        <AnimatePresence>
            {active && (
                <>
                    {/* 1. Resplandor y Relámpago en la Tarjeta */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 1.05 }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        onAnimationComplete={onComplete}
                        className={`absolute inset-0 pointer-events-none rounded-2xl z-40 overflow-hidden border-2 ${colorGlow}`}
                    >
                        {/* Destello eléctrico expansivo */}
                        <motion.div
                            initial={{ opacity: 0.9, scale: 0.8 }}
                            animate={{ opacity: 0, scale: 1.8 }}
                            transition={{ duration: 0.7 }}
                            className="absolute inset-0 bg-gradient-to-tr from-emerald-400/40 via-yellow-300/30 to-cyan-400/40 blur-xl"
                        />

                        {/* Rayo central iconográfico */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <motion.div
                                initial={{ scale: 0, rotate: -20 }}
                                animate={{ scale: [0, 1.4, 1.1], rotate: [0, 10, 0] }}
                                exit={{ scale: 0, opacity: 0 }}
                                transition={{ duration: 0.5 }}
                                className="p-3 rounded-full bg-black/80 border border-emerald-400/80 shadow-2xl backdrop-blur-md"
                            >
                                <Zap className="h-8 w-8 text-yellow-300 animate-bounce fill-yellow-400 drop-shadow-[0_0_12px_rgba(250,204,21,1)]" />
                            </motion.div>
                        </div>
                    </motion.div>

                    {/* 2. Toast Flotante Épico Móvil / Desktop (Power Toast) */}
                    {showToast && (
                        <motion.div
                            initial={{ opacity: 0, y: -40, scale: 0.85 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.9 }}
                            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                            className="fixed top-5 left-1/2 -translate-x-1/2 z-50 pointer-events-none w-[90%] max-w-md"
                        >
                            <div className="relative rounded-2xl bg-gradient-to-r from-slate-950/95 via-black/95 to-slate-950/95 border-2 border-amber-400/80 shadow-[0_0_40px_rgba(245,158,11,0.5)] p-3.5 flex items-center gap-3 backdrop-blur-xl">
                                <div className="p-2 rounded-xl bg-gradient-to-br from-amber-400 to-yellow-600 text-black shadow-lg shrink-0">
                                    <Shield className="h-5 w-5 fill-black" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-1.5 text-[11px] font-black text-amber-300 uppercase tracking-wider">
                                        <Sparkles className="h-3.5 w-3.5 text-yellow-300" />
                                        <span>¡Por el Poder de Grayskull!</span>
                                    </div>
                                    <p className="text-xs font-bold text-white truncate">
                                        {productName || 'Figura'} asegurada en tu Fortaleza
                                    </p>
                                </div>
                                <div className="px-2 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-[10px] font-black uppercase tracking-widest shrink-0">
                                    +1 Reliquia
                                </div>
                            </div>
                        </motion.div>
                    )}
                </>
            )}
        </AnimatePresence>
    );
};

export default GrayskullLightning;
