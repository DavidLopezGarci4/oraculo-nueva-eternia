import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import swordAsset from '../../assets/HemanGlassmorphSword.webp';
import vintageSwordAsset from '../../assets/GlassmorphSwordHeMan.webp';
import { getSystemSwordConfigs } from '../../api/admin';
import ProceduralLightningCanvas, { type LightningTheme } from './ProceduralLightningCanvas';

interface PowerSwordLoaderProps {
    className?: string;
    size?: number;
    text?: string;
    progress?: number; // 0 to 100
    variant?: 'inline' | 'fullScreen';
    isVintage?: boolean;
    vintageGuardX?: number;
    vintageGuardY?: number;
    vintageTipX?: number;
    vintageTipY?: number;
    isSkeletor?: boolean;
    skeletorGuardX?: number;
    skeletorGuardY?: number;
    skeletorTipX?: number;
    skeletorTipY?: number;
    modernGuardX?: number;
    modernGuardY?: number;
    modernTipX?: number;
    modernTipY?: number;
    disableRandom?: boolean;
}

const PowerSwordLoader: React.FC<PowerSwordLoaderProps> = ({
    className = '',
    size = 200,
    text,
    progress: manualProgress,
    variant = 'inline',
    isVintage = false,
    vintageGuardX,
    vintageGuardY,
    vintageTipX,
    vintageTipY,
    isSkeletor = false,
    skeletorGuardX,
    skeletorGuardY,
    skeletorTipX,
    skeletorTipY,
    modernGuardX,
    modernGuardY,
    modernTipX,
    modernTipY,
    disableRandom = false
}) => {
    const [internalProgress, setInternalProgress] = useState(0);

    // Random choice on mount between Vintage He-Man (vintage) and Modern He-Man (modern)
    const [randomTheme] = useState(() => Math.random() < 0.5 ? 'vintage' : 'modern');

    const activeIsSkeletor = disableRandom ? isSkeletor : (randomTheme === 'modern');
    const activeIsVintage = disableRandom ? isVintage : (randomTheme === 'vintage');
    const activeIsViolet = activeIsSkeletor || (!activeIsVintage);
    const lightningTheme: LightningTheme = activeIsSkeletor ? 'skeletor' : 'heman';

    const isFullScreen = variant === 'fullScreen';
    const activeSwordAsset = activeIsVintage ? vintageSwordAsset : swordAsset;

    // Get custom/stored vintage sword coordinates or use defaults
    const [vintageCoords, setVintageCoords] = useState({
        gX: 79.5,
        gY: 66.5,
        tX: 73.0,
        tY: 20.5
    });

    // Get custom/stored skeletor staff coordinates or use defaults
    const [skeletorCoords, setSkeletorCoords] = useState({
        gX: 125.0,
        gY: 175.0,
        tX: 125.0,
        tY: 10.0
    });

    // Get custom/stored modern sword coordinates or use defaults
    const [modernCoords, setModernCoords] = useState({
        gX: 125.0,
        gY: 175.0,
        tX: 125.0,
        tY: 10.0
    });

    const [loadedGlobal, setLoadedGlobal] = useState(false);

    // Cargar configuraciones globales desde el servidor
    useEffect(() => {
        const fetchGlobalConfigs = async () => {
            try {
                const configs = await getSystemSwordConfigs();
                if (configs && Object.keys(configs).length > 0) {
                    if (configs.vintage_sword_coords) {
                        setVintageCoords(configs.vintage_sword_coords);
                    }
                    if (configs.skeletor_sword_coords) {
                        setSkeletorCoords(configs.skeletor_sword_coords);
                    }
                    setLoadedGlobal(true);
                }
            } catch (e) {
                console.log("No se pudieron cargar las configuraciones de espadas globales o no hay sesión activa.", e);
            }
        };
        fetchGlobalConfigs();
    }, []);

    useEffect(() => {
        if (loadedGlobal) return;
        if (activeIsVintage) {
            const stored = localStorage.getItem('vintage_sword_coords');
            if (stored) {
                try {
                    setVintageCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse vintage sword coords", e);
                }
            }
        }
    }, [activeIsVintage, loadedGlobal]);

    useEffect(() => {
        if (loadedGlobal) return;
        if (activeIsSkeletor) {
            const stored = localStorage.getItem('skeletor_sword_coords');
            if (stored) {
                try {
                    setSkeletorCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse skeletor staff coords", e);
                }
            }
        }
    }, [activeIsSkeletor, loadedGlobal]);

    useEffect(() => {
        if (!activeIsVintage && !activeIsSkeletor) {
            const stored = localStorage.getItem('modern_sword_coords');
            if (stored) {
                try {
                    setModernCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse modern sword coords", e);
                }
            }
        }
    }, [activeIsVintage, activeIsSkeletor]);

    // Use props if provided (useful for visualizer), otherwise use state/localStorage, or fallback to defaults
    const activeGuardX = activeIsSkeletor 
        ? (skeletorGuardX !== undefined ? skeletorGuardX : skeletorCoords.gX) 
        : (activeIsVintage 
            ? (vintageGuardX !== undefined ? vintageGuardX : vintageCoords.gX) 
            : (modernGuardX !== undefined ? modernGuardX : modernCoords.gX));

    const activeGuardY = activeIsSkeletor 
        ? (skeletorGuardY !== undefined ? skeletorGuardY : skeletorCoords.gY) 
        : (activeIsVintage 
            ? (vintageGuardY !== undefined ? vintageGuardY : vintageCoords.gY) 
            : (modernGuardY !== undefined ? modernGuardY : modernCoords.gY));

    const activeTipX = activeIsSkeletor 
        ? (skeletorTipX !== undefined ? skeletorTipX : skeletorCoords.tX) 
        : (activeIsVintage 
            ? (vintageTipX !== undefined ? vintageTipX : vintageCoords.tX) 
            : (modernTipX !== undefined ? modernTipX : modernCoords.tX));

    const activeTipY = activeIsSkeletor 
        ? (skeletorTipY !== undefined ? skeletorTipY : skeletorCoords.tY) 
        : (activeIsVintage 
            ? (vintageTipY !== undefined ? vintageTipY : vintageCoords.tY) 
            : (modernTipY !== undefined ? modernTipY : modernCoords.tY));

    // Intelligent Progress Simulation (Trickle Strategy)
    useEffect(() => {
        if (manualProgress !== undefined) {
            setInternalProgress(manualProgress);
            return;
        }

        let timeoutId: any;

        const trickle = () => {
            setInternalProgress(prev => {
                if (prev >= 99) return 99; // Cap at 99 while waiting

                let inc = 0;
                if (prev < 40) inc = Math.random() * 8 + 3; // Fast initial burst
                else if (prev < 75) inc = Math.random() * 2 + 0.2; // Progressive steady move
                else if (prev < 95) inc = Math.random() * 0.4 + 0.05; // Dramatic slow down
                else inc = Math.random() * 0.02; // Very slow tail

                const next = prev + inc;
                return next >= 99 ? 99 : next;
            });

            // Randomize next tick for "organic" feel
            const nextTick = Math.random() * 150 + 50;
            timeoutId = setTimeout(trickle, nextTick);
        };

        trickle();
        return () => clearTimeout(timeoutId);
    }, [manualProgress]);

    const progress = manualProgress !== undefined ? manualProgress : internalProgress;

    const containerClasses = isFullScreen
        ? `fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#050608]`
        : `flex flex-col items-center justify-center gap-8 ${className}`;

    const svgWrapperStyles = isFullScreen
        ? { width: '100vw', height: '100vh', position: 'absolute' as const, inset: 0, opacity: 0.7 }
        : { width: size, height: size, position: 'relative' as const };

    return (
        <div className={containerClasses}>
            <style dangerouslySetInnerHTML={{__html: `
                @keyframes sword-blast-glow {
                    0% { filter: drop-shadow(0 0 10px rgba(14,165,233,0.5)); transform: scale(1); }
                    50% { filter: drop-shadow(0 0 35px rgba(14,165,233,0.85)) drop-shadow(0 0 70px rgba(34,211,238,0.7)); transform: scale(1.03); }
                    100% { filter: drop-shadow(0 0 10px rgba(14,165,233,0.5)); transform: scale(1); }
                }
                @keyframes skeletor-blast-glow {
                    0% { filter: drop-shadow(0 0 10px rgba(139,92,246,0.5)); transform: scale(1); }
                    50% { filter: drop-shadow(0 0 35px rgba(139,92,246,0.85)) drop-shadow(0 0 70px rgba(217,70,239,0.7)); transform: scale(1.03); }
                    100% { filter: drop-shadow(0 0 10px rgba(139,92,246,0.5)); transform: scale(1); }
                }
                .sword-glow-active {
                    animation: sword-blast-glow 2s infinite ease-in-out;
                    transform-origin: center center;
                }
                .skeletor-glow-active {
                    animation: skeletor-blast-glow 2s infinite ease-in-out;
                    transform-origin: center center;
                }
            `}} />
            <div className={isFullScreen ? "" : "relative"} style={svgWrapperStyles}>
                {/* SVG Definitions */}
                <svg width="0" height="0" className="absolute">
                    <defs>
                        <filter id="power-glow-v7" x="-50%" y="-50%" width="200%" height="200%">
                            <feGaussianBlur stdDeviation={isFullScreen ? 25 : 15} result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>

                        {/* Clipping Mask for Loading Effect */}
                        <clipPath id="sword-mask-v7">
                            <rect
                                x="0"
                                y={250 - (progress * 2.5)}
                                width="250"
                                height={progress * 2.5}
                                className="transition-all duration-300 ease-linear"
                            />
                        </clipPath>
                    </defs>
                </svg>

                {/* The Sword SVG Container */}
                <svg
                    viewBox="0 0 250 250"
                    preserveAspectRatio={isFullScreen ? "xMidYMid slice" : "xMidYMid meet"}
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className={`w-full h-full drop-shadow-[0_20px_50px_rgba(0,0,0,0.5)] transition-all duration-500 ${progress >= 99 ? (activeIsViolet ? 'skeletor-glow-active' : 'sword-glow-active') : ''}`}
                >
                    {/* 1. Fully Visible Base Layer (Sharp) */}
                    <image
                        href={activeSwordAsset}
                        x="0"
                        y="0"
                        width="250"
                        height="250"
                        className="opacity-100"
                    />

                    {/* Progress Text - Only if NOT fullScreen or explicitly desired */}
                    {!isFullScreen && (
                        <text
                            x="125"
                            y="245"
                            fill="white"
                            fontSize="14"
                            fontWeight="900"
                            textAnchor="middle"
                            className="font-black tracking-[0.4em] opacity-40 select-none blur-[0.3px]"
                        >
                            {Math.round(progress)}%
                        </text>
                    )}
                </svg>

                {/* 2. Procedural Lightning Canvas (Fractal 2D Multi-Pass Engine) */}
                <ProceduralLightningCanvas
                    startX={activeGuardX}
                    startY={activeGuardY}
                    endX={activeTipX}
                    endY={activeTipY}
                    progress={progress}
                    theme={lightningTheme}
                    isFullScreen={isFullScreen}
                />
            </div>

            {/* Overlay Content (Text and Progress Bar) */}
            {(text || isFullScreen) && (
                <div className={`relative z-10 space-y-6 text-center ${isFullScreen ? 'mt-[40vh]' : ''}`}>
                    {text && (
                        <p className={`${isFullScreen ? 'text-lg sm:text-2xl' : 'text-[11px]'} font-black uppercase tracking-[0.7em] text-white/60 animate-pulse italic drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]`}>
                            {text}
                        </p>
                    )}

                    <div className="flex flex-col items-center gap-3">
                        <div className={`relative ${isFullScreen ? 'h-[4px] w-80 sm:w-96' : 'h-[2px] w-64'} bg-white/5 rounded-full overflow-hidden backdrop-blur-sm border border-white/5`}>
                            <motion.div
                                className={`h-full ${activeIsViolet ? 'bg-purple-500 shadow-[0_0_30px_#A855F7]' : 'bg-cyan-400 shadow-[0_0_30px_#22D3EE]'}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                transition={{ ease: "linear", duration: 0.1 }}
                            />
                        </div>
                        {isFullScreen && (
                            <span className={`text-sm font-black tracking-[0.5em] ${activeIsViolet ? 'text-purple-400/60' : 'text-cyan-400/60'} transition-all`}>
                                {Math.round(progress)}%
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PowerSwordLoader;
