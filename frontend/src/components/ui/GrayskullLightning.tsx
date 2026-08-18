import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface GrayskullLightningProps {
    active: boolean;
    onComplete?: () => void;
    color?: 'emerald' | 'gold' | 'cyan';
}

export const GrayskullLightning: React.FC<GrayskullLightningProps> = ({
    active,
    onComplete,
    color = 'emerald'
}) => {
    const colorStyles = {
        emerald: 'from-emerald-400 via-teal-300 to-cyan-400 shadow-emerald-500/50',
        gold: 'from-amber-300 via-yellow-200 to-amber-500 shadow-yellow-500/50',
        cyan: 'from-cyan-400 via-sky-300 to-blue-500 shadow-cyan-500/50'
    }[color];

    return (
        <AnimatePresence>
            {active && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 1.02 }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    onAnimationComplete={onComplete}
                    className="absolute inset-0 pointer-events-none rounded-xl z-30 overflow-hidden"
                >
                    {/* Borde eléctrico animado */}
                    <div
                        className={`absolute inset-0 rounded-xl border-2 border-transparent bg-gradient-to-r ${colorStyles} opacity-80 animate-pulse`}
                        style={{
                            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                            maskComposite: 'exclude',
                            WebkitMaskComposite: 'xor',
                            padding: '2px'
                        }}
                    />

                    {/* Resplandor central de la Espada */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: [0, 0.6, 0], scale: [0.8, 1.2, 1.4] }}
                        transition={{ duration: 0.7 }}
                        className="absolute inset-0 bg-gradient-to-tr from-emerald-500/20 via-cyan-400/10 to-transparent blur-md"
                    />
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default GrayskullLightning;
