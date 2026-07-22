import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Terminal, Settings, Users, Package } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { resetSmartMatches, runScrapers, stopScrapers, getScraperLogs, type ScraperExecutionLog, getWallapopIpLogs, downloadWallapopIpLogs, type WallapopIpLog, runWallaManualHtml } from '../api/purgatory';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
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
import InventoryTab from '../components/config/InventoryTab';
import ScrapersTab from '../components/config/ScrapersTab';


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
    type TemporaryProduct,
    getDevices,
    authorizeDevice,
    deleteDevice,
    type Device
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

    const [devices, setDevices] = useState<Device[]>([]);
    const [loadingDevices, setLoadingDevices] = useState(false);

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

    const loadDevices = async () => {
        if (!isAdmin) return;
        setLoadingDevices(true);
        try {
            const data = await getDevices();
            setDevices(data || []);
        } catch (err) {
            console.error("Error cargando dispositivos:", err);
        } finally {
            setLoadingDevices(false);
        }
    };

    const handleAuthorizeDevice = async (deviceId: string) => {
        try {
            await authorizeDevice(deviceId);
            await loadDevices();
        } catch (err) {
            console.error("Error autorizando dispositivo:", err);
            alert("Error al autorizar el dispositivo.");
        }
    };

    const handleDeleteDevice = async (deviceId: string) => {
        try {
            await deleteDevice(deviceId);
            await loadDevices();
        } catch (err) {
            console.error("Error eliminando dispositivo:", err);
            alert("Error al revocar/eliminar el dispositivo.");
        }
    };

    const fetchData = async () => {
        try {
            // Fetch everything, but handle individual failures gracefully
            const [s, u, al, h, ms, tempProducts, devs] = await Promise.all([
                getScrapersStatus().catch((e: any) => { console.error("Scrapers error:", e); return []; }),
                getUserSettings(activeUserId).catch((e: any) => { console.error("User settings error:", e); return null; }),
                getScraperLogs().catch((e: any) => { console.error("Logs error:", e); return []; }),
                getHeroes().catch((e: any) => { console.error("Heroes list error:", e); return []; }),
                getDashboardMatchStats(activeUserId).catch((e: any) => { console.error("Match stats error:", e); return []; }),
                isAdmin ? getTemporaryProducts().catch((e: any) => { console.error("Temp products error:", e); return []; }) : Promise.resolve([]),
                isAdmin ? getDevices().catch((e: any) => { console.error("Devices error:", e); return []; }) : Promise.resolve([])
            ]);

            setStatuses(s || []);
            if (u) setUserSettings(u);
            setAdvancedLogs(al || []);
            setHeroes(h || []);
            setMatchStats(ms || []);
            setTemporaryProducts(tempProducts || []);
            setDevices(devs || []);

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
                    <ScrapersTab
                        statuses={statuses}
                        runScrapersMutation={runScrapersMutation}
                        stopScrapersMutation={stopScrapersMutation}
                        runWallaManualHtmlMutation={runWallaManualHtmlMutation}
                        syncingNexus={syncingNexus}
                        handleSyncNexus={handleSyncNexus}
                        handleOpenIpLogs={handleOpenIpLogs}
                        wallaManualLoading={wallaManualLoading}
                        logFilter={logFilter}
                        setLogFilter={setLogFilter}
                        advancedLogs={advancedLogs}
                        selectedLog={selectedLog}
                        setSelectedLog={setSelectedLog}
                        setTargetLogId={setTargetLogId}
                        handleCopyLogs={handleCopyLogs}
                        copied={copied}
                        consoleRef={consoleRef}
                        syncingSensores={syncingSensores}
                        setSyncingSensores={setSyncingSensores}
                        fetchData={fetchData}
                    />
                ) : activeTab === 'inventory' ? (
                    <InventoryTab
                        matchStats={matchStats}
                        isAdmin={isAdmin}
                        handleCardClick={handleCardClick}
                        temporaryProducts={temporaryProducts}
                        setTemporaryProducts={setTemporaryProducts}
                        loadingTemporary={loadingTemporary}
                        setLoadingTemporary={setLoadingTemporary}
                        freeMergeMode={freeMergeMode}
                        setFreeMergeMode={setFreeMergeMode}
                        mergeSource={mergeSource}
                        setMergeSource={setMergeSource}
                        mergeTarget={mergeTarget}
                        setMergeTarget={setMergeTarget}
                        mergeSearchQuery={mergeSearchQuery}
                        setMergeSearchQuery={setMergeSearchQuery}
                        mergeTargetSuggestions={mergeTargetSuggestions}
                        setMergeTargetSuggestions={setMergeTargetSuggestions}
                        searchingTarget={searchingTarget}
                        isFusing={isFusing}
                        freeMergeSourceQuery={freeMergeSourceQuery}
                        setFreeMergeSourceQuery={setFreeMergeSourceQuery}
                        freeMergeSourceSuggestions={freeMergeSourceSuggestions}
                        setFreeMergeSourceSuggestions={setFreeMergeSourceSuggestions}
                        showMergePanel={showMergePanel}
                        setShowMergePanel={setShowMergePanel}
                        handleConfirmMerge={handleConfirmMerge}
                    />
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
                        devices={devices}
                        loadingDevices={loadingDevices}
                        onAuthorizeDevice={handleAuthorizeDevice}
                        onDeleteDevice={handleDeleteDevice}
                        onRefreshDevices={loadDevices}
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
