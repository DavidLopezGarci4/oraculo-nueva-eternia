import React, { useEffect, useRef } from 'react';

export type LightningTheme = 'heman' | 'skeletor' | 'vintage';

interface ThemeConfig {
    core: string;
    plasma: string;
    glow: string;
    sparks: string;
    jitter: number;
    wobble: number;
}

const THEMES: Record<LightningTheme, ThemeConfig> = {
    heman: {
        core: '#FFFFFF',
        plasma: '#00F3FF',
        glow: '#0284C7',
        sparks: '#BAE6FD',
        jitter: 1.0,
        wobble: 1.0,
    },
    skeletor: {
        core: '#FFFFFF',
        plasma: '#D946EF',
        glow: '#7E22CE',
        sparks: '#F5D0FE',
        jitter: 1.45,
        wobble: 1.4,
    },
    vintage: {
        core: '#FFFBEB',
        plasma: '#F59E0B',
        glow: '#D97706',
        sparks: '#FDE68A',
        jitter: 0.95,
        wobble: 0.9,
    },
};

interface Point {
    x: number;
    y: number;
}

interface Segment {
    p1: Point;
    p2: Point;
}

interface ProceduralLightningCanvasProps {
    startX: number;
    startY: number;
    endX: number;
    endY: number;
    progress: number; // 0 to 100
    theme?: LightningTheme;
    isFullScreen?: boolean;
    className?: string;
}

export const ProceduralLightningCanvas: React.FC<ProceduralLightningCanvasProps> = ({
    startX,
    startY,
    endX,
    endY,
    progress,
    theme = 'heman',
    isFullScreen = false,
    className = '',
}) => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const animFrameRef = useRef<number>(0);
    const lastRenderTime = useRef<number>(0);

    const themeConfig = THEMES[theme] || THEMES.heman;

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Recursive Midpoint Displacement for fractal lightning
        const generateFractalPath = (
            p1: Point,
            p2: Point,
            px: number,
            py: number,
            len: number,
            ux: number,
            uy: number,
            maxDisplacement: number,
            depth: number,
            maxDepth: number,
            segments: Segment[],
            canBranch: boolean = true
        ) => {
            if (depth >= maxDepth) {
                segments.push({ p1, p2 });
                return;
            }

            const midX = (p1.x + p2.x) / 2;
            const midY = (p1.y + p2.y) / 2;

            const displacement = (Math.random() - 0.5) * 2 * maxDisplacement;
            const midPoint: Point = {
                x: midX + px * displacement,
                y: midY + py * displacement,
            };

            generateFractalPath(p1, midPoint, px, py, len, ux, uy, maxDisplacement * 0.58, depth + 1, maxDepth, segments, canBranch);
            generateFractalPath(midPoint, p2, px, py, len, ux, uy, maxDisplacement * 0.58, depth + 1, maxDepth, segments, canBranch);

            // Optional secondary branch splitting off
            if (canBranch && depth === 2 && Math.random() < 0.35) {
                const branchAngle = (Math.random() > 0.5 ? 1 : -1) * (0.3 + Math.random() * 0.4);
                const branchLen = (len * 0.18 + Math.random() * 15) * (1 - depth / maxDepth);
                const branchEnd: Point = {
                    x: midPoint.x + (ux * Math.cos(branchAngle) - uy * Math.sin(branchAngle)) * branchLen,
                    y: midPoint.y + (ux * Math.sin(branchAngle) + uy * Math.cos(branchAngle)) * branchLen,
                };
                generateFractalPath(midPoint, branchEnd, px, py, len, ux, uy, maxDisplacement * 0.45, depth + 1, maxDepth, segments, false);
            }
        };

        const render = (now: number) => {
            // Regulate frame rate to ~40-60 FPS for an energetic crackle effect without overhead
            if (now - lastRenderTime.current < 22) {
                animFrameRef.current = requestAnimationFrame(render);
                return;
            }
            lastRenderTime.current = now;

            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            const displayWidth = rect.width || (isFullScreen ? window.innerWidth : 250);
            const displayHeight = rect.height || (isFullScreen ? window.innerHeight : 250);

            const targetCanvasWidth = Math.round(displayWidth * dpr);
            const targetCanvasHeight = Math.round(displayHeight * dpr);

            if (canvas.width !== targetCanvasWidth || canvas.height !== targetCanvasHeight) {
                canvas.width = targetCanvasWidth;
                canvas.height = targetCanvasHeight;
            }

            ctx.save();
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, displayWidth, displayHeight);

            // SVG equivalent viewBox mapping (0..250, 0..250)
            const preserveMode = isFullScreen ? 'slice' : 'meet';
            const scaleFactor = preserveMode === 'slice'
                ? Math.max(displayWidth / 250, displayHeight / 250)
                : Math.min(displayWidth / 250, displayHeight / 250);

            const offsetX = (displayWidth - 250 * scaleFactor) / 2;
            const offsetY = (displayHeight - 250 * scaleFactor) / 2;

            // Map coordinates from 250x250 space to display space
            const sX = offsetX + startX * scaleFactor;
            const sY = offsetY + startY * scaleFactor;
            const eX = offsetX + endX * scaleFactor;
            const eY = offsetY + endY * scaleFactor;

            const dx = eX - sX;
            const dy = eY - sY;
            const len = Math.sqrt(dx * dx + dy * dy);
            const ux = len > 0 ? dx / len : 0;
            const uy = len > 0 ? dy / len : -1;
            const px = -uy;
            const py = ux;

            if (progress >= 4) {
                const bladeStart = len * 0.08;
                const activeBladeLen = bladeStart + (Math.min(100, progress) / 100) * (len - bladeStart);

                const boltCount = isFullScreen
                    ? (progress > 85 ? 12 : 7)
                    : (progress > 85 ? 7 : 4);

                const segments: Segment[] = [];

                // 1. Blade Lightning bolts (following the ridge)
                for (let i = 0; i < boltCount; i++) {
                    const startJitter = (Math.random() - 0.5) * 6 * scaleFactor * 0.03 * themeConfig.jitter;
                    const bStartDist = Math.max(0, bladeStart + (Math.random() - 0.5) * 8 * scaleFactor * 0.02);

                    const root: Point = {
                        x: sX + bStartDist * ux + startJitter * px,
                        y: sY + bStartDist * uy + startJitter * py,
                    };

                    const boltEndDist = Math.max(bStartDist + 8, activeBladeLen + (Math.random() - 0.5) * 12 * scaleFactor * 0.02);
                    const tipJitter = (Math.random() - 0.5) * 8 * scaleFactor * 0.03 * themeConfig.jitter;

                    const target: Point = {
                        x: sX + boltEndDist * ux + tipJitter * px,
                        y: sY + boltEndDist * uy + tipJitter * py,
                    };

                    const maxDisp = (7 + Math.random() * 10) * (scaleFactor / 1.5) * 0.03 * themeConfig.wobble * (isFullScreen ? 1.3 : 1.0);
                    generateFractalPath(root, target, px, py, len, ux, uy, maxDisp, 0, 4, segments, true);
                }

                // 2. Radial discharges around the guard / skull hilt
                if (progress > 12) {
                    const radialCount = isFullScreen ? 6 : 4;
                    for (let j = 0; j < radialCount; j++) {
                        const angle = (j * (Math.PI * 2 / radialCount)) + (Math.random() - 0.5) * 0.6;
                        const rDist = (15 + Math.random() * 20) * (scaleFactor / 1.5) * 0.035 * (isFullScreen ? 1.4 : 1.0);
                        const rTarget: Point = {
                            x: sX + Math.cos(angle) * rDist,
                            y: sY + Math.sin(angle) * rDist,
                        };
                        generateFractalPath({ x: sX, y: sY }, rTarget, px, py, len, ux, uy, 4 * themeConfig.wobble, 0, 3, segments, false);
                    }
                }

                // Additive blending creates real incandescence at overlaps
                ctx.globalCompositeOperation = 'lighter';
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                // --- PASS 1: PLASMA AURA GLOW ---
                ctx.strokeStyle = themeConfig.plasma;
                ctx.shadowColor = themeConfig.glow;
                ctx.shadowBlur = isFullScreen ? 22 : 12;
                ctx.lineWidth = isFullScreen ? 3.8 : 2.4;

                ctx.beginPath();
                for (let k = 0; k < segments.length; k++) {
                    const seg = segments[k];
                    ctx.moveTo(seg.p1.x, seg.p1.y);
                    ctx.lineTo(seg.p2.x, seg.p2.y);
                }
                ctx.stroke();

                // --- PASS 2: PURE INCANDESCENT WHITE CORE ---
                ctx.strokeStyle = themeConfig.core;
                ctx.shadowColor = '#FFFFFF';
                ctx.shadowBlur = 4;
                ctx.lineWidth = isFullScreen ? 1.5 : 0.9;

                ctx.beginPath();
                for (let k = 0; k < segments.length; k++) {
                    const seg = segments[k];
                    ctx.moveTo(seg.p1.x, seg.p1.y);
                    ctx.lineTo(seg.p2.x, seg.p2.y);
                }
                ctx.stroke();

                // --- PASS 3: MICRO-SPARKS ---
                if (progress > 20) {
                    const sparkCount = progress > 80 ? 10 : 5;
                    ctx.fillStyle = themeConfig.sparks;
                    ctx.shadowColor = themeConfig.plasma;
                    ctx.shadowBlur = 8;

                    for (let s = 0; s < sparkCount; s++) {
                        const sparkDist = bladeStart + Math.random() * (activeBladeLen - bladeStart);
                        const sparkOffset = (Math.random() - 0.5) * 35 * (scaleFactor / 1.5) * 0.03 * themeConfig.wobble;
                        const sparkX = sX + sparkDist * ux + sparkOffset * px;
                        const sparkY = sY + sparkDist * uy + sparkOffset * py;
                        const radius = Math.random() * 1.8 + 0.6;

                        ctx.beginPath();
                        ctx.arc(sparkX, sparkY, radius, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            ctx.restore();
            animFrameRef.current = requestAnimationFrame(render);
        };

        animFrameRef.current = requestAnimationFrame(render);

        return () => {
            if (animFrameRef.current) {
                cancelAnimationFrame(animFrameRef.current);
            }
        };
    }, [startX, startY, endX, endY, progress, theme, isFullScreen, themeConfig]);

    return (
        <canvas
            ref={canvasRef}
            className={`pointer-events-none absolute inset-0 w-full h-full z-20 ${className}`}
            style={{
                filter: `drop-shadow(0 0 10px ${themeConfig.glow})`,
            }}
        />
    );
};

export default ProceduralLightningCanvas;
