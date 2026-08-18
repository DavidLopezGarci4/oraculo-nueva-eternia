import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Sparkles, Flame } from 'lucide-react';
import { MOTUImage } from './MOTUImage';
import type { RitualPayload } from '../../context/GrayskullRitualContext';
import modernSwordAsset from '../../assets/HemanGlassmorphSword.webp';
import vintageSwordAsset from '../../assets/GlassmorphSwordHeMan.webp';

interface GrayskullRitualOverlayProps {
    ritual: RitualPayload;
    onFinish: () => void;
}

// Generador de efectos de sonido sintéticos mediante Web Audio API (100% nativo, 0 dependencias externas)
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
            osc.frequency.setValueAtTime(110, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 1.1);
            osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 1.8);

            gain.gain.setValueAtTime(0.02, ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.25, ctx.currentTime + 1.1);
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
        // Si el navegador bloquea audio automático, continuar visualmente sin interrupción
    }
};

export const GrayskullRitualOverlay: React.FC<GrayskullRitualOverlayProps> = ({ ritual, onFinish }) => {
    const { type, product } = ritual;
    const isClaim = type === 'claim';
    const swordAsset = product.is_vintage ? vintageSwordAsset : modernSwordAsset;

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

        // Fase 2: Clímax (1.2s -> El Rayo Cósmico de la Espada se eleva al cielo)
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
                {/* 1. Fondo Atmosférico de Grayskull / Infierno de Cenizas */}
                {isClaim ? (
                    <>
                        {/* Cielo tormentoso esmeralda de Grayskull */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.95 : 0.4,
                                scale: phase === 'climax' ? [1, 1.25, 1.1] : 1
                            }}
                            transition={{ duration: 0.6 }}
                            className="absolute inset-0 bg-gradient-to-t from-emerald-950 via-teal-950/40 to-black pointer-events-none"
                        />
                        {/* Relámpagos de fondo en el cielo */}
                        <motion.div
                            animate={{
                                opacity: phase === 'climax' ? [0, 1, 0.3, 1, 0] : [0, 0.2, 0]
                            }}
                            transition={{ duration: 0.8, repeat: phase === 'climax' ? 2 : Infinity }}
                            className="absolute inset-0 bg-radial from-emerald-400/30 via-yellow-200/10 to-transparent pointer-events-none"
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

                {/* 2. Rayo Celestial Disparado Hacia el Cielo (Claim - Desde la Espada hacia arriba) */}
                {isClaim && (phase === 'climax' || phase === 'raising') && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{
                            height: phase === 'climax' ? '65vh' : '25vh',
                            opacity: phase === 'climax' ? [0.8, 1, 0.9] : 0.5
                        }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        className="absolute top-0 left-1/2 -translate-x-1/2 w-8 sm:w-16 flex flex-col items-center pointer-events-none z-40"
                    >
                        {/* Columna central de plasma puro */}
                        <div className="w-full h-full bg-gradient-to-t from-yellow-300 via-emerald-300 to-white blur-[2px] shadow-[0_0_80px_#34d399]" />
                        {/* Haces exteriores de relámpago */}
                        <div className="absolute inset-0 w-full h-full bg-gradient-to-t from-transparent via-cyan-400 to-white blur-md opacity-80 animate-pulse" />
                        {/* Explosión cósmica en el cielo superior */}
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: [1, 2.5, 2], opacity: [0.8, 1, 0.7] }}
                            transition={{ duration: 0.5, repeat: Infinity }}
                            className="absolute -top-10 w-48 sm:w-72 h-48 sm:h-72 rounded-full bg-radial from-white via-yellow-300/80 to-emerald-500/0 blur-xl"
                        />
                    </motion.div>
                )}

                {/* 3. Partículas Cósmicas / Cenizas Flotantes */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {Array.from({ length: 30 }).map((_, i) => (
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
                                duration: Math.random() * 1.6 + 1.0,
                                repeat: Infinity,
                                delay: Math.random() * 0.7
                            }}
                            className={`absolute rounded-full ${
                                isClaim
                                    ? 'w-2 h-2 bg-yellow-200 blur-[0.5px] shadow-[0_0_10px_#fde047]'
                                    : 'w-2.5 h-2.5 bg-orange-500 blur-[1px] shadow-[0_0_10px_#ea580c]'
                            }`}
                        />
                    ))}
                </div>

                {/* 4. CONTENEDOR PRINCIPAL: Tarjeta y Espada de Grayskull */}
                <motion.div
                    initial={{ scale: 0.75, opacity: 0, y: 30 }}
                    animate={{
                        scale: phase === 'climax' ? (isClaim ? 1.04 : 0.95) : 1,
                        opacity: phase === 'exit' ? 0 : 1,
                        y: phase === 'exit' ? (isClaim ? -40 : 30) : 0
                    }}
                    transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                    className="relative w-full max-w-[320px] sm:max-w-[360px] flex flex-col items-center z-20 mt-4 sm:mt-8"
                >
                    {/* 🗡️ LA ESPADA DE GRAYSKULL APUNTANDO AL CIELO (Solo en Claim) */}
                    {isClaim && (
                        <motion.div
                            initial={{ y: 50, opacity: 0, scale: 0.8 }}
                            animate={{
                                y: phase === 'climax' ? -25 : -10,
                                opacity: 1,
                                scale: phase === 'climax' ? 1.15 : 1
                            }}
                            transition={{ duration: 0.5, ease: 'easeOut' }}
                            className="relative z-50 -mb-10 flex flex-col items-center drop-shadow-[0_0_35px_rgba(52,211,153,0.9)]"
                        >
                            <img
                                src={swordAsset}
                                alt="Espada de Poder de Grayskull"
                                className="h-32 sm:h-40 w-auto object-contain filter drop-shadow-[0_0_20px_#fde047]"
                            />
                            {/* Chispas de energía en la punta de la espada */}
                            <motion.div
                                animate={{ scale: [1, 1.8, 1], opacity: [0.6, 1, 0.7] }}
                                transition={{ duration: 0.3, repeat: Infinity }}
                                className="absolute top-0 w-8 h-8 rounded-full bg-radial from-white via-yellow-300 to-emerald-400 blur-sm shadow-[0_0_25px_#ffffff]"
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
                                    <Sparkles className="h-4 w-4 text-emerald-400 animate-spin" style={{ animationDuration: '3s' }} />
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-yellow-200 to-emerald-400 font-black">
                                        ¡Por el Poder de Grayskull!
                                    </span>
                                    <Sparkles className="h-4 w-4 text-yellow-300 animate-spin" style={{ animationDuration: '3s' }} />
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
                    <div className="relative w-full aspect-[3/4] rounded-3xl overflow-hidden shadow-[0_0_60px_rgba(0,0,0,0.9)] border-2 border-white/20 bg-slate-950 flex flex-col justify-between p-3.5 sm:p-4">
                        {/* IMAGEN DE LA FIGURA */}
                        <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-black/70 border border-white/10">
                            <MOTUImage
                                productId={product.id}
                                src={product.image_url}
                                alt={product.name}
                                className="max-h-[85%] max-w-[85%] object-contain drop-shadow-[0_20px_30px_rgba(0,0,0,0.95)]"
                            />

                            {/* Badge de Categoría */}
                            <div className="absolute top-2 left-2 px-2.5 py-1 rounded-lg bg-black/80 border border-white/20 text-[9px] font-black text-amber-300 uppercase tracking-wider backdrop-blur-md">
                                {product.sub_category || (product.is_vintage ? 'Vintage' : 'MOTU Origins')}
                            </div>
                        </div>

                        {/* Pie de Tarjeta con Nombre */}
                        <div className="mt-2 text-center">
                            <h4 className="text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-md">
                                {product.name}
                            </h4>
                        </div>

                        {/* ⚡ ESCENA A: ENERGÍA Y RAYO HACIA EL CIELO (CLAIM) */}
                        {isClaim && (
                            <>
                                {/* Aura perimetral de energía esmeralda */}
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: [0.5, 1, 0.7] }}
                                    transition={{ duration: 0.5, repeat: Infinity }}
                                    className="absolute inset-0 rounded-3xl border-4 border-emerald-400 shadow-[0_0_35px_#10b981] pointer-events-none"
                                />

                                {/* Corriente ascendente hacia la espada */}
                                <motion.div
                                    initial={{ y: '100%', opacity: 0.9 }}
                                    animate={{ y: '-100%', opacity: [0, 1, 0] }}
                                    transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
                                    className="absolute inset-0 bg-gradient-to-t from-transparent via-emerald-400/50 to-yellow-300/70 pointer-events-none blur-sm"
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
                            <div className="px-4 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/50 text-emerald-300 text-xs font-black uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                                <Shield className="h-4 w-4 fill-emerald-400" />
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
