import React, { useEffect, useState } from 'react';
import { Radio, Play, RefreshCw, CheckCircle2, XCircle, Clock, Loader2, Zap, ShieldQuestion } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { runScrapers, createWallapopJob, getWallapopJobs } from '../../api/purgatory';
import type { WallapopJob } from '../../api/purgatory';

const STATUS_META: Record<WallapopJob['status'], { label: string; className: string; icon: React.ReactNode }> = {
    pending: { label: 'Pendiente', className: 'bg-white/10 text-white/60', icon: <Clock className="h-3 w-3" /> },
    running: { label: 'En Ejecución', className: 'bg-blue-500/20 text-blue-400', icon: <Loader2 className="h-3 w-3 animate-spin" /> },
    done: { label: 'Completado', className: 'bg-green-500/20 text-green-400', icon: <CheckCircle2 className="h-3 w-3" /> },
    error: { label: 'Fallido', className: 'bg-red-500/20 text-red-400', icon: <XCircle className="h-3 w-3" /> },
};

/**
 * WallapopNexusBridge — UI de la Fase 3 del plan (docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md).
 *
 * Ofrece dos vías alternativas cuando Wallapop bloquea el scraper automático:
 *  1. Disparo directo del spider "WallapopManual" (API v3 firmada) para un intento inmediato.
 *  2. Encolar un trabajo para el Nexus Local Bridge, resuelto por un worker corriendo
 *     en el PC del usuario (IP residencial) vía scripts/nexus_local_worker.py.
 */
const WallapopNexusBridge: React.FC = () => {
    const [query, setQuery] = useState('auto');
    const [isRunningDirect, setIsRunningDirect] = useState(false);
    const [directResult, setDirectResult] = useState<{ success: boolean; message: string } | null>(null);

    const [isQueueing, setIsQueueing] = useState(false);
    const [queueResult, setQueueResult] = useState<{ success: boolean; message: string } | null>(null);

    const [jobs, setJobs] = useState<WallapopJob[]>([]);

    const fetchJobs = async () => {
        try {
            const data = await getWallapopJobs(15);
            setJobs(data);
        } catch (error) {
            console.error('Error fetching Nexus Bridge jobs:', error);
        }
    };

    useEffect(() => {
        fetchJobs();
        const hasActive = jobs.some(j => j.status === 'pending' || j.status === 'running');
        const interval = setInterval(fetchJobs, hasActive ? 6000 : 20000);
        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [jobs.some(j => j.status === 'pending' || j.status === 'running')]);

    const handleRunDirect = async () => {
        setIsRunningDirect(true);
        setDirectResult(null);
        try {
            await runScrapers('WallapopManual', 'manual_ui', query || 'auto');
            setDirectResult({ success: true, message: '⚔️ Incursión "WallapopManual" desplegada. Revisa la Consola Táctica para el resultado.' });
        } catch (error) {
            setDirectResult({ success: false, message: '❌ Error al desplegar la incursión. Verifica la conexión con el servidor.' });
        } finally {
            setIsRunningDirect(false);
        }
    };

    const handleEnqueueJob = async () => {
        setIsQueueing(true);
        setQueueResult(null);
        try {
            const res = await createWallapopJob(query || 'auto');
            setQueueResult({ success: true, message: `📡 ${res.message}` });
            fetchJobs();
        } catch (error) {
            setQueueResult({ success: false, message: '❌ Error al encolar el trabajo del Nexus Bridge.' });
        } finally {
            setIsQueueing(false);
        }
    };

    return (
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mt-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-cyan-500/20 rounded-lg">
                    <Radio className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-white">Wallapop Alternativo (Nexus Bridge)</h3>
                    <p className="text-sm text-slate-400">API v3 firmada (X-Signature) + resolución vía IP residencial</p>
                </div>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-4 mb-4 text-sm space-y-2">
                <p className="text-amber-400 font-medium flex items-center gap-2">
                    <ShieldQuestion className="w-4 h-4" /> ¿Cuándo usar esto?
                </p>
                <p className="text-slate-400 text-xs leading-relaxed">
                    Cuando el escaneo automático de Wallapop se agota (créditos de Apify/ScraperAPI) o queda bloqueado
                    por el WAF de CloudFront desde el servidor. Dos opciones:
                </p>
                <ul className="text-slate-400 text-xs leading-relaxed list-disc list-inside space-y-1">
                    <li><strong className="text-white/80">Incursión Directa</strong>: intenta ya mismo la API firmada desde el servidor (funciona si hay <code className="text-cyan-400">WALLAPOP_RESIDENTIAL_PROXY</code> configurado).</li>
                    <li><strong className="text-white/80">Nexus Local Bridge</strong>: encola el trabajo para que lo resuelva un worker en tu PC (IP residencial, gratis). Ejecuta <code className="text-cyan-400">.\run_nexus_bridge.ps1</code> en tu máquina y déjalo corriendo.</li>
                </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 mb-4">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    aria-label="Consulta de búsqueda para Wallapop"
                    placeholder="auto (masters del universo origins, motu origins...)"
                    className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500"
                />
                <button
                    onClick={handleRunDirect}
                    disabled={isRunningDirect}
                    className="flex items-center justify-center gap-2 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 px-4 py-2.5 font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-50"
                >
                    {isRunningDirect ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                    Incursión Directa
                </button>
                <button
                    onClick={handleEnqueueJob}
                    disabled={isQueueing}
                    className="flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2.5 font-bold text-xs uppercase tracking-wider transition-all hover:from-amber-400 hover:to-orange-400 disabled:opacity-50"
                >
                    {isQueueing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    Encolar en Nexus Bridge
                </button>
            </div>

            <AnimatePresence>
                {directResult && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className={`mb-3 p-3 rounded-lg text-xs font-medium ${directResult.success ? 'bg-green-500/10 text-green-400 border border-green-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'}`}
                    >
                        {directResult.message}
                    </motion.div>
                )}
                {queueResult && (
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className={`mb-3 p-3 rounded-lg text-xs font-medium ${queueResult.success ? 'bg-green-500/10 text-green-400 border border-green-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'}`}
                    >
                        {queueResult.message}
                    </motion.div>
                )}
            </AnimatePresence>

            <div>
                <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-bold uppercase tracking-widest text-white/60">Cola del Nexus Bridge</p>
                    <button onClick={fetchJobs} aria-label="Actualizar cola de trabajos" className="text-white/40 hover:text-cyan-400 transition-colors">
                        <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                </div>
                <div className="max-h-56 overflow-y-auto space-y-1.5 rounded-lg border border-white/5 bg-black/20 p-2 custom-scrollbar">
                    {jobs.length === 0 ? (
                        <p className="text-white/30 text-xs text-center py-4">Sin trabajos recientes. Encola uno para verlo aquí.</p>
                    ) : (
                        jobs.map((job) => {
                            const meta = STATUS_META[job.status] || STATUS_META.pending;
                            return (
                                <div key={job.id} className="flex items-center justify-between gap-2 rounded-md bg-white/[0.03] px-3 py-2 text-xs">
                                    <div className="flex items-center gap-2 min-w-0">
                                        <span className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md font-bold uppercase tracking-tighter text-[9px] ${meta.className}`}>
                                            {meta.icon} {meta.label}
                                        </span>
                                        <span className="text-white/70 truncate">#{job.id} · {job.query}</span>
                                    </div>
                                    <span className="text-white/40 whitespace-nowrap">
                                        {job.status === 'done' || job.status === 'error' ? `${job.result_count} ofertas` : job.worker_id || '—'}
                                    </span>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>
        </div>
    );
};

export default WallapopNexusBridge;
