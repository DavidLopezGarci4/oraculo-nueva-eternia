import React, { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Flame, Zap } from 'lucide-react';
import { MOTUImage } from './MOTUImage';
import type { RitualPayload } from '../../context/GrayskullRitualContext';
import hemanLightningArt from '../../assets/heman-power-sword-lightning.png';

interface GrayskullRitualOverlayProps {
    ritual: RitualPayload;
    onFinish: () => void;
}

// Reproductor de audio de alta fidelidad con clips reales masterizados y fallback WebAudio
const playAudioEffect = (type: 'claim' | 'burn') => {
    try {
        const audioSrc = type === 'claim' ? '/audio/grayskull_claim.mp3' : '/audio/grayskull_burn.mp3';
        const audio = new Audio(audioSrc);
        audio.volume = 0.95;
        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(() => {
                // Fallback a síntesis si la política del navegador bloquea el autoplay inicial
                playSyntheticFallback(type);
            });
        }
    } catch {
        playSyntheticFallback(type);
    }
};

const playSyntheticFallback = (type: 'claim' | 'burn') => {
    try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) return;
        const ctx = new AudioContextClass();
        const now = ctx.currentTime;

        if (type === 'claim') {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(140, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 1.2);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 2.4);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 2.5);
        } else {
            const bufferSize = ctx.sampleRate * 2.5;
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = (Math.random() * 2 - 1) * 0.4;
            }
            const noise = ctx.createBufferSource();
            noise.buffer = buffer;
            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(1000, now);
            filter.frequency.linearRampToValueAtTime(100, now + 2.2);
            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 2.4);
            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            noise.start(now);
            noise.stop(now + 2.5);
        }
    } catch {}
};

export const GrayskullRitualOverlay: React.FC<GrayskullRitualOverlayProps> = ({ ritual, onFinish }) => {
    const { type, product } = ritual;
    const isClaim = type === 'claim';

    // Fases del ritual:
    // 'intro' (0-300ms) -> 'charging' (300-1000ms: rayos suben por los bordes) -> 'climax' (1000-2400ms: colisión + rayo al cielo / cenizas) -> 'exit'
    const [phase, setPhase] = useState<'intro' | 'charging' | 'climax' | 'exit'>('intro');
    const [burnProgress, setBurnProgress] = useState(0); // 0% a 100%

    // Generar partículas de ceniza y ascuas flotantes con turbulencia
    const ashParticles = useMemo(() => {
        return Array.from({ length: 42 }).map((_, i) => ({
            id: i,
            xInit: Math.random() * 90 + 5, // %
            yInit: Math.random() * 80 + 10, // %
            xDrift: (Math.random() - 0.5) * 140, // px
            yRise: -(Math.random() * 240 + 120), // px
            size: Math.random() * 4.5 + 2, // px
            delay: Math.random() * 0.9,
            duration: Math.random() * 1.4 + 1.2,
            isEmber: Math.random() > 0.4
        }));
    }, []);

    useEffect(() => {
        playAudioEffect(type);

        // Fase 1: Inicio del ascenso de rayos por los laterales (0.3s)
        const t1 = setTimeout(() => setPhase('charging'), 300);

        // Fase 2: Si es cremación, animar la progresión del fuego consumiendo la tarjeta
        let burnInterval: any = null;
        if (!isClaim) {
            const startBurn = Date.now() + 250;
            burnInterval = setInterval(() => {
                const elapsed = Date.now() - startBurn;
                if (elapsed > 0) {
                    const progress = Math.min(100, (elapsed / 1600) * 100);
                    setBurnProgress(progress);
                }
            }, 25);
        }

        // Fase 3: Clímax (1.05s) -> Rayos chocan en el centro superior y se dispara el haz masivo al cielo
        const t2 = setTimeout(() => setPhase('climax'), 1050);

        // Fase 4: Desvanecimiento y salida (2.6s)
        const t3 = setTimeout(() => setPhase('exit'), 2600);

        // Fase 5: Finalización y cierre (2.9s)
        const t4 = setTimeout(() => {
            if (burnInterval) clearInterval(burnInterval);
            onFinish();
        }, 2900);

        return () => {
            clearTimeout(t1);
            clearTimeout(t2);
            clearTimeout(t3);
            clearTimeout(t4);
            if (burnInterval) clearInterval(burnInterval);
        };
    }, [type, isClaim, onFinish]);

    return (
        <AnimatePresence>
            <div 
                onClick={onFinish}
                className="fixed inset-0 z-[300] flex flex-col items-center justify-center p-3 sm:p-6 bg-black/95 backdrop-blur-3xl overflow-hidden select-none cursor-pointer"
                title="Toca o haz clic para continuar"
            >
                {/* 1. ATMÓSFERA Y FONDOS CÓSMICOS / RELÁMPAGOS */}
                {isClaim ? (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? [0.4, 0.95, 0.6, 0.9, 0.5] : 0.35,
                                scale: phase === 'climax' ? [1, 1.12, 1.05] : 1
                            }}
                            transition={{ duration: 0.8 }}
                            className="absolute inset-0 bg-gradient-to-t from-slate-950 via-sky-950/70 to-black pointer-events-none"
                        />
                        {/* Destello de relámpago celestial de fondo */}
                        {phase === 'climax' && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: [0, 0.8, 0.2, 0.9, 0] }}
                                transition={{ duration: 0.6, repeat: 2 }}
                                className="absolute inset-0 bg-cyan-400/25 pointer-events-none"
                            />
                        )}
                    </>
                ) : (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.9 : 0.45,
                                scale: phase === 'climax' ? [1, 1.1, 1] : 1
                            }}
                            transition={{ duration: 0.8 }}
                            className="absolute inset-0 bg-gradient-to-t from-black via-red-950/40 to-orange-950/30 pointer-events-none"
                        />
                    </>
                )}

                {/* 2. TÍTULOS Y LEYENDA DEL RITUAL */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-3 sm:mb-5 z-40"
                >
                    <div className="flex items-center justify-center gap-2 text-xs sm:text-sm font-black uppercase tracking-widest drop-shadow-lg">
                        {isClaim ? (
                            <>
                                <Zap className="h-4 w-4 text-cyan-300 animate-pulse" />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-white to-sky-400 font-black tracking-widest text-sm sm:text-base">
                                    ¡Por el Poder de Grayskull!
                                </span>
                                <Zap className="h-4 w-4 text-cyan-300 animate-pulse" />
                            </>
                        ) : (
                            <>
                                <Flame className="h-4 w-4 text-orange-400 animate-bounce" />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-red-400 to-amber-300 font-black text-sm sm:text-base">
                                    Liberando Reliquia en Cenizas
                                </span>
                                <Flame className="h-4 w-4 text-red-500 animate-bounce" />
                            </>
                        )}
                    </div>
                    <p className="text-[11px] text-cyan-200/90 font-bold tracking-widest mt-1">
                        {isClaim ? '⚡ ¡YO TENGO EL PODER! ⚡' : '🔥 Reduciendo la posesión a cenizas del tiempo'}
                    </p>
                </motion.div>

                {/* 3. ESCENARIO CENTRAL: TARJETA + ARCOS DE RAYO + HAZ AL CIELO */}
                <motion.div
                    initial={{ scale: 0.8, opacity: 0, y: 25 }}
                    animate={{
                        scale: phase === 'climax' ? (isClaim ? 1.05 : 0.95) : 1,
                        opacity: phase === 'exit' ? 0 : 1,
                        y: phase === 'exit' ? (isClaim ? -30 : 25) : 0
                    }}
                    transition={{ type: 'spring', stiffness: 280, damping: 22 }}
                    className="relative w-full max-w-[310px] sm:max-w-[340px] flex flex-col items-center z-20"
                >
                    {/* 🛡️ FONDO ÉPICO DETRÁS DE LA TARJETA: He-Man alzando la Espada */}
                    {isClaim && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.55 : 0.35,
                                scale: phase === 'climax' ? 1.1 : 1
                            }}
                            transition={{ duration: 0.6 }}
                            className="absolute -inset-6 sm:-inset-10 rounded-3xl overflow-hidden -z-10 flex items-center justify-center pointer-events-none"
                        >
                            <img
                                src={hemanLightningArt}
                                alt="He-Man y Castillo Grayskull"
                                className="w-full h-full object-cover filter saturate-150 brightness-75 blur-[1px]"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black via-cyan-950/40 to-black/80" />
                            <div className="absolute inset-0 border border-cyan-400/30 rounded-3xl shadow-[0_0_50px_rgba(6,182,212,0.4)]" />
                        </motion.div>
                    )}

                    {/* ⚡ 4. CONVERGENCIA EN LA CÚSPIDE: DESTELLO CÓSMICO Y CHIPAZO */}
                    {isClaim && (phase === 'charging' || phase === 'climax') && (
                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-50 pointer-events-none flex items-center justify-center">
                            {/* Núcleo de energía estelar */}
                            <motion.div
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{
                                    scale: phase === 'climax' ? [1.5, 3.2, 2.2] : [0.8, 1.4, 1],
                                    opacity: 1
                                }}
                                transition={{ duration: 0.4 }}
                                className="w-9 h-9 rounded-full bg-radial from-white via-cyan-200 to-blue-500 shadow-[0_0_40px_#00f3ff] blur-[1px]"
                            />
                            {/* Anillo de onda de choque expansiva al chocar los dos rayos */}
                            {phase === 'climax' && (
                                <motion.div
                                    initial={{ scale: 0.2, opacity: 1 }}
                                    animate={{ scale: 4.5, opacity: 0 }}
                                    transition={{ duration: 0.7, ease: 'easeOut' }}
                                    className="absolute w-20 h-20 rounded-full border-2 border-cyan-300 shadow-[0_0_30px_#00f3ff]"
                                />
                            )}
                        </div>
                    )}

                    {/* ⚡ 5. MEGARRAYO VERTICAL DISPARADO AL CIELO DESDE LA CÚSPIDE */}
                    {isClaim && phase === 'climax' && (
                        <motion.div
                            initial={{ scaleY: 0, opacity: 0 }}
                            animate={{ scaleY: 1, opacity: [0.95, 1, 0.9] }}
                            transition={{ duration: 0.25, ease: 'easeOut' }}
                            style={{ transformOrigin: 'bottom center' }}
                            className="absolute bottom-full left-1/2 -translate-x-1/2 w-16 sm:w-24 h-[80vh] flex flex-col items-center pointer-events-none z-50 -mb-2"
                        >
                            {/* Haz de plasma central blanco puro */}
                            <div className="w-3.5 h-full bg-white blur-[1px] shadow-[0_0_50px_#ffffff]" />
                            {/* Capa de energía cian/azul de Grayskull */}
                            <div className="absolute inset-x-0 w-full h-full bg-gradient-to-t from-cyan-300 via-sky-400 to-blue-600 blur-md opacity-90 animate-pulse" />
                            {/* Explosión y resplandor en la estratosfera */}
                            <motion.div
                                initial={{ scale: 0.5 }}
                                animate={{ scale: [1.2, 2.5, 1.8], opacity: [0.8, 1, 0.7] }}
                                transition={{ duration: 0.5, repeat: Infinity }}
                                className="absolute -top-16 w-64 sm:w-96 h-64 sm:h-96 rounded-full bg-radial from-white via-cyan-300/80 to-blue-600/0 blur-3xl"
                            />
                        </motion.div>
                    )}

                    {/* 🎴 6. LA TARJETA PRINCIPAL DE LA RELIQUIA */}
                    <div className={`relative w-full aspect-[3/4] rounded-3xl overflow-hidden shadow-[0_0_60px_rgba(0,0,0,0.95)] border-2 bg-slate-950 flex flex-col justify-between p-3.5 sm:p-4 z-20 transition-all ${
                        isClaim ? 'border-cyan-400/80 shadow-[0_0_45px_rgba(6,182,212,0.6)]' : 'border-white/20'
                    }`}>
                        {/* IMAGEN DE LA FIGURA */}
                        <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-black/80 border border-white/10">
                            <MOTUImage
                                productId={product.id}
                                src={product.image_url}
                                alt={product.name}
                                className={`max-h-[85%] max-w-[85%] object-contain transition-all duration-300 ${
                                    !isClaim && burnProgress > 15 ? 'filter grayscale contrast-200 brightness-50' : 'drop-shadow-[0_20px_30px_rgba(0,0,0,0.95)]'
                                }`}
                            />

                            {/* Badge de Categoría */}
                            <div className="absolute top-2 left-2 px-2.5 py-1 rounded-lg bg-black/85 border border-cyan-400/40 text-[9px] font-black text-cyan-300 uppercase tracking-wider backdrop-blur-md">
                                {product.sub_category || (product.is_vintage ? 'Vintage' : 'MOTU Origins')}
                            </div>
                        </div>

                        {/* Pie de Tarjeta con Nombre */}
                        <div className="mt-2 text-center">
                            <h4 className="text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-md">
                                {product.name}
                            </h4>
                        </div>

                        {/* ⚡ ESCENA A: RAYOS DE PLASMA RECORRIENDO LOS BORDES (CLAIM) */}
                        {isClaim && (phase === 'charging' || phase === 'climax') && (
                            <svg className="absolute inset-0 w-full h-full pointer-events-none z-30 overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
                                <defs>
                                    <filter id="lightningGlow" x="-50%" y="-50%" width="200%" height="200%">
                                        <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur1" />
                                        <feGaussianBlur in="SourceGraphic" stdDeviation="3.5" result="blur2" />
                                        <feMerge>
                                            <feMergeNode in="blur2" />
                                            <feMergeNode in="blur1" />
                                            <feMergeNode in="SourceGraphic" />
                                        </feMerge>
                                    </filter>
                                </defs>

                                {/* Rayo Izquierdo: Desde esquina inferior izquierda (0,100) sube a (0,0) y gira al centro superior (50,0) */}
                                <motion.path
                                    d="M 2 98 L 1 75 L 3 50 L 1 25 L 2 2 L 25 1 L 50 0"
                                    fill="none"
                                    stroke="#00f3ff"
                                    strokeWidth="3.5"
                                    filter="url(#lightningGlow)"
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: [0.8, 1, 0.9] }}
                                    transition={{ duration: 0.7, ease: 'easeOut' }}
                                />
                                <motion.path
                                    d="M 2 98 L 1 75 L 3 50 L 1 25 L 2 2 L 25 1 L 50 0"
                                    fill="none"
                                    stroke="#ffffff"
                                    strokeWidth="1.5"
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: 1 }}
                                    transition={{ duration: 0.7, ease: 'easeOut' }}
                                />

                                {/* Rayo Derecho: Desde esquina inferior derecha (100,100) sube a (100,0) y gira al centro superior (50,0) */}
                                <motion.path
                                    d="M 98 98 L 99 75 L 97 50 L 99 25 L 98 2 L 75 1 L 50 0"
                                    fill="none"
                                    stroke="#00f3ff"
                                    strokeWidth="3.5"
                                    filter="url(#lightningGlow)"
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: [0.8, 1, 0.9] }}
                                    transition={{ duration: 0.7, ease: 'easeOut' }}
                                />
                                <motion.path
                                    d="M 98 98 L 99 75 L 97 50 L 99 25 L 98 2 L 75 1 L 50 0"
                                    fill="none"
                                    stroke="#ffffff"
                                    strokeWidth="1.5"
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: 1 }}
                                    transition={{ duration: 0.7, ease: 'easeOut' }}
                                />
                            </svg>
                        )}

                        {/* 🔥 ESCENA B: COMBUSTIÓN, FUEGO Y CENIZAS DESINTEGRÁNDOSE (BURN) */}
                        {!isClaim && (
                            <>
                                {/* Máscara de ceniza y disolución de arriba a abajo */}
                                <div
                                    className="absolute inset-0 pointer-events-none z-20 overflow-hidden rounded-3xl"
                                    style={{
                                        background: `linear-gradient(to bottom, rgba(5, 5, 5, 0.98) 0%, rgba(15, 15, 15, 0.95) ${burnProgress}%, transparent ${Math.min(100, burnProgress + 8)}%)`
                                    }}
                                >
                                    {/* Frente de llama viva al rojo vivo en la línea de combustión */}
                                    {burnProgress > 0 && burnProgress < 98 && (
                                        <div
                                            className="absolute w-full h-12 -translate-y-1/2 bg-gradient-to-b from-yellow-300 via-orange-500 to-red-600 shadow-[0_0_35px_#ff4500] opacity-95 flex items-center justify-around"
                                            style={{ top: `${burnProgress}%` }}
                                        >
                                            <Flame className="h-7 w-7 text-yellow-200 fill-yellow-300 animate-bounce" />
                                            <Flame className="h-8 w-8 text-amber-100 fill-orange-500 animate-pulse" />
                                            <Flame className="h-7 w-7 text-yellow-200 fill-yellow-300 animate-bounce" />
                                        </div>
                                    )}
                                </div>

                                {/* Partículas de ascuas ardientes y cenizas volando hacia arriba */}
                                <div className="absolute inset-0 pointer-events-none z-30 overflow-hidden">
                                    {ashParticles.map((p) => {
                                        if (burnProgress < p.yInit) return null;
                                        return (
                                            <motion.div
                                                key={p.id}
                                                initial={{
                                                    x: `${p.xInit}%`,
                                                    y: `${p.yInit}%`,
                                                    opacity: 1,
                                                    scale: 1
                                                }}
                                                animate={{
                                                    x: `calc(${p.xInit}% + ${p.xDrift}px)`,
                                                    y: `calc(${p.yInit}% + ${p.yRise}px)`,
                                                    opacity: [1, 0.8, 0],
                                                    scale: [1, 0.6, 0.1],
                                                    rotate: Math.random() * 360
                                                }}
                                                transition={{
                                                    duration: p.duration,
                                                    delay: p.delay,
                                                    ease: 'easeOut'
                                                }}
                                                style={{
                                                    width: p.size,
                                                    height: p.size
                                                }}
                                                className={`absolute rounded-full ${
                                                    p.isEmber
                                                        ? 'bg-amber-300 shadow-[0_0_10px_#f59e0b]'
                                                        : 'bg-neutral-400 opacity-70 blur-[0.4px]'
                                                }`}
                                            />
                                        );
                                    })}
                                </div>
                            </>
                        )}
                    </div>

                    {/* PIE DE ESTADO DEL RITUAL */}
                    <div className="mt-3.5 flex items-center gap-2 z-30">
                        {isClaim ? (
                            <div className="px-4 py-1.5 rounded-full bg-cyan-500/20 border border-cyan-400/70 text-cyan-300 text-xs font-black uppercase tracking-widest flex items-center gap-2 shadow-[0_0_25px_rgba(6,182,212,0.5)]">
                                <Shield className="h-4 w-4 fill-cyan-400" />
                                <span>Asegurada en la Fortaleza</span>
                            </div>
                        ) : (
                            <div className="px-4 py-1.5 rounded-full bg-orange-500/20 border border-orange-500/50 text-orange-300 text-xs font-black uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(249,115,22,0.3)]">
                                <Flame className="h-4 w-4 fill-orange-400 animate-pulse" />
                                <span>Cremación Completada</span>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default GrayskullRitualOverlay;
