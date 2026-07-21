import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Download, RefreshCw, Activity } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';
import type { WallapopIpLog } from '../../api/purgatory';

interface IpLogsModalProps {
    isOpen: boolean;
    onClose: () => void;
    ipLogs: WallapopIpLog[];
    loadingIpLogs: boolean;
    onDownload: () => void;
}

/** Fase AAA-4a: extraido de Config.tsx ("Modal de Auditoría IP Wallapop"). */
export default function IpLogsModal({ isOpen, onClose, ipLogs, loadingIpLogs, onDownload }: IpLogsModalProps) {
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
                        aria-labelledby="ip-logs-modal-title"
                        tabIndex={-1}
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className="relative w-full max-w-4xl max-h-[85vh] overflow-hidden rounded-[2.5rem] border border-white/10 bg-black/90 p-6 md:p-8 shadow-2xl backdrop-blur-3xl ring-1 ring-white/5 flex flex-col gap-6 text-white outline-none"
                    >
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <div className="p-3 bg-brand-primary/10 rounded-2xl border border-brand-primary/20">
                                    <Globe className="h-6 w-6 text-brand-primary" />
                                </div>
                                <div>
                                    <h3 id="ip-logs-modal-title" className="text-lg font-black uppercase tracking-widest text-white">Auditoría de Conectividad IP</h3>
                                    <p className="text-xs text-white/65 font-bold uppercase tracking-wider">Historial de WAF checks y bloqueos de Wallapop</p>
                                </div>
                            </div>
                            <button
                                onClick={onDownload}
                                className="flex items-center gap-2 rounded-xl bg-brand-primary px-4 py-2.5 text-xs font-bold text-white transition-all hover:scale-105 hover:bg-brand-primary/80 active:scale-95 shadow-lg shadow-brand-primary/20 w-full sm:w-auto justify-center"
                            >
                                <Download className="h-4 w-4" />
                                DESCARGAR LOG (.TXT)
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto min-h-[300px] border border-white/5 rounded-2xl bg-white/[0.02] p-2 custom-scrollbar">
                            {loadingIpLogs ? (
                                <div className="flex h-64 flex-col items-center justify-center text-white/20 gap-4">
                                    <RefreshCw className="h-8 w-8 text-brand-primary animate-spin" />
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em]">Leyendo Crónicas de Red...</p>
                                </div>
                            ) : ipLogs.length === 0 ? (
                                <div className="flex h-64 flex-col items-center justify-center text-white/10 gap-3">
                                    <Activity className="h-12 w-12 text-white/5 animate-pulse" />
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em]">Ningún registro en las bitácoras</p>
                                </div>
                            ) : (
                                <table className="w-full text-left text-xs text-white/70">
                                    <thead>
                                        <tr className="border-b border-white/10 text-[9px] font-black uppercase tracking-widest text-white/65">
                                            <th className="p-3">Fecha</th>
                                            <th className="p-3">Dirección IP</th>
                                            <th className="p-3">Entorno</th>
                                            <th className="p-3">Estado</th>
                                            <th className="p-3 text-center">HTTP</th>
                                            <th className="p-3">Detalles WAF / Logs</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5 font-mono">
                                        {ipLogs.map((log) => {
                                            const isBlocked = log.status === 'blocked';
                                            const isAllowed = log.status === 'allowed';

                                            return (
                                                <tr key={log.id} className="hover:bg-white/[0.02] transition-colors">
                                                    <td className="p-3 whitespace-nowrap text-white/65 font-sans text-[10px]">
                                                        {new Date(log.recorded_at).toLocaleString('es-ES', {
                                                            year: 'numeric',
                                                            month: '2-digit',
                                                            day: '2-digit',
                                                            hour: '2-digit',
                                                            minute: '2-digit',
                                                            second: '2-digit'
                                                        })}
                                                    </td>
                                                    <td className="p-3 font-bold text-white/80">{log.ip_address}</td>
                                                    <td className="p-3 text-[10px] uppercase font-sans font-bold text-white/60">{log.environment || 'Local'}</td>
                                                    <td className="p-3">
                                                        <span className={`px-2 py-0.5 rounded text-[8px] font-black tracking-wider uppercase ${
                                                            isAllowed
                                                                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                                                : isBlocked
                                                                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                                                                    : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                                        }`}>
                                                            {log.status}
                                                        </span>
                                                    </td>
                                                    <td className="p-3 text-center font-bold">{log.response_code !== null && log.response_code !== undefined ? log.response_code : '-'}</td>
                                                    <td className="p-3 max-w-[250px] truncate text-[10px] text-white/65 font-sans" title={log.details}>
                                                        {log.details || 'Sin detalles'}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            )}
                        </div>

                        <div className="flex justify-end pt-2 border-t border-white/5">
                            <button
                                onClick={onClose}
                                className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all hover:scale-105 active:scale-95"
                            >
                                Cerrar Portal
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
