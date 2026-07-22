import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, AlertCircle, Shield, ChevronDown } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';

interface AddUserModalProps {
    isOpen: boolean;
    onClose: () => void;
}

/**
 * Fase AAA-4a: extraido de Config.tsx (era el bloque "Modal de Registro de
 * Usuario (Mock)"). Sigue siendo un mock de solo lectura -- el registro real
 * de usuarios se hace por otra via; este modal documenta el flujo futuro.
 */
export default function AddUserModal({ isOpen, onClose }: AddUserModalProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    useModalA11y(isOpen, onClose, containerRef);

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                    />
                    <motion.div
                        ref={containerRef}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="add-user-modal-title"
                        tabIndex={-1}
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className="relative w-full max-w-lg glass border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl outline-none"
                    >
                        <div className="p-8 space-y-6">
                            <div className="flex items-center justify-between">
                                <h3 id="add-user-modal-title" className="text-2xl font-black text-white uppercase tracking-tighter">Reclutar <span className="text-brand-primary">Héroe</span></h3>
                                <div className="bg-brand-primary/20 p-2 rounded-lg text-brand-primary"><Users className="h-5 w-5" /></div>
                            </div>

                            <div className="space-y-4 opacity-50">
                                <div className="space-y-2">
                                    <label htmlFor="mock-add-user-username" className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Nombre de Usuario</label>
                                    <input id="mock-add-user-username" type="text" disabled placeholder="Ej: He-Man" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                </div>
                                <div className="space-y-2">
                                    <label htmlFor="mock-add-user-email" className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Correo Electrónico</label>
                                    <input id="mock-add-user-email" type="email" disabled placeholder="defensor@eternia.com" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label htmlFor="mock-add-user-password" className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Contraseña</label>
                                        <input id="mock-add-user-password" type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                    <div className="space-y-2">
                                        <label htmlFor="mock-add-user-password-confirm" className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Confirmar</label>
                                        <input id="mock-add-user-password-confirm" type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label htmlFor="mock-add-user-role" className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Rango del Héroe (Rol)</label>
                                    <div className="relative flex items-center">
                                        <Shield className="absolute left-4 h-4 w-4 text-brand-primary pointer-events-none" />
                                        <select id="mock-add-user-role" disabled className="w-full bg-white/5 border border-white/10 rounded-2xl pl-11 pr-10 py-3 text-white/50 focus:outline-none appearance-none font-bold">
                                            <option>Guardián de Eternia (Viewer)</option>
                                            <option>Master del Universo (Admin)</option>
                                        </select>
                                        <ChevronDown className="absolute right-4 h-4 w-4 text-white/30 pointer-events-none" />
                                    </div>
                                </div>
                            </div>

                            <div className="pt-4 flex flex-col gap-3">
                                <div className="flex items-center gap-2 text-[10px] text-brand-primary font-bold uppercase tracking-widest justify-center">
                                    <AlertCircle className="h-3 w-3" />
                                    Modo Lectura Activo
                                </div>
                                <button
                                    disabled
                                    className="w-full bg-brand-primary opacity-30 text-white py-4 rounded-2xl font-black uppercase tracking-widest"
                                >
                                    REGISTRAR EN EL ORÁCULO
                                </button>
                                <button
                                    onClick={onClose}
                                    className="w-full py-2 text-white/60 text-xs font-bold hover:text-white transition-colors"
                                >
                                    VOLVAR ATRÁS
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
