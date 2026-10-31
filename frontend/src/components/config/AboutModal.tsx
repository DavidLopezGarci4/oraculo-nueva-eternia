import React, { useState, useEffect } from 'react';
import {
    X,
    Sparkles,
    ShieldCheck,
    ChevronDown,
    Network,
    Calendar,
    Layers,
    Lock,
} from 'lucide-react';
import changelogManifest from '../../config/changelog.user.json';

interface AboutModalProps {
    isOpen: boolean;
    isAdmin: boolean;
    onClose: () => void;
    onOpenArchitectureGraph: () => void;
}

/**
 * Parsea de forma segura (sin dangerouslySetInnerHTML) viñetas humanas del tipo:
 * "✨ **Título corto:** Explicación directa para el coleccionista."
 */
function renderHumanHighlight(text: string): React.ReactNode {
    const match = text.match(/^(.*?)\*\*(.+?)\*\*\s*(.*)$/);
    if (!match) {
        return <span className="text-white/80">{text}</span>;
    }
    const [, prefix, boldTitle, rest] = match;
    return (
        <>
            {prefix && <span className="mr-1">{prefix}</span>}
            <strong className="text-white font-black">{boldTitle}</strong>{' '}
            <span className="text-white/75">{rest}</span>
        </>
    );
}

export default function AboutModal({
    isOpen,
    isAdmin,
    onClose,
    onOpenArchitectureGraph,
}: AboutModalProps) {
    const [expandedVersion, setExpandedVersion] = useState<string | null>(null);
    const [logoError, setLogoError] = useState(false);

    useEffect(() => {
        if (!isOpen) return;
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const currentRelease = changelogManifest.versions[0];
    const previousReleases = changelogManifest.versions.slice(1);

    return (
        <div
            onClick={(e) => {
                if (e.target === e.currentTarget) onClose();
            }}
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md animate-fade-in"
            role="dialog"
            aria-modal="true"
            aria-labelledby="about-modal-title"
        >
            <div className="bg-[#0d111a] border border-brand-primary/35 rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
                {/* Barra superior */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 bg-white/[0.02]">
                    <div className="flex items-center gap-2 text-brand-primary text-xs font-black uppercase tracking-widest">
                        <Sparkles className="h-4 w-4" />
                        <span>Acerca de &amp; Novedades</span>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Cerrar ventana Acerca de"
                        className="p-2 rounded-xl bg-white/5 hover:bg-red-500/20 text-white/70 hover:text-red-400 transition-all cursor-pointer"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>

                {/* Cuerpo desplazable */}
                <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5 custom-scrollbar">
                    {/* 1. Ficha de Identidad */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-brand-primary/10 via-white/[0.02] to-transparent border border-brand-primary/25 flex flex-col sm:flex-row items-start sm:items-center gap-4">
                        <div className="h-16 w-16 rounded-2xl bg-black/60 border border-brand-primary/40 shadow-lg shadow-brand-primary/15 flex items-center justify-center shrink-0 overflow-hidden">
                            {!logoError ? (
                                <img
                                    src="/oraculo-logo.png"
                                    alt={changelogManifest.appName}
                                    onError={() => setLogoError(true)}
                                    className="h-14 w-14 object-contain"
                                />
                            ) : (
                                <Sparkles className="h-8 w-8 text-brand-primary" />
                            )}
                        </div>
                        <div className="space-y-2 flex-1">
                            <div>
                                <h2
                                    id="about-modal-title"
                                    className="text-lg sm:text-xl font-black text-white tracking-tight"
                                >
                                    {changelogManifest.appName}
                                </h2>
                                <p className="text-xs text-white/70 leading-relaxed mt-0.5">
                                    {changelogManifest.appDescription}
                                </p>
                            </div>
                            <div className="flex flex-wrap gap-1.5 pt-0.5">
                                <span className="text-[10px] font-mono font-black px-2.5 py-0.5 rounded-full bg-brand-primary/20 border border-brand-primary/40 text-brand-primary">
                                    v{changelogManifest.currentVersion}
                                </span>
                                <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-white/75 flex items-center gap-1">
                                    <Layers className="h-3 w-3 text-cyan-400" />
                                    Build {changelogManifest.buildNumber}
                                </span>
                                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/25 text-cyan-300">
                                    Web / PWA Full-Stack
                                </span>
                                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-emerald-300 flex items-center gap-1">
                                    <ShieldCheck className="h-3 w-3" />
                                    Privacidad Blindada
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* 2. Tarjeta Heroica: Novedades de la Versión Actual */}
                    {currentRelease && (
                        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-amber-500/[0.08] via-brand-primary/[0.05] to-transparent border border-amber-500/35 space-y-3">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                                <div className="flex items-center gap-2">
                                    <span className="px-2 py-0.5 rounded-md bg-amber-500 text-black text-[9px] font-black uppercase tracking-wider">
                                        Versión Actual · v{currentRelease.version}
                                    </span>
                                    <span className="text-[10px] text-white/55 font-mono flex items-center gap-1">
                                        <Calendar className="h-3 w-3" />
                                        {currentRelease.date}
                                    </span>
                                </div>
                            </div>
                            <h3 className="text-sm font-black text-amber-300">
                                {currentRelease.title}
                            </h3>
                            <ul className="space-y-2.5 text-xs leading-relaxed">
                                {currentRelease.highlights.map((item, idx) => (
                                    <li
                                        key={idx}
                                        className="p-2.5 rounded-xl bg-black/35 border border-white/5"
                                    >
                                        {renderHumanHighlight(item)}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* 3. Historial de Versiones Anteriores (Acordeón) */}
                    {previousReleases.length > 0 && (
                        <div className="space-y-2.5">
                            <div className="text-[10px] font-black uppercase tracking-[0.18em] text-white/50 px-1">
                                Historial de Versiones Anteriores
                            </div>
                            <div className="space-y-2">
                                {previousReleases.map((rel) => {
                                    const isExpanded = expandedVersion === rel.version;
                                    return (
                                        <div
                                            key={rel.version}
                                            className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden"
                                        >
                                            <button
                                                type="button"
                                                aria-expanded={isExpanded}
                                                onClick={() =>
                                                    setExpandedVersion(isExpanded ? null : rel.version)
                                                }
                                                className="w-full px-4 py-3 flex items-center justify-between gap-3 text-left hover:bg-white/[0.04] transition-all cursor-pointer"
                                            >
                                                <div className="flex flex-wrap items-center gap-2 min-w-0">
                                                    <span className="text-[10px] font-mono font-black px-2 py-0.5 rounded-md bg-white/10 text-cyan-300 shrink-0">
                                                        v{rel.version}
                                                    </span>
                                                    <span className="text-xs font-bold text-white truncate">
                                                        {rel.title}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-2 shrink-0">
                                                    <span className="text-[10px] font-mono text-white/45 hidden sm:inline">
                                                        {rel.date}
                                                    </span>
                                                    <ChevronDown
                                                        className={`h-4 w-4 text-white/50 transition-transform duration-200 ${
                                                            isExpanded ? 'rotate-180 text-white' : ''
                                                        }`}
                                                    />
                                                </div>
                                            </button>

                                            {isExpanded && (
                                                <div className="px-4 pb-3.5 pt-1 border-t border-white/5 space-y-2 text-xs leading-relaxed">
                                                    {rel.highlights.map((hl, idx) => (
                                                        <div
                                                            key={idx}
                                                            className="p-2.5 rounded-xl bg-black/30 border border-white/5"
                                                        >
                                                            {renderHumanHighlight(hl)}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* 4. Integración con Salud del Stack (Exclusivo Master / Admin) */}
                    {isAdmin && (
                        <div className="p-4 rounded-2xl bg-cyan-500/[0.05] border border-cyan-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                            <div className="space-y-0.5">
                                <div className="text-[11px] font-black uppercase tracking-wider text-cyan-300 flex items-center gap-1.5">
                                    <Network className="h-3.5 w-3.5" />
                                    Topología &amp; Salud en Tiempo Real
                                </div>
                                <p className="text-[10px] text-white/65 leading-relaxed">
                                    Abre el mapa interactivo TecnoRed v2.0 con sondas de latencia, rutas de flujo y funciones reales por nodo.
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => {
                                    onClose();
                                    onOpenArchitectureGraph();
                                }}
                                className="w-full sm:w-auto shrink-0 px-3.5 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500 text-cyan-300 hover:text-black border border-cyan-400/40 text-[10px] font-black uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                            >
                                <Network className="h-3.5 w-3.5" />
                                Inspeccionar Salud de la Arquitectura
                            </button>
                        </div>
                    )}

                    {/* 5. Ficha Legal, Privacidad y Créditos */}
                    <div className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-1.5 text-[10px] text-white/55">
                        <div className="flex items-center gap-1.5 text-emerald-400 font-black uppercase tracking-wider">
                            <Lock className="h-3 w-3" />
                            <span>Garantía de Privacidad del Coleccionista</span>
                        </div>
                        <p className="leading-relaxed text-white/65">
                            {changelogManifest.privacyPolicy} Activa el Modo Incógnito en cualquier pantalla con{' '}
                            <span className="font-mono text-white/85">Ctrl+I</span> o doble pulsación de{' '}
                            <span className="font-mono text-white/85">Esc</span>.
                        </p>
                        <div className="pt-1.5 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-[9px] font-mono text-white/40">
                            <span>Oráculo de Nueva Eternia · Ecosistema Privado MOTU</span>
                            <span>Actualizado: {changelogManifest.lastUpdated}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
