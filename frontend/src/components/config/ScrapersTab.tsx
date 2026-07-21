import React from 'react';
import { motion } from 'framer-motion';
import type { UseMutationResult } from '@tanstack/react-query';
import {
    ShieldAlert, Zap, Activity, Globe, Database, History, Terminal, CheckCircle2, Copy,
    RefreshCw, Play, Swords, Search, Compass, MousePointer, Sparkles, AlertCircle, Home,
    Shield, Settings, Download, Package, Wifi, CloudLightning, Cookie, Clock, Gift,
    Network, Trash2, XCircle, Keyboard, FileText, ChevronsDown, ArrowDown, BarChart2,
    CornerDownRight, Flag, Archive, Hexagon,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { parseUtcDate } from '../../utils/dateUtils';
import { getParsedMetrics, getStepperStatus } from './configHelpers';
import type { ScraperStatus } from '../../api/admin';
import type { ScraperExecutionLog } from '../../api/purgatory';

const EMOJI_MAP: { [key: string]: React.ReactNode } = {
    '🚀': <Play className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '⚔️': <Swords className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '🔎': <Search className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '🔍': <Search className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '🧭': <Compass className="inline h-3 w-3 mr-1 text-blue-400 align-middle" />,
    '🖱️': <MousePointer className="inline h-3 w-3 mr-1 text-slate-400 align-middle" />,
    '🕵️‍♂️': <Search className="inline h-3 w-3 mr-1 text-amber-400 align-middle" />,
    '🔮': <Sparkles className="inline h-3 w-3 mr-1 text-purple-400 align-middle" />,
    '⚡': <Zap className="inline h-3 w-3 mr-1 text-yellow-400 align-middle" />,
    '⚠️': <AlertCircle className="inline h-3 w-3 mr-1 text-yellow-500 align-middle" />,
    '🌐': <Globe className="inline h-3 w-3 mr-1 text-blue-400 align-middle" />,
    '🏠': <Home className="inline h-3 w-3 mr-1 text-green-400 align-middle" />,
    '🛡️': <Shield className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '⚙️': <Settings className="inline h-3 w-3 mr-1 text-slate-400 align-middle" />,
    '📥': <Download className="inline h-3 w-3 mr-1 text-green-400 align-middle" />,
    '📦': <Package className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '📡': <Wifi className="inline h-3 w-3 mr-1 text-blue-400 align-middle" />,
    '🌩️': <CloudLightning className="inline h-3 w-3 mr-1 text-purple-400 align-middle" />,
    '🕵️': <Search className="inline h-3 w-3 mr-1 text-amber-400 align-middle" />,
    '🍪': <Cookie className="inline h-3 w-3 mr-1 text-yellow-600 align-middle" />,
    '💾': <Database className="inline h-3 w-3 mr-1 text-indigo-400 align-middle" />,
    '✅': <CheckCircle2 className="inline h-3 w-3 mr-1 text-green-500 align-middle" />,
    '⌛': <Clock className="inline h-3 w-3 mr-1 text-cyan-400 align-middle" />,
    '🎉': <Sparkles className="inline h-3 w-3 mr-1 text-pink-400 align-middle" />,
    '🎁': <Gift className="inline h-3 w-3 mr-1 text-pink-400 align-middle" />,
    '🕸️': <Network className="inline h-3 w-3 mr-1 text-slate-500 align-middle" />,
    '🧹': <Trash2 className="inline h-3 w-3 mr-1 text-red-400 align-middle" />,
    '❌': <XCircle className="inline h-3 w-3 mr-1 text-red-500 align-middle" />,
    '🚫': <XCircle className="inline h-3 w-3 mr-1 text-red-500 align-middle" />,
    '⌨️': <Keyboard className="inline h-3 w-3 mr-1 text-slate-400 align-middle" />,
    '📄': <FileText className="inline h-3 w-3 mr-1 text-slate-300 align-middle" />,
    '⏬': <ChevronsDown className="inline h-3 w-3 mr-1 text-cyan-400 align-middle" />,
    '⬇️': <ArrowDown className="inline h-3 w-3 mr-1 text-cyan-400 align-middle" />,
    '📊': <BarChart2 className="inline h-3 w-3 mr-1 text-indigo-400 align-middle" />,
    '↪️': <CornerDownRight className="inline h-3 w-3 mr-1 text-cyan-500 align-middle" />,
    '🏁': <Flag className="inline h-3 w-3 mr-1 text-green-400 align-middle" />,
    '🔄': <RefreshCw className="inline h-3 w-3 mr-1 text-cyan-400 align-middle" />,
    '🟢': <CheckCircle2 className="inline h-3 w-3 mr-1 text-green-500 align-middle" />,
    '🗄️': <Archive className="inline h-3 w-3 mr-1 text-indigo-400 align-middle" />,
    '⎔': <Hexagon className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '⏣': <Hexagon className="inline h-3 w-3 mr-1 text-brand-primary align-middle" />,
    '⚡️': <Zap className="inline h-3 w-3 mr-1 text-yellow-400 align-middle" />,
};
const EMOJI_REGEX = /(🚀|⚔️|🔎|🔍|🔮|⚡|⚠️|🌐|🏠|🛡️|⚙️|📥|📦|📡|🌩️|🕵️‍♂️|🕵️|🧭|🖱️|🍪|💾|✅|⌛|🎉|🎁|🕸️|🧹|❌|🚫|⌨️|📄|⏬|⬇️|📊|↪️|🏁|🔄|🟢|🗄️|⎔|⏣|⚡️)/g;

interface ScrapersTabProps {
    statuses: ScraperStatus[];
    runScrapersMutation: UseMutationResult<any, any, string>;
    stopScrapersMutation: UseMutationResult<any, any, void>;
    runWallaManualHtmlMutation: UseMutationResult<any, any, File | undefined, void>;
    syncingNexus: boolean;
    handleSyncNexus: () => void;
    handleOpenIpLogs: () => void;
    wallaManualLoading: boolean;
    logFilter: 'all' | 'error';
    setLogFilter: (f: 'all' | 'error') => void;
    advancedLogs: ScraperExecutionLog[];
    selectedLog: ScraperExecutionLog | null;
    setSelectedLog: (log: ScraperExecutionLog) => void;
    setTargetLogId: (id: number | null) => void;
    handleCopyLogs: () => void;
    copied: boolean;
    consoleRef: React.RefObject<HTMLDivElement | null>;
    syncingSensores: boolean;
    setSyncingSensores: (v: boolean) => void;
    fetchData: () => Promise<void> | void;
}

/** Fase AAA-4a: extraido de Config.tsx (pestaña "scrapers" / "Centro de Mando"). */
export default function ScrapersTab({
    statuses,
    runScrapersMutation,
    stopScrapersMutation,
    runWallaManualHtmlMutation,
    syncingNexus,
    handleSyncNexus,
    handleOpenIpLogs,
    wallaManualLoading,
    logFilter,
    setLogFilter,
    advancedLogs,
    selectedLog,
    setSelectedLog,
    setTargetLogId,
    handleCopyLogs,
    copied,
    consoleRef,
    syncingSensores,
    setSyncingSensores,
    fetchData,
}: ScrapersTabProps) {
    return (
        <motion.div
            key="scrapers"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-8"
        >
            {/* CENTRO DE MANDO OPERATIVO */}
            <div className="space-y-2 md:space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-700">

                {/* Banner de Control Global */}
                <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                    <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px] pointer-events-none"></div>

                    <div className="relative flex flex-col items-start justify-between gap-4 md:flex-row md:items-center mb-0 md:mb-0 pb-4 md:pb-0">
                        <div className="relative z-10 flex flex-col gap-1">
                            <div className="flex items-center gap-2 text-brand-primary">
                                <div className="h-2 w-2 rounded-full bg-brand-primary animate-pulse" />
                                <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                    Centro de <span className="text-brand-primary">Mando</span>
                                </h2>
                            </div>
                            <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium uppercase tracking-[0.1em]">
                                Orquestador de Incursiones
                            </p>
                        </div>

                        <div className="flex flex-col sm:flex-row items-center gap-2 w-full sm:w-auto">
                            <button
                                onClick={() => {
                                    if (confirm('¿DETENER TODAS LAS INCURSIONES?')) {
                                        stopScrapersMutation.mutate();
                                    }
                                }}
                                className={`group flex items-center justify-center gap-2 rounded-xl border px-4 py-2 font-bold transition-all shadow-lg hover:scale-105 active:scale-95 w-full sm:w-auto ${statuses.some(s => s.status === 'running')
                                    ? 'bg-red-500 text-white border-red-400 shadow-red-500/20 animate-pulse'
                                    : 'bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20 shadow-red-500/5'
                                    }`}
                            >
                                <ShieldAlert className="h-4 w-4" />
                                <span className="text-[11px] uppercase tracking-wider">Detener</span>
                            </button>

                            <button
                                onClick={() => runScrapersMutation.mutate('all')}
                                disabled={statuses.some(s => s.status === 'running')}
                                className="group relative flex items-center justify-center gap-2 overflow-hidden rounded-xl bg-brand-primary px-4 py-2 font-bold text-white transition-all hover:scale-105 hover:bg-brand-primary/80 active:scale-95 shadow-lg shadow-brand-primary/20 disabled:opacity-50 w-full sm:w-auto"
                            >
                                <Zap className="h-4 w-4 fill-current" />
                                <span className="text-[11px] uppercase tracking-wider">Incursión Total</span>
                            </button>

                            <button
                                onClick={handleSyncNexus}
                                disabled={syncingNexus || statuses.some(s => s.status === 'running')}
                                className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 py-2 rounded-xl font-bold text-[11px] transition-all flex items-center justify-center gap-2 disabled:opacity-30 hover:scale-105 active:scale-95 w-full sm:w-auto"
                            >
                                <Activity className="h-4 w-4 text-brand-primary" />
                                <span className="uppercase tracking-wider">Nexus</span>
                            </button>

                            <button
                                onClick={handleOpenIpLogs}
                                className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 py-2 rounded-xl font-bold text-[11px] transition-all flex items-center justify-center gap-2 hover:scale-105 active:scale-95 w-full sm:w-auto"
                            >
                                <Globe className="h-4 w-4 text-brand-primary" />
                                <span className="uppercase tracking-wider">Auditoría IP</span>
                            </button>

                            <button
                                onClick={() => {
                                    if (statuses.some(s => s.status === 'running')) return;
                                    const fileInput = document.createElement('input');
                                    fileInput.type = 'file';
                                    fileInput.accept = '.html';
                                    fileInput.onchange = (e: any) => {
                                        const file = e.target.files?.[0];
                                        if (file) {
                                            runWallaManualHtmlMutation.mutate(file);
                                        }
                                    };
                                    fileInput.click();
                                }}
                                disabled={wallaManualLoading || statuses.some(s => s.status === 'running')}
                                className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 py-2 rounded-xl font-bold text-[11px] transition-all flex items-center justify-center gap-2 hover:scale-105 active:scale-95 w-full sm:w-auto disabled:opacity-50"
                                title="Procesar archivo HTML guardado de Wallapop"
                            >
                                {wallaManualLoading ? (
                                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
                                        <Activity className="h-4 w-4 text-cyan-400" />
                                    </motion.div>
                                ) : (
                                    <Database className="h-4 w-4 text-cyan-400" />
                                )}
                                <span className="uppercase tracking-wider">WallaManual</span>
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                        {statuses.filter(s => !['all', 'nexus', 'harvester'].includes(s.spider_name.toLowerCase())).map((s) => (
                            <div
                                key={s.spider_name}
                                className={`group relative flex items-center justify-between rounded-xl border px-3 py-2 transition-all ${s.status === 'running'
                                    ? 'bg-brand-primary/50 border-brand-primary shadow-[0_0_15px_rgba(14,165,233,0.3)]'
                                    : 'bg-white/[0.03] border-white/5 hover:bg-white/10'
                                    }`}
                            >
                                <span className={`text-[10px] font-black uppercase tracking-tight truncate ${s.status === 'running' ? 'text-white' : 'text-white/65'}`}>
                                    {s.spider_name}
                                </span>

                                <div className="flex items-center">
                                    {s.status === 'running' ? (
                                        <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
                                            <Activity className="h-3 w-3 text-white" />
                                        </motion.div>
                                    ) : (
                                        <button
                                            onClick={() => runScrapersMutation.mutate(s.spider_name)}
                                            disabled={statuses.some(stat => stat.status === 'running')}
                                            className="h-6 w-6 rounded-lg flex items-center justify-center hover:bg-brand-primary/20 text-white/20 hover:text-brand-primary transition-all disabled:opacity-0"
                                        >
                                            <Play className="h-2.5 w-2.5 fill-current" />
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Consola Táctica y Bitácora */}
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                    {/* Lista de Incursiones Previas */}
                    <div className="lg:col-span-1 space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <History className="h-5 w-5 text-brand-primary" />
                            <h3 className="text-sm font-black uppercase tracking-widest text-white">Historial Operativo</h3>
                        </div>
                        <div className="flex gap-2 px-2 text-[9px] font-black uppercase tracking-widest">
                            <button
                                onClick={() => setLogFilter('all')}
                                className={`px-3 py-1 rounded-full border transition-all ${logFilter === 'all' ? 'bg-brand-primary/10 border-brand-primary/30 text-white' : 'border-white/5 text-white/40 hover:text-white/80'}`}
                            >
                                Todos
                            </button>
                            <button
                                onClick={() => setLogFilter('error')}
                                className={`px-3 py-1 rounded-full border transition-all ${logFilter === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'border-white/5 text-white/40 hover:text-white/80'}`}
                            >
                                Fallidos
                            </button>
                        </div>
                        <div className="max-h-[460px] overflow-y-auto space-y-2 rounded-[2.5rem] border border-white/5 bg-black/40 p-3 scrollbar-none custom-scrollbar shadow-inner">
                            {advancedLogs.filter(log => logFilter === 'all' || log.status === 'error').map((log) => (
                                <button
                                    key={log.id}
                                    onClick={() => { setSelectedLog(log); setTargetLogId(null); }}
                                    className={`group w-full flex flex-col gap-2 rounded-2xl border p-4 text-left transition-all relative overflow-hidden ${selectedLog?.id === log.id
                                        ? 'bg-brand-primary/10 border-brand-primary/30 shadow-lg'
                                        : 'bg-white/[0.03] border-white/5 hover:bg-white/5'
                                        }`}
                                >
                                    {selectedLog?.id === log.id && (
                                        <motion.div layoutId="log-active" className="absolute left-0 top-0 bottom-0 w-1 bg-brand-primary" />
                                    )}
                                    <div className="flex items-center justify-between">
                                        <span className="text-[10px] font-black uppercase tracking-widest text-white group-hover:text-brand-primary transition-colors">{log.spider_name}</span>
                                        <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded-md uppercase tracking-tighter ${log.status === 'success' ? 'bg-green-500/20 text-green-400' : log.status === 'running' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                                            {log.status === 'success' ? 'Éxito' : log.status === 'running' ? 'En Ejecución' : 'Fallo'}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between text-[10px] text-white/60 font-bold">
                                        <div className="flex items-center gap-3">
                                            <span className="flex items-center gap-1.5"><Database className="h-3 w-3" /> {log.items_found} items</span>
                                            <span className="flex items-center gap-1 text-brand-primary/60"><Zap className="h-3 w-3" /> {log.new_items || 0} nuevos</span>
                                        </div>
                                        <span>{formatDistanceToNow(parseUtcDate(log.start_time), { addSuffix: true, locale: es })}</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Consola de Salida Real-Time */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="flex items-center justify-between px-2">
                            <div className="flex items-center gap-3">
                                <Terminal className="h-5 w-5 text-brand-primary" />
                                <h3 className="text-sm font-black uppercase tracking-widest text-white">Telemetría de Datos</h3>
                            </div>
                            {selectedLog && (
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={handleCopyLogs}
                                        className="flex items-center gap-1.5 px-3 py-1 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-brand-primary/10 hover:border-brand-primary/20 text-white/60 hover:text-white transition-all text-[9px] font-black uppercase tracking-wider"
                                    >
                                        {copied ? (
                                            <>
                                                <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
                                                ¡Copiado!
                                            </>
                                        ) : (
                                            <>
                                                <Copy className="h-3.5 w-3.5" />
                                                Copiar Logs
                                            </>
                                        )}
                                    </button>
                                    <span className="text-[10px] font-bold text-white/60 uppercase tracking-[0.2em] font-mono">
                                        {selectedLog.spider_name} #0x{selectedLog.id.toString(16)}
                                    </span>
                                    {selectedLog.status === 'running' && (
                                        <RefreshCw className="h-4 w-4 text-brand-primary animate-spin" />
                                    )}
                                </div>
                            )}
                        </div>

                        {selectedLog && (
                            <div className="mb-6 border border-white/10 bg-black/40 p-5 rounded-[2rem] backdrop-blur-3xl shadow-xl relative overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-r from-brand-primary/5 via-brand-secondary/5 to-transparent pointer-events-none"></div>
                                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 relative z-10">
                                    {getStepperStatus(selectedLog.logs, selectedLog.status).map((s) => {
                                        const isCompleted = s.status === 'completed';
                                        const isRunning = s.status === 'running';
                                        const isError = s.status === 'error';

                                        let circleColor = 'border-white/10 text-white/40 bg-white/[0.02]';
                                        let textColor = 'text-white/45';
                                        if (isCompleted) {
                                            circleColor = 'border-green-500/30 bg-green-500/10 text-green-400';
                                            textColor = 'text-green-400';
                                        } else if (isRunning) {
                                            circleColor = 'border-brand-primary bg-brand-primary/10 text-brand-primary animate-pulse';
                                            textColor = 'text-brand-primary font-bold';
                                        } else if (isError) {
                                            circleColor = 'border-red-500/30 bg-red-500/10 text-red-400';
                                            textColor = 'text-red-400 font-bold';
                                        }

                                        return (
                                            <div key={s.step} className="flex items-center sm:items-start gap-3 p-3 rounded-2xl bg-white/[0.01] border border-white/[0.03] hover:border-white/5 transition-all">
                                                <div className={`h-8 w-8 rounded-full border flex items-center justify-center font-bold text-xs shrink-0 ${circleColor}`}>
                                                    {isCompleted ? '✓' : isError ? '✗' : s.step}
                                                </div>
                                                <div className="flex flex-col min-w-0">
                                                    <span className={`text-[10px] font-black uppercase tracking-wider truncate ${textColor}`}>{s.title}</span>
                                                    <span className="text-[9px] text-white/40 truncate">{s.description}</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        <div className="relative group">
                            <div className="absolute inset-0 bg-brand-primary/5 blur-3xl rounded-[2.5rem] -z-10 group-hover:bg-brand-primary/10 transition-all"></div>
                            <div className="overflow-hidden rounded-[2.5rem] border border-white/10 bg-black/90 p-1 shadow-2xl backdrop-blur-3xl ring-1 ring-white/5">
                                <div
                                    ref={consoleRef}
                                    className="h-[440px] overflow-y-auto p-8 font-mono text-[11px] leading-relaxed space-y-1.5 scrollbar-thin scrollbar-thumb-brand-primary/20 custom-scrollbar"
                                >
                                    {selectedLog?.error_message && (
                                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 font-bold">
                                            <div className="flex items-center gap-2 mb-1">
                                                <ShieldAlert className="h-4 w-4" />
                                                CRITICAL ERROR DETECTED
                                            </div>
                                            <p className="text-[10px] opacity-80 uppercase tracking-wider">{selectedLog.error_message}</p>
                                        </div>
                                    )}

                                    {(() => {
                                        const metrics = getParsedMetrics(selectedLog?.logs);
                                        if (!metrics) return null;
                                        return (
                                            <div className="mb-6 grid grid-cols-2 sm:grid-cols-4 gap-3 border border-white/5 bg-white/[0.02] p-4 rounded-3xl backdrop-blur-xl">
                                                <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex flex-col gap-0.5">
                                                    <span className="text-[9px] font-black uppercase text-blue-400 tracking-wider">Nuevas (Purgatorio)</span>
                                                    <span className="text-base font-black text-white">{metrics.newItems}</span>
                                                </div>
                                                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex flex-col gap-0.5">
                                                    <span className="text-[9px] font-black uppercase text-amber-400 tracking-wider">Actualizadas</span>
                                                    <span className="text-base font-black text-white">{metrics.priceUpdates}</span>
                                                </div>
                                                <div className="p-3 bg-slate-500/10 border border-slate-500/20 rounded-2xl flex flex-col gap-0.5">
                                                    <span className="text-[9px] font-black uppercase text-slate-400 tracking-wider">Sin Cambios</span>
                                                    <span className="text-base font-black text-white">{metrics.unchanged}</span>
                                                </div>
                                                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-2xl flex flex-col gap-0.5">
                                                    <span className="text-[9px] font-black uppercase text-red-400 tracking-wider">Descartadas</span>
                                                    <span className="text-base font-black text-white">{metrics.discarded}</span>
                                                </div>
                                            </div>
                                        );
                                    })()}

                                    {selectedLog?.logs ? (
                                        selectedLog.logs.split(/\n|\\n/).map((line, i) => {
                                            const isError = line.toLowerCase().includes('error') || line.toLowerCase().includes('fail') || line.toLowerCase().includes('exception');
                                            const isSuccess = line.toLowerCase().includes('success') || line.toLowerCase().includes('found') || line.toLowerCase().includes('completed');
                                            const isWarning = line.toLowerCase().includes('warning') || line.toLowerCase().includes('alert');

                                            const parts = line.split(EMOJI_REGEX);

                                            return (
                                                <div key={i} className={`flex gap-4 group/line ${isError ? 'text-red-400' : isSuccess ? 'text-green-400' : isWarning ? 'text-yellow-400' : 'text-white/60'}`}>
                                                    <span className="text-white/10 select-none w-8 text-right group-hover/line:text-white/60 transition-colors">{String(i + 1).padStart(3, '0')}</span>
                                                    <p className="break-all whitespace-pre-wrap flex-1 align-middle">
                                                        {parts.map((part, idx) => EMOJI_MAP[part] ? <React.Fragment key={idx}>{EMOJI_MAP[part]}</React.Fragment> : part)}
                                                    </p>
                                                </div>
                                            );
                                        })
                                    ) : (
                                        <div className="flex h-full flex-col items-center justify-center text-white/5 gap-6">
                                            <div className="h-20 w-20 rounded-full border border-dashed border-white/5 flex items-center justify-center animate-spin-slow">
                                                <Terminal className="h-10 w-10" />
                                            </div>
                                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-white/20">A la espera de enlace táctico...</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Widget de Estado de Scrapers */}
            <div className="space-y-4 pt-6 border-t border-white/5">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <h4 className="text-xs font-black uppercase tracking-widest text-white/65">Sensores de Incursión (Scrapers)</h4>
                        {syncingSensores && (
                            <RefreshCw className="h-3 w-3 text-brand-primary animate-spin" />
                        )}
                    </div>
                    <button
                        onClick={async () => {
                            setSyncingSensores(true);
                            await fetchData();
                            setSyncingSensores(false);
                        }}
                        className="flex items-center gap-1 text-[9px] font-black text-brand-primary hover:text-white uppercase tracking-widest bg-brand-primary/10 border border-brand-primary/20 hover:bg-brand-primary/20 px-2.5 py-1 rounded-lg transition-all"
                    >
                        <RefreshCw className={`h-2.5 w-2.5 ${syncingSensores ? 'animate-spin' : ''}`} />
                        Sincronizar Sensores
                    </button>
                </div>
                <div className="rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-6">
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                        {(() => {
                            const filteredScrapers = statuses?.filter(s => s.status !== 'completed') || [];
                            if (filteredScrapers.length === 0) {
                                return (
                                    <div className="col-span-full py-10 flex flex-col items-center justify-center gap-2">
                                        <CheckCircle2 className="h-8 w-8 text-green-500 animate-pulse" />
                                        <div className="text-[10px] font-black uppercase tracking-widest text-green-400">Todos los sensores están listos (Listo)</div>
                                    </div>
                                );
                            }
                            return filteredScrapers.map((scraper) => {
                                const isRunning = scraper.status === 'running';
                                const isCompleted = scraper.status === 'completed';
                                const isError = scraper.status.startsWith('error') || scraper.status === 'stopped';

                                return (
                                    <div
                                        key={scraper.spider_name}
                                        className={`relative overflow-hidden flex flex-col gap-1.5 rounded-xl p-3 border transition-all duration-300 ${
                                            isRunning ? 'bg-yellow-500/5 border-yellow-500/20 shadow-[0_0_15px_-5px_rgba(234,179,8,0.15)]' :
                                            isCompleted ? 'bg-green-500/5 border-green-500/10' :
                                            'bg-white/[0.02] border-white/5'
                                        }`}
                                    >
                                        <div className="flex items-center justify-between gap-2">
                                            <span className="text-[9px] font-bold text-white/80 truncate max-w-[80%]">{scraper.spider_name}</span>
                                            <span className={`h-1.5 w-1.5 rounded-full ${
                                                isRunning ? 'bg-yellow-500 animate-pulse' :
                                                isCompleted ? 'bg-green-500' :
                                                isError ? 'bg-red-500' : 'bg-white/20'
                                            }`}></span>
                                        </div>

                                        <div className="flex items-center justify-between text-[7px] font-black uppercase tracking-wider text-white/60">
                                            <span>Estado</span>
                                            <span className={
                                                isRunning ? 'text-yellow-500' :
                                                isCompleted ? 'text-green-500' :
                                                isError ? 'text-red-500' : 'text-white/60'
                                            }>
                                                {isRunning ? 'Activo' : isCompleted ? 'Listo' : 'Pausado'}
                                            </span>
                                        </div>
                                    </div>
                                );
                            });
                        })()}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
