import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Activity, Clock, AlertCircle, CheckCircle2, RefreshCw, Terminal, Settings, Users, ShieldAlert, Trash2, Zap, History, Database, Download, Globe, Package, Swords, Shield, Search, Sparkles, Home, Wifi, CloudLightning, Cookie, Copy, Gift, Compass, MousePointer, ArrowDown, BarChart2, FileText, XCircle, Keyboard, ChevronsDown, Flag, Hexagon, Network, Archive, CornerDownRight, GitMerge, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { resetSmartMatches, runScrapers, stopScrapers, getScraperLogs, type ScraperExecutionLog, getWallapopIpLogs, downloadWallapopIpLogs, type WallapopIpLog, runWallaManualHtml } from '../api/purgatory';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { parseUtcDate } from '../utils/dateUtils';
import WallapopImporter from '../components/admin/WallapopImporter';
import WallapopNexusBridge from '../components/admin/WallapopNexusBridge';
import { getDashboardMatchStats } from '../api/dashboard';
import AddUserModal from '../components/config/AddUserModal';
import ResetConfirmModal from '../components/config/ResetConfirmModal';
import IpLogsModal from '../components/config/IpLogsModal';
import VintageCalibratorModal from '../components/config/VintageCalibratorModal';
import ModernCalibratorModal from '../components/config/ModernCalibratorModal';
import UsersTab from '../components/config/UsersTab';
import SystemTab from '../components/config/SystemTab';
import { getParsedMetrics, getStepperStatus, CHART_COLORS } from '../components/config/configHelpers';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip as RechartsTooltip
} from 'recharts';


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
    getSystemSwordConfigs,
    saveSystemSwordConfigs,
    runSystemMaintenance,
    type ScraperStatus,
    type Hero,
    getTemporaryProducts,
    mergeProducts,
    type TemporaryProduct
} from '../api/admin';

interface ConfigProps {
    user?: Hero | null;
    onUserUpdate?: () => void;
    onIdentityChange?: (targetId: number) => void;
}

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
    const [logFilter, setLogFilter] = useState<'all' | 'error'>('all');
    const [targetLogId, setTargetLogId] = useState<number | null>(null);
    const [copied, setCopied] = useState(false);
    const [wallaManualLoading, setWallaManualLoading] = useState(false);

    const [showIpLogsModal, setShowIpLogsModal] = useState(false);
    const [ipLogs, setIpLogs] = useState<WallapopIpLog[]>([]);
    const [loadingIpLogs, setLoadingIpLogs] = useState(false);

    const [, setLocalImagesEnabled] = useState(() => localStorage.getItem('use_local_images') === 'true');
    const [downloadStatus, setDownloadStatus] = useState({ active: false, total: 0, current: 0, errors: 0, last_error: null as string | null });
    const [cachedImagesCount, setCachedImagesCount] = useState(0);
    const [syncingExcel, setSyncingExcel] = useState(false);
    const [runningMaintenance, setRunningMaintenance] = useState(false);
    const cancelDownloadRef = React.useRef(false);
    const [forceRender, setForceRender] = useState(0);

    useEffect(() => {
        // Lectura defensiva para TypeScript
        void forceRender;
    }, [forceRender]);

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

    // Nexo de Fusión Divina States
    const [temporaryProducts, setTemporaryProducts] = useState<TemporaryProduct[]>([]);
    const [loadingTemporary, setLoadingTemporary] = useState(false);
    const [showMergePanel, setShowMergePanel] = useState(false);
    const [mergeSource, setMergeSource] = useState<any>(null);
    const [mergeTarget, setMergeTarget] = useState<any>(null);
    const [mergeSearchQuery, setMergeSearchQuery] = useState('');
    const [mergeTargetSuggestions, setMergeTargetSuggestions] = useState<any[]>([]);
    const [searchingTarget, setSearchingTarget] = useState(false);
    const [isFusing, setIsFusing] = useState(false);
    const [freeMergeMode, setFreeMergeMode] = useState(false);
    const [freeMergeSourceQuery, setFreeMergeSourceQuery] = useState('');
    const [freeMergeSourceSuggestions, setFreeMergeSourceSuggestions] = useState<any[]>([]);

    const isAdmin = user?.role === 'admin' || user?.username === 'David';
    const [showShowcaseGuide, setShowShowcaseGuide] = useState(false);

    const handleCardClick = (shop: string) => {
        localStorage.setItem('catalog_shop_filter', shop);
        window.dispatchEvent(new CustomEvent('navigate-to-catalog', { detail: { shop } }));
    };

    useEffect(() => {
        const loadConfigs = async () => {
            let loadedRemote = false;
            try {
                const configs = await getSystemSwordConfigs();
                if (configs && Object.keys(configs).length > 0) {
                    if (configs.vintage_sword_coords) {
                        setCalibCoords(configs.vintage_sword_coords);
                    }
                    if (configs.skeletor_sword_coords) {
                        setModernCoords(configs.skeletor_sword_coords);
                    }
                    loadedRemote = true;
                }
            } catch (e) {
                console.error("Failed to load remote configs", e);
            }

            if (!loadedRemote) {
                const storedVintage = localStorage.getItem('vintage_sword_coords');
                if (storedVintage) {
                    try { setCalibCoords(JSON.parse(storedVintage)); } catch(e){}
                }
                const storedSkeletor = localStorage.getItem('skeletor_sword_coords');
                if (storedSkeletor) {
                    try { setModernCoords(JSON.parse(storedSkeletor)); } catch(e){}
                }
            }
        };
        loadConfigs();
    }, []);

    const handleSaveCalib = async () => {
        localStorage.setItem('vintage_sword_coords', JSON.stringify(calibCoords));
        if (isAdmin) {
            try {
                await saveSystemSwordConfigs({
                    vintage_sword_coords: calibCoords,
                    skeletor_sword_coords: modernCoords
                });
            } catch (e) {
                console.error("Error saving global vintage coords", e);
                alert("Error al guardar en el servidor global. Se guardó localmente.");
            }
        }
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

    const handleSaveModernCalib = async () => {
        localStorage.setItem('skeletor_sword_coords', JSON.stringify(modernCoords));
        if (isAdmin) {
            try {
                await saveSystemSwordConfigs({
                    vintage_sword_coords: calibCoords,
                    skeletor_sword_coords: modernCoords
                });
            } catch (e) {
                console.error("Error saving global skeletor coords", e);
                alert("Error al guardar en el servidor global. Se guardó localmente.");
            }
        }
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
            const [s, u, al, h, ms, tempProducts] = await Promise.all([
                getScrapersStatus().catch((e: any) => { console.error("Scrapers error:", e); return []; }),
                getUserSettings(activeUserId).catch((e: any) => { console.error("User settings error:", e); return null; }),
                getScraperLogs().catch((e: any) => { console.error("Logs error:", e); return []; }),
                getHeroes().catch((e: any) => { console.error("Heroes list error:", e); return []; }),
                getDashboardMatchStats(activeUserId).catch((e: any) => { console.error("Match stats error:", e); return []; }),
                isAdmin ? getTemporaryProducts().catch((e: any) => { console.error("Temp products error:", e); return []; }) : Promise.resolve([])
            ]);

            setStatuses(s || []);
            if (u) setUserSettings(u);
            setAdvancedLogs(al || []);
            setHeroes(h || []);
            setMatchStats(ms || []);
            setTemporaryProducts(tempProducts || []);

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

    const handleCopyLogs = () => {
        const textToCopy = [
            selectedLog?.error_message ? `ERROR CRÍTICO DETECTADO:\n${selectedLog.error_message}\n\n=== LOG COMPLETO ===\n` : '',
            selectedLog?.logs || ''
        ].join('');
        
        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
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

    // Nexo de Fusión Divina Handlers
    const handleConfirmMerge = async () => {
        if (!mergeSource || !mergeTarget) return;
        setIsFusing(true);
        try {
            const res = await mergeProducts(mergeSource.id, mergeTarget.id);
            alert(`🎉 Fusión exitosa: ${res.message}`);
            setShowMergePanel(false);
            setMergeSource(null);
            setMergeTarget(null);
            setMergeSearchQuery('');
            setMergeTargetSuggestions([]);
            fetchData();
        } catch (e: any) {
            const msg = e.response?.data?.detail || e.message || String(e);
            alert(`❌ Error al fusionar reliquias: ${msg}`);
        } finally {
            setIsFusing(false);
        }
    };

    // Debounce for target suggestions search
    useEffect(() => {
        if (mergeSearchQuery.trim().length < 2) {
            setMergeTargetSuggestions([]);
            return;
        }

        const delayDebounce = setTimeout(async () => {
            setSearchingTarget(true);
            try {
                const res = await axios.get(`/api/products/search?q=${mergeSearchQuery}`);
                const filtered = (res.data || []).filter((p: any) => p.id !== mergeSource?.id);
                setMergeTargetSuggestions(filtered);
            } catch (e) {
                console.error("Error searching target product", e);
            } finally {
                setSearchingTarget(false);
            }
        }, 300);

        return () => clearTimeout(delayDebounce);
    }, [mergeSearchQuery, mergeSource]);

    // Debounce for source suggestions search (free merge)
    useEffect(() => {
        if (freeMergeSourceQuery.trim().length < 2) {
            setFreeMergeSourceSuggestions([]);
            return;
        }

        const delayDebounce = setTimeout(async () => {
            try {
                const res = await axios.get(`/api/products/search?q=${freeMergeSourceQuery}`);
                setFreeMergeSourceSuggestions(res.data || []);
            } catch (e) {
                console.error("Error searching source product", e);
            }
        }, 300);

        return () => clearTimeout(delayDebounce);
    }, [freeMergeSourceQuery]);

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

    const runWallaManualHtmlMutation = useMutation({
        mutationFn: runWallaManualHtml,
        onMutate: () => {
            setWallaManualLoading(true);
        },
        onSuccess: (data: any) => {
            alert(`🎉 WallaManual: Sincronización HTML exitosa.\n\n- Ofertas encontradas: ${data.total_found}\n- Ofertas omitidas (ya catalogadas/descartadas): ${data.total_skipped}\n- Ofertas insertadas en Purgatorio: ${data.total_inserted}`);
            queryClient.invalidateQueries({ queryKey: ['scrapers-status'] });
            fetchData();
        },
        onError: (error: any) => {
            const detail = error.response?.data?.detail || error.message || String(error);
            alert(`❌ WallaManual: Error al procesar el HTML.\nDetalle: ${detail}`);
        },
        onSettled: () => {
            setWallaManualLoading(false);
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

    const handleRunMaintenance = async () => {
        if (!confirm('🧹 MANTENIMIENTO DEL ORÁCULO:\n\nEsta acción ejecutará la consolidación de precios históricos por mes, y purgará los registros y logs redundantes de la base de datos de producción.\n\n¿Deseas iniciar la incursión de mantenimiento FinOps?')) return;
        
        setRunningMaintenance(true);
        try {
            const res = await runSystemMaintenance();
            alert(`🧹 Purificación FinOps Iniciada:\n\n${res.message}`);
        } catch (error: any) {
            console.error('Error running database maintenance:', error);
            const detail = error.response?.data?.detail 
                || error.message 
                || "Fallo en la comunicación con el servidor.";
            alert(`❌ Error en Mantenimiento: ${detail}`);
        } finally {
            setRunningMaintenance(false);
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

                                                        // Parse emojis to Lucide icons
                                                        const emojiMap: { [key: string]: React.ReactNode } = {
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
                                                            '⚡️': <Zap className="inline h-3 w-3 mr-1 text-yellow-400 align-middle" />
                                                        };
                                                        
                                                        const regex = /(🚀|⚔️|🔎|🔍|🔮|⚡|⚠️|🌐|🏠|🛡️|⚙️|📥|📦|📡|🌩️|🕵️‍♂️|🕵️|🧭|🖱️|🍪|💾|✅|⌛|🎉|🎁|🕸️|🧹|❌|🚫|⌨️|📄|⏬|⬇️|📊|↪️|🏁|🔄|🟢|🗄️|⎔|⏣|⚡️)/g;
                                                        const parts = line.split(regex);

                                                        return (
                                                            <div key={i} className={`flex gap-4 group/line ${isError ? 'text-red-400' : isSuccess ? 'text-green-400' : isWarning ? 'text-yellow-400' : 'text-white/60'}`}>
                                                                <span className="text-white/10 select-none w-8 text-right group-hover/line:text-white/60 transition-colors">{String(i + 1).padStart(3, '0')}</span>
                                                                <p className="break-all whitespace-pre-wrap flex-1 align-middle">
                                                                    {parts.map((part, idx) => emojiMap[part] ? <React.Fragment key={idx}>{emojiMap[part]}</React.Fragment> : part)}
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
                ) : activeTab === 'inventory' ? (
                    (() => {
                        const totalMatches = matchStats?.reduce((sum, item) => sum + item.count, 0) || 0;
                        const sortedMatchStats = matchStats ? [...matchStats].sort((a, b) => b.count - a.count) : [];
                        const chartData = sortedMatchStats.map(item => ({
                            name: item.shop,
                            value: item.count
                        }));

                        return (
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

                                <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 md:gap-8">
                                    {/* Left Column: Sorted market cards grid */}
                                    <div className="xl:col-span-7 rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 space-y-6">
                                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-2">Desglose de Conquistas</h3>
                                        
                                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
                                            {sortedMatchStats.map((item) => (
                                                <button
                                                    key={item.shop}
                                                    onClick={() => handleCardClick(item.shop)}
                                                    className="flex flex-col gap-1 rounded-2xl bg-white/[0.03] p-3 md:p-4 border border-white/5 text-left hover:bg-white/[0.08] hover:border-white/10 active:scale-[0.98] transition-all cursor-pointer w-full group outline-none focus:ring-1 focus:ring-brand-primary/50"
                                                >
                                                    <span className="text-[8px] md:text-[9px] font-black uppercase text-white/60 tracking-widest truncate w-full">{item.shop}</span>
                                                    <span className="text-xl md:text-2xl font-black text-white">{item.count}</span>
                                                </button>
                                            ))}
                                            {sortedMatchStats.length === 0 && (
                                                <div className="col-span-full py-6 text-center text-white/60 uppercase font-black text-[9px] tracking-widest">
                                                    Sin estadísticas de mercado
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Right Column: Beautiful Doughnut Chart */}
                                    <div className="xl:col-span-5 rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 flex flex-col justify-between space-y-6 min-h-[350px]">
                                        <div>
                                            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-1">Cuota de Mercado</h3>
                                            <p className="text-[9px] font-bold text-white/50 uppercase tracking-wider leading-relaxed">Representación de la presencia de tus reliquias en diferentes portales.</p>
                                        </div>

                                        {sortedMatchStats.length > 0 ? (
                                            <>
                                                <div className="relative flex-1 flex items-center justify-center min-h-[260px]">
                                                    <ResponsiveContainer width="100%" height={260}>
                                                        <PieChart>
                                                            <Pie
                                                                data={chartData}
                                                                cx="50%"
                                                                cy="50%"
                                                                innerRadius={70}
                                                                outerRadius={95}
                                                                paddingAngle={3}
                                                                dataKey="value"
                                                            >
                                                                {chartData.map((_, index) => (
                                                                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                                                ))}
                                                            </Pie>
                                                            <RechartsTooltip
                                                                content={({ active, payload }: any) => {
                                                                    if (active && payload && payload.length) {
                                                                        return (
                                                                            <div className="bg-black/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md flex flex-col gap-0.5 select-none">
                                                                                <span className="text-[9px] font-black uppercase tracking-widest text-white/50">
                                                                                    {payload[0].name}
                                                                                </span>
                                                                                <span className="text-xs font-black text-brand-primary uppercase tracking-wider">
                                                                                    {payload[0].value} Reliquias
                                                                                </span>
                                                                            </div>
                                                                        );
                                                                    }
                                                                    return null;
                                                                }}
                                                            />
                                                        </PieChart>
                                                    </ResponsiveContainer>
                                                    <div className="absolute flex flex-col items-center justify-center pointer-events-none">
                                                        <span className="text-[9px] font-black uppercase tracking-[0.2em] text-white/30">Total</span>
                                                        <span className="text-3xl font-black text-white tracking-tighter leading-none my-1">{totalMatches}</span>
                                                        <span className="text-[8px] font-bold uppercase tracking-wider text-brand-primary">Vinculadas</span>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-2 mt-2">
                                                    {sortedMatchStats.slice(0, 6).map((item, index) => {
                                                        const pct = totalMatches > 0 ? ((item.count / totalMatches) * 100).toFixed(1) : '0.0';
                                                        return (
                                                            <div key={item.shop} className="flex items-center gap-2 bg-white/[0.01] border border-white/[0.03] px-3 py-1.5 rounded-xl min-w-0">
                                                                <span 
                                                                    className="w-2.5 h-2.5 rounded-full shrink-0" 
                                                                    style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} 
                                                                />
                                                                <div className="flex flex-col min-w-0 flex-1">
                                                                    <span className="text-[8px] font-black uppercase text-white/50 truncate tracking-wider">{item.shop}</span>
                                                                    <span className="text-[10px] font-black text-white leading-tight">{pct}% <span className="text-[8px] font-bold text-white/40">({item.count})</span></span>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </>
                                        ) : (
                                            <div className="flex-1 flex flex-col items-center justify-center text-white/20 uppercase font-black text-[9px] tracking-widest">
                                                Sin datos de mercado para graficar
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {isAdmin && (
                                    <div className="col-span-full rounded-2xl md:rounded-[2.5rem] border border-white/5 bg-black/50 backdrop-blur-md p-4 md:p-8 space-y-6 mt-6">
                                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/10 pb-4">
                                            <div>
                                                <h3 className="text-lg font-black uppercase tracking-[0.15em] text-white flex items-center gap-2">
                                                    <GitMerge className="h-5 w-5 text-amber-500" />
                                                    Nexo de Fusión Divina
                                                </h3>
                                                <p className="text-[11px] text-white/50 uppercase tracking-wider font-bold mt-1">
                                                    Consolida el catálogo unificando reliquias temporales con oficiales o fusionando duplicados.
                                                </p>
                                            </div>
                                            
                                            {/* Selector de Modo */}
                                            <div className="flex bg-white/[0.03] border border-white/10 rounded-xl p-1 shrink-0">
                                                <button
                                                    onClick={() => {
                                                        setFreeMergeMode(false);
                                                        setMergeSource(null);
                                                        setMergeTarget(null);
                                                        setMergeSearchQuery('');
                                                    }}
                                                    className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${!freeMergeMode ? 'bg-amber-500 text-black shadow-md' : 'text-white/60 hover:text-white'}`}
                                                >
                                                    ⚡ Fusión Rápida (Customs)
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setFreeMergeMode(true);
                                                        setMergeSource(null);
                                                        setMergeTarget(null);
                                                        setMergeSearchQuery('');
                                                        setFreeMergeSourceQuery('');
                                                    }}
                                                    className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${freeMergeMode ? 'bg-amber-500 text-black shadow-md' : 'text-white/60 hover:text-white'}`}
                                                >
                                                    🔮 Fusión Libre (Manual)
                                                </button>
                                            </div>
                                        </div>

                                        {/* Modos */}
                                        {!freeMergeMode ? (
                                            /* MODO FUSIÓN RÁPIDA (LISTA DE TEMPORALES) */
                                            <div className="space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[9px] font-black uppercase text-white/45 tracking-wider">
                                                        Reliquias Temporales Detectadas ({temporaryProducts.length})
                                                    </span>
                                                    <button 
                                                        onClick={async () => {
                                                            setLoadingTemporary(true);
                                                            try {
                                                                const res = await getTemporaryProducts();
                                                                setTemporaryProducts(res);
                                                            } catch (e) {
                                                                console.error(e);
                                                            } finally {
                                                                setLoadingTemporary(false);
                                                            }
                                                        }}
                                                        className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:text-white flex items-center gap-1"
                                                    >
                                                        <RefreshCw className={`h-3 w-3 ${loadingTemporary ? 'animate-spin' : ''}`} />
                                                        Recargar Lista
                                                    </button>
                                                </div>

                                                {temporaryProducts.length === 0 ? (
                                                    <div className="rounded-2xl border border-dashed border-white/10 p-8 flex flex-col items-center justify-center text-center space-y-3 bg-white/[0.01]">
                                                        <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                                            <CheckCircle2 className="h-5 w-5 text-green-400" />
                                                        </div>
                                                        <div>
                                                            <p className="text-xs font-black text-white uppercase tracking-wider">Nexo en Armonía</p>
                                                            <p className="text-[10px] text-white/40 uppercase tracking-widest mt-1">No hay figuras temporales (VINT-/ORIG-) pendientes de consolidación.</p>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                                        {temporaryProducts.map(p => {
                                                            const isVintage = p.figure_id.startsWith('VINT');
                                                            return (
                                                                <div key={p.id} className="glass p-4 rounded-2xl border border-white/5 bg-white/[0.02] flex items-center justify-between gap-4 hover:border-white/10 transition-colors">
                                                                    <div className="flex items-center gap-3 min-w-0">
                                                                        <div className="h-12 w-12 rounded-xl overflow-hidden bg-black/40 border border-white/10 shrink-0 flex items-center justify-center">
                                                                            {p.image_url ? (
                                                                                <img src={p.image_url} alt={p.name} className="h-full w-full object-cover" />
                                                                            ) : (
                                                                                <Package className="h-5 w-5 text-white/20" />
                                                                            )}
                                                                        </div>
                                                                        <div className="min-w-0">
                                                                            <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{p.name}</h4>
                                                                            <div className="flex items-center gap-1.5 mt-1">
                                                                                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded tracking-widest uppercase font-mono ${isVintage ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'}`}>
                                                                                    {p.figure_id}
                                                                                </span>
                                                                                <span className="text-[8px] font-bold text-white/45 uppercase tracking-wider">
                                                                                    {p.offer_count} offers • {p.collection_count} coll
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                    <button
                                                                        onClick={() => {
                                                                            setMergeSource(p);
                                                                            setMergeTarget(null);
                                                                            setMergeSearchQuery('');
                                                                            setShowMergePanel(true);
                                                                        }}
                                                                        className="bg-brand-primary/10 hover:bg-brand-primary text-brand-primary hover:text-black border border-brand-primary/20 px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all shrink-0 flex items-center gap-1 cursor-pointer"
                                                                    >
                                                                        <GitMerge className="h-3 w-3" />
                                                                        Unificar
                                                                    </button>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            /* MODO FUSIÓN LIBRE (BUSCADOR DUAL) */
                                            <div className="space-y-4">
                                                <p className="text-[10px] text-white/50 uppercase tracking-wider leading-relaxed">
                                                    Selecciona libremente cualquier figura de catálogo como origen y destino. Ideal para unificar duplicados oficiales con IDs diferentes.
                                                </p>
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
                                                    {/* Buscador Origen */}
                                                    <div className="space-y-2 relative">
                                                        <label className="text-[9px] font-black uppercase tracking-widest text-white/40">1. Seleccionar Figura Origen (Será Eliminada)</label>
                                                        {mergeSource ? (
                                                            <div className="glass p-4 rounded-2xl border border-red-500/25 bg-red-500/5 flex items-center justify-between">
                                                                <div className="flex items-center gap-3">
                                                                    <div className="h-10 w-10 rounded-xl overflow-hidden bg-black/40 border border-white/10 flex items-center justify-center">
                                                                        {mergeSource.image_url ? (
                                                                            <img src={mergeSource.image_url} alt={mergeSource.name} className="h-full w-full object-cover" />
                                                                        ) : (
                                                                            <Package className="h-4 w-4 text-white/20" />
                                                                        )}
                                                                    </div>
                                                                    <div>
                                                                        <h4 className="text-xs font-black text-white uppercase tracking-wider">{mergeSource.name}</h4>
                                                                        <span className="text-[8px] font-mono text-white/60 tracking-wider bg-white/10 px-1.5 py-0.5 rounded">{mergeSource.figure_id || `#${mergeSource.id}`}</span>
                                                                    </div>
                                                                </div>
                                                                <button 
                                                                    onClick={() => setMergeSource(null)}
                                                                    className="text-[9px] font-black uppercase text-red-400 hover:text-white cursor-pointer"
                                                                >
                                                                    Remover
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <div className="relative">
                                                                <input
                                                                    type="text"
                                                                    value={freeMergeSourceQuery}
                                                                    onChange={(e) => setFreeMergeSourceQuery(e.target.value)}
                                                                    placeholder="Escribe el nombre de la figura origen..."
                                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary transition-all"
                                                                />
                                                                {freeMergeSourceQuery.trim().length > 1 && freeMergeSourceSuggestions.length > 0 && (
                                                                    <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-2xl max-h-48 overflow-y-auto shadow-2xl custom-scrollbar">
                                                                        {freeMergeSourceSuggestions.map((p: any) => (
                                                                            <div
                                                                                key={p.id}
                                                                                onClick={() => {
                                                                                    setMergeSource(p);
                                                                                    setFreeMergeSourceQuery('');
                                                                                    setFreeMergeSourceSuggestions([]);
                                                                                }}
                                                                                className="px-4 py-2.5 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                                                            >
                                                                                {p.name} <span className="opacity-45 ml-2 font-mono text-[10px]">#{p.figure_id}</span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Buscador Destino */}
                                                    <div className="space-y-2 relative">
                                                        <label className="text-[9px] font-black uppercase tracking-widest text-white/40">2. Seleccionar Figura Destino (Conservada)</label>
                                                        {mergeTarget ? (
                                                            <div className="glass p-4 rounded-2xl border border-green-500/25 bg-green-500/5 flex items-center justify-between">
                                                                <div className="flex items-center gap-3">
                                                                    <div className="h-10 w-10 rounded-xl overflow-hidden bg-black/40 border border-white/10 flex items-center justify-center">
                                                                        {mergeTarget.image_url ? (
                                                                            <img src={mergeTarget.image_url} alt={mergeTarget.name} className="h-full w-full object-cover" />
                                                                        ) : (
                                                                            <Package className="h-4 w-4 text-white/20" />
                                                                        )}
                                                                    </div>
                                                                    <div>
                                                                        <h4 className="text-xs font-black text-white uppercase tracking-wider">{mergeTarget.name}</h4>
                                                                        <span className="text-[8px] font-mono text-white/60 tracking-wider bg-white/10 px-1.5 py-0.5 rounded">{mergeTarget.figure_id || `#${mergeTarget.id}`}</span>
                                                                    </div>
                                                                </div>
                                                                <button 
                                                                    onClick={() => setMergeTarget(null)}
                                                                    className="text-[9px] font-black uppercase text-green-400 hover:text-white cursor-pointer"
                                                                >
                                                                    Remover
                                                                </button>
                                                            </div>
                                                        ) : (
                                                            <div className="relative">
                                                                <input
                                                                    type="text"
                                                                    value={mergeSearchQuery}
                                                                    onChange={(e) => setMergeSearchQuery(e.target.value)}
                                                                    placeholder="Escribe el nombre de la figura destino..."
                                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary transition-all"
                                                                />
                                                                {mergeSearchQuery.trim().length > 1 && mergeTargetSuggestions.length > 0 && (
                                                                    <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-2xl max-h-48 overflow-y-auto shadow-2xl custom-scrollbar">
                                                                        {mergeTargetSuggestions.map((p: any) => (
                                                                            <div
                                                                                key={p.id}
                                                                                onClick={() => {
                                                                                    setMergeTarget(p);
                                                                                    setMergeSearchQuery('');
                                                                                    setMergeTargetSuggestions([]);
                                                                                }}
                                                                                className="px-4 py-2.5 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                                                            >
                                                                                {p.name} <span className="opacity-45 ml-2 font-mono text-[10px]">#{p.figure_id}</span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* PANEL CONFIRMACIÓN DE FUSIÓN */}
                                        {mergeSource && (showMergePanel || mergeTarget) && (
                                            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-4">
                                                <div className="flex items-center justify-between border-b border-white/5 pb-2">
                                                    <span className="text-[10px] font-black uppercase text-brand-primary tracking-wider">Flujo de Fusión Divina</span>
                                                    <button 
                                                        onClick={() => {
                                                            setShowMergePanel(false);
                                                            setMergeSource(null);
                                                            setMergeTarget(null);
                                                            setMergeSearchQuery('');
                                                        }}
                                                        className="text-[9px] font-black uppercase text-white/40 hover:text-white cursor-pointer"
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>

                                                <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-4">
                                                    {/* Origen */}
                                                    <div className="glass p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-center min-w-[200px] max-w-[250px]">
                                                        <span className="text-[8px] font-black uppercase tracking-widest text-red-400 block mb-1">ORIGEN (SE ELIMINA)</span>
                                                        <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{mergeSource.name}</h4>
                                                        <span className="text-[8px] font-mono text-white/50 mt-1 inline-block bg-white/10 px-1 py-0.5 rounded">{mergeSource.figure_id || `#${mergeSource.id}`}</span>
                                                    </div>

                                                    <div className="flex flex-col items-center">
                                                        <ArrowRight className="h-6 w-6 text-brand-primary animate-pulse hidden sm:block" />
                                                        <ArrowDown className="h-6 w-6 text-brand-primary animate-pulse sm:hidden" />
                                                    </div>

                                                    {/* Destino */}
                                                    <div className="min-w-[200px] max-w-[250px] space-y-2">
                                                        {mergeTarget ? (
                                                            <div className="glass p-4 rounded-xl border border-green-500/20 bg-green-500/5 text-center">
                                                                <span className="text-[8px] font-black uppercase tracking-widest text-green-400 block mb-1">DESTINO (SE CONSERVA)</span>
                                                                <h4 className="text-xs font-black text-white truncate uppercase tracking-wider">{mergeTarget.name}</h4>
                                                                <span className="text-[8px] font-mono text-white/50 mt-1 inline-block bg-white/10 px-1 py-0.5 rounded">{mergeTarget.figure_id || `#${mergeTarget.id}`}</span>
                                                            </div>
                                                        ) : (
                                                            <div className="relative">
                                                                <label className="text-[8px] font-black uppercase tracking-widest text-white/40 block mb-1">Buscar Destino</label>
                                                                <input
                                                                    type="text"
                                                                    value={mergeSearchQuery}
                                                                    onChange={(e) => setMergeSearchQuery(e.target.value)}
                                                                    placeholder="Buscar destino..."
                                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white placeholder-white/20 focus:outline-none focus:border-brand-primary"
                                                                />
                                                                {searchingTarget && <span className="text-[8px] text-white/50 uppercase tracking-widest mt-1 block">Buscando...</span>}
                                                                
                                                                {mergeSearchQuery.trim().length > 1 && mergeTargetSuggestions.length > 0 && (
                                                                    <div className="absolute z-50 w-full mt-1 bg-black/95 border border-white/10 rounded-xl max-h-36 overflow-y-auto shadow-2xl custom-scrollbar">
                                                                        {mergeTargetSuggestions.map((p: any) => (
                                                                            <div
                                                                                key={p.id}
                                                                                onClick={() => {
                                                                                    setMergeTarget(p);
                                                                                    setMergeSearchQuery('');
                                                                                    setMergeTargetSuggestions([]);
                                                                                }}
                                                                                className="px-3 py-2 hover:bg-white/5 text-[11px] text-white/70 hover:text-white cursor-pointer font-bold border-b border-white/5 last:border-0"
                                                                            >
                                                                                {p.name} <span className="opacity-40 text-[9px] font-mono">#{p.figure_id}</span>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                                {mergeTarget && (
                                                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/25 space-y-3">
                                                        <p className="text-[10px] text-red-400 font-bold uppercase leading-normal">
                                                            ⚠️ ADVERTENCIA CRÍTICA: Al fusionar, se transferirán de forma atómica todas las ofertas, dueños de la colección, alias y alertas a '{mergeTarget.name}'. El ítem '{mergeSource.name}' ({mergeSource.figure_id || `#${mergeSource.id}`}) será permanentemente destruido. Las ofertas se ajustarán a {mergeTarget.is_vintage ? 'Vintage' : 'Nueva Eternia'}.
                                                        </p>
                                                        
                                                        <div className="flex gap-3 justify-end pt-2">
                                                            <button
                                                                onClick={() => {
                                                                    setShowMergePanel(false);
                                                                    setMergeSource(null);
                                                                    setMergeTarget(null);
                                                                    setMergeSearchQuery('');
                                                                }}
                                                                className="px-4 py-2 border border-white/10 rounded-xl text-[10px] font-black uppercase text-white/60 hover:text-white cursor-pointer"
                                                            >
                                                                Cancelar
                                                            </button>
                                                            <button
                                                                onClick={handleConfirmMerge}
                                                                disabled={isFusing}
                                                                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center gap-1 shadow-lg shadow-red-600/25 cursor-pointer"
                                                            >
                                                                {isFusing ? 'Fusionando...' : '🔥 Ejecutar Fusión Divina'}
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </motion.div>
                        );
                    })()
                ) : activeTab === 'system' ? (
                    <SystemTab
                        user={user}
                        isAdmin={isAdmin}
                        userSettings={userSettings}
                        savingSettings={savingSettings}
                        showShowcaseGuide={showShowcaseGuide}
                        setShowShowcaseGuide={setShowShowcaseGuide}
                        handleToggleShowcase={handleToggleShowcase}
                        handleCopyShowcaseLink={handleCopyShowcaseLink}
                        handleUpdateLocation={handleUpdateLocation}
                        downloadStatus={downloadStatus}
                        cachedImagesCount={cachedImagesCount}
                        handleTriggerDownload={handleTriggerDownload}
                        handleCancelDownload={handleCancelDownload}
                        setLocalImagesEnabled={setLocalImagesEnabled}
                        fetchData={fetchData}
                        forceRender={forceRender}
                        setForceRender={setForceRender}
                        setShowModernCalibrator={setShowModernCalibrator}
                        setShowCalibrator={setShowCalibrator}
                        syncingExcel={syncingExcel}
                        handleSyncExcel={handleSyncExcel}
                        runningMaintenance={runningMaintenance}
                        handleRunMaintenance={handleRunMaintenance}
                        setResetStep={setResetStep}
                    />
                ) : activeTab === 'users' ? (
                    <UsersTab
                        heroes={heroes}
                        onAddUserClick={() => setShowAddUserModal(true)}
                        onIdentityChange={onIdentityChange}
                        handleUpdateRole={handleUpdateRole}
                        handleExportExcelAdmin={handleExportExcelAdmin}
                        handleExportSqliteAdmin={handleExportSqliteAdmin}
                        handlePasswordReset={handlePasswordReset}
                        handleDeleteHero={handleDeleteHero}
                    />
                ) : activeTab === 'wallapop' ? (
                    <motion.div
                        key="wallapop"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                    >
                        <WallapopImporter />
                        <WallapopNexusBridge />
                    </motion.div>
                ) : null}
            </AnimatePresence>

            <AddUserModal isOpen={showAddUserModal} onClose={() => setShowAddUserModal(false)} />

            <ResetConfirmModal
                resetStep={resetStep}
                isResetting={isResetting}
                onCancel={() => setResetStep(0)}
                onAdvance={() => setResetStep(2)}
                onConfirm={handleResetSmartMatches}
            />

            <IpLogsModal
                isOpen={showIpLogsModal}
                onClose={() => setShowIpLogsModal(false)}
                ipLogs={ipLogs}
                loadingIpLogs={loadingIpLogs}
                onDownload={handleDownloadIpLogs}
            />

            <VintageCalibratorModal
                isOpen={showCalibrator}
                coords={calibCoords}
                onChange={setCalibCoords}
                onSave={handleSaveCalib}
                onReset={handleResetCalib}
                onClose={() => setShowCalibrator(false)}
            />

            <ModernCalibratorModal
                isOpen={showModernCalibrator}
                coords={modernCoords}
                onChange={setModernCoords}
                onSave={handleSaveModernCalib}
                onReset={handleResetModernCalib}
                onClose={() => setShowModernCalibrator(false)}
            />
        </div >
    );
};

export default Config;
