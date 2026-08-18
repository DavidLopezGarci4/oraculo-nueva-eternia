import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Sparkles, Flame } from 'lucide-react';
import { MOTUImage } from './MOTUImage';
import type { RitualPayload } from '../../context/GrayskullRitualContext';
import hemanLightningArt from '../../assets/heman-power-sword-lightning.png';

interface GrayskullRitualOverlayProps {
    ritual: RitualPayload;
    onFinish: () => void;
}

// Generador de efectos de sonido sintéticos mediante Web Audio API (100% nativo)
const playAudioEffect = (type: 'claim' | 'burn') => {
    try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) return;
        const ctx = new AudioContextClass();

        if (type === 'claim') {
            // Creciente de energía cósmica de Grayskull y trueno masivo al cielo
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(120, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1400, ctx.currentTime + 1.1);
            osc.frequency.exponentialRampToValueAtTime(90, ctx.currentTime + 1.8);

            gain.gain.setValueAtTime(0.02, ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.28, ctx.currentTime + 1.1);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.2);

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 2.3);
        } else {
            // Sonido de Cremación y Ceniza: Ruido blanco filtrado simulando fuego
            const bufferSize = ctx.sampleRate * 2.5;
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }

            const noise = ctx.createBufferSource();
            noise.buffer = buffer;

            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(900, ctx.currentTime);
            filter.frequency.linearRampToValueAtTime(100, ctx.currentTime + 2.2);

            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.18, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.2);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            noise.start();
            noise.stop(ctx.currentTime + 2.3);
        }
    } catch {
        // Fallback silencioso si el navegador no permite audio inmediato
    }
};

export const GrayskullRitualOverlay: React.FC<GrayskullRitualOverlayProps> = ({ ritual, onFinish }) => {
    const { type, product } = ritual;
    const isClaim = type === 'claim';

    const [phase, setPhase] = useState<'intro' | 'raising' | 'climax' | 'exit'>('intro');
    const [burnProgress, setBurnProgress] = useState(0); // 0% a 100% para la cremación

    useEffect(() => {
        playAudioEffect(type);

        // Fase 1: Intro (0s -> 0.4s)
        const t1 = setTimeout(() => setPhase('raising'), 400);

        // Si es cremación, animar la progresión del fuego de arriba a abajo
        let burnInterval: any = null;
        if (!isClaim) {
            const startBurn = Date.now() + 300;
            burnInterval = setInterval(() => {
                const elapsed = Date.now() - startBurn;
                if (elapsed > 0) {
                    const progress = Math.min(100, (elapsed / 1300) * 100);
                    setBurnProgress(progress);
                }
            }, 30);
        }

        // Fase 2: Clímax (1.2s -> El Rayo Azul Cósmico se eleva al cielo)
        const t2 = setTimeout(() => setPhase('climax'), 1200);

        // Fase 3: Exit (2.1s)
        const t3 = setTimeout(() => setPhase('exit'), 2100);

        // Finalización (2.4s)
        const t4 = setTimeout(() => {
            if (burnInterval) clearInterval(burnInterval);
            onFinish();
        }, 2400);

        return () => {
            clearTimeout(t1);
            clearTimeout(t2);
            clearTimeout(t3);
            clearTimeout(t4);
            if (burnInterval) clearInterval(burnInterval);
        };
    }, [type, onFinish]);

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[300] flex flex-col items-center justify-center p-3 sm:p-6 bg-black/95 backdrop-blur-3xl overflow-hidden select-none">
                {/* 1. FONDO ATMOSFÉRICO DE GRAYSKULL (AZUL ELÉCTRICO) / INFIERNO DE CENIZAS */}
                {isClaim ? (
                    <>
                        {/* Cielo tormentoso azul eléctrico / cian de Grayskull */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.95 : 0.4,
                                scale: phase === 'climax' ? [1, 1.2, 1.1] : 1
                            }}
                            transition={{ duration: 0.6 }}
                            className="absolute inset-0 bg-gradient-to-t from-sky-950 via-cyan-950/50 to-black pointer-events-none"
                        />
                        {/* Destellos de relámpagos azulados en el cielo superior */}
                        <motion.div
                            animate={{
                                opacity: phase === 'climax' ? [0, 1, 0.4, 1, 0] : [0, 0.25, 0]
                            }}
                            transition={{ duration: 0.7, repeat: phase === 'climax' ? 2 : Infinity }}
                            className="absolute inset-0 bg-radial from-cyan-400/35 via-sky-300/15 to-transparent pointer-events-none"
                        />
                    </>
                ) : (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.9 : 0.5,
                                scale: phase === 'climax' ? [1, 1.15, 1] : 1
                            }}
                            transition={{ duration: 0.8 }}
                            className="absolute inset-0 bg-gradient-to-t from-black via-red-950/40 to-orange-950/30 pointer-events-none"
                        />
                    </>
                )}

                {/* 2. ⚡ RAYO AZUL ELÉCTRICO DISPARADO HACIA EL CIELO (CLAIM - Estilo He-Man en Grayskull) */}
                {isClaim && (phase === 'climax' || phase === 'raising') && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{
                            height: phase === 'climax' ? '70vh' : '30vh',
                            opacity: phase === 'climax' ? [0.9, 1, 0.95] : 0.6
                        }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        className="absolute top-0 left-1/2 -translate-x-1/2 w-12 sm:w-20 flex flex-col items-center pointer-events-none z-40"
                    >
                        {/* Columna central de plasma azul eléctrico y blanco */}
                        <div className="w-full h-full bg-gradient-to-t from-cyan-400 via-sky-300 to-white blur-[2px] shadow-[0_0_90px_#00f0ff]" />
                        {/* Haces exteriores de relámpago azul cobalto */}
                        <div className="absolute inset-0 w-full h-full bg-gradient-to-t from-transparent via-blue-500 to-cyan-200 blur-md opacity-90 animate-pulse" />
                        {/* Explosión cósmica en el cielo superior */}
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: [1, 2.8, 2.2], opacity: [0.8, 1, 0.7] }}
                            transition={{ duration: 0.4, repeat: Infinity }}
                            className="absolute -top-12 w-56 sm:w-80 h-56 sm:h-80 rounded-full bg-radial from-white via-cyan-300/90 to-blue-600/0 blur-2xl"
                        />
                    </motion.div>
                )}

                {/* 3. PARTÍCULAS CÓSMICAS AZULES / CENIZAS FLOTANTES */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {Array.from({ length: 32 }).map((_, i) => (
                        <motion.div
                            key={i}
                            initial={{
                                x: `${(i * 13) % 100}vw`,
                                y: isClaim ? '105vh' : '45vh',
                                opacity: 0,
                                scale: Math.random() * 0.9 + 0.4
                            }}
                            animate={{
                                y: isClaim ? '-15vh' : '-20vh',
                                opacity: [0, 0.9, 0],
                                x: `calc(${(i * 13) % 100}vw + ${(i % 2 === 0 ? 1 : -1) * 60}px)`
                            }}
                            transition={{
                                duration: Math.random() * 1.5 + 0.9,
                                repeat: Infinity,
                                delay: Math.random() * 0.6
                            }}
                            className={`absolute rounded-full ${
                                isClaim
                                    ? 'w-2 h-2 bg-cyan-300 blur-[0.5px] shadow-[0_0_12px_#38bdf8]'
                                    : 'w-2.5 h-2.5 bg-orange-500 blur-[1px] shadow-[0_0_10px_#ea580c]'
                            }`}
                        />
                    ))}
                </div>

                {/* 4. CONTENEDOR PRINCIPAL: Tarjeta y Portal de Grayskull */}
                <motion.div
                    initial={{ scale: 0.75, opacity: 0, y: 30 }}
                    animate={{
                        scale: phase === 'climax' ? (isClaim ? 1.04 : 0.95) : 1,
                        opacity: phase === 'exit' ? 0 : 1,
                        y: phase === 'exit' ? (isClaim ? -40 : 30) : 0
                    }}
                    transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                    className="relative w-full max-w-[320px] sm:max-w-[360px] flex flex-col items-center z-20 mt-2 sm:mt-4"
                >
                    {/* 🛡️ HE-MAN Y LA ESPADA DE GRAYSKULL (Escena Oficial con Rayos Azules) */}
                    {isClaim && (
                        <motion.div
                            initial={{ y: 30, opacity: 0, scale: 0.85 }}
                            animate={{
                                y: phase === 'climax' ? -15 : -5,
                                opacity: 1,
                                scale: phase === 'climax' ? 1.08 : 1
                            }}
                            transition={{ duration: 0.5, ease: 'easeOut' }}
                            className="relative z-50 -mb-6 flex flex-col items-center"
                        >
                            <div className="relative h-28 sm:h-36 rounded-2xl overflow-hidden border-2 border-cyan-400/80 shadow-[0_0_40px_rgba(6,182,212,0.8)] bg-slate-950/80">
                                <img
                                    src={hemanLightningArt}
                                    alt="He-Man alzando la Espada de Poder en Grayskull"
                                    className="h-full w-auto object-contain"
                                />
                                {/* Halo azul de energía en la punta */}
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-cyan-400/20 pointer-events-none" />
                            </div>

                            {/* Chispas y haz de plasma azul saliendo de la punta */}
                            <motion.div
                                animate={{ scale: [1, 2, 1.2], opacity: [0.7, 1, 0.8] }}
                                transition={{ duration: 0.25, repeat: Infinity }}
                                className="absolute -top-3 w-10 h-10 rounded-full bg-radial from-white via-cyan-300 to-blue-500 blur-sm shadow-[0_0_35px_#00f0ff]"
                            />
                        </motion.div>
                    )}

                    {/* TÍTULO Y SUBTÍTULO DEL RITUAL */}
                    <motion.div
                        initial={{ opacity: 0, y: -15 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center mb-3 sm:mb-4 z-30"
                    >
                        <div className="flex items-center justify-center gap-1.5 text-xs sm:text-sm font-black uppercase tracking-widest drop-shadow-lg">
                            {isClaim ? (
                                <>
                                    <Sparkles className="h-4 w-4 text-cyan-400 animate-spin" style={{ animationDuration: '3s' }} />
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-sky-100 to-blue-400 font-black tracking-widest">
                                        ¡Por el Poder de Grayskull!
                                    </span>
                                    <Sparkles className="h-4 w-4 text-sky-300 animate-spin" style={{ animationDuration: '3s' }} />
                                </>
                            ) : (
                                <>
                                    <Flame className="h-4 w-4 text-orange-400 animate-bounce" />
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-red-400 to-amber-300 font-black">
                                        Liberando de la Fortaleza
                                    </span>
                                    <Flame className="h-4 w-4 text-red-500 animate-bounce" />
                                </>
                            )}
                        </div>
                        <p className="text-[11px] text-slate-300 font-bold truncate max-w-xs mt-0.5 tracking-wider">
                            {isClaim ? '⚡ ¡YO TENGO EL PODER! ⚡' : '🔥 Desintegrando en cenizas de retorno'}
                        </p>
                    </motion.div>

                    {/* LA TARJETA CINEMÁTICA */}
                    <div className={`relative w-full aspect-[3/4] rounded-3xl overflow-hidden shadow-[0_0_60px_rgba(0,0,0,0.9)] border-2 bg-slate-950 flex flex-col justify-between p-3.5 sm:p-4 ${
                        isClaim ? 'border-cyan-400/60 shadow-[0_0_40px_rgba(6,182,212,0.4)]' : 'border-white/20'
                    }`}>
                        {/* IMAGEN DE LA FIGURA */}
                        <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-black/70 border border-white/10">
                            <MOTUImage
                                productId={product.id}
                                src={product.image_url}
                                alt={product.name}
                                className="max-h-[85%] max-w-[85%] object-contain drop-shadow-[0_20px_30px_rgba(0,0,0,0.95)]"
                            />

                            {/* Badge de Categoría */}
                            <div className="absolute top-2 left-2 px-2.5 py-1 rounded-lg bg-black/80 border border-white/20 text-[9px] font-black text-cyan-300 uppercase tracking-wider backdrop-blur-md">
                                {product.sub_category || (product.is_vintage ? 'Vintage' : 'MOTU Origins')}
                            </div>
                        </div>

                        {/* Pie de Tarjeta con Nombre */}
                        <div className="mt-2 text-center">
                            <h4 className="text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-md">
                                {product.name}
                            </h4>
                        </div>

                        {/* ⚡ ESCENA A: ENERGÍA Y RAYO AZUL HACIA EL CIELO (CLAIM) */}
                        {isClaim && (
                            <>
                                {/* Aura perimetral de energía azul eléctrico / cian */}
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: [0.5, 1, 0.7] }}
                                    transition={{ duration: 0.5, repeat: Infinity }}
                                    className="absolute inset-0 rounded-3xl border-4 border-cyan-400 shadow-[0_0_35px_#00f0ff] pointer-events-none"
                                />

                                {/* Corriente ascendente de plasma azul hacia la espada */}
                                <motion.div
                                    initial={{ y: '100%', opacity: 0.9 }}
                                    animate={{ y: '-100%', opacity: [0, 1, 0] }}
                                    transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
                                    className="absolute inset-0 bg-gradient-to-t from-transparent via-cyan-400/50 to-sky-300/70 pointer-events-none blur-sm"
                                />
                            </>
                        )}

                        {/* 🔥 ESCENA B: DESINTEGRACIÓN EN CENIZAS (BURN / RELEASE) */}
                        {!isClaim && (
                            <>
                                {/* Máscara de fuego y cenizas que consume de arriba a abajo */}
                                <div
                                    className="absolute inset-0 pointer-events-none z-20 overflow-hidden rounded-3xl"
                                    style={{
                                        background: `linear-gradient(to bottom, rgba(10, 10, 10, 0.98) 0%, rgba(15, 15, 15, 0.95) ${burnProgress}%, transparent ${burnProgress + 6}%)`
                                    }}
                                >
                                    {/* Borde de fuego vivo en la línea de combustión */}
                                    {burnProgress > 0 && burnProgress < 100 && (
                                        <div
                                            className="absolute w-full h-10 -translate-y-1/2 bg-gradient-to-b from-orange-500 via-yellow-200 to-red-600 shadow-[0_0_30px_#ea580c] opacity-95 flex items-center justify-around"
                                            style={{ top: `${burnProgress}%` }}
                                        >
                                            <Flame className="h-6 w-6 text-yellow-100 fill-yellow-200 animate-bounce" />
                                            <Flame className="h-7 w-7 text-amber-200 fill-orange-400 animate-pulse" />
                                            <Flame className="h-6 w-6 text-yellow-100 fill-yellow-200 animate-bounce" />
                                        </div>
                                    )}
                                </div>

                                {/* Textura de carbón ardiente y humo sobre la parte consumida */}
                                <div
                                    className="absolute inset-0 pointer-events-none z-10"
                                    style={{
                                        opacity: Math.min(1, burnProgress / 50),
                                        background: 'radial-gradient(circle, rgba(220, 38, 38, 0.35) 0%, rgba(0, 0, 0, 0.8) 75%)'
                                    }}
                                />
                            </>
                        )}
                    </div>

                    {/* PIE DE ESTADO DEL RITUAL */}
                    <div className="mt-3.5 flex items-center gap-2">
                        {isClaim ? (
                            <div className="px-4 py-1.5 rounded-full bg-cyan-500/20 border border-cyan-400/60 text-cyan-300 text-xs font-black uppercase tracking-widest flex items-center gap-2 shadow-[0_0_25px_rgba(6,182,212,0.4)]">
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
