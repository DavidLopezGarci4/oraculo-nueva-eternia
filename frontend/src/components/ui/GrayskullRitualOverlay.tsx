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

// Motor de Efectos de Sonido Cinemáticos HD (Multicapa, Estéreo, Cero Dependencias Externas)
const playAudioEffect = (type: 'claim' | 'burn') => {
    try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) return;
        const ctx = new AudioContextClass();
        const now = ctx.currentTime;

        if (type === 'claim') {
            // === RITUAL DE PODER DE GRAYSKULL (CLAIM) ===
            
            // Capa 1: Sub-bass Rumble & Impacto del Castillo (60Hz -> 35Hz)
            const subOsc = ctx.createOscillator();
            const subGain = ctx.createGain();
            subOsc.type = 'sine';
            subOsc.frequency.setValueAtTime(80, now);
            subOsc.frequency.exponentialRampToValueAtTime(35, now + 1.6);
            subGain.gain.setValueAtTime(0.35, now);
            subGain.gain.exponentialRampToValueAtTime(0.001, now + 2.2);
            subOsc.connect(subGain);
            subGain.connect(ctx.destination);
            subOsc.start(now);
            subOsc.stop(now + 2.3);

            // Capa 2: Ascenso de Energía Cósmica de la Espada (Sawtooth + Triangle Shimmer)
            const swordOsc = ctx.createOscillator();
            const swordGain = ctx.createGain();
            swordOsc.type = 'sawtooth';
            swordOsc.frequency.setValueAtTime(140, now);
            swordOsc.frequency.exponentialRampToValueAtTime(1450, now + 1.0);
            swordOsc.frequency.exponentialRampToValueAtTime(120, now + 2.1);
            swordGain.gain.setValueAtTime(0.01, now);
            swordGain.gain.linearRampToValueAtTime(0.22, now + 0.9);
            swordGain.gain.exponentialRampToValueAtTime(0.001, now + 2.3);
            swordOsc.connect(swordGain);
            swordGain.connect(ctx.destination);
            swordOsc.start(now);
            swordOsc.stop(now + 2.4);

            // Capa 3: Trueno y Rayo de Plasma en el Clímax (1.0s)
            setTimeout(() => {
                try {
                    const thunderBuffer = ctx.createBuffer(1, ctx.sampleRate * 1.5, ctx.sampleRate);
                    const data = thunderBuffer.getChannelData(0);
                    for (let i = 0; i < data.length; i++) {
                        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.4));
                    }
                    const noise = ctx.createBufferSource();
                    noise.buffer = thunderBuffer;
                    const bpf = ctx.createBiquadFilter();
                    bpf.type = 'bandpass';
                    bpf.frequency.setValueAtTime(600, ctx.currentTime);
                    bpf.frequency.exponentialRampToValueAtTime(90, ctx.currentTime + 1.2);
                    const tGain = ctx.createGain();
                    tGain.gain.setValueAtTime(0.38, ctx.currentTime);
                    tGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.4);
                    noise.connect(bpf);
                    bpf.connect(tGain);
                    tGain.connect(ctx.destination);
                    noise.start();
                } catch {}
            }, 900);

            // Capa 4: Armónicos Sagrados de Grayskull (Campana Cósmica en Fa sostenido)
            [554.37, 830.61, 1108.73, 1661.22].forEach((freq, idx) => {
                const chimeOsc = ctx.createOscillator();
                const chimeGain = ctx.createGain();
                chimeOsc.type = 'triangle';
                chimeOsc.frequency.setValueAtTime(freq, now + 0.95);
                chimeGain.gain.setValueAtTime(0.0, now);
                chimeGain.gain.setValueAtTime(0.08 / (idx + 1), now + 1.0);
                chimeGain.gain.exponentialRampToValueAtTime(0.0001, now + 2.2);
                chimeOsc.connect(chimeGain);
                chimeGain.connect(ctx.destination);
                chimeOsc.start(now + 0.95);
                chimeOsc.stop(now + 2.3);
            });

        } else {
            // === RITUAL DE CREMACIÓN / LIBERACIÓN DE LA FORTALEZA (BURN) ===
            
            // Capa 1: Remolino de Vórtice y Succión (180Hz -> 45Hz)
            const whooshOsc = ctx.createOscillator();
            const whooshGain = ctx.createGain();
            whooshOsc.type = 'sine';
            whooshOsc.frequency.setValueAtTime(220, now);
            whooshOsc.frequency.exponentialRampToValueAtTime(40, now + 1.8);
            whooshGain.gain.setValueAtTime(0.25, now);
            whooshGain.gain.exponentialRampToValueAtTime(0.001, now + 2.1);
            whooshOsc.connect(whooshGain);
            whooshGain.connect(ctx.destination);
            whooshOsc.start(now);
            whooshOsc.stop(now + 2.2);

            // Capa 2: Combustión e Incineración (Ruido blanco modulado y filtrado)
            const bufferSize = ctx.sampleRate * 2.3;
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                // Simulación de chispas y crepitar de fuego
                const spark = Math.random() > 0.985 ? (Math.random() * 2 - 1) * 1.5 : 0;
                data[i] = (Math.random() * 2 - 1) * 0.4 + spark;
            }

            const noise = ctx.createBufferSource();
            noise.buffer = buffer;

            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(1100, now);
            filter.frequency.linearRampToValueAtTime(120, now + 2.0);

            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.22, now);
            gain.gain.linearRampToValueAtTime(0.30, now + 0.7);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 2.2);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            noise.start(now);
            noise.stop(now + 2.3);
        }
    } catch {
        // Fallback silencioso si las políticas del navegador bloquean audio no interactivo
    }
};

export const GrayskullRitualOverlay: React.FC<GrayskullRitualOverlayProps> = ({ ritual, onFinish }) => {
    const { type, product } = ritual;
    const isClaim = type === 'claim';

    const [phase, setPhase] = useState<'intro' | 'raising' | 'climax' | 'exit'>('intro');
    const [burnProgress, setBurnProgress] = useState(0); // 0% a 100% para la cremación

    useEffect(() => {
        playAudioEffect(type);

        // Fase 1: Intro (0s -> 0.3s)
        const t1 = setTimeout(() => setPhase('raising'), 300);

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

        // Fase 2: Clímax (1.0s -> Los rayos se unen en el centro superior y el gran rayo azul se dispara al cielo)
        const t2 = setTimeout(() => setPhase('climax'), 1000);

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
            <div 
                onClick={onFinish}
                className="fixed inset-0 z-[300] flex flex-col items-center justify-center p-3 sm:p-6 bg-black/95 backdrop-blur-3xl overflow-hidden select-none cursor-pointer"
                title="Toca o haz clic para omitir"
            >
                {/* 1. FONDO ATMOSFÉRICO DE GRAYSKULL / INFIERNO */}
                {isClaim ? (
                    <>
                        {/* Cielo tormentoso azul eléctrico de Grayskull */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.95 : 0.45,
                                scale: phase === 'climax' ? [1, 1.15, 1.08] : 1
                            }}
                            transition={{ duration: 0.6 }}
                            className="absolute inset-0 bg-gradient-to-t from-slate-950 via-sky-950/60 to-black pointer-events-none"
                        />
                        {/* Relámpagos celestes de fondo */}
                        <motion.div
                            animate={{
                                opacity: phase === 'climax' ? [0, 1, 0.4, 1, 0] : [0, 0.2, 0]
                            }}
                            transition={{ duration: 0.7, repeat: phase === 'climax' ? 2 : Infinity }}
                            className="absolute inset-0 bg-radial from-cyan-400/30 via-sky-300/10 to-transparent pointer-events-none"
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

                {/* 2. PARTÍCULAS CÓSMICAS AZULES / CENIZAS FLOTANTES */}
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

                {/* 3. TÍTULO Y SUBTÍTULO DEL RITUAL (DESPEJADO ARRIBA) */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-3 sm:mb-5 z-40"
                >
                    <div className="flex items-center justify-center gap-2 text-xs sm:text-sm font-black uppercase tracking-widest drop-shadow-lg">
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
                    <p className="text-[11px] text-cyan-200/90 font-bold tracking-widest mt-1">
                        {isClaim ? '⚡ ¡YO TENGO EL PODER! ⚡' : '🔥 Desintegrando en cenizas de retorno'}
                    </p>
                </motion.div>

                {/* 4. CONTENEDOR PRINCIPAL: Tarjeta con Portal Detrás y Rayos en los Bordes */}
                <motion.div
                    initial={{ scale: 0.75, opacity: 0, y: 30 }}
                    animate={{
                        scale: phase === 'climax' ? (isClaim ? 1.04 : 0.95) : 1,
                        opacity: phase === 'exit' ? 0 : 1,
                        y: phase === 'exit' ? (isClaim ? -40 : 30) : 0
                    }}
                    transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                    className="relative w-full max-w-[310px] sm:max-w-[340px] flex flex-col items-center z-20"
                >
                    {/* 🛡️ FONDO ÉPICO DETRÁS DE LA TARJETA: He-Man alzando la Espada en Grayskull */}
                    {isClaim && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{
                                opacity: phase === 'climax' ? 0.45 : 0.3,
                                scale: phase === 'climax' ? 1.08 : 1
                            }}
                            transition={{ duration: 0.6 }}
                            className="absolute -inset-6 sm:-inset-10 rounded-3xl overflow-hidden -z-10 flex items-center justify-center pointer-events-none"
                        >
                            <img
                                src={hemanLightningArt}
                                alt="He-Man y Castillo Grayskull"
                                className="w-full h-full object-cover filter saturate-150 brightness-75 blur-[1px]"
                            />
                            {/* Halo azul envolvente */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black via-cyan-950/40 to-black/80" />
                            <div className="absolute inset-0 border border-cyan-400/30 rounded-3xl shadow-[0_0_50px_rgba(6,182,212,0.3)]" />
                        </motion.div>
                    )}

                    {/* ⚡ 5. RAYO AZUL ELÉCTRICO BROTANDO DESDE EL CENTRO SUPERIOR AL CIELO */}
                    {isClaim && phase === 'climax' && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: '65vh', opacity: [0.9, 1, 0.95] }}
                            transition={{ duration: 0.35, ease: 'easeOut' }}
                            className="absolute bottom-full left-1/2 -translate-x-1/2 w-12 sm:w-20 flex flex-col items-center pointer-events-none z-50 -mb-2"
                        >
                            {/* Columna central de plasma azul eléctrico y blanco */}
                            <div className="w-full h-full bg-gradient-to-t from-white via-cyan-400 to-sky-300 blur-[2px] shadow-[0_0_90px_#00f0ff]" />
                            {/* Haces exteriores de relámpago */}
                            <div className="absolute inset-0 w-full h-full bg-gradient-to-t from-cyan-200 via-blue-500 to-transparent blur-md opacity-90 animate-pulse" />
                            {/* Explosión cósmica en el cielo superior */}
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: [1, 2.5, 2], opacity: [0.8, 1, 0.7] }}
                                transition={{ duration: 0.4, repeat: Infinity }}
                                className="absolute -top-12 w-56 sm:w-80 h-56 sm:h-80 rounded-full bg-radial from-white via-cyan-300/90 to-blue-600/0 blur-2xl"
                            />
                        </motion.div>
                    )}

                    {/* ⚡ NÚCLEO DE GRAYSKULL EN EL CENTRO DEL TOPE SUPERIOR */}
                    {isClaim && (phase === 'raising' || phase === 'climax') && (
                        <motion.div
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{
                                scale: phase === 'climax' ? [1.2, 2.2, 1.6] : 1,
                                opacity: 1
                            }}
                            transition={{ duration: 0.3 }}
                            className="absolute -top-3 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-radial from-white via-cyan-300 to-blue-600 blur-sm shadow-[0_0_35px_#00f0ff] z-50 pointer-events-none"
                        />
                    )}

                    {/* LA TARJETA CINEMÁTICA */}
                    <div className={`relative w-full aspect-[3/4] rounded-3xl overflow-hidden shadow-[0_0_60px_rgba(0,0,0,0.95)] border-2 bg-slate-950 flex flex-col justify-between p-3.5 sm:p-4 z-20 ${
                        isClaim ? 'border-cyan-400/80 shadow-[0_0_45px_rgba(6,182,212,0.6)]' : 'border-white/20'
                    }`}>
                        {/* IMAGEN DE LA FIGURA */}
                        <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-black/75 border border-white/10">
                            <MOTUImage
                                productId={product.id}
                                src={product.image_url}
                                alt={product.name}
                                className="max-h-[85%] max-w-[85%] object-contain drop-shadow-[0_20px_30px_rgba(0,0,0,0.95)]"
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

                        {/* ⚡ ESCENA A: RAYOS AZULES FLUYENDO POR LOS BORDES HACIA EL TOPE SUPERIOR */}
                        {isClaim && (
                            <>
                                {/* Rayo Borde Izquierdo (Sube de abajo hacia arriba) */}
                                <motion.div
                                    initial={{ height: 0 }}
                                    animate={{ height: '100%' }}
                                    transition={{ duration: 0.6, ease: 'easeOut' }}
                                    className="absolute left-0 bottom-0 w-1.5 bg-gradient-to-t from-cyan-500 via-sky-300 to-white shadow-[0_0_15px_#00f0ff] pointer-events-none z-30"
                                />

                                {/* Rayo Borde Derecho (Sube de abajo hacia arriba) */}
                                <motion.div
                                    initial={{ height: 0 }}
                                    animate={{ height: '100%' }}
                                    transition={{ duration: 0.6, ease: 'easeOut' }}
                                    className="absolute right-0 bottom-0 w-1.5 bg-gradient-to-t from-cyan-500 via-sky-300 to-white shadow-[0_0_15px_#00f0ff] pointer-events-none z-30"
                                />

                                {/* Rayo Borde Superior Izquierdo (Viaja hacia el centro) */}
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: '50%' }}
                                    transition={{ duration: 0.4, delay: 0.5, ease: 'easeOut' }}
                                    className="absolute top-0 left-0 h-1.5 bg-gradient-to-r from-sky-400 via-cyan-300 to-white shadow-[0_0_20px_#00f0ff] pointer-events-none z-30"
                                />

                                {/* Rayo Borde Superior Derecho (Viaja hacia el centro) */}
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: '50%' }}
                                    transition={{ duration: 0.4, delay: 0.5, ease: 'easeOut' }}
                                    className="absolute top-0 right-0 h-1.5 bg-gradient-to-l from-sky-400 via-cyan-300 to-white shadow-[0_0_20px_#00f0ff] pointer-events-none z-30"
                                />

                                {/* Aura luminosa de plasma por toda la tarjeta */}
                                <motion.div
                                    animate={{ opacity: phase === 'climax' ? [0.6, 1, 0.8] : 0.4 }}
                                    transition={{ duration: 0.3, repeat: Infinity }}
                                    className="absolute inset-0 rounded-3xl border-2 border-cyan-400/70 shadow-[inset_0_0_25px_rgba(6,182,212,0.5)] pointer-events-none"
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
