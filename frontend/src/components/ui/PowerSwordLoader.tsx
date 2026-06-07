import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import swordAsset from '../../assets/HemanGlassmorphSword.png';
import vintageSwordAsset from '../../assets/bddg-heman.png';
import skeletorStaffAsset from '../../assets/skeletor_staff.png';

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
    skeletorTipY
}) => {
    const [internalProgress, setInternalProgress] = useState(0);

    const isFullScreen = variant === 'fullScreen';
    const activeSwordAsset = isSkeletor ? skeletorStaffAsset : (isVintage ? vintageSwordAsset : swordAsset);

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
        gY: 100.0,
        tX: 125.0,
        tY: 35.0
    });

    useEffect(() => {
        if (isVintage) {
            const stored = localStorage.getItem('vintage_sword_coords');
            if (stored) {
                try {
                    setVintageCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse vintage sword coords", e);
                }
            }
        }
    }, [isVintage]);

    useEffect(() => {
        if (isSkeletor) {
            const stored = localStorage.getItem('skeletor_staff_coords');
            if (stored) {
                try {
                    setSkeletorCoords(JSON.parse(stored));
                } catch (e) {
                    console.error("Failed to parse skeletor staff coords", e);
                }
            }
        }
    }, [isSkeletor]);

    // Use props if provided (useful for visualizer), otherwise use state/localStorage, or fallback to default modern coords
    const activeGuardX = vintageGuardX !== undefined ? vintageGuardX : (skeletorGuardX !== undefined ? skeletorGuardX : (isSkeletor ? skeletorCoords.gX : (isVintage ? vintageCoords.gX : 125)));
    const activeGuardY = vintageGuardY !== undefined ? vintageGuardY : (skeletorGuardY !== undefined ? skeletorGuardY : (isSkeletor ? skeletorCoords.gY : (isVintage ? vintageCoords.gY : 175)));
    const activeTipX = vintageTipX !== undefined ? vintageTipX : (skeletorTipX !== undefined ? skeletorTipX : (isSkeletor ? skeletorCoords.tX : (isVintage ? vintageCoords.tX : 125)));
    const activeTipY = vintageTipY !== undefined ? vintageTipY : (skeletorTipY !== undefined ? skeletorTipY : (isSkeletor ? skeletorCoords.tY : (isVintage ? vintageCoords.tY : 10)));

    // Vector calculations for the sword axis (from guard to tip)
    const dx = activeTipX - activeGuardX;
    const dy = activeTipY - activeGuardY;
    const len = Math.sqrt(dx * dx + dy * dy);
    const ux = len > 0 ? dx / len : 0;
    const uy = len > 0 ? dy / len : -1;
    const px = -uy; // Perpendicular vector x
    const py = ux;  // Perpendicular vector y

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

    // Lightning rays generation following the central ridge
    const renderLightning = () => {
        if (progress < 5) return null;
        const count = isFullScreen ? (progress > 80 ? 20 : 10) : (progress > 80 ? 12 : 6);

        // Blade lightning starts ~9% along the length to leave guard clean, extending to current progress
        const startDist = len * 0.09;
        const maxBladeLen = len - startDist;
        const currentLength = startDist + (progress / 100) * maxBladeLen;

        return [...Array(count)].map((_, i) => {
            const side = i % 2 === 0 ? 1 : -1;

            // Randomize start and end points slightly around the sword axis
            const rayStartDist = startDist + (Math.random() * 4 - 2);
            const startX = activeGuardX + rayStartDist * ux + (Math.random() * 1.5 - 0.75) * px;
            const startY = activeGuardY + rayStartDist * uy + (Math.random() * 1.5 - 0.75) * py;

            const rayEndDist = Math.max(startDist + 2, currentLength + (Math.random() * 6 - 3));
            const endX = activeGuardX + rayEndDist * ux + (Math.random() * 1.5 - 0.75) * px;
            const endY = activeGuardY + rayEndDist * uy + (Math.random() * 1.5 - 0.75) * py;

            // Wobble control point
            const midDist = startDist + Math.random() * (rayEndDist - startDist);
            const wobble = side * (5 + Math.random() * 10) * (isFullScreen ? 1.5 : 1);
            const cx = activeGuardX + midDist * ux + wobble * px;
            const cy = activeGuardY + midDist * uy + wobble * py;

             return (
                <motion.path
                    key={`blade-${i}`}
                    d={`M ${startX} ${startY} Q ${cx} ${cy} ${endX} ${endY}`}
                    stroke={isSkeletor ? (i % 3 === 0 ? "#F5D0FE" : "#D946EF") : (i % 3 === 0 ? "#BAE6FD" : "#38BDF8")}
                    strokeWidth={isFullScreen ? 2.5 : (Math.random() * 1.5 + 0.5)}
                    fill="none"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{
                        pathLength: [0, 1, 0.4],
                        opacity: [0, 1, 0],
                    }}
                    transition={{
                        duration: 0.12 + (Math.random() * 0.15),
                        repeat: Infinity,
                        repeatDelay: Math.random() * 0.2
                    }}
                />
            );
        });
    };

    // New Central Lightning (around the guard)
    const renderCentralLightning = () => {
        if (progress < 10) return null;
        const count = isFullScreen ? 8 : 4;
        return [...Array(count)].map((_, i) => {
            const angle = (i * (360 / count)) + (Math.random() * 20 - 10);
            const rad = angle * Math.PI / 180;
            const distance = isFullScreen ? 60 : 40;
            const x2 = activeGuardX + Math.cos(rad) * distance;
            const y2 = activeGuardY + Math.sin(rad) * distance;
            return (
                <motion.path
                    key={`central-${i}`}
                    d={`M ${activeGuardX} ${activeGuardY} L ${x2} ${y2}`}
                    stroke={isSkeletor ? "#E9D5FF" : "#7DD3FC"}
                    strokeWidth={isFullScreen ? 3 : 1.5}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: [0, 1, 0], opacity: [0, 1, 0] }}
                    transition={{
                        duration: 0.2,
                        repeat: Infinity,
                        repeatDelay: Math.random() * 0.5
                    }}
                />
            );
        });
    };

    const containerClasses = isFullScreen
        ? `fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#050608]`
        : `flex flex-col items-center justify-center gap-8 ${className}`;

    const svgWrapperStyles = isFullScreen
        ? { width: '100vw', height: '100vh', position: 'absolute' as const, inset: 0, opacity: 0.7 }
        : { width: size, height: size, position: 'relative' as const };

    return (
        <div className={containerClasses}>
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
                    className="w-full h-full drop-shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
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

                    {/* 2. Lightning Effects (With Glow) */}
                    <g filter="url(#power-glow-v7)">
                        {renderLightning()}
                        {renderCentralLightning()}
                    </g>

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
                                className={`h-full ${isSkeletor ? 'bg-purple-500 shadow-[0_0_30px_#A855F7]' : 'bg-cyan-400 shadow-[0_0_30px_#22D3EE]'}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                transition={{ ease: "linear", duration: 0.1 }}
                            />
                        </div>
                        {isFullScreen && (
                            <span className={`text-sm font-black tracking-[0.5em] ${isSkeletor ? 'text-purple-400/60' : 'text-cyan-400/60'} transition-all`}>
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
