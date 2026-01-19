import React, { useState, useEffect } from 'react';
import { Play, Activity, Clock, AlertCircle, CheckCircle2, RefreshCw, Terminal, GitMerge, Target, Settings, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getScrapersStatus, getScrapersLogs, runScraper, getDuplicates, mergeProducts, syncNexus, type ScraperStatus, type ScraperLog } from '../api/admin';
import { formatDistanceToNow, format } from 'date-fns';
import { es } from 'date-fns/locale';
import WallapopImporter from '../components/admin/WallapopImporter';

const Config: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'scrapers' | 'radar' | 'system' | 'users' | 'wallapop'>('scrapers');
    const [statuses, setStatuses] = useState<ScraperStatus[]>([]);
    const [logs, setLogs] = useState<ScraperLog[]>([]);
    const [duplicates, setDuplicates] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [runningScraper, setRunningScraper] = useState<string | null>(null);
    const [mergingId, setMergingId] = useState<number | null>(null);
    const [syncingNexus, setSyncingNexus] = useState(false);
    const [showAddUserModal, setShowAddUserModal] = useState(false);

    const fetchData = async () => {
        try {
            const [s, l, d] = await Promise.all([
                getScrapersStatus(),
                getScrapersLogs(),
                getDuplicates()
            ]);
            setStatuses(s);
            setLogs(l);
            setDuplicates(d);
        } catch (error) {
            console.error('Error fetching admin data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Polling every 10s
        return () => clearInterval(interval);
    }, []);

    const handleRunScraper = async (name: string) => {
        setRunningScraper(name);
        try {
            await runScraper(name);
            setTimeout(fetchData, 2000);
        } catch (error) {
            console.error('Error starting scraper:', error);
        } finally {
            setTimeout(() => setRunningScraper(null), 5000);
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
        } catch (error) {
            console.error('Error syncing Nexus:', error);
            alert("❌ Nexus: Error al iniciar la sincronización.");
        } finally {
            setSyncingNexus(false);
        }
    };

    const getStatusVariant = (status: string) => {
        if (status === 'running') return 'text-brand-primary bg-brand-primary/10 border-brand-primary/30';
        if (status === 'completed' || status === 'success') return 'text-green-400 bg-green-400/10 border-green-400/30';
        if (status.startsWith('error')) return 'text-red-400 bg-red-400/10 border-red-400/30';
        return 'text-white/30 bg-white/5 border-white/10';
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
                        Poderes del <span className="text-brand-primary">Arquitecto de Nueva Eternia</span>
                    </h2>
                    <p className="text-white/50">Control absoluto sobre las reliquias y sus fuentes.</p>
                </div>

                <div className="flex bg-white/5 p-1 rounded-2xl border border-white/10 backdrop-blur-xl">
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
                    <button
                        onClick={() => setActiveTab('system')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'system' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                    >
                        <Settings className="h-4 w-4" />
                        Ajustes de Sistema
                    </button>
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'users' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/40 hover:text-white'}`}
                    >
                        <Users className="h-4 w-4" />
                        Gestión de Héroes
                    </button>
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
                        {/* Quick Actions / All Scrapers */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                className="col-span-1 md:col-span-2 glass border border-brand-primary/30 p-6 rounded-2xl flex items-center justify-between bg-gradient-to-br from-brand-primary/10 to-transparent"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="bg-brand-primary/20 p-4 rounded-xl shadow-[0_0_20px_rgba(14,165,233,0.3)]">
                                        <Activity className="h-8 w-8 text-brand-primary" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white">Incursión Global</h3>
                                        <p className="text-white/50 text-sm">Escaneo completo de todas las tiendas.</p>
                                    </div>
                                </div>
                                <div className="flex flex-col gap-2">
                                    <button
                                        onClick={() => handleRunScraper('all')}
                                        disabled={runningScraper === 'all'}
                                        className="bg-brand-primary hover:bg-brand-primary/80 text-white px-6 py-3 rounded-2xl font-black text-sm transition-all shadow-lg shadow-brand-primary/20 flex items-center gap-2 disabled:opacity-50"
                                    >
                                        {runningScraper === 'all' ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
                                        INCURSIÓN TOTAL
                                    </button>

                                    <button
                                        onClick={handleSyncNexus}
                                        disabled={syncingNexus}
                                        className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-3 rounded-2xl font-black text-sm transition-all flex items-center gap-2 disabled:opacity-50"
                                    >
                                        {syncingNexus ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Activity className="h-4 w-4 text-brand-primary" />}
                                        SINCRONIZAR NEXO MAESTRO
                                    </button>
                                </div>
                            </motion.div>

                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                className="glass border border-white/10 p-6 rounded-2xl flex flex-col gap-4"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="h-10 w-10 bg-white/5 rounded-lg flex items-center justify-center">
                                        <RefreshCw className="h-5 w-5 text-purple-400" />
                                    </div>
                                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold border ${getStatusVariant(statuses.find(s => s.spider_name === 'harvester')?.status || 'idle')}`}>
                                        {statuses.find(s => s.spider_name === 'harvester')?.status || 'Inactivo'}
                                    </span>
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Harvester</h3>
                                    <p className="text-white/40 text-xs">Búsqueda manual dirigida.</p>
                                </div>
                                <button
                                    onClick={() => handleRunScraper('harvester')}
                                    disabled={runningScraper === 'harvester'}
                                    className="w-full bg-white/5 hover:bg-white/10 text-white py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 border border-white/10"
                                >
                                    {runningScraper === 'harvester' ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current text-white/40" />}
                                    Lanzar
                                </button>
                            </motion.div>

                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                className="glass border border-white/10 p-6 rounded-2xl flex flex-col gap-4"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="h-10 w-10 bg-white/5 rounded-lg flex items-center justify-center">
                                        <span className="text-orange-400 font-bold">A</span>
                                    </div>
                                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold border ${getStatusVariant(statuses.find(s => s.spider_name === 'amazon')?.status || 'idle')}`}>
                                        {statuses.find(s => s.spider_name === 'amazon')?.status || 'Inactivo'}
                                    </span>
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Amazon</h3>
                                    <p className="text-white/40 text-xs">Vigilancia centinela.</p>
                                </div>
                                <button
                                    onClick={() => handleRunScraper('amazon')}
                                    disabled={runningScraper === 'amazon'}
                                    className="w-full bg-white/5 hover:bg-white/10 text-white py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 border border-white/10"
                                >
                                    {runningScraper === 'amazon' ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current text-white/40" />}
                                    Escanear
                                </button>
                            </motion.div>
                        </div>

                        {/* Individual Scrapers Grid */}
                        <div className="space-y-4">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Activity className="h-5 w-5 text-brand-primary" />
                                Estados Individuales
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                                {statuses.filter(s => s.spider_name !== 'all' && s.spider_name !== 'harvester' && s.spider_name !== 'amazon').map((s) => (
                                    <div key={s.spider_name} className="glass border border-white/5 p-3 rounded-xl flex flex-col gap-2 relative">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[10px] font-bold text-white/70 uppercase tracking-wider">{s.spider_name}</span>
                                            <div className={`h-1.5 w-1.5 rounded-full ${s.status === 'running' ? 'bg-brand-primary animate-pulse' : s.status === 'completed' ? 'bg-green-400' : 'bg-white/20'}`}></div>
                                        </div>
                                        <button
                                            onClick={() => handleRunScraper(s.spider_name)}
                                            disabled={runningScraper === s.spider_name}
                                            className="text-[11px] bg-white/5 py-1 rounded-md text-white/50 hover:bg-brand-primary/20 hover:text-brand-primary transition-all flex items-center justify-center gap-1"
                                        >
                                            {runningScraper === s.spider_name ? <RefreshCw className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3 fill-current" />}
                                            RUN
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Recent logs */}
                        <div className="space-y-4">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Clock className="h-5 w-5 text-brand-primary" />
                                Bitácora de Incursiones
                            </h3>
                            <div className="glass border border-white/10 rounded-2xl overflow-hidden">
                                <div className="overflow-x-auto text-sm">
                                    <table className="w-full text-left">
                                        <thead className="bg-white/5 text-white/30 uppercase text-[10px] font-bold">
                                            <tr>
                                                <th className="px-6 py-4">Scraper</th>
                                                <th className="px-6 py-4">Estado</th>
                                                <th className="px-6 py-4 text-center">Items</th>
                                                <th className="px-6 py-4">Tiempo</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5 text-white/70">
                                            {logs.map((log) => (
                                                <tr key={log.id} className="hover:bg-white/5 transition-colors">
                                                    <td className="px-6 py-4 font-bold">{log.spider_name}</td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${log.status === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                                                            {log.status}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-center font-black text-white">{log.items_found}</td>
                                                    <td className="px-6 py-4 text-[10px]">
                                                        {format(new Date(log.start_time), "dd/MM/yyyy HH:mm", { locale: es })}
                                                        <span className="block opacity-40 text-[9px]">
                                                            ({formatDistanceToNow(new Date(log.start_time), { addSuffix: true, locale: es })})
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
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
                        <div className="flex flex-col gap-2 mb-4">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Settings className="h-6 w-6 text-brand-primary" />
                                Configuración del Núcleo
                            </h3>
                            <p className="text-white/40 text-sm">Ajustes sistémicos del Oráculo. Actualmente en modo lectura (inactivos).</p>
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

                        <div className="glass border border-white/10 rounded-3xl overflow-hidden opacity-60">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-white/5 text-white/30 uppercase text-[10px] font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Usuario</th>
                                        <th className="px-6 py-4">Rol</th>
                                        <th className="px-6 py-4">Colección</th>
                                        <th className="px-6 py-4">Última Actividad</th>
                                        <th className="px-6 py-4 text-right">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5 text-white/70">
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="h-8 w-8 rounded-full bg-brand-primary/20 flex items-center justify-center text-brand-primary font-bold text-xs border border-brand-primary/30">D</div>
                                                <div>
                                                    <p className="font-bold text-white">David</p>
                                                    <p className="text-[10px] text-white/30">david@eternia.com</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="px-2 py-0.5 rounded bg-brand-primary/10 text-brand-primary text-[10px] uppercase font-bold border border-brand-primary/20">Admin</span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <Target className="h-3 w-3 text-brand-primary" />
                                                <span className="font-black text-white">75</span>
                                                <span className="text-[10px] text-white/30 tracking-tighter">items</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-[10px]">Hace 5 minutos</td>
                                        <td className="px-6 py-4 text-right">
                                            <button disabled className="text-white/20 hover:text-white p-2"><Settings className="h-4 w-4" /></button>
                                        </td>
                                    </tr>
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-4 text-white/30 italic" colSpan={5}>
                                            Espacio reservado para futuros reclutas...
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 opacity-60">
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="bg-green-500/10 p-3 rounded-lg"><CheckCircle2 className="h-5 w-5 text-green-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Registro Abierto</h4>
                                        <p className="text-[10px] text-white/40">Permitir que nuevos usuarios se unan.</p>
                                    </div>
                                </div>
                                <div className="h-4 w-8 bg-brand-primary/30 rounded-full relative"><div className="absolute right-1 top-1 h-2 w-2 bg-brand-primary rounded-full"></div></div>
                            </div>
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="bg-red-500/10 p-3 rounded-lg"><AlertCircle className="h-5 w-5 text-red-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Modo Invitado</h4>
                                        <p className="text-[10px] text-white/40">Visualización sin registro.</p>
                                    </div>
                                </div>
                                <div className="h-4 w-8 bg-white/10 rounded-full relative"><div className="absolute left-1 top-1 h-2 w-2 bg-white/30 rounded-full"></div></div>
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
        </div>
    );
};

export default Config;
