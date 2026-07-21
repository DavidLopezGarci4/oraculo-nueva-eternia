import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';

interface ResetConfirmModalProps {
    resetStep: number; // 0: idle, 1: first confirm, 2: second confirm
    isResetting: boolean;
    onCancel: () => void;
    onAdvance: () => void; // resetStep 1 -> 2
    onConfirm: () => void; // resetStep 2 -> handleResetSmartMatches
}

/** Fase AAA-4a: extraido de Config.tsx ("Double Confirmation Modal for Reset"). */
export default function ResetConfirmModal({ resetStep, isResetting, onCancel, onAdvance, onConfirm }: ResetConfirmModalProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    useModalA11y(resetStep > 0, () => { if (!isResetting) onCancel(); }, containerRef);

    return (
        <AnimatePresence>
            {resetStep > 0 && (
                <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => !isResetting && onCancel()}
                        className="absolute inset-0 bg-black/95 backdrop-blur-xl"
                    />
                    <motion.div
                        ref={containerRef}
                        role="alertdialog"
                        aria-modal="true"
                        aria-labelledby="reset-modal-title"
                        tabIndex={-1}
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className={`relative w-full max-w-md overflow-hidden rounded-[2.5rem] border p-8 shadow-2xl outline-none ${resetStep === 1 ? 'border-orange-500/30 bg-orange-950/20' : 'border-red-500/50 bg-red-950/30'}`}
                    >
                        <div className="flex flex-col items-center gap-6 text-center">
                            <div className={`h-20 w-20 rounded-full flex items-center justify-center border animate-pulse ${resetStep === 1 ? 'bg-orange-500/20 border-orange-500/50' : 'bg-red-500/20 border-red-500/80'}`}>
                                <ShieldAlert className={`h-10 w-10 ${resetStep === 1 ? 'text-orange-500' : 'text-red-500'}`} />
                            </div>

                            <div className="space-y-2">
                                <h3 id="reset-modal-title" className="text-3xl font-black text-white uppercase tracking-tighter">
                                    {resetStep === 1 ? '¿ESTÁS SEGURO?' : '¡ÚLTIMO AVISO!'}
                                </h3>
                                <p className="text-sm text-white/60 leading-relaxed font-bold">
                                    {resetStep === 1
                                        ? 'Esta acción devolverá todas las vinculaciones automáticas al Purgatorio. Las capturas manuales están a salvo.'
                                        : 'Estás a un paso de reiniciar el ecosistema de SmartMatch. Esta acción no se puede deshacer.'}
                                </p>
                            </div>

                            <div className="grid w-full grid-cols-2 gap-4">
                                <button
                                    disabled={isResetting}
                                    onClick={onCancel}
                                    className="rounded-2xl border border-white/10 bg-white/5 py-4 text-xs font-black text-white/65 hover:bg-white/10 transition-all uppercase tracking-widest"
                                >
                                    Cancelar
                                </button>
                                <button
                                    disabled={isResetting}
                                    onClick={() => resetStep === 1 ? onAdvance() : onConfirm()}
                                    className={`rounded-2xl py-4 text-xs font-black text-white transition-all uppercase tracking-widest shadow-lg ${resetStep === 1 ? 'bg-orange-500 hover:bg-orange-600 shadow-orange-500/20' : 'bg-red-600 hover:bg-red-700 shadow-red-500/40'}`}
                                >
                                    {isResetting ? 'PURIFICANDO...' : resetStep === 1 ? 'COMPRENDO' : 'PURIFICAR TODO'}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
