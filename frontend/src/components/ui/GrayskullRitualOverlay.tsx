import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Shield, Sparkles, Flame } from 'lucide-react';
import { MOTUImage } from './MOTUImage';
import type { RitualPayload } from '../../context/GrayskullRitualContext';

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
            // Sonido de Rayo y Poder: Creciente de energía y trueno
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(80, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 1.2);
            osc.frequency.exponentialRampToValueAtTime(110, ctx.currentTime + 1.8);

            gain.gain.setValueAtTime(0.01, ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 1.2);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.0);

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 2.1);
        } else {
            // Sonido de Cremación y Ceniza: Ruido blanco filtrado simulando fuego
            const bufferSize = ctx.sampleRate * 2;
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }

            const noise = ctx.createBufferSource();
            noise.buffer = buffer;

            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(800, ctx.currentTime);
            filter.frequency.linearRampToValueAtTime(150, ctx.currentTime + 2.0);

            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.12, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.0);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            noise.start();
            noise.stop(ctx.currentTime + 2.1);
        }
    } catch {
        // Si el navegador bloquea audio automático, continuar visualmente sin interrupción
    }
};

export const GrayskullRitualOverlay: React.FC<GrayskullRitualOverlayProps> = ({ ritual, onFinish }) => {
    const { type, product } = ritual;
    const isClaim = type === 'claim';
    const [phase, setPhase] = useState<'intro' | 'active' | 'climax' | 'exit'>('intro');
    const [burnProgress, setBurnProgress] = useState(0); // 0% a 100% para la cremación

    useEffect(() => {
        playAudioEffect(type);

        // Fase 1: Intro (0s -> 0.4s)
        const t1 = setTimeout(() => setPhase('active'), 400);

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

        // Fase 2: Clímax (1.3s -> Rayo de la Espada o Cenizas totales)
        const t2 = setTimeout(() => setPhase('climax'), 1300);

        // Fase 3: Exit (2.0s)
        const t3 = setTimeout(() => setPhase('exit'), 2000);

        // Finalización y retorno (2.3s)
        const t4 = setTimeout(() => {
            if (burnInterval) clearInterval(burnInterval);
            onFinish();
        }, 2300);

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
            <div className="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/90 backdrop-blur-2xl overflow-hidden select-none">
                {/* 1. Fondo Ambiental Dinámico */}
                {isClaim ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{
                            opacity: phase === 'climax' ? 0.9 : 0.4,
                            scale: phase === 'climax' ? [1, 1.2, 1] : 1
                        }}
                        transition={{ duration: 0.8 }}
                        className="absolute inset-0 bg-radial from-emerald-500/30 via-cyan-950/20 to-black pointer-events-none"
                    />
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{
                            opacity: phase === 'climax' ? 0.8 : 0.5,
                            scale: phase === 'climax' ? [1, 1.15, 1] : 1
                        }}
                        transition={{ duration: 0.8 }}
                        className="absolute inset-0 bg-radial from-orange-600/30 via-red-950/25 to-black pointer-events-none"
                    />
                )}

                {/* 2. Partículas Cósmicas / Cenizas Flotantes */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {Array.from({ length: 24 }).map((_, i) => (
                        <motion.div
                            key={i}
                            initial={{
                                x: `${(i * 17) % 100}vw`,
                                y: isClaim ? '110vh' : '40vh',
                                opacity: 0,
                                scale: Math.random() * 0.8 + 0.4
                            }}
                            animate={{
                                y: isClaim ? '-10vh' : '-20vh',
                                opacity: [0, 0.8, 0],
                                x: `calc(${(i * 17) % 100}vw + ${(i % 2 === 0 ? 1 : -1) * 40}px)`
                            }}
                            transition={{
                                duration: Math.random() * 1.5 + 1.2,
                                repeat: Infinity,
                                delay: Math.random() * 0.8
                            }}
                            className={`absolute w-2.5 h-2.5 rounded-full blur-[1px] ${
                                isClaim
                                    ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                                    : 'bg-amber-500 shadow-[0_0_8px_#f97316]'
                            }`}
                        />
                    ))}
                </div>

                {/* 3. CONTENEDOR PRINCIPAL: Tarjeta Centrada en Zoom Responsive */}
                <motion.div
                    initial={{ scale: 0.7, opacity: 0, y: 30 }}
                    animate={{
                        scale: phase === 'climax' ? (isClaim ? 1.05 : 0.95) : 1,
                        opacity: phase === 'exit' ? 0 : 1,
                        y: phase === 'exit' ? (isClaim ? -30 : 20) : 0
                    }}
                    transition={{ type: 'spring', stiffness: 300, damping: 22 }}
                    className="relative w-full max-w-[320px] sm:max-w-[360px] flex flex-col items-center z-10"
                >
                    {/* TÍTULO DEL RITUAL */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center mb-3 sm:mb-4"
                    >
                        <div className="flex items-center justify-center gap-1.5 text-xs sm:text-sm font-black uppercase tracking-widest drop-shadow-md">
                            {isClaim ? (
                                <>
                                    <Sparkles className="h-4 w-4 text-emerald-400 animate-spin" style={{ animationDuration: '4s' }} />
                                    <span className="text-emerald-300">¡Por el Poder de Grayskull!</span>
                                    <Sparkles className="h-4 w-4 text-amber-400 animate-spin" style={{ animationDuration: '4s' }} />
                                </>
                            ) : (
                                <>
                                    <Flame className="h-4 w-4 text-orange-400 animate-bounce" />
                                    <span className="text-orange-400">Liberando de la Fortaleza</span>
                                    <Flame className="h-4 w-4 text-red-400 animate-bounce" />
                                </>
                            )}
                        </div>
                        <p className="text-[11px] text-slate-300 font-semibold truncate max-w-xs mt-0.5">
                            {isClaim ? 'Asegurando en tu Colección Sagrada' : 'De vuelta a los Catálogos de Eternia'}
                        </p>
                    </motion.div>

                    {/* LA TARJETA CINEMÁTICA */}
                    <div className="relative w-full aspect-[3/4] rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)] border-2 border-white/20 bg-slate-950 flex flex-col justify-between p-3.5 sm:p-4">
                        {/* IMAGEN DE LA FIGURA */}
                        <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-black/60 border border-white/10">
                            <MOTUImage
                                productId={product.id}
                                src={product.image_url}
                                alt={product.name}
                                className="max-h-[85%] max-w-[85%] object-contain drop-shadow-[0_15px_25px_rgba(0,0,0,0.9)]"
                            />

                            {/* Badge de Categoría */}
                            <div className="absolute top-2 left-2 px-2.5 py-1 rounded-lg bg-black/75 border border-white/20 text-[9px] font-black text-amber-300 uppercase tracking-wider backdrop-blur-md">
                                {product.sub_category || (product.is_vintage ? 'Vintage' : 'MOTU Origins')}
                            </div>
                        </div>

                        {/* Pie de Tarjeta con Nombre */}
                        <div className="mt-2 text-center">
                            <h4 className="text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-sm">
                                {product.name}
                            </h4>
                        </div>

                        {/* ⚡ ESCENA A: RAYO Y PODER DE GRAYSKULL (CLAIM) */}
                        {isClaim && (
                            <>
                                {/* Corriente eléctrica que recorre de abajo hacia arriba los bordes */}
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: [0.3, 1, 0.7] }}
                                    transition={{ duration: 0.6, repeat: Infinity }}
                                    className="absolute inset-0 rounded-3xl border-4 border-emerald-400 shadow-[0_0_30px_#10b981] pointer-events-none"
                                />

                                {/* Flujo ascendente de plasma */}
                                <motion.div
                                    initial={{ y: '100%', opacity: 0.8 }}
                                    animate={{ y: '-100%', opacity: [0, 1, 0] }}
                                    transition={{ duration: 1.1, repeat: Infinity, ease: 'linear' }}
                                    className="absolute inset-0 bg-gradient-to-t from-transparent via-emerald-400/40 to-cyan-300/60 pointer-events-none blur-sm"
                                />

                                {/* Rayo Celestial de la Espada de Grayskull que impacta en el Clímax */}
                                {phase === 'climax' && (
                                    <motion.div
                                        initial={{ opacity: 0, scaleY: 0 }}
                                        animate={{ opacity: 1, scaleY: 1 }}
                                        exit={{ opacity: 0 }}
                                        transition={{ duration: 0.2 }}
                                        className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-30"
                                    >
                                        {/* Haz de luz de la Espada */}
                                        <div className="w-4 h-full bg-gradient-to-b from-white via-yellow-300 to-emerald-400 shadow-[0_0_50px_#fef08a] rounded-full animate-pulse" />
                                        <div className="absolute top-1/2 -translate-y-1/2 p-4 rounded-full bg-black/80 border-2 border-yellow-300 shadow-[0_0_40px_#fde047]">
                                            <Zap className="h-12 w-12 text-yellow-300 fill-yellow-400 animate-bounce drop-shadow-[0_0_20px_#eab308]" />
                                        </div>
                                    </motion.div>
                                )}
                            </>
                        )}

                        {/* 🔥 ESCENA B: DESINTEGRACIÓN EN CENIZAS (BURN / RELEASE) */}
                        {!isClaim && (
                            <>
                                {/* Máscara de fuego y cenizas que consume de arriba a abajo */}
                                <div
                                    className="absolute inset-0 pointer-events-none z-20 overflow-hidden rounded-3xl"
                                    style={{
                                        background: `linear-gradient(to bottom, rgba(15, 15, 15, 0.96) 0%, rgba(20, 20, 20, 0.94) ${burnProgress}%, transparent ${burnProgress + 5}%)`
                                    }}
                                >
                                    {/* Borde ardiente de fuego en la línea de corte */}
                                    {burnProgress > 0 && burnProgress < 100 && (
                                        <div
                                            className="absolute w-full h-8 -translate-y-1/2 bg-gradient-to-b from-orange-500 via-amber-300 to-red-600 shadow-[0_0_25px_#f97316] opacity-90 blur-[1px] flex items-center justify-around"
                                            style={{ top: `${burnProgress}%` }}
                                        >
                                            <Flame className="h-5 w-5 text-yellow-200 fill-yellow-300 animate-bounce" />
                                            <Flame className="h-6 w-6 text-amber-200 fill-orange-400 animate-pulse" />
                                            <Flame className="h-5 w-5 text-yellow-200 fill-yellow-300 animate-bounce" />
                                        </div>
                                    )}
                                </div>

                                {/* Textura de grietas de brasas y ceniza sobre la parte quemada */}
                                <div
                                    className="absolute inset-0 pointer-events-none z-10"
                                    style={{
                                        opacity: Math.min(1, burnProgress / 60),
                                        background: 'radial-gradient(circle, rgba(239, 68, 68, 0.25) 0%, rgba(0, 0, 0, 0.6) 70%)'
                                    }}
                                />
                            </>
                        )}
                    </div>

                    {/* PIE DE ESTADO DEL RITUAL */}
                    <div className="mt-3 flex items-center gap-2">
                        {isClaim ? (
                            <div className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-black uppercase tracking-widest flex items-center gap-1.5 shadow-lg shadow-emerald-500/10">
                                <Shield className="h-3.5 w-3.5 fill-emerald-400" />
                                <span>Reliquia Asegurada</span>
                            </div>
                        ) : (
                            <div className="px-3 py-1 rounded-full bg-orange-500/20 border border-orange-500/40 text-orange-300 text-xs font-black uppercase tracking-widest flex items-center gap-1.5 shadow-lg shadow-orange-500/10">
                                <Flame className="h-3.5 w-3.5 fill-orange-400" />
                                <span>Desintegrando en Cenizas</span>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default GrayskullRitualOverlay;
