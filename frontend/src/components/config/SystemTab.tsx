import { motion } from 'framer-motion';
import {
    Database, Lock, AlertCircle, Target, Clock, Globe, Repeat, ChevronDown,
    CheckCircle2, RefreshCw, Download, Package, Sparkles, Settings, ShieldAlert,
    FileSpreadsheet, Trash2, Zap,
} from 'lucide-react';
import { downloadImagesZip, type Hero } from '../../api/admin';

interface DownloadStatus {
    active: boolean;
    total: number;
    current: number;
    errors: number;
    last_error: string | null;
}

interface SystemTabProps {
    user?: Hero | null;
    isAdmin: boolean;
    userSettings: any;
    savingSettings: boolean;
    showShowcaseGuide: boolean;
    setShowShowcaseGuide: (v: boolean) => void;
    handleToggleShowcase: () => void;
    handleCopyShowcaseLink: () => void;
    handleUpdateLocation: (loc: string) => void;
    downloadStatus: DownloadStatus;
    cachedImagesCount: number;
    handleTriggerDownload: () => void;
    handleCancelDownload: () => void;
    setLocalImagesEnabled: (v: boolean) => void;
    fetchData: () => void;
    forceRender: number;
    setForceRender: (updater: (prev: number) => number) => void;
    setShowModernCalibrator: (v: boolean) => void;
    setShowCalibrator: (v: boolean) => void;
    syncingExcel: boolean;
    handleSyncExcel: () => void;
    runningMaintenance: boolean;
    handleRunMaintenance: () => void;
    setResetStep: (n: number) => void;
}

/** Fase AAA-4a: extraido de Config.tsx (pestaña "system" / "Ajustes"). */
export default function SystemTab({
    user,
    isAdmin,
    userSettings,
    savingSettings,
    showShowcaseGuide,
    setShowShowcaseGuide,
    handleToggleShowcase,
    handleCopyShowcaseLink,
    handleUpdateLocation,
    downloadStatus,
    cachedImagesCount,
    handleTriggerDownload,
    handleCancelDownload,
    setLocalImagesEnabled,
    fetchData,
    forceRender,
    setForceRender,
    setShowModernCalibrator,
    setShowCalibrator,
    syncingExcel,
    handleSyncExcel,
    runningMaintenance,
    handleRunMaintenance,
    setResetStep,
}: SystemTabProps) {
    return (
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
                            <label htmlFor="sentinel-price-threshold" className="text-xs text-white/50 block font-medium">Umbral de Alerta de Precio (%)</label>
                            <input id="sentinel-price-threshold" type="range" disabled className="w-full accent-brand-primary" value="15" />
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
                            <label htmlFor="grail-min-roi" className="text-xs text-white/50 block font-medium">ROI Mínimo para Grial (%)</label>
                            <div className="flex items-center gap-3">
                                <input id="grail-min-roi" type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="50" />
                                <span className="text-white/60 text-xs">%</span>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="grail-value-threshold" className="text-xs text-white/50 block font-medium">Valor Umbral Grial (€)</label>
                            <div className="flex items-center gap-3">
                                <input id="grail-value-threshold" type="number" disabled className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/50 w-full" value="150" />
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
                            <label htmlFor="scraper-page-delay" className="text-xs text-white/50 block font-medium">Delay entre Páginas (seg)</label>
                            <input id="scraper-page-delay" type="range" disabled className="w-full accent-blue-400" value="10" />
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
                            <span id="public-showcase-label" className="text-xs text-white/70">Santuario Público</span>
                            <button
                                onClick={handleToggleShowcase}
                                role="switch"
                                aria-checked={!!userSettings?.is_public_showcase}
                                aria-labelledby="public-showcase-label"
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
                                    const label = src === 'supabase' ? 'Nube' : 'Caché';
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
                                        onClick={() => downloadImagesZip()}
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

                 {/* Rendimiento e Inteligencia Visual */}
                 <div className="glass border border-white/10 p-6 rounded-3xl space-y-4 bg-white/5" data-render={forceRender}>
                     <div className="flex items-center gap-3 text-brand-secondary font-bold uppercase tracking-widest text-xs mb-2">
                         <Sparkles className="h-4 w-4" />
                         Rendimiento y Efectos Visuales
                     </div>
                     <div className="space-y-4">
                         <p className="text-[10px] text-white/65 font-bold uppercase leading-tight">
                             Activa o desactiva las animaciones avanzadas y efectos 3D de las tarjetas de figuras para optimizar el rendimiento en dispositivos móviles.
                         </p>
                         <div className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                             <span className="text-xs text-white/70">
                                 Efectos Hover 3D e Iluminación Neón
                             </span>
                             <button
                                 type="button"
                                 onClick={() => {
                                     const current = localStorage.getItem('motu_premium_effects') !== 'false';
                                     localStorage.setItem('motu_premium_effects', current ? 'false' : 'true');
                                     window.dispatchEvent(new Event('storage'));
                                     setForceRender(prev => prev + 1);
                                 }}
                                 className={`px-4 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all cursor-pointer ${
                                     localStorage.getItem('motu_premium_effects') !== 'false'
                                         ? 'bg-brand-secondary text-white shadow-lg'
                                         : 'bg-white/5 text-white/60 hover:text-white'
                                 }`}
                             >
                                 {localStorage.getItem('motu_premium_effects') !== 'false' ? 'Activados' : 'Clásicos'}
                             </button>
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

                {/* --- DATABASE MAINTENANCE: FINOPS --- */}
                {isAdmin && (
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <Database className="h-6 w-6 text-brand-primary" />
                            <h3 className="text-xl font-black uppercase tracking-[0.2em] text-white">Base de Datos</h3>
                        </div>
                        <div className="glass border border-white/10 p-6 rounded-3xl group hover:bg-white/5 transition-all max-w-md">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-4">
                                    <div className="bg-brand-primary/10 p-3 rounded-lg group-hover:bg-brand-primary/20 transition-all">
                                        <Database className="h-5 w-5 text-brand-primary" />
                                    </div>
                                    <div>
                                        <h4 className="text-white font-bold text-sm">Purificación FinOps</h4>
                                        <p className="text-[10px] text-white/60 font-mono">Optimización de Supabase</p>
                                    </div>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[8px] font-black text-brand-primary uppercase tracking-widest bg-brand-primary/10 px-2 py-0.5 rounded">FinOps Layer 1</span>
                                </div>
                            </div>
                            <p className="text-[11px] text-white/50 mb-6 leading-relaxed">
                                Compacta el historial de precios en resúmenes mensuales y purga registros y logs redundantes de la nube.
                            </p>
                            <button
                                onClick={handleRunMaintenance}
                                disabled={runningMaintenance}
                                className={`w-full bg-brand-primary/10 hover:bg-brand-primary text-brand-primary hover:text-white border border-brand-primary/20 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-brand-primary/0 hover:shadow-brand-primary/20 ${runningMaintenance ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                <RefreshCw className={`h-3 w-3 ${runningMaintenance ? 'animate-spin' : ''}`} />
                                {runningMaintenance ? 'Purificando...' : '🧹 Limpieza y Compactación'}
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
    );
}
