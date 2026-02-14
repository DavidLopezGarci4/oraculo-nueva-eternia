import React, { useState, useEffect } from 'react';
import { Play, Activity, Clock, AlertCircle, CheckCircle2, RefreshCw, Terminal, GitMerge, Target, Settings, Users, ShieldAlert, Trash2, Zap, History, Database, Loader2, Download, Upload, FileSpreadsheet } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { resetSmartMatches, runScrapers, stopScrapers, getScraperLogs, type ScraperExecutionLog } from '../api/purgatory';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import WallapopImporter from '../components/admin/WallapopImporter';

import { getScrapersStatus, getDuplicates, mergeProducts, syncNexus, type ScraperStatus, type Hero } from '../api/admin';

interface ConfigProps {
    user?: Hero | null;
    onUserUpdate?: () => void;
}

const Config: React.FC<ConfigProps> = ({ user, onUserUpdate }) => {
    const consoleRef = React.useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'scrapers' | 'radar' | 'system' | 'users' | 'wallapop'>('scrapers');
    const [statuses, setStatuses] = useState<ScraperStatus[]>([]);
    const [heroes, setHeroes] = useState<any[]>([]);
    const [duplicates, setDuplicates] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [mergingId, setMergingId] = useState<number | null>(null);
    const [syncingNexus, setSyncingNexus] = useState(false);
    const [showAddUserModal, setShowAddUserModal] = useState(false);
    const [userSettings, setUserSettings] = useState<any>(null);
    const [savingSettings, setSavingSettings] = useState(false);
    const [resetStep, setResetStep] = useState(0); // 0: idle, 1: first confirm, 2: second confirm
    const [isResetting, setIsResetting] = useState(false);
    const [selectedLog, setSelectedLog] = useState<ScraperExecutionLog | null>(null);
    const [advancedLogs, setAdvancedLogs] = useState<ScraperExecutionLog[]>([]);

    const queryClient = useQueryClient();

    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');

    useEffect(() => {
        if (user && user.role !== 'admin' && (activeTab === 'scrapers' || activeTab === 'radar')) {
            setActiveTab('system');
        }
    }, [user, activeTab]);

    const fetchData = async () => {
        try {
            const [s, d, u, al, h] = await Promise.all([
                getScrapersStatus(),
                getDuplicates(),
                import('../api/admin').then(m => m.getUserSettings(activeUserId)),
                getScraperLogs(),
                import('../api/admin').then(m => m.getHeroes())
            ]);
            setStatuses(s);
            setDuplicates(d);
            setUserSettings(u);
            setAdvancedLogs(al);
            setHeroes(h);

            // Si hay un log seleccionado que está corriendo, actualizarlo
            if (selectedLog && al.find(log => log.id === selectedLog.id)) {
                setSelectedLog(al.find(log => log.id === selectedLog.id) || null);
            } else if (!selectedLog && al.length > 0) {
                // Auto-seleccionar el último por defecto
                setSelectedLog(al[0]);
            }
        } catch (error) {
            console.error('Error fetching admin data:', error);
        } finally {
            setLoading(false);
        }
    };

    const runScrapersMutation = useMutation({
        mutationFn: (scraperName: string) => runScrapers(scraperName, 'manual'),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
            fetchData();
        }
    });

    const stopScrapersMutation = useMutation({
        mutationFn: stopScrapers,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
            fetchData();
        }
    });

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Polling every 10s
        return () => clearInterval(interval);
    }, []);

    const handleUpdateLocation = async (loc: string) => {
        setSavingSettings(true);
        try {
            const { updateUserLocation } = await import('../api/admin');
            await updateUserLocation(activeUserId, loc);
            setUserSettings({ ...userSettings, location: loc });
        } catch (error) {
            console.error('Error updating location:', error);
        } finally {
            setSavingSettings(false);
        }
    };


    const handleMerge = async (sourceId: number, targetId: number) => {
        setMergingId(sourceId);
        try {
            await mergeProducts(sourceId, targetId);
            fetchData();
        } catch (error) {
            console.error('Error merging products:', error);
        } finally {
            setMergingId(null);
        }
    };

    const handleSyncNexus = async () => {
        setSyncingNexus(true);
        try {
            await syncNexus();
            alert("📡 Nexus: Sincronización maestro iniciada en segundo plano. Las nuevas imágenes y datos se verán reflejados en unos minutos.");
        } catch (error: any) {
            console.error('Error syncing Nexus:', error);
            const detail = error.response?.data?.detail || error.message || "Error de red o servidor";
            alert(`❌ Nexus: Error al iniciar la sincronización. Detalle: ${detail}`);
        } finally {
            setSyncingNexus(false);
        }
    };

    const handleResetSmartMatches = async () => {
        setIsResetting(true);
        try {
            await resetSmartMatches();
            alert("🧹 Purificación completada: El SmartMatch ha sido reiniciado.");
            setResetStep(0);
            fetchData();
        } catch (error) {
            console.error('Error resetting smart matches:', error);
            alert("❌ Error en la purificación.");
        } finally {
            setIsResetting(false);
        }
    };

    const handleUpdateRole = async (userId: number, newRole: string) => {
        try {
            const m = await import('../api/admin');
            await m.updateHeroRole(userId, newRole);
            const updatedHeroes = await m.getHeroes();
            setHeroes(updatedHeroes);

            // If we updated the current active user, refresh global state
            if (userId === activeUserId && onUserUpdate) {
                onUserUpdate();
            }
        } catch (error) {
            console.error('Error updating role:', error);
        }
    };

    const handlePasswordReset = async (userId: number) => {
        if (!confirm('¿Seguro que deseas iniciar el Protocolo de Reseteo para este héroe?')) return;
        try {
            const m = await import('../api/admin');
            await m.resetHeroPassword(userId);
            alert('🛡️ Protocolo de reseteo iniciado satisfactoriamente en los registros del Oráculo.');
        } catch (error) {
            console.error('Error resetting password:', error);
        }
    };

    const handleDownloadVault = async () => {
        try {
            const m = await import('../api/admin');
            await m.downloadVault(activeUserId);
            alert('📦 Bóveda Personal generada y descargada. Guárdala en un lugar seguro.');
        } catch (error) {
            console.error('Error downloading vault:', error);
            alert('❌ Error al generar la Bóveda.');
        }
    };

    const handleSyncExcel = async () => {
        try {
            const m = await import('../api/admin');
            const res = await m.syncExcel(activeUserId);
            alert(`📊 Excel Bridge: ${res.message}`);
        } catch (error: any) {
            console.error('Error syncing excel:', error);
            const detail = error.response?.data?.detail || "Fallo en la conexión local.";
            alert(`❌ Error en Excel Bridge: ${detail}`);
        }
    };

    const handleExportExcelAdmin = async (userId: number) => {
        try {
            const m = await import('../api/admin');
            await m.exportCollectionExcel(userId);
            alert('📦 Bóveda Digital: Excel generado y descargado con éxito.');
        } catch (error) {
            console.error('Error exporting excel:', error);
            alert('❌ Error al exportar Excel.');
        }
    };

    const handleExportExcel = async () => {
        let userId: number = activeUserId;
        if (user?.role === 'admin') {
            const input = prompt('🕵️ ACCESO AL ARCHIVO MAESTRO\nIngrese el ID del Héroe para exportar su Colección Excel:', activeUserId.toString());
            if (input === null) return;
            const parsed = parseInt(input);
            if (!isNaN(parsed)) userId = parsed;
        }
        await handleExportExcelAdmin(userId);
    };

    const handleExportSqliteAdmin = async (userId: number) => {
        try {
            const m = await import('../api/admin');
            await m.exportCollectionSqlite(userId);
            alert('🗄️ Bóveda Digital: SQLite generado y descargado con éxito.');
        } catch (error) {
            console.error('Error exporting sqlite:', error);
            alert('❌ Error al exportar SQLite.');
        }
    };

    const handleExportSqlite = async () => {
        let userId: number = activeUserId;
        if (user?.role === 'admin') {
            const input = prompt('🗄️ ACCESO AL BÚNKER DE DATOS\nIngrese el ID del Héroe para extraer su Bóveda SQLite:', activeUserId.toString());
            if (input === null) return;
            const parsed = parseInt(input);
            if (!isNaN(parsed)) userId = parsed;
        }
        await handleExportSqliteAdmin(userId);
    };


    if (loading && statuses.length === 0) {
        return (
            <div className="flex h-[60vh] items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <RefreshCw className="h-8 w-8 animate-spin text-brand-primary" />
                    <p className="text-white/50 text-sm">Cargando Mando de Scrapers...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
            {/* Header & Tabs */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="flex flex-col gap-2">
                    <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                        <Terminal className="h-8 w-8 text-brand-primary" />
                        Poderes del <span className="text-brand-primary">{user?.role === 'admin' ? 'Arquitecto' : 'Guardián'} de Nueva Eternia</span>
                    </h2>
                    <p className="text-white/50">{user?.role === 'admin' ? 'Control absoluto sobre las reliquias y sus fuentes.' : 'Gestiona tu legado personal y sincroniza tu bóveda sagrada.'}</p>
                </div>

                <div className="flex bg-white/5 p-1 rounded-2xl border border-white/10 backdrop-blur-xl">
                    {user?.role === 'admin' && (
                        <>
                            <button
                                onClick={() => setActiveTab('scrapers')}
                                className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'scrapers' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                            >
                                <Activity className="h-4 w-4" />
                                Scrapers
                            </button>
                            <button
                                onClick={() => setActiveTab('radar')}
                                className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'radar' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                            >
                                <Target className="h-4 w-4" />
                                Radar Duplicados
                                {duplicates.length > 0 && (
                                    <span className="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full ml-1 animate-pulse">
                                        {duplicates.length}
                                    </span>
                                )}
                            </button>
                        </>
                    )}
                    <button
                        onClick={() => setActiveTab('system')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'system' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                    >
                        <Settings className="h-4 w-4" />
                        {user?.role === 'admin' ? 'Ajustes de Sistema' : 'Mi Bóveda Personal'}
                    </button>
                    {user?.role === 'admin' && (
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'users' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                        >
                            <Users className="h-4 w-4" />
                            Gestión de Héroes
                        </button>
                    )}
                    {/* Wallapop tab disabled */}
                </div>
            </div>

            <AnimatePresence mode="wait">
                {activeTab === 'scrapers' ? (
                    <motion.div
                        key="scrapers"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-8"
                    >
                        {/* CENTRO DE MANDO OPERATIVO */}
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

                            {/* Banner de Control Global */}
                            <div className="relative overflow-hidden rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-white/[0.05] to-black p-6 md:p-8 backdrop-blur-xl">
                                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px]"></div>

                                <div className="relative mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <div className="h-2 w-2 rounded-full bg-brand-primary animate-pulse" />
                                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-brand-primary/70">Orquestador de Incursiones</span>
                                        </div>
                                        <h2 className="text-3xl font-black tracking-tighter text-white md:text-4xl"> CENTRO DE <span className="text-brand-primary">MANDO</span></h2>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <button
                                            onClick={() => {
                                                if (confirm('¿DETENER TODAS LAS INCURSIONES? Esta acción forzará el cierre de todos los procesos de extracción.')) {
                                                    stopScrapersMutation.mutate();
                                                }
                                            }}
                                            disabled={!statuses.some(s => s.status === 'running')}
                                            className={`group flex items-center gap-3 rounded-2xl border px-6 py-4 font-black transition-all shadow-xl ${statuses.some(s => s.status === 'running')
                                                ? 'bg-red-500 text-white border-red-400 hover:scale-105 active:scale-95 shadow-red-500/20'
                                                : 'bg-white/5 border-white/10 text-white/20 opacity-30 cursor-not-allowed'}`}
                                        >
                                            <ShieldAlert className={`h-5 w-5 ${statuses.some(s => s.status === 'running') ? 'animate-pulse' : ''}`} />
                                            <span className="text-sm uppercase tracking-widest">Protocolo Emergency</span>
                                        </button>

                                        <button
                                            onClick={() => runScrapersMutation.mutate('all')}
                                            disabled={statuses.some(s => s.status === 'running')}
                                            className="group relative flex items-center gap-3 overflow-hidden rounded-2xl bg-brand-primary px-8 py-4 font-black text-white transition-all hover:scale-105 hover:bg-brand-primary/80 active:scale-95 shadow-xl shadow-brand-primary/20 disabled:opacity-50 disabled:hover:scale-100"
                                        >
                                            <Zap className="h-5 w-5 fill-current" />
                                            <span className="text-sm uppercase tracking-widest">Incursión Total</span>
                                            <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000 group-hover:translate-x-full"></div>
                                        </button>

                                        <button
                                            onClick={handleSyncNexus}
                                            disabled={syncingNexus || statuses.some(s => s.status === 'running')}
                                            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-4 rounded-2xl font-black text-sm transition-all flex items-center gap-3 disabled:opacity-30 disabled:scale-100 hover:scale-105 active:scale-95"
                                        >
                                            {syncingNexus ? <Loader2 className="h-5 w-5 animate-spin" /> : <Activity className="h-5 w-5 text-brand-primary" />}
                                            <span className="uppercase tracking-widest">Sincro Nexus</span>
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
                                    {statuses.filter(s => !['all', 'nexus', 'harvester'].includes(s.spider_name.toLowerCase())).map((s) => (
                                        <div
                                            key={s.spider_name}
                                            className={`group relative flex flex-col gap-3 rounded-2xl border p-4 transition-all hover:bg-white/5 ${s.status === 'running' ? 'bg-brand-primary/10 border-brand-primary/40 shadow-[0_0_20px_rgba(14,165,233,0.1)]' : 'bg-white/[0.02] border-white/5'}`}
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="text-[10px] font-black uppercase tracking-widest text-white/40">{s.spider_name}</span>
                                                <div className={`h-2 w-2 rounded-full ${s.status === 'running' ? 'bg-brand-primary animate-pulse shadow-[0_0_8px_rgba(14,165,233,0.8)]' : 'bg-white/10'}`}></div>
                                            </div>
                                            <div className="flex items-center justify-between mt-1">
                                                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase ${s.status === 'running' ? 'bg-blue-500/20 text-blue-400' : 'bg-white/5 text-white/30'}`}>
                                                    {s.status === 'running' ? 'En Ejecución' : 'Standby'}
                                                </span>
                                                <button
                                                    onClick={() => runScrapersMutation.mutate(s.spider_name)}
                                                    disabled={statuses.some(stat => stat.status === 'running')}
                                                    className={`h-8 w-8 rounded-xl flex items-center justify-center border transition-all ${statuses.some(stat => stat.status === 'running')
                                                        ? 'bg-transparent border-transparent opacity-0 cursor-default'
                                                        : 'bg-white/5 border-white/10 hover:bg-brand-primary/20 hover:border-brand-primary/40 text-white/40 hover:text-brand-primary active:scale-90 hover:scale-110'}`}
                                                >
                                                    <Play className="h-3 w-3 fill-current" />
                                                </button>
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
                                    <div className="max-h-[500px] overflow-y-auto space-y-2 rounded-[2.5rem] border border-white/5 bg-black/40 p-3 scrollbar-none custom-scrollbar shadow-inner">
                                        {advancedLogs.map((log) => (
                                            <button
                                                key={log.id}
                                                onClick={() => setSelectedLog(log)}
                                                className={`group w-full flex flex-col gap-2 rounded-2xl border p-4 text-left transition-all relative overflow-hidden ${selectedLog?.id === log.id
                                                    ? 'bg-brand-primary/10 border-brand-primary/30 shadow-lg'
                                                    : 'bg-white/[0.03] border-white/5 hover:bg-white/5'}`}
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
                                                <div className="flex items-center justify-between text-[10px] text-white/30 font-bold">
                                                    <div className="flex items-center gap-3">
                                                        <span className="flex items-center gap-1.5"><Database className="h-3 w-3" /> {log.items_found} items</span>
                                                        <span className="flex items-center gap-1 text-brand-primary/60"><Zap className="h-3 w-3" /> {log.new_items || 0} nuevos</span>
                                                    </div>
                                                    <span>{formatDistanceToNow(new Date(log.start_time), { addSuffix: true, locale: es })}</span>
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
                                                <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] font-mono">
                                                    {selectedLog.spider_name} #0x{selectedLog.id.toString(16)}
                                                </span>
                                                {selectedLog.status === 'running' && (
                                                    <Loader2 className="h-3 w-3 text-brand-primary animate-spin" />
                                                )}
                                            </div>
                                        )}
                                    </div>

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

                                                {selectedLog?.logs ? (
                                                    selectedLog.logs.split(/\n|\\n/).map((line, i) => {
                                                        const isError = line.toLowerCase().includes('error') || line.toLowerCase().includes('fail') || line.toLowerCase().includes('exception');
                                                        const isSuccess = line.toLowerCase().includes('success') || line.toLowerCase().includes('found') || line.toLowerCase().includes('completed');
                                                        const isWarning = line.toLowerCase().includes('warning') || line.toLowerCase().includes('alert');

                                                        return (
                                                            <div key={i} className={`flex gap-4 group/line ${isError ? 'text-red-400' : isSuccess ? 'text-green-400' : isWarning ? 'text-yellow-400' : 'text-white/60'}`}>
                                                                <span className="text-white/10 select-none w-8 text-right group-hover/line:text-white/30 transition-colors">{String(i + 1).padStart(3, '0')}</span>
                                                                <p className="break-all whitespace-pre-wrap flex-1">{line}</p>
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
                    </motion.div>
                ) : activeTab === 'radar' ? (
                    <motion.div
                        key="radar"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        <div className="flex flex-col gap-2 mb-4">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Target className="h-6 w-6 text-brand-primary" />
                                Radar de Similitud por EAN
                            </h3>
                            <p className="text-white/40 text-sm">Detección de reliquias duplicadas que deben ser fusionadas para preservar la coherencia del Oráculo.</p>
                        </div>

                        {duplicates.length === 0 ? (
                            <div className="flex flex-col items-center justify-center p-20 glass border border-dashed border-white/10 rounded-[3rem]">
                                <CheckCircle2 className="h-16 w-16 text-green-500/20 mb-4" />
                                <p className="text-white/30 font-bold uppercase tracking-[0.2em]">No hay anomalías detectadas en el catálogo</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {duplicates.map((dup, idx) => (
                                    <div key={idx} className="glass border border-brand-primary/20 rounded-3xl p-6 space-y-4 bg-gradient-to-r from-brand-primary/5 to-transparent">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2 text-brand-primary font-bold uppercase tracking-widest text-xs">
                                                <AlertCircle className="h-4 w-4" />
                                                {dup.reason}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {dup.products.map((p: any) => (
                                                <div key={p.id} className="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/5 relative group">
                                                    <div className="h-16 w-16 rounded-xl overflow-hidden border border-white/10">
                                                        <img src={p.image_url} className="h-full w-full object-cover" />
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <h4 className="text-white font-bold truncate">{p.name}</h4>
                                                        <p className="text-[10px] text-white/30 uppercase font-black">ID: #{p.id} • {p.sub_category}</p>
                                                    </div>
                                                    <div className="flex flex-col gap-2">
                                                        <button
                                                            onClick={() => {
                                                                const target = dup.products.find((prod: any) => prod.id !== p.id);
                                                                if (target) handleMerge(p.id, target.id);
                                                            }}
                                                            disabled={mergingId === p.id}
                                                            className="bg-brand-primary/20 text-brand-primary hover:bg-brand-primary hover:text-white px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2"
                                                        >
                                                            {mergingId === p.id ? <RefreshCw className="h-3 w-3 animate-spin" /> : <GitMerge className="h-3 w-3" />}
                                                            Absorber
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                ) : activeTab === 'system' ? (
                    <motion.div
                        key="system"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <h2 className="text-2xl font-bold flex items-center gap-2">
                                    <Database className="w-6 h-6 text-blue-400" />
                                    {user?.role === 'admin' ? 'Cámara de Reliquias de Eternia' : 'Mi Bóveda Digital'}
                                </h2>
                                <p className="text-gray-400 text-sm">Resguardo y sincronización de tu legado físico.</p>
                            </div>
                            <div className="px-3 py-1 rounded-full bg-blue-900/30 text-blue-400 text-xs font-mono border border-blue-800/50">
                                SHIELD LAYER 2
                            </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Sentinel Settings */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60">
                                <div className="flex items-center gap-3 text-orange-400 font-bold uppercase tracking-widest text-xs mb-2">
                                    <AlertCircle className="h-4 w-4" />
                                    Vigilancia (Sentinel)
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Umbral de Alerta de Precio (%)</label>
                                        <input type="range" disabled className="w-full accent-brand-primary" value="15" />
                                        <div className="flex justify-between text-[10px] text-white/30 font-bold">
                                            <span>5%</span>
                                            <span className="text-brand-primary">15%</span>
                                            <span>50%</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl">
                                        <span className="text-xs text-white/70">Notificaciones Push</span>
                                        <div className="h-4 w-8 bg-white/10 rounded-full relative">
                                            <div className="absolute left-1 top-1 h-2 w-2 bg-white/30 rounded-full"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Financial Engine Settings */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60">
                                <div className="flex items-center gap-3 text-yellow-500 font-bold uppercase tracking-widest text-xs mb-2">
                                    <Target className="h-4 w-4" />
                                    Motor Financiero (Griales)
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">ROI Mínimo para Grial (%)</label>
                                        <div className="flex items-center gap-3">
                                            <input type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="50" />
                                            <span className="text-white/30 text-xs">%</span>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Valor Umbral Grial (€)</label>
                                        <div className="flex items-center gap-3">
                                            <input type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="150" />
                                            <span className="text-white/30 text-xs">€</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Scraper Global Timing */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60">
                                <div className="flex items-center gap-3 text-blue-400 font-bold uppercase tracking-widest text-xs mb-2">
                                    <Clock className="h-4 w-4" />
                                    Tiempos de Incursión
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Delay entre Páginas (seg)</label>
                                        <input type="range" disabled className="w-full accent-blue-400" value="10" />
                                        <div className="flex justify-between text-[10px] text-white/30 font-bold">
                                            <span>1s</span>
                                            <span className="text-blue-400">10s (Auto)</span>
                                            <span>30s</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl">
                                        <span className="text-xs text-white/70">Stealth Mode (Playwright)</span>
                                        <div className="h-4 w-8 bg-green-500/30 rounded-full relative">
                                            <div className="absolute right-1 top-1 h-2 w-2 bg-green-400 rounded-full"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Geographical Location (Oráculo Logístico) */}
                            <div className="glass border border-brand-primary/30 p-6 rounded-3xl space-y-4 bg-brand-primary/5">
                                <div className="flex items-center gap-3 text-brand-primary font-bold uppercase tracking-widest text-xs mb-2">
                                    <Target className="h-4 w-4" />
                                    Ubicación Geográfica (Oráculo)
                                </div>
                                <div className="space-y-4">
                                    <p className="text-[10px] text-white/40 font-bold uppercase leading-tight">
                                        Define tu contexto territorial para que el Oráculo calcule envíos, aduanas e IVA de importación automáticamente.
                                    </p>

                                    <div className="grid grid-cols-2 gap-2">
                                        {[
                                            { code: 'ES', label: 'España 🇪🇸' },
                                            { code: 'DE', label: 'Alemania 🇩🇪' },
                                            { code: 'IT', label: 'Italia 🇮🇹' },
                                            { code: 'FR', label: 'Francia 🇫🇷' },
                                            { code: 'US', label: 'USA 🇺🇸' }
                                        ].map((country) => (
                                            <button
                                                key={country.code}
                                                onClick={() => handleUpdateLocation(country.code)}
                                                disabled={savingSettings}
                                                className={`flex items-center justify-between px-4 py-3 rounded-2xl border transition-all ${userSettings?.location === country.code
                                                    ? 'bg-brand-primary border-brand-primary text-white shadow-lg shadow-brand-primary/20'
                                                    : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10 hover:text-white'
                                                    }`}
                                            >
                                                <span className="text-xs font-bold">{country.label}</span>
                                                {userSettings?.location === country.code && (
                                                    <CheckCircle2 className="h-4 w-4" />
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                {savingSettings && (
                                    <div className="flex items-center gap-2 text-[8px] font-black text-brand-primary uppercase animate-pulse justify-center">
                                        <RefreshCw className="h-3 w-3 animate-spin" />
                                        Sincronizando con el Núcleo...
                                    </div>
                                )}
                            </div>

                            {/* --- SHIELD ARCHITECTURE: VAULT & EXCEL BRIDGE --- */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="glass border border-white/10 p-6 rounded-3xl group hover:bg-white/5 transition-all">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-4">
                                            <div className="bg-brand-primary/10 p-3 rounded-lg group-hover:bg-brand-primary/20 transition-all">
                                                <Database className="h-5 w-5 text-brand-primary" />
                                            </div>
                                            <div>
                                                <h4 className="text-white font-bold text-sm">Eternia Vault</h4>
                                                <p className="text-[10px] text-white/30 font-mono">Bóveda SQLite Independiente</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-[8px] font-black text-brand-primary uppercase tracking-widest bg-brand-primary/10 px-2 py-0.5 rounded">Shield Layer 1</span>
                                        </div>
                                    </div>
                                    <p className="text-[11px] text-white/50 mb-6 leading-relaxed">
                                        Genera un archivo de base de datos portátil con tu inventario, precios y configuración personal para resguardo offline.
                                    </p>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={handleDownloadVault}
                                            className="flex-1 bg-brand-primary/10 hover:bg-brand-primary text-brand-primary hover:text-white border border-brand-primary/20 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-brand-primary/0 hover:shadow-brand-primary/20"
                                        >
                                            <Download className="h-3 w-3" />
                                            📦 Descargar Bóveda
                                        </button>
                                        <button
                                            disabled
                                            title="Zona de Cuarentena (Próximamente)"
                                            className="bg-white/5 text-white/20 border border-white/5 p-2.5 rounded-2xl cursor-not-allowed opacity-50"
                                        >
                                            <Upload className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>

                                <div className="glass border border-white/10 p-6 rounded-3xl group hover:bg-white/5 transition-all">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-4">
                                            <div className="bg-green-500/10 p-3 rounded-lg group-hover:bg-green-500/20 transition-all">
                                                <FileSpreadsheet className="h-5 w-5 text-green-400" />
                                            </div>
                                            <div>
                                                <h4 className="text-white font-bold text-sm">Excel Bridge</h4>
                                                <p className="text-[10px] text-white/30 font-mono">Sincronización David MOTU</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-[8px] font-black text-green-400 uppercase tracking-widest bg-green-500/10 px-2 py-0.5 rounded">Shield Layer 2</span>
                                        </div>
                                    </div>
                                    <p className="text-[11px] text-white/50 mb-6 leading-relaxed">
                                        Actualiza automáticamente la columna de adquisiciones en tu archivo Excel local de MOTU para control humano.
                                    </p>
                                    <button
                                        onClick={handleSyncExcel}
                                        className="w-full bg-green-500/10 hover:bg-green-500 text-green-400 hover:text-white border border-green-500/20 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-500/0 hover:shadow-green-500/20"
                                    >
                                        <RefreshCw className="h-3 w-3" />
                                        📊 Sincronizar Excel
                                    </button>
                                </div>
                            </div>

                            {/* --- MI BÓVEDA DIGITAL: UNIVERSAL ACCESS --- */}
                            <div className="lg:col-span-3 space-y-6">
                                <div className="flex items-center gap-3 px-2">
                                    <ShieldAlert className="h-6 w-6 text-brand-primary" />
                                    <h3 className="text-xl font-black uppercase tracking-[0.2em] text-white">Mi Bóveda Digital</h3>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="relative overflow-hidden group">
                                        <div className="absolute inset-0 bg-gradient-to-br from-brand-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-[2.5rem]"></div>
                                        <div className="relative glass border border-white/10 p-8 rounded-[2.5rem] flex flex-col gap-6 shadow-2xl backdrop-blur-3xl h-full transition-all group-hover:border-brand-primary/30">
                                            <div className="flex items-center justify-between">
                                                <div className="bg-brand-primary/10 p-4 rounded-2xl">
                                                    <FileSpreadsheet className="h-8 w-8 text-brand-primary" />
                                                </div>
                                                <span className="text-[10px] font-black text-brand-primary uppercase tracking-[0.3em] bg-brand-primary/10 px-3 py-1 rounded-full">Heritage Sync</span>
                                            </div>
                                            <div>
                                                <h4 className="text-2xl font-black text-white mb-2 uppercase tracking-tighter">Bóveda Excel</h4>
                                                <p className="text-sm text-white/50 leading-relaxed font-medium">
                                                    Descarga tu colección completa en formato Excel. Ideal para visualización rápida y edición manual heredada.
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => handleExportExcel()}
                                                className="mt-auto w-full group relative flex items-center justify-center gap-3 overflow-hidden rounded-2xl bg-brand-primary py-5 font-black text-white transition-all hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-brand-primary/20"
                                            >
                                                <Download className="h-5 w-5" />
                                                <span className="uppercase tracking-[0.1em]">Bajar Excel Actualizado</span>
                                            </button>
                                        </div>
                                    </div>

                                    <div className="relative overflow-hidden group">
                                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-[2.5rem]"></div>
                                        <div className="relative glass border border-white/10 p-8 rounded-[2.5rem] flex flex-col gap-6 shadow-2xl backdrop-blur-3xl h-full transition-all group-hover:border-indigo-500/30">
                                            <div className="flex items-center justify-between">
                                                <div className="bg-indigo-500/10 p-4 rounded-2xl">
                                                    <Database className="h-8 w-8 text-indigo-400" />
                                                </div>
                                                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] bg-indigo-500/10 px-3 py-1 rounded-full">Deep Backup</span>
                                            </div>
                                            <div>
                                                <h4 className="text-2xl font-black text-white mb-2 uppercase tracking-tighter">Bóveda SQLite</h4>
                                                <p className="text-sm text-white/50 leading-relaxed font-medium">
                                                    Tu base de datos íntegra en un solo archivo. Es el respaldo definitivo de todas tus reliquias y su historial.
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => handleExportSqlite()}
                                                className="mt-auto w-full group relative flex items-center justify-center gap-3 overflow-hidden rounded-2xl bg-indigo-600 py-5 font-black text-white transition-all hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-indigo-600/20"
                                            >
                                                <Database className="h-5 w-5" />
                                                <span className="uppercase tracking-[0.1em]">Bajar Base de Datos</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Purification (Admin Power) */}
                            {user?.role === 'admin' && (
                                <div className="glass border border-red-500/30 p-6 rounded-3xl space-y-4 bg-red-500/5 col-span-1 md:col-span-2 lg:col-span-1">
                                    <div className="flex items-center gap-3 text-red-500 font-bold uppercase tracking-widest text-xs mb-2">
                                        <ShieldAlert className="h-4 w-4" />
                                        Purificación del Abismo
                                    </div>
                                    <div className="space-y-4">
                                        <p className="text-[10px] text-white/40 font-bold uppercase leading-tight">
                                            Desvincula masivamente todos los items automatizados por SmartMatch. <span className="text-red-400">Acción irreversible que requiere doble autorización.</span>
                                        </p>

                                        <button
                                            onClick={() => setResetStep(1)}
                                            className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/30 py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center gap-2"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                            PUERTA DE PURIFICACIÓN
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="p-8 glass border border-dashed border-white/10 rounded-[3rem] bg-brand-primary/5 flex flex-col items-center gap-4">
                            <AlertCircle className="h-8 w-8 text-brand-primary animate-pulse" />
                            <div className="text-center">
                                <h4 className="text-white font-bold">Panel Protector Activo</h4>
                                <p className="text-white/40 text-sm max-w-md mx-auto">Estas configuraciones se sincronizarán con los workers de GitHub Actions y el Backend en la Phase 13.</p>
                            </div>
                        </div>
                    </motion.div>
                ) : activeTab === 'users' ? (
                    <motion.div
                        key="users"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                            <div className="flex flex-col gap-1">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Users className="h-6 w-6 text-brand-primary" />
                                    Gestión de Héroes del Reino
                                </h3>
                                <p className="text-white/40 text-sm">Control de acceso, roles y estados de las fortalezas individuales.</p>
                            </div>
                            <button
                                onClick={() => setShowAddUserModal(true)}
                                className="bg-brand-primary/20 text-brand-primary border border-brand-primary/30 hover:bg-brand-primary hover:text-white px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                            >
                                <Users className="h-4 w-4" />
                                RECLUTAR NUEVO HÉROE
                            </button>
                        </div>

                        <div className="glass border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-white/5 text-white/30 uppercase text-[10px] font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Héroe</th>
                                        <th className="px-3 py-4 text-center w-12">ID</th>
                                        <th className="px-6 py-4">Rango (Rol)</th>
                                        <th className="px-6 py-4">Fortaleza (Items)</th>
                                        <th className="px-6 py-4">Ubicación</th>
                                        <th className="px-6 py-4 text-right">Acciones de Poder</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5 text-white/70">
                                    {heroes.map((hero: Hero) => (
                                        <tr key={hero.id} className="hover:bg-white/5 transition-colors group">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="h-10 w-10 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary font-bold text-sm border border-brand-primary/30 shadow-inner group-hover:scale-110 transition-transform">
                                                        {hero.username.charAt(0).toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <p className="font-bold text-white group-hover:text-brand-primary transition-colors">{hero.username}</p>
                                                        <p className="text-[10px] text-white/30 font-mono">{hero.email}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-3 py-4 text-center">
                                                <span className="text-xs font-mono text-brand-primary/70 bg-brand-primary/10 px-2 py-0.5 rounded-md border border-brand-primary/20">{hero.id}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <select
                                                    value={hero.role}
                                                    onChange={(e) => handleUpdateRole(hero.id, e.target.value)}
                                                    className="bg-brand-primary/10 text-brand-primary text-[10px] uppercase font-black border border-brand-primary/20 rounded px-2 py-0.5 outline-none cursor-pointer hover:bg-brand-primary/20"
                                                >
                                                    <option value="viewer" className="bg-black text-white">🛡️ Guardián</option>
                                                    <option value="admin" className="bg-black text-white">⚔️ Maestro</option>
                                                </select>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <Target className="h-3 w-3 text-brand-primary" />
                                                    <span className="font-black text-lg text-white">{hero.collection_size}</span>
                                                    <span className="text-[10px] text-brand-primary/50 font-black uppercase tracking-tighter">unidades</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest bg-white/5 px-2 py-1 rounded-md">{hero.location}</span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button
                                                        onClick={() => handleExportExcelAdmin(hero.id)}
                                                        title="Bajar Excel Personal"
                                                        className="h-8 w-8 rounded-lg bg-green-500/10 text-green-400 hover:bg-green-500 hover:text-white border border-green-500/20 flex items-center justify-center transition-all shadow-lg shadow-green-500/0 hover:shadow-green-500/20"
                                                    >
                                                        <FileSpreadsheet className="h-4 w-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleExportSqliteAdmin(hero.id)}
                                                        title="Bajar Bóveda SQLite"
                                                        className="h-8 w-8 rounded-lg bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500 hover:text-white border border-indigo-500/20 flex items-center justify-center transition-all shadow-lg shadow-indigo-500/0 hover:shadow-indigo-500/20"
                                                    >
                                                        <Database className="h-4 w-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handlePasswordReset(hero.id)}
                                                        title="Protocolo de Reseteo"
                                                        className="h-8 w-8 rounded-lg bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 flex items-center justify-center transition-all shadow-lg shadow-orange-500/0 hover:shadow-orange-500/20"
                                                    >
                                                        <ShieldAlert className="h-4 w-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    {heroes.length === 0 && (
                                        <tr>
                                            <td colSpan={6} className="px-6 py-8 text-center text-white/20 italic">
                                                No hay héroes reclutados en este momento...
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all">
                                <div className="flex items-center gap-4">
                                    <div className="bg-green-500/10 p-3 rounded-lg"><CheckCircle2 className="h-5 w-5 text-green-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Registro Abierto</h4>
                                        <p className="text-[10px] text-white/40">Permitir que nuevos usuarios se unan.</p>
                                    </div>
                                </div>
                                <div className="h-4 w-8 bg-brand-primary/30 rounded-full relative shadow-inner cursor-pointer"><div className="absolute right-1 top-1 h-2 w-2 bg-brand-primary rounded-full shadow-[0_0_8px_rgba(14,165,233,0.5)]"></div></div>
                            </div>
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all opacity-50">
                                <div className="flex items-center gap-4">
                                    <div className="bg-red-500/10 p-3 rounded-lg"><Activity className="h-5 w-5 text-red-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Vigilancia de Sesión</h4>
                                        <p className="text-[10px] text-white/40">Cierre automático por inactividad.</p>
                                    </div>
                                </div>
                                <div className="h-4 w-8 bg-white/10 rounded-full relative cursor-not-allowed"><div className="absolute left-1 top-1 h-2 w-2 bg-white/30 rounded-full"></div></div>
                            </div>
                        </div>
                    </motion.div>
                ) : activeTab === 'wallapop' ? (
                    <motion.div
                        key="wallapop"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                    >
                        <WallapopImporter />
                    </motion.div>
                ) : null}
            </AnimatePresence>

            {/* Modal de Registro de Usuario (Mock) */}
            <AnimatePresence>
                {showAddUserModal && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowAddUserModal(false)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="relative w-full max-w-lg glass border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl"
                        >
                            <div className="p-8 space-y-6">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-white uppercase tracking-tighter">Reclutar <span className="text-brand-primary">Héroe</span></h3>
                                    <div className="bg-brand-primary/20 p-2 rounded-lg text-brand-primary"><Users className="h-5 w-5" /></div>
                                </div>

                                <div className="space-y-4 opacity-50">
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest pl-1">Nombre de Usuario</label>
                                        <input type="text" disabled placeholder="Ej: He-Man" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest pl-1">Correo Electrónico</label>
                                        <input type="email" disabled placeholder="defensor@eternia.com" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-white/40 uppercase tracking-widest pl-1">Contraseña</label>
                                            <input type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-white/40 uppercase tracking-widest pl-1">Confirmar</label>
                                            <input type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-white/40 uppercase tracking-widest pl-1">Rango del Héroe (Rol)</label>
                                        <select disabled className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white/50 focus:outline-none appearance-none font-bold">
                                            <option>🛡️ Guardián de Eternia (Viewer)</option>
                                            <option>⚔️ Master del Universo (Admin)</option>
                                        </select>
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
                                        onClick={() => setShowAddUserModal(false)}
                                        className="w-full py-2 text-white/30 text-xs font-bold hover:text-white transition-colors"
                                    >
                                        VOLVAR ATRÁS
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Double Confirmation Modal for Reset */}
            <AnimatePresence>
                {resetStep > 0 && (
                    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => !isResetting && setResetStep(0)}
                            className="absolute inset-0 bg-black/95 backdrop-blur-xl"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className={`relative w-full max-w-md overflow-hidden rounded-[2.5rem] border p-8 shadow-2xl ${resetStep === 1 ? 'border-orange-500/30 bg-orange-950/20' : 'border-red-500/50 bg-red-950/30'}`}
                        >
                            <div className="flex flex-col items-center gap-6 text-center">
                                <div className={`h-20 w-20 rounded-full flex items-center justify-center border animate-pulse ${resetStep === 1 ? 'bg-orange-500/20 border-orange-500/50' : 'bg-red-500/20 border-red-500/80'}`}>
                                    <ShieldAlert className={`h-10 w-10 ${resetStep === 1 ? 'text-orange-500' : 'text-red-500'}`} />
                                </div>

                                <div className="space-y-2">
                                    <h3 className="text-3xl font-black text-white uppercase tracking-tighter">
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
                                        onClick={() => setResetStep(0)}
                                        className="rounded-2xl border border-white/10 bg-white/5 py-4 text-xs font-black text-white/40 hover:bg-white/10 transition-all uppercase tracking-widest"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        disabled={isResetting}
                                        onClick={() => resetStep === 1 ? setResetStep(2) : handleResetSmartMatches()}
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
        </div >
    );
};

export default Config;
