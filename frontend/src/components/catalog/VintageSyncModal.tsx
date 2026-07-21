import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, X } from 'lucide-react';

interface VintageSyncModalProps {
    showVintageSyncModal: boolean;
    setShowVintageSyncModal: (show: boolean) => void;
    vintageSyncStatus: string;
    vintageSyncLogs: string;
}

const VintageSyncModal: React.FC<VintageSyncModalProps> = ({
    showVintageSyncModal,
    setShowVintageSyncModal,
    vintageSyncStatus,
    vintageSyncLogs
}) => {
    if (!showVintageSyncModal) return null;

    return (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="w-full max-w-2xl overflow-hidden rounded-3xl border border-amber-500/25 bg-[#0f0e0c]/95 backdrop-blur-2xl shadow-[0_0_50px_rgba(245,158,11,0.2)]"
            >
                <div className="p-6 border-b border-white/5 bg-gradient-to-r from-amber-500/10 to-transparent flex items-center justify-between">
                    <div className="flex items-center gap-2 text-amber-500">
                        <RefreshCw className={`h-5 w-5 ${vintageSyncStatus === 'running' ? 'animate-spin' : ''}`} />
                        <h3 className="font-black uppercase tracking-widest text-white text-sm md:text-base">
                            Nexo Maestro Vintage: Telemetría
                        </h3>
                    </div>
                    {vintageSyncStatus !== 'running' && (
                        <button
                            onClick={() => setShowVintageSyncModal(false)}
                            className="rounded-xl bg-white/5 p-2 text-white/50 hover:bg-white/10 hover:text-white transition-all border border-white/5 cursor-pointer"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>

                <div className="p-6 space-y-4">
                    <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-white/65">
                        <span>Estado de la Incursión</span>
                        <span className={`px-2.5 py-0.5 rounded-full border text-[8px] font-black uppercase tracking-widest ${
                            vintageSyncStatus === 'running' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400 animate-pulse' :
                            vintageSyncStatus === 'completed' ? 'bg-green-500/10 border-green-500/20 text-green-400' :
                            vintageSyncStatus === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                            'bg-white/5 border-white/10 text-white/50'
                        }`}>
                            {vintageSyncStatus === 'running' ? 'Sincronizando...' :
                             vintageSyncStatus === 'completed' ? 'Completado' :
                             vintageSyncStatus === 'error' ? 'Fallo Crítico' :
                             'Inactivo'}
                        </span>
                    </div>

                    {/* Terminal window */}
                    <div className="h-64 overflow-y-auto rounded-2xl bg-black/80 p-5 border border-white/5 font-mono text-[10px] md:text-xs text-amber-400/90 space-y-1.5 shadow-inner scrollbar-thin">
                        {vintageSyncLogs.split('\n').map((line, i) => (
                            <div key={i} className={line.startsWith('❌') ? 'text-red-400' : line.startsWith('✅') ? 'text-green-400' : ''}>
                                {line}
                            </div>
                        ))}
                    </div>
                </div>

                <div className="p-6 border-t border-white/5 bg-white/[0.01] flex items-center justify-end gap-3">
                    {vintageSyncStatus !== 'running' ? (
                        <button
                            onClick={() => setShowVintageSyncModal(false)}
                            className="bg-amber-500 hover:bg-amber-600 text-black px-6 py-2.5 rounded-xl font-black uppercase tracking-widest text-xs transition-all shadow-[0_0_20px_rgba(245,158,11,0.2)] cursor-pointer"
                        >
                            Cerrar Telemetría
                        </button>
                    ) : (
                        <span className="text-[10px] font-bold uppercase tracking-wider text-white/60 animate-pulse">
                            Ejecutando Secuencia en Segundo Plano...
                        </span>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default VintageSyncModal;
