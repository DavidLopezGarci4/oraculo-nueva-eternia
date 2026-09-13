import React, { useEffect, useRef } from 'react';

export type LightningTheme = 'heman' | 'skeletor' | 'vintage';

interface ThemeConfig {
    core: string;
    plasma: string;
    glow: string;
    sparks: string;
    ambient: string;
}

const THEMES: Record<LightningTheme, ThemeConfig> = {
    heman: {
        core: '#FFFFFF',
        plasma: '#38BDF8',
        glow: '#0284C7',
        sparks: '#BAE6FD',
        ambient: 'rgba(56, 189, 248, 0.15)',
    },
    skeletor: {
        core: '#FFFFFF',
        plasma: '#E879F9',
        glow: '#9333EA',
        sparks: '#F5D0FE',
        ambient: 'rgba(232, 121, 249, 0.15)',
    },
    vintage: {
        core: '#FFFBEB',
        plasma: '#FBBF24',
        glow: '#D97706',
        sparks: '#FDE68A',
        ambient: 'rgba(251, 191, 36, 0.15)',
    },
};

interface Point {
    x: number;
    y: number;
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
    const starRotationRef = useRef<number>(0);
    const ringPhaseRef = useRef<number>(0);

    const themeConfig = THEMES[theme] || THEMES.heman;

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Recursive jagged bolt generator (no fishbones or straight trees)
        const drawJaggedBolt = (
            p1: Point,
            p2: Point,
            perpX: number,
            perpY: number,
            displacement: number,
            iterations: number,
            plasmaWidth: number,
            coreWidth: number
        ) => {
            let pts: Point[] = [p1, p2];

            for (let i = 0; i < iterations; i++) {
                const newPts: Point[] = [];
                for (let j = 0; j < pts.length - 1; j++) {
                    const a = pts[j];
                    const b = pts[j + 1];
                    const midX = (a.x + b.x) / 2;
                    const midY = (a.y + b.y) / 2;
                    const disp = (Math.random() - 0.5) * displacement * Math.pow(0.55, i);
                    newPts.push(a);
                    newPts.push({
                        x: midX + perpX * disp,
                        y: midY + perpY * disp,
                    });
                }
                newPts.push(pts[pts.length - 1]);
                pts = newPts;
            }

            // Render Pass 1: Plasma Glow
            ctx.save();
            ctx.globalCompositeOperation = 'lighter';
            ctx.strokeStyle = themeConfig.plasma;
            ctx.shadowColor = themeConfig.glow;
            ctx.shadowBlur = isFullScreen ? 20 : 12;
            ctx.lineWidth = plasmaWidth;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            ctx.beginPath();
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let k = 1; k < pts.length; k++) {
                ctx.lineTo(pts[k].x, pts[k].y);
            }
            ctx.stroke();

            // Render Pass 2: White Core
            ctx.strokeStyle = themeConfig.core;
            ctx.shadowColor = '#FFFFFF';
            ctx.shadowBlur = 4;
            ctx.lineWidth = coreWidth;

            ctx.beginPath();
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let k = 1; k < pts.length; k++) {
                ctx.lineTo(pts[k].x, pts[k].y);
            }
            ctx.stroke();
            ctx.restore();
        };

        // Canonical Starburst at the tip of the sword
        const drawStarburst = (cx: number, cy: number, radius: number, rotAngle: number) => {
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(rotAngle);
            ctx.globalCompositeOperation = 'lighter';

            // 1. Radial Energy Core
            const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
            grad.addColorStop(0, '#FFFFFF');
            grad.addColorStop(0.25, themeConfig.core);
            grad.addColorStop(0.55, themeConfig.plasma);
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(0, 0, radius * 1.2, 0, Math.PI * 2);
            ctx.fill();

            // 2. Main 4 Long Diffraction Spikes
            ctx.shadowColor = themeConfig.plasma;
            ctx.shadowBlur = 18;
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = isFullScreen ? 3.2 : 2.2;

            const longRay = radius * 3.2;
            ctx.beginPath();
            ctx.moveTo(0, -longRay);
            ctx.lineTo(0, longRay);
            ctx.moveTo(-longRay, 0);
            ctx.lineTo(longRay, 0);
            ctx.stroke();

            // 3. Diagonal 4 Secondary Spikes
            ctx.strokeStyle = themeConfig.plasma;
            ctx.lineWidth = isFullScreen ? 2.0 : 1.4;
            const shortRay = radius * 1.8;
            ctx.beginPath();
            ctx.moveTo(-shortRay, -shortRay);
            ctx.lineTo(shortRay, shortRay);
            ctx.moveTo(-shortRay, shortRay);
            ctx.lineTo(shortRay, -shortRay);
            ctx.stroke();

            ctx.restore();
        };

        const render = () => {
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

            const preserveMode = isFullScreen ? 'slice' : 'meet';
            const scaleFactor = preserveMode === 'slice'
                ? Math.max(displayWidth / 250, displayHeight / 250)
                : Math.min(displayWidth / 250, displayHeight / 250);

            const offsetX = (displayWidth - 250 * scaleFactor) / 2;
            const offsetY = (displayHeight - 250 * scaleFactor) / 2;

            // Guard (Empuñadura) and Tip (Punta)
            const sX = offsetX + startX * scaleFactor;
            const sY = offsetY + startY * scaleFactor;
            const tX = offsetX + endX * scaleFactor;
            const tY = offsetY + endY * scaleFactor;

            const dx = tX - sX;
            const dy = tY - sY;
            const bladeLen = Math.sqrt(dx * dx + dy * dy);
            const ux = bladeLen > 0 ? dx / bladeLen : 0;
            const uy = bladeLen > 0 ? dy / bladeLen : -1;
            const px = -uy; // Perpendicular vector (normal to blade)
            const py = ux;

            // Blade half width in display pixels (approx 12-16 units in 250 space)
            const bladeHalfWidth = 14 * scaleFactor;

            if (progress >= 3) {
                const activeRatio = Math.min(100, progress) / 100;
                const currentBladeHeight = bladeLen * activeRatio;

                // --- 1. CELESTIAL STRIKE: Rayos que caen del cosmos sobre la punta ---
                // En Filmation / MOTU, el relámpago celestial golpea la punta desde lo alto
                const skyOriginY = Math.max(0, tY - (180 * scaleFactor));
                const skyCount = progress > 70 ? 2 : 1;

                for (let c = 0; c < skyCount; c++) {
                    const skyOriginX = tX + (Math.random() - 0.5) * 60 * scaleFactor;
                    drawJaggedBolt(
                        { x: skyOriginX, y: skyOriginY },
                        { x: tX, y: tY },
                        px,
                        py,
                        32 * scaleFactor,
                        4,
                        isFullScreen ? 4.5 : 3.0,
                        isFullScreen ? 1.8 : 1.1
                    );
                }

                // --- 2. ENVELOPING BLADE ARCS: Arcos que abrazan la espada por fuera ---
                // No son espinas ni ramas: son bucles eléctricos que envuelven los filos
                const arcCount = isFullScreen ? 4 : 3;
                for (let a = 0; a < arcCount; a++) {
                    const side = a % 2 === 0 ? 1 : -1;
                    const arcStartDist = Math.random() * (currentBladeHeight * 0.5);
                    const arcEndDist = Math.min(currentBladeHeight, arcStartDist + (bladeLen * (0.3 + Math.random() * 0.35)));

                    const p1: Point = {
                        x: sX + arcStartDist * ux + side * (bladeHalfWidth * 0.7) * px,
                        y: sY + arcStartDist * uy + side * (bladeHalfWidth * 0.7) * py,
                    };

                    const p2: Point = {
                        x: sX + arcEndDist * ux + side * (bladeHalfWidth * 0.7) * px,
                        y: sY + arcEndDist * uy + side * (bladeHalfWidth * 0.7) * py,
                    };

                    // Arco que sobresale por el exterior del filo
                    const bulge = side * (bladeHalfWidth + (Math.random() * 18 + 8) * scaleFactor);
                    const midDist = (arcStartDist + arcEndDist) / 2;
                    const midPoint: Point = {
                        x: sX + midDist * ux + bulge * px,
                        y: sY + midDist * uy + bulge * py,
                    };

                    drawJaggedBolt(p1, midPoint, px, py, 14 * scaleFactor, 3, isFullScreen ? 3.2 : 2.2, 1.0);
                    drawJaggedBolt(midPoint, p2, px, py, 14 * scaleFactor, 3, isFullScreen ? 3.2 : 2.2, 1.0);
                }

                // --- 3. POWER SURGE RINGS: Anillos de energía que ascienden por la hoja ---
                ringPhaseRef.current = (ringPhaseRef.current + 0.03) % 1;
                const ringDist = (ringPhaseRef.current * currentBladeHeight);
                if (ringDist > 10) {
                    const ringCenterX = sX + ringDist * ux;
                    const ringCenterY = sY + ringDist * uy;
                    const ringRadiusX = bladeHalfWidth * 1.5;
                    const ringRadiusY = 5 * scaleFactor;

                    ctx.save();
                    ctx.globalCompositeOperation = 'lighter';
                    ctx.strokeStyle = themeConfig.plasma;
                    ctx.shadowColor = themeConfig.glow;
                    ctx.shadowBlur = 12;
                    ctx.lineWidth = 2.0;

                    ctx.beginPath();
                    ctx.ellipse(ringCenterX, ringCenterY, ringRadiusX, ringRadiusY, 0, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.restore();
                }

                // --- 4. CANONICAL STARBURST AT THE TIP (Fulgur estelar de Grayskull) ---
                starRotationRef.current += 0.025;
                const starBaseRadius = (8 + (progress / 100) * 14) * scaleFactor;
                // Pulso vibratorio
                const pulse = 1 + Math.sin(Date.now() * 0.015) * 0.22;
                drawStarburst(tX, tY, starBaseRadius * pulse, starRotationRef.current);

                // --- 5. SPARK DETONATIONS IN GUARD & TIP ---
                const sparkCount = progress > 50 ? 6 : 3;
                ctx.save();
                ctx.globalCompositeOperation = 'lighter';
                ctx.fillStyle = themeConfig.sparks;
                ctx.shadowColor = themeConfig.plasma;
                ctx.shadowBlur = 8;

                for (let s = 0; s < sparkCount; s++) {
                    const sparkDist = Math.random() * currentBladeHeight;
                    const sparkOffset = (Math.random() - 0.5) * (bladeHalfWidth * 3.5);
                    const spX = sX + sparkDist * ux + sparkOffset * px;
                    const spY = sY + sparkDist * uy + sparkOffset * py;
                    const r = Math.random() * 2.2 + 0.8;

                    ctx.beginPath();
                    ctx.arc(spX, spY, r, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();
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
                filter: `drop-shadow(0 0 15px ${themeConfig.glow})`,
            }}
        />
    );
};

export default ProceduralLightningCanvas;
