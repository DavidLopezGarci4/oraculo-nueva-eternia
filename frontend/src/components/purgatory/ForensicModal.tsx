import React from 'react';
import { Trash2, ExternalLink, CheckCircle2, ShieldAlert, X } from 'lucide-react';

interface ForensicModalProps {
    showForensic: boolean;
    forensicModalRef: React.RefObject<HTMLDivElement | null>;
    failedActions: any[];
    setFailedActions: React.Dispatch<React.SetStateAction<any[]>>;
    setShowForensic: (show: boolean) => void;
    setPendingActions: React.Dispatch<React.SetStateAction<any[]>>;
    setLocallyProcessedIds: React.Dispatch<React.SetStateAction<Set<number>>>;
}

const ForensicModal: React.FC<ForensicModalProps> = ({
    showForensic,
    forensicModalRef,
    failedActions,
    setFailedActions,
    setShowForensic,
    setPendingActions,
    setLocallyProcessedIds
}) => {
    if (!showForensic) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/90 backdrop-blur-xl animate-in fade-in duration-300">
            <div
                ref={forensicModalRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby="forensic-modal-title"
                tabIndex={-1}
                className="relative w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden rounded-[2.5rem] border border-white/10 bg-gradient-to-br from-white/5 to-black shadow-2xl outline-none"
            >
                <div className="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                    <div className="space-y-1">
                        <div className="flex items-center gap-3">
                            <ShieldAlert className="h-6 w-6 text-red-400" />
                            <h3 id="forensic-modal-title" className="text-2xl font-black text-white uppercase tracking-tight">Sala de Autopsia Forense</h3>
                        </div>
                        <p className="text-xs text-white/65 uppercase tracking-widest font-bold">Inspección de acciones estancadas en el búfer ({failedActions.length} items)</p>
                    </div>
                    <div className="flex items-center gap-3">
                        {failedActions.length > 1 && (
                            <button
                                onClick={() => {
                                    setFailedActions([]);
                                    // Removing from failures allows the sync engine to pick them up in the next cycle
                                }}
                                className="px-6 py-2.5 rounded-2xl bg-brand-primary/20 border border-brand-primary/30 text-brand-primary text-[10px] font-black uppercase tracking-widest hover:bg-brand-primary hover:text-white transition-all"
                            >
                                Reintentar Todo ({failedActions.length})
                            </button>
                        )}
                        <button
                            onClick={() => setShowForensic(false)}
                            aria-label="Cerrar"
                            className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/65 hover:text-white transition-all"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    {failedActions.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center gap-4 text-white/20">
                            <CheckCircle2 className="h-12 w-12" />
                            <p className="text-sm font-bold uppercase tracking-widest">No hay fallos registrados en esta sesión</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {failedActions.map((f, idx) => (
                                <div key={idx} className="group relative overflow-hidden rounded-2xl border border-red-500/20 bg-red-500/[0.02] p-6 hover:bg-red-500/[0.04] transition-all">
                                    <div className="flex flex-col md:flex-row gap-6 items-start">
                                        <div className="flex-1 space-y-4 min-w-0">
                                            <div className="flex items-center gap-3">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter ${f.action.type === 'match' ? 'bg-brand-primary text-white' : 'bg-orange-500 text-white'}`}>
                                                    {f.action.type === 'match' ? 'VINCULACIÓN' : 'DESCARTE'}
                                                </span>
                                                <span className="text-[10px] font-bold text-white/20 font-mono">ID ACCIÓN: {f.action.id}</span>
                                            </div>

                                            <div className="space-y-1">
                                                <h4 className="text-lg font-bold text-white leading-tight truncate" title={f.action.scrapedName || f.action.action_url || 'Sin Nombre'}>
                                                    {f.action.scrapedName || (f.action.action_url ? `URL: ${f.action.action_url.substring(0, 50)}...` : 'Ítem sin nombre (Carga previa)')}
                                                </h4>
                                                <div className="flex items-center gap-4">
                                                    {(f.action.action_url || f.url) && (
                                                        <a href={f.action.action_url || f.url} target="_blank" rel="noreferrer" className="text-[10px] font-bold text-brand-primary hover:underline flex items-center gap-1">
                                                            <ExternalLink className="h-3 w-3" /> Ver Oferta Original
                                                        </a>
                                                    )}
                                                    {f.action.productId && (
                                                        <span className="text-[10px] font-bold text-white/60 truncate">
                                                            Objetivo: Producto #{f.action.productId}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            <div className="p-3 rounded-xl bg-black/40 border border-white/5">
                                                <p className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-1 opacity-50">Log del Servidor:</p>
                                                <p className="text-xs font-mono font-bold text-red-300 break-words">{f.error}</p>
                                            </div>
                                        </div>

                                        <div className="flex flex-row md:flex-col gap-2 w-full md:w-auto shrink-0">
                                            <button
                                                onClick={() => {
                                                    // Force retry: Remove from failedActions to let the sync engine pick it up again
                                                    setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                }}
                                                className="flex-1 md:w-32 py-2.5 rounded-xl bg-brand-primary text-white text-[10px] font-black uppercase tracking-widest hover:brightness-110 transition-all"
                                            >
                                                Reintentar
                                            </button>
                                            <button
                                                onClick={() => {
                                                    // Forced return to abyss: Remove from failedActions AND pendingActions
                                                    setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                    setPendingActions(prev => prev.filter(a => a.id !== f.action.id));
                                                    setLocallyProcessedIds(prev => {
                                                        const next = new Set(prev);
                                                        f.action.pendingIds.forEach((id: number) => next.delete(id));
                                                        return next;
                                                    });
                                                }}
                                                className="flex-1 md:w-32 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/60 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 hover:text-white transition-all"
                                            >
                                                Devolver al Abismo
                                            </button>
                                            <button
                                                onClick={() => {
                                                    // Remove from failures but keep in ghost mode (uncommon case, but available)
                                                    setFailedActions(prev => prev.filter(fail => fail.action.id !== f.action.id));
                                                }}
                                                className="p-2.5 rounded-xl bg-red-500/10 text-red-500/60 hover:bg-red-500 hover:text-white transition-all"
                                                title="Limpiar Log de Error"
                                            >
                                                <Trash2 className="h-4 w-4 mx-auto" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-white/5 bg-black/40 flex justify-end">
                    <button
                        onClick={() => setShowForensic(false)}
                        className="px-8 py-3 rounded-2xl bg-white/10 text-white text-xs font-black uppercase tracking-widest hover:bg-white/20 transition-all"
                    >
                        Salir de Autopsia
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ForensicModal;
