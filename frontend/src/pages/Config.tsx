import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Activity, Clock, AlertCircle, CheckCircle2, RefreshCw, Terminal, Target, Settings, Users, ShieldAlert, Trash2, Zap, History, Database, Download, FileSpreadsheet, Repeat, Globe, Package, ChevronDown, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { resetSmartMatches, runScrapers, stopScrapers, getScraperLogs, type ScraperExecutionLog, getWallapopIpLogs, downloadWallapopIpLogs, type WallapopIpLog } from '../api/purgatory';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import WallapopImporter from '../components/admin/WallapopImporter';
import { getDashboardMatchStats } from '../api/dashboard';


import {
    getScrapersStatus,
    syncNexus,
    getUserSettings,
    getHeroes,
    updateHeroRole,
    resetHeroPassword,
    deleteHero,
    syncExcel,
    exportCollectionExcel,
    exportCollectionSqlite,
    updateUserLocation,
    updateUserPublicShowcase,
    type ScraperStatus,
    type Hero
} from '../api/admin';

interface ConfigProps {
    user?: Hero | null;
    onUserUpdate?: () => void;
    onIdentityChange?: (targetId: number) => void;
}

const getParsedMetrics = (logsText?: string) => {
    if (!logsText) return null;
    const match = logsText.match(/📊 \[Resumen\] Nuevas en Purgatorio: (\d+) \| Precios actualizados: (\d+) \| Sin cambios: (\d+) \| Descartadas: (\d+)/);
    if (match) {
        return {
            newItems: parseInt(match[1]),
            priceUpdates: parseInt(match[2]),
            unchanged: parseInt(match[3]),
            discarded: parseInt(match[4])
        };
    }
    return null;
};

interface StepperStatus {
    step: number;
    title: string;
    description: string;
    status: 'pending' | 'running' | 'completed' | 'error' | 'warning';
}

const getStepperStatus = (logsText?: string, statusText?: string): StepperStatus[] => {
    const steps: StepperStatus[] = [
        { step: 1, title: 'Inicialización', description: 'Arranque de sistemas', status: 'pending' },
        { step: 2, title: 'Bypass de WAF', description: 'Validación de CloudFront', status: 'pending' },
        { step: 3, title: 'Extracción', description: 'Raspado de ofertas', status: 'pending' },
        { step: 4, title: 'Ingesta', description: 'Persistencia en BD', status: 'pending' },
    ];
    
    if (!logsText) return steps;

    const lower = logsText.toLowerCase();

    // --- STEP 1: Inicialización ---
    if (lower.includes('desplegando incursión') || lower.includes('iniciando secuencia') || lower.includes('buscando reliquias')) {
        steps[0].status = 'completed';
        steps[0].description = 'Sistemas listos';
    }
    
    // --- STEP 2: Bypass de WAF ---
    if (lower.includes('validando estado de conexión') || lower.includes('intentando conexión directa') || lower.includes('ip de origen detectada')) {
        steps[1].status = 'running';
        steps[1].description = 'Verificando firewall';
    }
    
    if (lower.includes('bloqueada por waf')) {
        if (lower.includes('re-intentando playwright con proxy') || lower.includes('ruteando wallapop api a través de scraperapi')) {
            steps[1].status = 'completed';
            steps[1].description = 'Bypass con Proxy';
        } else {
            steps[1].status = 'error';
            steps[1].description = 'IP bloqueada por WAF';
        }
    } else if (lower.includes('ip de origen detectada') || lower.includes('bypassing probe') || lower.includes('de forma directa')) {
        steps[1].status = 'completed';
        steps[1].description = 'Conexión directa limpia';
    }

    // --- STEP 3: Extracción ---
    if (lower.includes('navegando directamente') || lower.includes('buscando') || lower.includes('iniciando búsqueda') || lower.includes('re-intentando playwright con proxy')) {
        if (steps[1].status !== 'error') {
            steps[2].status = 'running';
            steps[2].description = 'Buscando reliquias';
        }
    }

    if (lower.includes('halladas') || lower.includes('encontrados') || lower.includes('encontradas') || lower.includes('persistiendo')) {
        steps[2].status = 'completed';
        const matchFound = logsText.match(/(?:halladas|encontrados|encontradas) (\d+) reliquias/i) || logsText.match(/encontrados (\d+) objetos/i);
        const count = matchFound ? matchFound[1] : '?';
        steps[2].description = `Encontradas ${count} reliquias`;
    } else if (lower.includes('timeout') || lower.includes('falló la comprobación de red') || lower.includes('error general')) {
        steps[2].status = 'error';
        steps[2].description = 'Error de red / Timeout';
    }

    // --- STEP 4: Ingesta ---
    if (lower.includes('persistiendo')) {
        steps[3].status = 'running';
        steps[3].description = 'Persistiendo ofertas...';
    }

    if (lower.includes('incursión completada con éxito') || lower.includes('incursión completada') || statusText === 'success' || statusText === 'completed') {
        steps[3].status = 'completed';
        steps[3].description = 'BD Purificada con éxito';
        if (steps[2].status === 'running') steps[2].status = 'completed';
    } else if (lower.includes('fallo crítico') || statusText === 'error' || lower.includes('error detectado')) {
        steps[3].status = 'error';
        steps[3].description = 'Fallo de persistencia';
    }

    return steps;
};

const Config: React.FC<ConfigProps> = ({ user, onUserUpdate, onIdentityChange }) => {
    const consoleRef = React.useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'scrapers' | 'system' | 'users' | 'wallapop' | 'inventory'>('scrapers');
    const [statuses, setStatuses] = useState<ScraperStatus[]>([]);
    const [matchStats, setMatchStats] = useState<any[]>([]);
    const [syncingSensores, setSyncingSensores] = useState(false);
    const [heroes, setHeroes] = useState<any[]>([]);
    // const [duplicates, setDuplicates] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    // const [mergingId, setMergingId] = useState<number | null>(null);
    const [syncingNexus, setSyncingNexus] = useState(false);
    const [showAddUserModal, setShowAddUserModal] = useState(false);
    const [userSettings, setUserSettings] = useState<any>(null);
    const [savingSettings, setSavingSettings] = useState(false);
    const [resetStep, setResetStep] = useState(0); // 0: idle, 1: first confirm, 2: second confirm
    const [isResetting, setIsResetting] = useState(false);
    const [selectedLog, setSelectedLog] = useState<ScraperExecutionLog | null>(null);
    const [advancedLogs, setAdvancedLogs] = useState<ScraperExecutionLog[]>([]);
    const [targetLogId, setTargetLogId] = useState<number | null>(null);

    const [showIpLogsModal, setShowIpLogsModal] = useState(false);
    const [ipLogs, setIpLogs] = useState<WallapopIpLog[]>([]);
    const [loadingIpLogs, setLoadingIpLogs] = useState(false);

    const [, setLocalImagesEnabled] = useState(() => localStorage.getItem('use_local_images') === 'true');
    const [downloadStatus, setDownloadStatus] = useState({ active: false, total: 0, current: 0, errors: 0, last_error: null as string | null });
    const [cachedImagesCount, setCachedImagesCount] = useState(0);
    const [syncingExcel, setSyncingExcel] = useState(false);
    const cancelDownloadRef = React.useRef(false);

    // Vintage Sword Light Ray Calibrator States
    const [showCalibrator, setShowCalibrator] = useState(false);
    const [calibCoords, setCalibCoords] = useState({
        gX: 79.5,
        gY: 66.5,
        tX: 73.0,
        tY: 20.5
    });

    // He-Man Modern Sword Light Ray Calibrator States (Renamed visually to Skeletor)
    const [showModernCalibrator, setShowModernCalibrator] = useState(false);
    const [modernCoords, setModernCoords] = useState({
        gX: 125.0,
        gY: 175.0,
        tX: 125.0,
        tY: 10.0
    });

    const isAdmin = user?.role === 'admin' || user?.username === 'David';
    const [showShowcaseGuide, setShowShowcaseGuide] = useState(false);

    useEffect(() => {
        if (showCalibrator) {
            const stored = localStorage.getItem('vintage_sword_coords');
            if (stored) {
                try {
                    setCalibCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse vintage sword coords", e);
                }
            }
        }
    }, [showCalibrator]);

    useEffect(() => {
        if (showModernCalibrator) {
            const stored = localStorage.getItem('skeletor_sword_coords');
            if (stored) {
                try {
                    setModernCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse modern sword coords", e);
                }
            }
        }
    }, [showModernCalibrator]);

    const handleSaveCalib = () => {
        localStorage.setItem('vintage_sword_coords', JSON.stringify(calibCoords));
        setShowCalibrator(false);
    };

    const handleResetCalib = () => {
        setCalibCoords({
            gX: 79.5,
            gY: 66.5,
            tX: 73.0,
            tY: 20.5
        });
    };

    const handleSaveModernCalib = () => {
        localStorage.setItem('skeletor_sword_coords', JSON.stringify(modernCoords));
        setShowModernCalibrator(false);
    };

    const handleResetModernCalib = () => {
        setModernCoords({
            gX: 125.0,
            gY: 175.0,
            tX: 125.0,
            tY: 10.0
        });
    };

    const handleOpenIpLogs = async () => {
        setShowIpLogsModal(true);
        setLoadingIpLogs(true);
        try {
            const data = await getWallapopIpLogs();
            setIpLogs(data);
        } catch (error) {
            console.error('Error fetching Wallapop IP logs:', error);
        } finally {
            setLoadingIpLogs(false);
        }
    };

    const handleDownloadIpLogs = async () => {
        try {
            await downloadWallapopIpLogs();
        } catch (error) {
            console.error('Error downloading Wallapop IP logs:', error);
            alert('Error al descargar los logs. Compruebe la conexión.');
        }
    };

    // We will download images directly in the browser's Cache API for Option C
    const handleTriggerDownload = async () => {
        cancelDownloadRef.current = false;
        setDownloadStatus({
            active: true,
            total: 0,
            current: 0,
            errors: 0,
            last_error: null
        });

        try {
            // 1. Fetch both non-vintage and vintage products to get their IDs and image URLs
            const [modernRes, vintageRes] = await Promise.all([
                axios.get('/api/products'),
                axios.get('/api/products?is_vintage=true')
            ]);
            const products = [...modernRes.data, ...vintageRes.data];
            // Filter products that actually have image urls
            const productsWithImages = products.filter((p: any) => p.image_url);
            const totalCount = productsWithImages.length;

            setDownloadStatus(prev => ({ ...prev, total: totalCount }));

            // 2. Open the browser's Cache API storage
            const cache = await caches.open('motu-image-cache');

            // 3. Download and cache each image sequentially
            let current = 0;
            let errors = 0;
            let last_error: string | null = null;

            for (const p of productsWithImages) {
                if (cancelDownloadRef.current) {
                    break;
                }

                const cacheKey = `/api/static/images/${p.id}.webp`;
                
                try {
                    // Intentar descargar desde el servidor de estáticos local primero
                    let imgResponse = await fetch(cacheKey);
                    if (!imgResponse.ok) {
                        // Fallback a la URL remota de Supabase si falla el estático local
                        imgResponse = await fetch(p.image_url);
                    }
                    
                    if (imgResponse.ok) {
                        // Store the response in the cache
                        await cache.put(cacheKey, imgResponse);
                    } else {
                        throw new Error(`HTTP ${imgResponse.status}`);
                    }
                } catch (err: any) {
                    console.error(`Error caching image for product ${p.id}:`, err);
                    errors++;
                    last_error = err.message || String(err);
                }

                current++;
                setDownloadStatus(prev => ({
                    ...prev,
                    current,
                    errors,
                    last_error
                }));
            }

            setDownloadStatus(prev => ({ ...prev, active: false }));
            if (cancelDownloadRef.current) {
                alert("Descarga en el navegador cancelada por el usuario.");
            } else {
                alert(`Descarga completada. ${current - errors} imágenes guardadas en el navegador.`);
            }
        } catch (e: any) {
            console.error("Failed to download images to browser cache", e);
            setDownloadStatus(prev => ({ ...prev, active: false, last_error: e.message || String(e) }));
            alert("Error al iniciar la descarga de imágenes en el navegador: " + (e.message || String(e)));
        }
    };

    const handleCancelDownload = () => {
        cancelDownloadRef.current = true;
        setDownloadStatus(prev => ({ ...prev, active: false }));
    };

    const queryClient = useQueryClient();

    const activeUserId = parseInt(localStorage.getItem('active_user_id') || '2');

    useEffect(() => {
        if (user && user.role !== 'admin' && activeTab === 'scrapers') {
            setActiveTab('system');
        }
    }, [user, activeTab]);

    // Auto-scroll log console to bottom when new logs are added
    useEffect(() => {
        if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [selectedLog?.logs]);

    const fetchData = async () => {
        try {
            // Fetch everything, but handle individual failures gracefully
            const [s, u, al, h, ms] = await Promise.all([
                getScrapersStatus().catch((e: any) => { console.error("Scrapers error:", e); return []; }),
                getUserSettings(activeUserId).catch((e: any) => { console.error("User settings error:", e); return null; }),
                getScraperLogs().catch((e: any) => { console.error("Logs error:", e); return []; }),
                getHeroes().catch((e: any) => { console.error("Heroes list error:", e); return []; }),
                getDashboardMatchStats(activeUserId).catch((e: any) => { console.error("Match stats error:", e); return []; })
            ]);

            setStatuses(s || []);
            if (u) setUserSettings(u);
            setAdvancedLogs(al || []);
            setHeroes(h || []);
            setMatchStats(ms || []);

            // update selected log if necessary
            if (al && al.length > 0) {
                const targetId = targetLogId;
                if (targetId) {
                    const matched = al.find((l: any) => l.id === targetId);
                    if (matched) {
                        setSelectedLog(matched);
                        if (matched.status !== 'running') {
                            setTargetLogId(null);
                        }
                    } else {
                        setSelectedLog(al[0]);
                    }
                } else if (selectedLog) {
                    const current = al.find((l: any) => l.id === selectedLog.id);
                    if (current) setSelectedLog(current);
                } else {
                    setSelectedLog(al[0]);
                }
            }
        } catch (error) {
            console.error('Error fetching admin data:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateCachedImagesCount = async () => {
        try {
            const cache = await caches.open('motu-image-cache');
            const keys = await cache.keys();
            setCachedImagesCount(keys.length);
        } catch (e) {
            console.error("Error checking cache count", e);
        }
    };

    useEffect(() => {
        updateCachedImagesCount();
    }, [downloadStatus.active]);

    const runScrapersMutation = useMutation({
        mutationFn: (scraperName: string) => runScrapers(scraperName, 'manual'),
        onSuccess: (data: any) => {
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
            if (data && data.log_id) {
                setTargetLogId(data.log_id);
            }
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

    // Adaptive polling: 5s when scrapers running, 60s when idle
    const hasRunning = statuses.some(s => s.status === 'running');
    useEffect(() => {
        fetchData();
        const pollMs = hasRunning ? 5000 : 60000;
        const interval = setInterval(fetchData, pollMs);
        return () => clearInterval(interval);
    }, [hasRunning]);

    const handleUpdateLocation = async (loc: string) => {
        setSavingSettings(true);
        try {
            await updateUserLocation(activeUserId, loc);
            setUserSettings({ ...userSettings, location: loc });
        } catch (error) {
            console.error('Error updating location:', error);
        } finally {
            setSavingSettings(false);
        }
    };

    const handleToggleShowcase = async () => {
        if (!userSettings) return;
        const targetState = !userSettings.is_public_showcase;
        try {
            await updateUserPublicShowcase(activeUserId, targetState);
            setUserSettings({ ...userSettings, is_public_showcase: targetState });
        } catch (error) {
            console.error('Error updating public showcase state:', error);
            alert('Error al actualizar el estado del Santuario');
        }
    };

    const handleCopyShowcaseLink = () => {
        if (!userSettings) return;
        const link = `${window.location.origin}/santuario/${userSettings.username}`;
        navigator.clipboard.writeText(link)
            .then(() => alert('📋 Enlace de Santuario copiado al portapapeles!'))
            .catch(() => alert('Fallo al copiar enlace.'));
    };


    /*
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
    */

    const handleSyncNexus = async () => {
        setSyncingNexus(true);
        try {
            await syncNexus();
            alert("📡 Nexus: Sincronización maestro iniciada en segundo plano. Las nuevas imágenes y datos se verán reflejados en unos minutos.");
        } catch (error: any) {
            console.error('Error syncing Nexus:', error);
            const detail = error.response?.data?.detail || error.message || "Error de red o servidor";
            alert(`❌ Nexus: Error al iniciar la sincronización.Detalle: ${detail} `);
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
            await updateHeroRole(userId, newRole);
            const updatedHeroes = await getHeroes();
            setHeroes(updatedHeroes);

            // If we updated the current active user, refresh global state
            if (userId === activeUserId && onUserUpdate) {
                onUserUpdate();
            }
        } catch (error) {
            console.error('Error updating role:', error);
        }
    };

    const handlePasswordReset = async (heroId: number) => {
        if (!confirm('¿Deseas enviar un protocolo de reseteo a este héroe?')) return;
        try {
            await resetHeroPassword(heroId);
            alert('Protocolo de reseteo iniciado con éxito.');
        } catch (error) {
            console.error('Error in password reset:', error);
            alert('Fallo al iniciar protocolo de reseteo.');
        }
    };

    const handleDeleteHero = async (heroId: number, username: string) => {
        if (!confirm(`🚨 ACCIÓN CRÍTICA: ¿Estás seguro de que deseas eliminar permanentemente a ${username} del Oráculo ? Esta acción es irreversible y borrará toda su colección.`)) return;

        try {
            await deleteHero(heroId);
            fetchData(); // Recargar lista
            alert(`Justicia del Arquitecto: ${username} ha sido purgado.`);
        } catch (error) {
            console.error('Error deleting hero:', error);
            alert('El escudo del héroe resistió el borrado o hubo un fallo de red.');
        }
    };

    const handleSyncExcel = async () => {
        setSyncingExcel(true);
        try {
            const res = await syncExcel(activeUserId);
            alert(`📊 Excel Bridge: ${res.message} `);
        } catch (error: any) {
            console.error('Error syncing excel:', error);
            const detail = error.response?.data?.detail || "Fallo en la conexión local.";
            alert(`❌ Error en Excel Bridge: ${detail} `);
        } finally {
            setSyncingExcel(false);
        }
    };

    const handleExportExcelAdmin = async (userId: number) => {
        try {
            await exportCollectionExcel(userId);
            alert('📦 Bóveda Digital: Excel generado y descargado con éxito.');
        } catch (error) {
            console.error('Error exporting excel:', error);
            alert('❌ Error al exportar Excel.');
        }
    };

    const handleExportSqliteAdmin = async (userId: number) => {
        try {
            await exportCollectionSqlite(userId);
            alert('🗄️ Bóveda Digital: SQLite generado y descargado con éxito.');
        } catch (error) {
            console.error('Error exporting sqlite:', error);
            alert('❌ Error al exportar SQLite.');
        }
    };


    if (loading && statuses.length === 0) {
        return <PowerSwordLoader variant="fullScreen" text="Invocando archivos del Oráculo..." />;
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
                    <p className="text-white/50">
                        {user?.role === 'admin' 
                            ? 'Administra los scrapers de incursión, el catálogo de reliquias, la gestión de héroes y la calibración del sistema.' 
                            : 'Configura tu ubicación geográfica, el Santuario público y la caché de imágenes local.'}
                    </p>
                </div>

                {user?.role === 'admin' && (
                    <div className="flex flex-wrap items-center justify-center gap-1 bg-white/5 p-1 rounded-2xl border border-white/10 backdrop-blur-xl w-full md:w-auto shadow-lg">
                        <button
                            onClick={() => setActiveTab('scrapers')}
                            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 flex-1 sm:flex-initial min-w-[100px] sm:min-w-0 ${activeTab === 'scrapers' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/65 hover:text-white'}`}
                        >
                            <Activity className="h-3.5 w-3.5" />
                            Scrapers
                        </button>
                        <button
                            onClick={() => setActiveTab('inventory')}
                            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 flex-1 sm:flex-initial min-w-[100px] sm:min-w-0 ${activeTab === 'inventory' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/65 hover:text-white'}`}
                        >
                            <Package className="h-3.5 w-3.5" />
                            Inventario
                        </button>
                        <button
                            onClick={() => setActiveTab('system')}
                            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 flex-1 sm:flex-initial min-w-[100px] sm:min-w-0 ${activeTab === 'system' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/65 hover:text-white'}`}
                        >
                            <Settings className="h-3.5 w-3.5" />
                            Ajustes
                        </button>
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 flex-1 sm:flex-initial min-w-[100px] sm:min-w-0 ${activeTab === 'users' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'text-white/65 hover:text-white'}`}
                        >
                            <Users className="h-4 w-4" />
                            Héroes
                        </button>
                    </div>
                )}
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
                                    <div className="max-h-[500px] overflow-y-auto space-y-2 rounded-[2.5rem] border border-white/5 bg-black/40 p-3 scrollbar-none custom-scrollbar shadow-inner">
                                        {advancedLogs.map((log) => (
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

                                                        return (
                                                            <div key={i} className={`flex gap-4 group/line ${isError ? 'text-red-400' : isSuccess ? 'text-green-400' : isWarning ? 'text-yellow-400' : 'text-white/60'}`}>
                                                                <span className="text-white/10 select-none w-8 text-right group-hover/line:text-white/60 transition-colors">{String(i + 1).padStart(3, '0')}</span>
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
                ) : activeTab === 'inventory' ? (
                    <motion.div
                        key="inventory"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <h2 className="text-2xl font-bold flex items-center gap-2">
                                    <Package className="w-6 h-6 text-brand-primary" />
                                    Conquistas de Mercado (Inventario)
                                </h2>
                                <p className="text-white/70 text-sm">Resumen de reliquias indexadas por cada portal del mercado.</p>
                            </div>
                        </div>

                        <div className="rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 space-y-6">
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3 md:gap-4">
                                {matchStats?.map((item) => (
                                    <div key={item.shop} className="flex flex-col gap-1 rounded-2xl bg-white/[0.03] p-3 md:p-4 border border-white/5">
                                        <span className="text-[8px] md:text-[9px] font-black uppercase text-white/60 tracking-widest truncate">{item.shop}</span>
                                        <span className="text-xl md:text-2xl font-black text-white">{item.count}</span>
                                    </div>
                                ))}
                                {(!matchStats || matchStats.length === 0) && (
                                    <div className="col-span-full py-6 text-center text-white/60 uppercase font-black text-[9px] tracking-widest">
                                        Sin estadísticas de mercado
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                ) : activeTab === 'system' ? (
                    <motion.div
                        key="system"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        {user?.role === 'admin' && (
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h2 className="text-2xl font-bold flex items-center gap-2">
                                        <Database className="w-6 h-6 text-blue-400" />
                                        Cámara de Reliquias de Eternia
                                    </h2>
                                    <p className="text-white/70 text-sm">Resguardo y sincronización de tu legado físico.</p>
                                </div>
                                <div className="px-3 py-1 rounded-full bg-blue-900/30 text-blue-400 text-xs font-mono border border-blue-800/50">
                                    SHIELD LAYER 2
                                </div>
                            </div>
                        )}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Sentinel Settings */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60 relative group">
                                <div className="absolute right-4 top-4 text-white/30 group-hover:text-white/60 transition-colors cursor-help" title="Configuración de solo lectura en .env">
                                    <Lock className="h-3.5 w-3.5" />
                                </div>
                                <div className="flex items-center gap-3 text-orange-400 font-bold uppercase tracking-widest text-xs mb-2">
                                    <AlertCircle className="h-4 w-4" />
                                    Vigilancia (Sentinel)
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Umbral de Alerta de Precio (%)</label>
                                        <input type="range" disabled className="w-full accent-brand-primary" value="15" />
                                        <div className="flex justify-between text-[10px] text-white/60 font-bold">
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
                                    <div className="text-[8px] text-white/40 font-bold uppercase tracking-wider text-center mt-2 border-t border-white/5 pt-2">
                                        Parámetro fijado en el Servidor (.env)
                                    </div>
                                </div>
                            </div>

                            {/* Financial Engine Settings */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60 relative group">
                                <div className="absolute right-4 top-4 text-white/30 group-hover:text-white/60 transition-colors cursor-help" title="Configuración de solo lectura en .env">
                                    <Lock className="h-3.5 w-3.5" />
                                </div>
                                <div className="flex items-center gap-3 text-yellow-500 font-bold uppercase tracking-widest text-xs mb-2">
                                    <Target className="h-4 w-4" />
                                    Motor Financiero (Griales)
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">ROI Mínimo para Grial (%)</label>
                                        <div className="flex items-center gap-3">
                                            <input type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="50" />
                                            <span className="text-white/60 text-xs">%</span>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Valor Umbral Grial (€)</label>
                                        <div className="flex items-center gap-3">
                                            <input type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="150" />
                                            <span className="text-white/60 text-xs">€</span>
                                        </div>
                                    </div>
                                    <div className="text-[8px] text-white/40 font-bold uppercase tracking-wider text-center mt-2 border-t border-white/5 pt-2">
                                        Parámetro fijado en el Servidor (.env)
                                    </div>
                                </div>
                            </div>

                            {/* Scraper Global Timing */}
                            <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 opacity-60 relative group">
                                <div className="absolute right-4 top-4 text-white/30 group-hover:text-white/60 transition-colors cursor-help" title="Configuración de solo lectura en .env">
                                    <Lock className="h-3.5 w-3.5" />
                                </div>
                                <div className="flex items-center gap-3 text-blue-400 font-bold uppercase tracking-widest text-xs mb-2">
                                    <Clock className="h-4 w-4" />
                                    Tiempos de Incursión
                                </div>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-white/50 block font-medium">Delay entre Páginas (seg)</label>
                                        <input type="range" disabled className="w-full accent-blue-400" value="10" />
                                        <div className="flex justify-between text-[10px] text-white/60 font-bold">
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
                                    <div className="text-[8px] text-white/40 font-bold uppercase tracking-wider text-center mt-2 border-t border-white/5 pt-2">
                                        Parámetro fijado en el Servidor (.env)
                                    </div>
                                </div>
                            </div>

                            {/* Compartir Santuario (Public Showcase) */}
                            <div className="glass border border-brand-primary/30 p-6 rounded-3xl space-y-4 bg-brand-primary/5">
                                <div className="flex items-center gap-3 text-brand-primary font-bold uppercase tracking-widest text-xs mb-2">
                                    <Globe className="h-4 w-4" />
                                    Compartir Santuario (Público)
                                </div>
                                <div className="space-y-4">
                                    <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
                                        Permite que cualquier persona vea tu colección de figuras sin necesidad de registrarse. Se ocultarán todos tus datos financieros.
                                    </p>

                                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl">
                                        <span className="text-xs text-white/70">Santuario Público</span>
                                        <button
                                            onClick={handleToggleShowcase}
                                            className={`relative h-5 w-10 rounded-full transition-all ${userSettings?.is_public_showcase ? 'bg-brand-primary' : 'bg-white/10'}`}
                                        >
                                            <div className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all ${userSettings?.is_public_showcase ? 'right-0.5' : 'left-0.5'}`} />
                                        </button>
                                    </div>

                                    {userSettings?.is_public_showcase && (
                                        <button
                                            onClick={handleCopyShowcaseLink}
                                            className="w-full bg-brand-primary/10 hover:bg-brand-primary text-brand-primary hover:text-white border border-brand-primary/25 px-4 py-2.5 rounded-2xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                                        >
                                            <Repeat className="h-3 w-3 animate-pulse text-brand-primary" />
                                            Copiar Enlace Santuario
                                        </button>
                                    )}

                                    {/* Collapsible Showcase Guide Section */}
                                    <div className="w-full border-t border-white/5 pt-3">
                                        <button
                                            type="button"
                                            onClick={() => setShowShowcaseGuide(!showShowcaseGuide)}
                                            className="w-full flex items-center justify-between px-3 py-2 bg-white/5 hover:bg-white/10 rounded-xl transition-all border border-white/5 group"
                                        >
                                            <span className="text-[9px] font-black text-white/80 uppercase tracking-widest flex items-center gap-1.5">
                                                📋 ¿Cómo funciona el Santuario Público?
                                            </span>
                                            <ChevronDown className={`h-3 w-3 text-white/50 group-hover:text-white transition-transform duration-300 ${showShowcaseGuide ? 'rotate-180' : ''}`} />
                                        </button>

                                        {showShowcaseGuide && (
                                            <div className="mt-2 p-3 bg-white/[0.02] border border-white/5 rounded-xl text-[9px] text-white/60 space-y-2.5 leading-relaxed">
                                                <div>
                                                    <h4 className="font-black text-white uppercase tracking-wider mb-1">1. Enlace Compartible</h4>
                                                    <p className="text-[8px] leading-normal text-white/70">
                                                        Cualquier persona a la que le envíes el link podrá ver tu colección en tiempo real, sin necesidad de tener cuenta ni registrarse.
                                                    </p>
                                                </div>
                                                <div>
                                                    <h4 className="font-black text-white uppercase tracking-wider mb-1">2. Privacidad de Datos</h4>
                                                    <p className="text-[8px] leading-normal text-amber-500 font-bold">
                                                        Se ocultan automáticamente tu inversión, precios de adquisición, ROI y todas tus anotaciones personales de la base de datos.
                                                    </p>
                                                </div>
                                                <div>
                                                    <h4 className="font-black text-white uppercase tracking-wider mb-1">3. Control de Acceso</h4>
                                                    <p className="text-[8px] leading-normal text-white/70">
                                                        Si desactivas el interruptor, el enlace dejará de ser accesible de inmediato para todo el mundo, mostrando una advertencia de acceso restringido.
                                                    </p>
                                                </div>
                                            </div>
                                        )}
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
                                    <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
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

                            {/* Local Image Cache */}
                            <div className="glass border border-brand-primary/30 p-6 rounded-3xl space-y-4 bg-brand-primary/5">
                                <div className="flex items-center gap-3 text-brand-primary font-bold uppercase tracking-widest text-xs mb-2">
                                    <Download className="h-4 w-4" />
                                    Caché de Imágenes Local
                                </div>
                                <div className="space-y-4">
                                    <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
                                        Permite almacenar y cargar las imágenes de tus figuras directamente desde el almacenamiento interno del navegador para navegación instantánea y modo offline.
                                    </p>
                                    {/* Origen de Imágenes Selection */}
                                    <div className="space-y-2 p-3 bg-white/5 rounded-xl border border-white/5">
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-white/70 flex items-center gap-1.5">
                                                <Globe className="h-3.5 w-3.5" />
                                                Origen de Imágenes
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-1 pt-1">
                                            {(['supabase', 'local_cache'] as const).map((src) => {
                                                const isActive = (localStorage.getItem('image_source') || 'supabase') === src;
                                                let label = src === 'supabase' ? 'Nube' : 'Caché';
                                                return (
                                                    <button
                                                        key={src}
                                                        onClick={() => {
                                                            localStorage.setItem('image_source', src);
                                                            localStorage.setItem('use_local_images', src !== 'supabase' ? 'true' : 'false');
                                                            setLocalImagesEnabled(src !== 'supabase');
                                                            window.dispatchEvent(new Event('storage'));
                                                            fetchData();
                                                        }}
                                                        className={`py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all cursor-pointer ${
                                                            isActive
                                                                ? 'bg-brand-primary text-white shadow-lg'
                                                                : 'bg-white/5 hover:bg-white/10 text-white/60 hover:text-white'
                                                        }`}
                                                    >
                                                        {label}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    </div>

                                    {/* Download Controls */}
                                    <div className="space-y-2 pt-2 border-t border-white/5">
                                        {downloadStatus.active ? (
                                            <div className="space-y-2">
                                                <div className="flex justify-between text-[10px] font-black uppercase text-white/60">
                                                    <span>Descargando a caché...</span>
                                                    <span>{downloadStatus.current} / {downloadStatus.total}</span>
                                                </div>
                                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-brand-primary transition-all duration-300"
                                                        style={{ width: `${downloadStatus.total > 0 ? (downloadStatus.current / downloadStatus.total) * 100 : 0}%` }}
                                                    />
                                                </div>
                                                {downloadStatus.errors > 0 && (
                                                    <p className="text-[8px] text-red-400 font-bold uppercase">
                                                        Errores: {downloadStatus.errors}
                                                    </p>
                                                )}
                                                <button
                                                    onClick={handleCancelDownload}
                                                    className="w-full bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white border border-red-500/20 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all"
                                                >
                                                    Cancelar Descarga
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                <button
                                                    onClick={handleTriggerDownload}
                                                    className="w-full bg-brand-primary/15 hover:bg-brand-primary text-brand-primary hover:text-white border border-brand-primary/30 py-2.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                                                >
                                                    <Download className="h-3 w-3" />
                                                    Descargar todas las imágenes a la caché
                                                </button>
                                                <button
                                                    onClick={() => window.open('/api/vault/download-images/zip', '_blank')}
                                                    className="w-full bg-emerald-500/15 hover:bg-emerald-500 text-emerald-400 hover:text-white border border-emerald-500/30 py-2.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                                                >
                                                    <Package className="h-3 w-3" />
                                                    Descargar ZIP de imágenes WebP
                                                </button>
                                                <div className="text-[9px] font-bold text-white/40 uppercase text-center mt-1">
                                                    Imágenes en la caché del navegador: <span className="text-brand-primary">{cachedImagesCount}</span>
                                                </div>
                                                <div className="mt-3 p-3 rounded-2xl bg-white/[0.01] border border-white/[0.03] space-y-2">
                                                    <span className="text-[8px] font-black uppercase tracking-widest text-white/40 block">Jerarquía de Resolución Resiliente:</span>
                                                    <div className="space-y-1 text-[8px] uppercase font-bold text-white/50">
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="h-1.5 w-1.5 rounded-full bg-brand-primary shrink-0"></span>
                                                            <span>1. Supabase CDN (Nube / Principal por defecto)</span>
                                                        </div>
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="h-1.5 w-1.5 rounded-full bg-amber-500 shrink-0"></span>
                                                            <span>2. Caché del Navegador (Caché local si está activa)</span>
                                                        </div>
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="h-1.5 w-1.5 rounded-full bg-green-500 shrink-0"></span>
                                                            <span>3. Servidor de Estáticos local (Bypass automático/Offline)</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Calibradores de Haces de Luz */}
                            {isAdmin && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {/* Calibrador de Haces de Luz Moderno (Visualmente Skeletor) */}
                                    <div className="glass border border-purple-500/30 p-6 rounded-3xl space-y-4 bg-purple-500/5">
                                        <div className="flex items-center gap-3 text-purple-400 font-bold uppercase tracking-widest text-xs mb-2">
                                            <Zap className="h-4 w-4" />
                                            Skeletor
                                        </div>
                                        <div className="space-y-4">
                                            <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
                                                Calibra los haces de luz sobre el báculo de Skeletor en la pantalla de carga.
                                            </p>
                                            <button
                                                onClick={() => setShowModernCalibrator(true)}
                                                className="w-full bg-purple-500/10 hover:bg-purple-500 text-purple-400 hover:text-black border border-purple-500/25 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/0 hover:shadow-purple-500/25"
                                            >
                                                <Settings className="h-3.5 w-3.5" />
                                                Calibrar Espada He-Man
                                            </button>
                                        </div>
                                    </div>

                                    {/* Calibrador de Haces de Luz Vintage */}
                                    <div className="glass border border-amber-500/30 p-6 rounded-3xl space-y-4 bg-amber-500/5">
                                        <div className="flex items-center gap-3 text-amber-500 font-bold uppercase tracking-widest text-xs mb-2">
                                            <Zap className="h-4 w-4" />
                                            He-Man Vintage
                                        </div>
                                        <div className="space-y-4">
                                            <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
                                                Calibra la posición exacta de los haces de luz sobre la espada en la silueta de He-Man Vintage.
                                            </p>
                                            <button
                                                onClick={() => setShowCalibrator(true)}
                                                className="w-full bg-amber-500/10 hover:bg-amber-500 text-amber-500 hover:text-black border border-amber-500/25 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-amber-500/0 hover:shadow-amber-500/25"
                                            >
                                                <Settings className="h-3.5 w-3.5" />
                                                Calibrar Espada Vintage
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* --- SHIELD ARCHITECTURE: EXCEL BRIDGE --- */}
                            {isAdmin && (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3 px-2">
                                        <ShieldAlert className="h-6 w-6 text-brand-primary" />
                                        <h3 className="text-xl font-black uppercase tracking-[0.2em] text-white">Excel Bridge</h3>
                                    </div>
                                    <div className="glass border border-white/10 p-6 rounded-3xl group hover:bg-white/5 transition-all max-w-md">
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="flex items-center gap-4">
                                                <div className="bg-green-500/10 p-3 rounded-lg group-hover:bg-green-500/20 transition-all">
                                                    <FileSpreadsheet className="h-5 w-5 text-green-400" />
                                                </div>
                                                <div>
                                                    <h4 className="text-white font-bold text-sm">Excel Bridge</h4>
                                                    <p className="text-[10px] text-white/60 font-mono">Sincronización {isAdmin ? 'David' : user?.username} MOTU</p>
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
                                            disabled={syncingExcel}
                                            className={`w-full bg-green-500/10 hover:bg-green-500 text-green-400 hover:text-white border border-green-500/20 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-500/0 hover:shadow-green-500/20 ${syncingExcel ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                            <RefreshCw className={`h-3 w-3 ${syncingExcel ? 'animate-spin' : ''}`} />
                                            {syncingExcel ? 'Sincronizando...' : '📊 Sincronizar Excel'}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Purification (Admin Power) */}
                            {user?.role === 'admin' && (
                                <div className="glass border border-red-500/30 p-6 rounded-3xl space-y-4 bg-red-500/5 col-span-1 md:col-span-2 lg:col-span-1">
                                    <div className="flex items-center gap-3 text-red-500 font-bold uppercase tracking-widest text-xs mb-2">
                                        <ShieldAlert className="h-4 w-4" />
                                        Purificación del Abismo
                                    </div>
                                    <div className="space-y-4">
                                        <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
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
                                <p className="text-white/65 text-sm">Control de acceso, roles y estados de las fortalezas individuales.</p>
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
                            <div className="overflow-x-auto scrollbar-none custom-scrollbar">
                                <table className="w-full text-left text-sm min-w-[700px]">
                                    <thead className="bg-white/5 text-white/60 uppercase text-[9px] font-bold">
                                        <tr>
                                            <th className="px-4 py-3">Héroe</th>
                                            <th className="px-2 py-3 text-center w-10">ID</th>
                                            <th className="px-4 py-3">Rango</th>
                                            <th className="px-4 py-3">Fortaleza</th>
                                            <th className="px-4 py-3">Ubicación</th>
                                            <th className="px-4 py-3 text-right">Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5 text-white/70">
                                        {heroes.map((hero: Hero) => (
                                            <tr key={hero.id} className="hover:bg-white/5 transition-colors group">
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="h-8 w-8 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary font-bold text-xs border border-brand-primary/30 shadow-inner group-hover:scale-110 transition-transform flex-shrink-0">
                                                            {hero.username.charAt(0).toUpperCase()}
                                                        </div>
                                                        <div className="truncate max-w-[120px]">
                                                            <p className="font-bold text-white text-xs group-hover:text-brand-primary transition-colors truncate">{hero.username}</p>
                                                            <p className="text-[9px] text-white/60 font-mono truncate">{hero.email}</p>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-2 py-3 text-center">
                                                    <span className="text-[10px] font-mono text-brand-primary/70 bg-brand-primary/10 px-1.5 py-0.5 rounded-md border border-brand-primary/20">{hero.id}</span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <select
                                                        value={hero.role}
                                                        onChange={(e) => handleUpdateRole(hero.id, e.target.value)}
                                                        className="bg-brand-primary/10 text-brand-primary text-[9px] uppercase font-black border border-brand-primary/20 rounded px-1.5 py-0.5 outline-none cursor-pointer hover:bg-brand-primary/30"
                                                    >
                                                        <option value="viewer" className="bg-black text-white">🛡️ Guardián</option>
                                                        <option value="admin" className="bg-black text-white">⚔️ Maestro</option>
                                                    </select>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center gap-1.5">
                                                        <Target className="h-3 w-3 text-brand-primary" />
                                                        <span className="font-black text-sm text-white">{hero.collection_size}</span>
                                                        <span className="text-[9px] text-brand-primary/50 font-black uppercase tracking-tighter">unidades</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className="text-[9px] font-bold text-white/65 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded-md truncate block max-w-[80px]">{hero.location}</span>
                                                </td>
                                                <td className="px-4 py-3 text-right">
                                                    <div className="flex items-center justify-end gap-1 transition-opacity">
                                                        <button
                                                            onClick={() => onIdentityChange?.(hero.id)}
                                                            title={`Asumir Identidad`}
                                                            className="h-7 w-7 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white border border-brand-primary/20 flex items-center justify-center transition-all"
                                                        >
                                                            <Repeat className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleExportExcelAdmin(hero.id)}
                                                            title="Bajar Excel"
                                                            className="h-7 w-7 rounded-lg bg-green-500/10 text-green-400 hover:bg-green-500 hover:text-white border border-green-500/20 flex items-center justify-center transition-all"
                                                        >
                                                            <FileSpreadsheet className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleExportSqliteAdmin(hero.id)}
                                                            title="Bajar SQLite"
                                                            className="h-7 w-7 rounded-lg bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500 hover:text-white border border-indigo-500/20 flex items-center justify-center transition-all"
                                                        >
                                                            <Database className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handlePasswordReset(hero.id)}
                                                            title="Reset Password"
                                                            className="h-7 w-7 rounded-lg bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 flex items-center justify-center transition-all"
                                                        >
                                                            <ShieldAlert className="h-3.5 w-3.5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleDeleteHero(hero.id, hero.username)}
                                                            title="Purgar"
                                                            className="h-7 w-7 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white border border-red-500/20 flex items-center justify-center transition-all"
                                                        >
                                                            <Trash2 className="h-3.5 w-3.5" />
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
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all">
                                <div className="flex items-center gap-4">
                                    <div className="bg-green-500/10 p-3 rounded-lg"><CheckCircle2 className="h-5 w-5 text-green-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Registro Abierto</h4>
                                        <p className="text-[10px] text-white/65">Permitir que nuevos usuarios se unan.</p>
                                    </div>
                                </div>
                                <div className="h-4 w-8 bg-brand-primary/30 rounded-full relative shadow-inner cursor-pointer"><div className="absolute right-1 top-1 h-2 w-2 bg-brand-primary rounded-full shadow-[0_0_8px_rgba(14,165,233,0.5)]"></div></div>
                            </div>
                            <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all opacity-50">
                                <div className="flex items-center gap-4">
                                    <div className="bg-red-500/10 p-3 rounded-lg"><Activity className="h-5 w-5 text-red-400" /></div>
                                    <div>
                                        <h4 className="text-sm font-bold text-white">Vigilancia de Sesión</h4>
                                        <p className="text-[10px] text-white/65">Cierre automático por inactividad.</p>
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
                                        <label className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Nombre de Usuario</label>
                                        <input type="text" disabled placeholder="Ej: He-Man" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Correo Electrónico</label>
                                        <input type="email" disabled placeholder="defensor@eternia.com" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Contraseña</label>
                                            <input type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Confirmar</label>
                                            <input type="password" disabled value="********" className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none" />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-white/65 uppercase tracking-widest pl-1">Rango del Héroe (Rol)</label>
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
                                        className="rounded-2xl border border-white/10 bg-white/5 py-4 text-xs font-black text-white/65 hover:bg-white/10 transition-all uppercase tracking-widest"
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

            {/* Modal de Auditoría IP Wallapop */}
            <AnimatePresence>
                {showIpLogsModal && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowIpLogsModal(false)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="relative w-full max-w-4xl max-h-[85vh] overflow-hidden rounded-[2.5rem] border border-white/10 bg-black/90 p-6 md:p-8 shadow-2xl backdrop-blur-3xl ring-1 ring-white/5 flex flex-col gap-6 text-white"
                        >
                            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-brand-primary/10 rounded-2xl border border-brand-primary/20">
                                        <Globe className="h-6 w-6 text-brand-primary" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-black uppercase tracking-widest text-white">Auditoría de Conectividad IP</h3>
                                        <p className="text-xs text-white/65 font-bold uppercase tracking-wider">Historial de WAF checks y bloqueos de Wallapop</p>
                                    </div>
                                </div>
                                <button
                                    onClick={handleDownloadIpLogs}
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
                                    onClick={() => setShowIpLogsModal(false)}
                                    className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all hover:scale-105 active:scale-95"
                                >
                                    Cerrar Portal
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Vintage Sword Light Ray Calibrator Modal */}
            {showCalibrator && (
                <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md p-4 flex justify-center items-start animate-in fade-in duration-300 custom-scrollbar">
                    <div className="relative w-full max-w-4xl my-8 md:my-12 rounded-[2.5rem] border border-amber-500/30 bg-[#0A0A0B] p-6 md:p-8 flex flex-col gap-6 shadow-[0_0_50px_rgba(245,158,11,0.2)]">
                        <div className="flex items-center gap-3">
                            <div className="p-3 rounded-xl bg-amber-500/10">
                                <Zap className="h-6 w-6 text-amber-500" />
                            </div>
                            <div>
                                <h4 className="text-2xl font-black text-white">Calibrador de Haces de Luz <span className="text-amber-500">Vintage</span></h4>
                                <p className="text-[10px] text-white/50 font-bold uppercase tracking-wider">Alinea los rayos de energía de Grayskull sobre la espada de He-Man</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center justify-center">
                            {/* Preview Area */}
                            <div className="flex flex-col items-center justify-center gap-4 bg-black/40 border border-white/5 p-6 rounded-3xl">
                                <span className="text-[10px] font-black uppercase tracking-widest text-amber-500/60">Simulador de Pantalla de Carga</span>
                                
                                <div className="relative w-64 h-64 border border-white/10 rounded-2xl overflow-hidden bg-[#050608] flex items-center justify-center shadow-inner">
                                    <PowerSwordLoader 
                                        isVintage={true} 
                                        disableRandom={true}
                                        size={250} 
                                        vintageGuardX={calibCoords.gX}
                                        vintageGuardY={calibCoords.gY}
                                        vintageTipX={calibCoords.tX}
                                        vintageTipY={calibCoords.tY}
                                        progress={parseFloat(localStorage.getItem('calib_test_progress') || '75')} 
                                    />
                                    
                                    {/* Overlay helper lines to visually debug guard & tip points */}
                                    <svg viewBox="0 0 250 250" className="absolute inset-0 w-full h-full pointer-events-none">
                                        {/* Guard center indicator */}
                                        <circle cx={calibCoords.gX} cy={calibCoords.gY} r="4" fill="#10B981" stroke="white" strokeWidth="1" />
                                        <text x={calibCoords.gX + 6} y={calibCoords.gY + 3} fill="#10B981" fontSize="8" fontWeight="bold">Empuñadura ({calibCoords.gX.toFixed(1)}, {calibCoords.gY.toFixed(1)})</text>
                                        
                                        {/* Tip indicator */}
                                        <circle cx={calibCoords.tX} cy={calibCoords.tY} r="4" fill="#EF4444" stroke="white" strokeWidth="1" />
                                        <text x={calibCoords.tX + 6} y={calibCoords.tY + 3} fill="#EF4444" fontSize="8" fontWeight="bold">Punta ({calibCoords.tX.toFixed(1)}, {calibCoords.tY.toFixed(1)})</text>
                                        
                                        {/* Axis line */}
                                        <line x1={calibCoords.gX} y1={calibCoords.gY} x2={calibCoords.tX} y2={calibCoords.tY} stroke="rgba(245,158,11,0.3)" strokeDasharray="3" strokeWidth="1.5" />
                                    </svg>
                                </div>
                                
                                <div className="w-full space-y-1">
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold">
                                        <span>PROGRESO DE PRUEBA</span>
                                        <span className="text-amber-500 font-mono">{localStorage.getItem('calib_test_progress') || '75'}%</span>
                                    </div>
                                    <input 
                                        type="range" 
                                        min="0" 
                                        max="100" 
                                        value={localStorage.getItem('calib_test_progress') || '75'}
                                        onChange={(e) => {
                                            localStorage.setItem('calib_test_progress', e.target.value);
                                            // Trigger state update to re-render preview
                                            setCalibCoords({ ...calibCoords });
                                        }}
                                        className="w-full accent-amber-500" 
                                    />
                                </div>
                            </div>

                            {/* Controls Area */}
                            <div className="space-y-6">
                                <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                                    <div className="flex items-center gap-2 text-[#10B981] font-bold text-xs uppercase tracking-widest">
                                        <div className="h-2 w-2 rounded-full bg-[#10B981]" />
                                        Punto de Empuñadura / Hilt (X, Y)
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Horizontal (X)</span>
                                                <span className="text-white font-mono">{calibCoords.gX}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={calibCoords.gX}
                                                onChange={(e) => setCalibCoords({ ...calibCoords, gX: parseFloat(e.target.value) })}
                                                className="w-full accent-green-500" 
                                            />
                                        </div>
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Vertical (Y)</span>
                                                <span className="text-white font-mono">{calibCoords.gY}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={calibCoords.gY}
                                                onChange={(e) => setCalibCoords({ ...calibCoords, gY: parseFloat(e.target.value) })}
                                                className="w-full accent-green-500" 
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                                    <div className="flex items-center gap-2 text-[#EF4444] font-bold text-xs uppercase tracking-widest">
                                        <div className="h-2 w-2 rounded-full bg-[#EF4444]" />
                                        Punto de la Punta / Tip (X, Y)
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Horizontal (X)</span>
                                                <span className="text-white font-mono">{calibCoords.tX}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={calibCoords.tX}
                                                onChange={(e) => setCalibCoords({ ...calibCoords, tX: parseFloat(e.target.value) })}
                                                className="w-full accent-red-500" 
                                            />
                                        </div>
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Vertical (Y)</span>
                                                <span className="text-white font-mono">{calibCoords.tY}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={calibCoords.tY}
                                                onChange={(e) => setCalibCoords({ ...calibCoords, tY: parseFloat(e.target.value) })}
                                                className="w-full accent-red-500" 
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 pt-2">
                                    <button
                                        onClick={handleResetCalib}
                                        className="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-white/70 hover:text-white hover:bg-white/5 font-black text-[10px] uppercase tracking-widest transition-all"
                                    >
                                        Restablecer
                                    </button>
                                    <button
                                        onClick={handleSaveCalib}
                                        className="flex-1 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-black font-black text-[10px] uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                                    >
                                        Guardar en Eternia
                                    </button>
                                    <button
                                        onClick={() => setShowCalibrator(false)}
                                        className="px-4 py-2.5 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 text-white font-black text-[10px] uppercase tracking-widest transition-all"
                                    >
                                        Cerrar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Skeletor Light Ray Calibrator Modal */}
            {showModernCalibrator && (
                <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md p-4 flex justify-center items-start animate-in fade-in duration-300 custom-scrollbar">
                    <div className="relative w-full max-w-4xl my-8 md:my-12 rounded-[2.5rem] border border-purple-500/30 bg-[#0A0A0B] p-6 md:p-8 flex flex-col gap-6 shadow-[0_0_50px_rgba(168,85,247,0.2)]">
                        <div className="flex items-center gap-3">
                            <div className="p-3 rounded-xl bg-purple-500/10">
                                <Zap className="h-6 w-6 text-purple-400 animate-pulse" />
                            </div>
                            <div>
                                <h4 className="text-2xl font-black text-white">Calibrador de Pantalla de Carga <span className="text-purple-400">Skeletor</span></h4>
                                <p className="text-[10px] text-white/50 font-bold uppercase tracking-wider">Alinea los rayos de energía de Grayskull sobre el báculo de Skeletor en la pantalla de carga</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center justify-center">
                            {/* Preview Area */}
                            <div className="flex flex-col items-center justify-center gap-4 bg-black/40 border border-white/5 p-6 rounded-3xl">
                                <span className="text-[10px] font-black uppercase tracking-widest text-purple-400/60">Simulador de Pantalla de Carga</span>
                                
                                <div className="relative w-64 h-64 border border-white/10 rounded-2xl overflow-hidden bg-[#050608] flex items-center justify-center shadow-inner">
                                    <PowerSwordLoader 
                                        isVintage={false} 
                                        isSkeletor={true}
                                        disableRandom={true}
                                        size={250} 
                                        skeletorGuardX={modernCoords.gX}
                                        skeletorGuardY={modernCoords.gY}
                                        skeletorTipX={modernCoords.tX}
                                        skeletorTipY={modernCoords.tY}
                                        progress={parseFloat(localStorage.getItem('calib_test_progress_modern') || '75')} 
                                    />
                                    
                                    {/* Overlay helper lines to visually debug guard & tip points */}
                                    <svg viewBox="0 0 250 250" className="absolute inset-0 w-full h-full pointer-events-none">
                                        {/* Guard center indicator */}
                                        <circle cx={modernCoords.gX} cy={modernCoords.gY} r="4" fill="#A855F7" stroke="white" strokeWidth="1" />
                                        <text x={modernCoords.gX + 6} y={modernCoords.gY + 3} fill="#A855F7" fontSize="8" fontWeight="bold">Empuñadura ({modernCoords.gX.toFixed(1)}, {modernCoords.gY.toFixed(1)})</text>
                                        
                                        {/* Tip indicator */}
                                        <circle cx={modernCoords.tX} cy={modernCoords.tY} r="4" fill="#A855F7" stroke="white" strokeWidth="1" />
                                        <text x={modernCoords.tX + 6} y={modernCoords.tY + 3} fill="#A855F7" fontSize="8" fontWeight="bold">Punta ({modernCoords.tX.toFixed(1)}, {modernCoords.tY.toFixed(1)})</text>
                                        
                                        {/* Axis line */}
                                        <line x1={modernCoords.gX} y1={modernCoords.gY} x2={modernCoords.tX} y2={modernCoords.tY} stroke="rgba(168,85,247,0.3)" strokeDasharray="3" strokeWidth="1.5" />
                                    </svg>
                                </div>
                                
                                <div className="w-full space-y-1">
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold">
                                        <span>PROGRESO DE PRUEBA</span>
                                        <span className="text-purple-400 font-mono">{localStorage.getItem('calib_test_progress_modern') || '75'}%</span>
                                    </div>
                                    <input 
                                        type="range" 
                                        min="0" 
                                        max="100" 
                                        value={localStorage.getItem('calib_test_progress_modern') || '75'}
                                        onChange={(e) => {
                                            localStorage.setItem('calib_test_progress_modern', e.target.value);
                                            // Trigger state update to re-render preview
                                            setModernCoords({ ...modernCoords });
                                        }}
                                        className="w-full accent-purple-500" 
                                    />
                                </div>
                            </div>

                            {/* Controls Area */}
                            <div className="space-y-6">
                                <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                                    <div className="flex items-center gap-2 text-purple-400 font-bold text-xs uppercase tracking-widest">
                                        <div className="h-2 w-2 rounded-full bg-purple-400" />
                                        Punto de Empuñadura (X, Y)
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Horizontal (X)</span>
                                                <span className="text-white font-mono">{modernCoords.gX}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={modernCoords.gX}
                                                onChange={(e) => setModernCoords({ ...modernCoords, gX: parseFloat(e.target.value) })}
                                                className="w-full accent-purple-500" 
                                            />
                                        </div>
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Vertical (Y)</span>
                                                <span className="text-white font-mono">{modernCoords.gY}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={modernCoords.gY}
                                                onChange={(e) => setModernCoords({ ...modernCoords, gY: parseFloat(e.target.value) })}
                                                className="w-full accent-purple-500" 
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                                    <div className="flex items-center gap-2 text-purple-400 font-bold text-xs uppercase tracking-widest">
                                        <div className="h-2 w-2 rounded-full bg-purple-400" />
                                        Punto de la Punta (X, Y)
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Horizontal (X)</span>
                                                <span className="text-white font-mono">{modernCoords.tX}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={modernCoords.tX}
                                                onChange={(e) => setModernCoords({ ...modernCoords, tX: parseFloat(e.target.value) })}
                                                className="w-full accent-purple-500" 
                                            />
                                        </div>
                                        <div>
                                            <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                                <span>Vertical (Y)</span>
                                                <span className="text-white font-mono">{modernCoords.tY}px</span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min="0" 
                                                max="250" 
                                                step="0.5"
                                                value={modernCoords.tY}
                                                onChange={(e) => setModernCoords({ ...modernCoords, tY: parseFloat(e.target.value) })}
                                                className="w-full accent-purple-500" 
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 pt-2">
                                    <button
                                        onClick={handleResetModernCalib}
                                        className="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-white/70 hover:text-white hover:bg-white/5 font-black text-[10px] uppercase tracking-widest transition-all"
                                    >
                                        Restablecer
                                    </button>
                                    <button
                                        onClick={handleSaveModernCalib}
                                        className="flex-1 px-4 py-2.5 rounded-xl bg-purple-500 hover:bg-purple-600 text-black font-black text-[10px] uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(168,85,247,0.2)]"
                                    >
                                        Guardar en Eternia
                                    </button>
                                    <button
                                        onClick={() => setShowModernCalibrator(false)}
                                        className="px-4 py-2.5 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 text-white font-black text-[10px] uppercase tracking-widest transition-all"
                                    >
                                        Cerrar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div >
    );
};

export default Config;
