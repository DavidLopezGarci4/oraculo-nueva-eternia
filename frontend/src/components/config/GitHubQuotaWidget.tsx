import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Activity, Clock, Download, RefreshCw, AlertTriangle,
    CheckCircle2, Flame, Shield, Layers
} from 'lucide-react';
import { getGitHubQuotaStatus, downloadExecutionLogsCsv, type GitHubQuotaStatus } from '../../api/admin';

const GitHubQuotaWidget: React.FC = () => {
    const [quota, setQuota] = useState<GitHubQuotaStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchQuota = async (isManual = false) => {
        try {
            if (isManual) setRefreshing(true);
            else setLoading(true);
            setError(null);
            const data = await getGitHubQuotaStatus();
            setQuota(data);
        } catch (err: any) {
            console.error('Error fetching GitHub quota:', err);
            setError(err?.response?.data?.detail || 'No se pudo obtener el estado de la cuota');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchQuota();
    }, []);

    const handleDownload = async () => {
        try {
            setDownloading(true);
            await downloadExecutionLogsCsv();
        } catch (err) {
            console.error('Error downloading execution logs:', err);
            alert('Error al descargar el log de ejecuciones.');
        } finally {
            setDownloading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 mb-6 backdrop-blur-md animate-pulse">
                <div className="flex items-center justify-between mb-4">
                    <div className="h-5 bg-slate-800 rounded w-48"></div>
                    <div className="h-5 bg-slate-800 rounded w-24"></div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="h-20 bg-slate-800/60 rounded-lg"></div>
                    <div className="h-20 bg-slate-800/60 rounded-lg"></div>
                    <div className="h-20 bg-slate-800/60 rounded-lg"></div>
                    <div className="h-20 bg-slate-800/60 rounded-lg"></div>
                </div>
            </div>
        );
    }

    if (error || !quota) {
        return (
            <div className="bg-slate-900/60 border border-red-500/30 rounded-xl p-4 mb-6 flex items-center justify-between text-sm text-red-400">
                <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-400 shrink-0" />
                    <span>Telemetría FinOps no disponible: {error}</span>
                </div>
                <button
                    onClick={() => fetchQuota(true)}
                    className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded text-xs transition"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    // Determinar colores de la barra según porcentaje
    const pct = quota.percentage_used;
    const progressColor =
        pct > 85
            ? 'from-red-600 to-rose-500'
            : pct > 65
            ? 'from-amber-500 to-yellow-400'
            : 'from-cyan-500 to-emerald-400';

    const cadenceBadge = {
        optimal: { bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300', icon: CheckCircle2 },
        warning: { bg: 'bg-amber-500/15 border-amber-500/30 text-amber-300', icon: AlertTriangle },
        critical: { bg: 'bg-red-500/15 border-red-500/30 text-red-300', icon: Flame }
    }[quota.cadence_status] || { bg: 'bg-slate-800 border-slate-700 text-slate-300', icon: Activity };

    const CadenceIcon = cadenceBadge.icon;

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950 border border-slate-700/60 rounded-xl p-5 mb-6 shadow-xl backdrop-blur-md relative overflow-hidden"
        >
            {/* Header del Widget */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2.5">
                    <div className="p-2 bg-brand-primary/10 border border-brand-primary/30 rounded-lg text-brand-primary">
                        <Activity className="h-5 w-5" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-100 tracking-wide">
                                Cuota de Ejecución en la Nube (GitHub Actions)
                            </h3>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 font-mono">
                                2.000 min / mes
                            </span>
                            {quota.source === 'github_api_live' && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                    ● En Vivo
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-slate-400">
                            Telemetría de consumo de runners efímeros para Daily Scan, Centinelas y Cazas Vinted
                        </p>
                    </div>
                </div>

                {/* Acciones: Refrescar y Descargar CSV */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => fetchQuota(true)}
                        disabled={refreshing}
                        title="Sincronizar telemetría en vivo"
                        className="p-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-white rounded-lg transition disabled:opacity-50"
                    >
                        <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin text-cyan-400' : ''}`} />
                    </button>
                    <button
                        onClick={handleDownload}
                        disabled={downloading}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-primary/20 hover:bg-brand-primary/30 border border-brand-primary/40 text-brand-primary text-xs font-semibold rounded-lg transition disabled:opacity-50 shadow-sm"
                    >
                        <Download className="h-3.5 w-3.5" />
                        {downloading ? 'Descargando...' : 'Descargar Log (CSV)'}
                    </button>
                </div>
            </div>

            {/* Barra de Progreso de Cuota */}
            <div className="mb-4">
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                    <span className="text-slate-300">
                        Consumido este mes: <strong className="text-white">{quota.used_minutes} min</strong> ({quota.percentage_used}%)
                    </span>
                    <span className="text-slate-400">
                        Límite: <strong className="text-slate-200">{quota.total_quota_minutes} min</strong>
                    </span>
                </div>
                <div className="w-full h-3 bg-slate-950/80 rounded-full overflow-hidden border border-slate-800/80 p-0.5">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(100, Math.max(2, quota.percentage_used))}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className={`h-full rounded-full bg-gradient-to-r ${progressColor} shadow-lg`}
                    />
                </div>
            </div>

            {/* Tarjetas KPI de Estado */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                        <Activity className="h-3.5 w-3.5 text-cyan-400" />
                        <span>Minutos Usados</span>
                    </div>
                    <div className="text-lg font-bold text-white">
                        {quota.used_minutes}{' '}
                        <span className="text-xs font-normal text-slate-400">min</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                        ~{quota.daily_average_minutes} min/día de media
                    </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                        <Shield className="h-3.5 w-3.5 text-emerald-400" />
                        <span>Minutos Libres</span>
                    </div>
                    <div className="text-lg font-bold text-emerald-400">
                        {quota.remaining_minutes}{' '}
                        <span className="text-xs font-normal text-slate-400">min</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                        Saldo seguro en la nube
                    </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                        <Clock className="h-3.5 w-3.5 text-amber-400" />
                        <span>Reposición de Cuota</span>
                    </div>
                    <div className="text-sm font-bold text-white truncate">
                        En {quota.days_until_reset} días
                    </div>
                    <div className="text-[10px] text-amber-300/80 mt-0.5 truncate" title={quota.reset_date}>
                        {quota.reset_date}
                    </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                        <Layers className="h-3.5 w-3.5 text-purple-400" />
                        <span>Incursiones Mes</span>
                    </div>
                    <div className="text-lg font-bold text-white">
                        {quota.total_runs_this_month}{' '}
                        <span className="text-xs font-normal text-slate-400">ejecuciones</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                        Workflows completados
                    </div>
                </div>
            </div>

            {/* Desglose por Origen de Workflow */}
            <div className="bg-slate-950/40 border border-slate-800/60 rounded-lg p-3 mb-3">
                <div className="text-xs font-semibold text-slate-300 mb-2">Desglose de Consumo por Proceso:</div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800">
                        <span className="text-slate-400">🔄 Daily Scan:</span>
                        <span className="font-semibold text-cyan-300">
                            {quota.breakdown.daily_scan.minutes} min <span className="text-[10px] text-slate-400">({quota.breakdown.daily_scan.runs})</span>
                        </span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800">
                        <span className="text-slate-400">🏹 Centinela Vinted:</span>
                        <span className="font-semibold text-emerald-300">
                            {quota.breakdown.vinted_sentinel.minutes} min <span className="text-[10px] text-slate-400">({quota.breakdown.vinted_sentinel.runs})</span>
                        </span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800">
                        <span className="text-slate-400">🧪 CI / Tests:</span>
                        <span className="font-semibold text-indigo-300">
                            {quota.breakdown.ci_tests.minutes} min <span className="text-[10px] text-slate-400">({quota.breakdown.ci_tests.runs})</span>
                        </span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800">
                        <span className="text-slate-400">⚡ Otros:</span>
                        <span className="font-semibold text-purple-300">
                            {quota.breakdown.others.minutes} min <span className="text-[10px] text-slate-400">({quota.breakdown.others.runs})</span>
                        </span>
                    </div>
                </div>
            </div>

            {/* Banner de Diagnóstico y Recomendación de Cadencia */}
            <div className={`flex items-start gap-2.5 p-3 rounded-lg border text-xs ${cadenceBadge.bg}`}>
                <CadenceIcon className="h-4 w-4 shrink-0 mt-0.5" />
                <div>
                    <span className="font-semibold">Diagnóstico FinOps y Cadencia:</span> {quota.cadence_recommendation}
                </div>
            </div>
        </motion.div>
    );
};

export default GitHubQuotaWidget;
