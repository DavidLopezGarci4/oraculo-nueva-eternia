import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    Sparkles,
    Download,
    Share2,
    Copy,
    Check,
    X,
    Award,
    TrendingUp,
    Calendar,
    Lock,
    Loader2,
    Wand2,
    RotateCcw,
    Zap,
    BookOpen
} from 'lucide-react';
import { toPng } from 'html-to-image';
import { MOTUImage } from '../ui/MOTUImage';
import { enhanceCardWithAI, type CardAiEnhanceResult } from '../../api/cards';

interface TradingCardModalProps {
    isOpen: boolean;
    onClose: () => void;
    item: {
        id: number;
        product_name?: string;
        name?: string;
        image_url?: string;
        condition?: string;
        grading?: number;
        purchase_price?: number;
        current_value?: number;
        sub_category?: string;
        release_year?: number;
        sku?: string;
        shelf_wear?: string;
    } | null;
}

// Convertidor de DataURL base64 a Blob nativo
const dataUrlToBlob = async (dataUrl: string): Promise<Blob> => {
    const res = await fetch(dataUrl);
    return await res.blob();
};

// Generador de Cromo PNG con html-to-image y fallback infalible mediante Canvas 2D
const generateTradingCardDataUrl = async (node: HTMLElement, item: any, activeImageSrc?: string, aiLore?: string | null): Promise<string> => {
    try {
        // Intento 1: Renderizado vectorial nítido con html-to-image (skipFonts evita bloqueos de CORS en fuentes)
        return await toPng(node, {
            pixelRatio: 2,
            skipFonts: true,
            cacheBust: false,
            style: { transform: 'none' }
        });
    } catch (e1) {
        console.warn('html-to-image falló, ejecutando motor de composición directa por Canvas:', e1);
        
        // Intento 2: Motor de Dibujo Canvas 2D Nativo (100% libre de errores CORS y de red)
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return reject('No se pudo inicializar contexto Canvas 2D');

            const width = 720;
            const height = 1080;
            canvas.width = width;
            canvas.height = height;

            // 1. Fondo Oscuro Gradiente
            const grad = ctx.createLinearGradient(0, 0, 0, height);
            grad.addColorStop(0, '#030712');
            grad.addColorStop(0.5, '#0f172a');
            grad.addColorStop(1, '#000000');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);

            // 2. Marco Dorado Metálico
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 10;
            ctx.strokeRect(15, 15, width - 30, height - 30);

            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 3;
            ctx.strokeRect(30, 30, width - 60, height - 60);

            // 3. Cabecera y Grado
            ctx.fillStyle = '#fde68a';
            ctx.font = 'bold 28px sans-serif';
            ctx.fillText(item.sub_category || 'MOTU ORIGINS', 50, 85);

            ctx.fillStyle = '#94a3b8';
            ctx.font = '18px monospace';
            ctx.fillText(`HERITAGE ARCHIVE • #${(item.sku || String(item.id)).slice(-5)}`, 50, 115);

            ctx.fillStyle = '#34d399';
            ctx.font = 'bold 24px monospace';
            ctx.fillText(`GRADE ${(item.grading || 10.0).toFixed(1)} • GEM MINT`, width - 380, 85);

            // 4. Área de Imagen
            ctx.fillStyle = '#090d16';
            ctx.fillRect(50, 145, width - 100, 520);
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 2;
            ctx.strokeRect(50, 145, width - 100, 520);

            const finishDraw = () => {
                // 5. Nombre de la Figura
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 36px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(item.product_name || item.name || 'FIGURA MOTU', width / 2, 725);

                // Lore o Estado
                if (aiLore) {
                    ctx.fillStyle = '#67e8f9';
                    ctx.font = 'italic 18px sans-serif';
                    ctx.fillText(aiLore.slice(0, 75) + (aiLore.length > 75 ? '...' : ''), width / 2, 765);
                } else {
                    ctx.fillStyle = '#10b981';
                    ctx.font = 'bold 20px sans-serif';
                    ctx.fillText('🛡️ 100% AUTÉNTICO • COLECCIÓN OFICIAL', width / 2, 765);
                }

                // 6. Matriz de Valoración y Rendimiento
                ctx.fillStyle = '#0f172a';
                ctx.fillRect(50, 800, width - 100, 160);
                ctx.strokeStyle = '#f59e0b';
                ctx.lineWidth = 2;
                ctx.strokeRect(50, 800, width - 100, 160);

                const purchase = item.purchase_price || 0;
                const market = item.current_value || purchase || 19.99;
                const profit = market - purchase;
                const roi = purchase > 0 ? ((profit / purchase) * 100).toFixed(0) : '0';

                ctx.textAlign = 'left';
                ctx.fillStyle = '#94a3b8';
                ctx.font = '20px sans-serif';
                ctx.fillText('INVERSIÓN:', 90, 850);
                ctx.fillText('VALOR MERCADO:', 90, 895);
                ctx.fillText('PLUSVALÍA:', 90, 940);

                ctx.textAlign = 'right';
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 24px monospace';
                ctx.fillText(`${purchase.toFixed(2)} €`, width - 90, 850);

                ctx.fillStyle = '#fde047';
                ctx.fillText(`${market.toFixed(2)} €`, width - 90, 895);

                ctx.fillStyle = profit >= 0 ? '#34d399' : '#f87171';
                ctx.fillText(`${profit >= 0 ? '+' : ''}${profit.toFixed(2)} € (+${roi}%)`, width - 90, 940);

                // 7. Sello de Grayskull
                ctx.textAlign = 'center';
                ctx.fillStyle = '#f59e0b';
                ctx.font = 'bold 22px monospace';
                ctx.fillText('⚔️ FORTALEZA DE GRAYSKULL • NUEVA ETERNIA ⚔️', width / 2, 1025);

                resolve(canvas.toDataURL('image/png'));
            };

            // Dibujar imagen (la de IA si existe, o la original)
            const targetImgUrl = activeImageSrc || item.image_url;
            if (targetImgUrl) {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = () => {
                    try {
                        const aspect = img.width / img.height;
                        let drawW = width - 140;
                        let drawH = drawW / aspect;
                        if (drawH > 480) {
                            drawH = 480;
                            drawW = drawH * aspect;
                        }
                        const drawX = (width - drawW) / 2;
                        const drawY = 165 + (480 - drawH) / 2;
                        ctx.drawImage(img, drawX, drawY, drawW, drawH);
                    } catch {}
                    finishDraw();
                };
                img.onerror = () => {
                    finishDraw();
                };
                img.src = targetImgUrl;
            } else {
                finishDraw();
            }
        });
    }
};

export const TradingCardModal: React.FC<TradingCardModalProps> = ({ isOpen, onClose, item }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [exporting, setExporting] = useState(false);
    const [copied, setCopied] = useState(false);
    const [shared, setShared] = useState(false);
    const [downloaded, setDownloaded] = useState(false);
    const [rotateX, setRotateX] = useState(0);
    const [rotateY, setRotateY] = useState(0);
    const [glarePos, setGlarePos] = useState({ x: 50, y: 50, opacity: 0 });

    // Estado para la transformación mágica con Gemini
    const [showAiDrawer, setShowAiDrawer] = useState(false);
    const [aiResult, setAiResult] = useState<CardAiEnhanceResult | null>(null);
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [aiError, setAiError] = useState<string | null>(null);

    if (!isOpen || !item) return null;

    const name = item.product_name || item.name || 'Figura MOTU';
    const condition = (item.condition || 'MOC').toUpperCase();
    const isMoc = condition === 'MOC';
    const grade = item.grading || 10.0;
    const purchase = item.purchase_price || 0.0;
    const market = item.current_value || purchase || 19.99;
    const profit = market - purchase;
    const roiPct = purchase > 0 ? ((profit / purchase) * 100).toFixed(0) : '0';
    const multiplier = purchase > 0 ? (market / purchase).toFixed(1) : '1.0';

    // Manejo de giro 3D holográfico con el ratón
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotX = ((y - centerY) / centerY) * -12;
        const rotY = ((x - centerX) / centerX) * 12;

        setRotateX(rotX);
        setRotateY(rotY);
        setGlarePos({
            x: (x / rect.width) * 100,
            y: (y / rect.height) * 100,
            opacity: 0.6
        });
    };

    const handleMouseLeave = () => {
        setRotateX(0);
        setRotateY(0);
        setGlarePos((prev) => ({ ...prev, opacity: 0 }));
    };

    // Manejador de Transformación con Gemini
    const handleTransformWithAI = async (
        style: 'obrero_norem_80s' | 'alcala_texeira_minicomic' | 'gimenez_santalucia_modern' | 'heavy_metal_dark_eternia'
    ) => {
        try {
            setIsAiLoading(true);
            setAiError(null);
            const res = await enhanceCardWithAI({
                product_name: name,
                sub_category: item.sub_category,
                style,
                condition,
                grading: grade,
                image_url: item.image_url
            });
            setAiResult(res);
        } catch (err: any) {
            console.error('Error transformando con Gemini:', err);
            setAiError('No se pudo conectar con Gemini. Inténtalo de nuevo.');
        } finally {
            setIsAiLoading(false);
        }
    };

    // 1. Descargar imagen PNG HD
    const handleDownload = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            const activeImage = aiResult?.image_base64 || undefined;
            const dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore);

            const link = document.createElement('a');
            link.download = `Cromo_MOTU_${name.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            link.href = dataUrl;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setDownloaded(true);
            setTimeout(() => setDownloaded(false), 3000);
        } catch (err) {
            console.error('Error descargando cromo:', err);
        } finally {
            setExporting(false);
        }
    };

    // 2. Copiar Imagen al Portapapeles (para pegar directo en WhatsApp Web / Telegram)
    const handleCopyImage = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            const activeImage = aiResult?.image_base64 || undefined;
            const dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore);
            const blob = await dataUrlToBlob(dataUrl);

            if (navigator.clipboard && (window as any).ClipboardItem) {
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);
                setCopied(true);
                setTimeout(() => setCopied(false), 3000);
            } else {
                handleDownload();
            }
        } catch (err) {
            console.error('Error copiando imagen:', err);
            handleDownload();
        } finally {
            setExporting(false);
        }
    };

    // 3. Compartir nativo (WhatsApp, Telegram, Móvil)
    const handleNativeShare = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            const activeImage = aiResult?.image_base64 || undefined;
            const dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore);
            const blob = await dataUrlToBlob(dataUrl);
            const file = new File([blob], `Cromo_MOTU_${name.replace(/\s+/g, '_')}.png`, {
                type: 'image/png'
            });

            let shareText = `🏰 Cromo Oficial: ${name} custodiado en La Fortaleza de Grayskull.\nValor de Mercado: ${market.toFixed(2)}€ (${profit >= 0 ? '+' : ''}${profit.toFixed(2)}€ | ${roiPct}% ROI)`;
            
            if (aiResult?.lore) {
                shareText += `\n\n📜 Lore Canónico (Gemini AI):\n"${aiResult.lore}"`;
            }
            if (aiResult?.special_move) {
                shareText += `\n⚡ Técnica Definitiva: ${aiResult.special_move}`;
            }

            if (navigator.canShare && navigator.canShare({ files: [file] })) {
                await navigator.share({
                    title: `Cromo MOTU: ${name}`,
                    text: shareText,
                    files: [file]
                });
                setShared(true);
                setTimeout(() => setShared(false), 3000);
            } else {
                // Fallback para PC/Desktop: Abrir WhatsApp Web mediante enlace directo seguro
                const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;
                const waLink = document.createElement('a');
                waLink.href = waUrl;
                waLink.target = '_blank';
                waLink.rel = 'noopener noreferrer';
                document.body.appendChild(waLink);
                waLink.click();
                document.body.removeChild(waLink);

                setShared(true);
                setTimeout(() => setShared(false), 3000);
            }
        } catch (err) {
            console.error('Error compartiendo cromo:', err);
            // Fallback de emergencia a WhatsApp Web directo si falla el canvas o navigator
            let emergencyText = `🏰 Cromo Oficial: ${name} custodiado en La Fortaleza de Grayskull.`;
            if (aiResult?.lore) emergencyText += `\n\n📜 Lore (Gemini AI):\n"${aiResult.lore}"`;
            window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(emergencyText)}`, '_blank');
        } finally {
            setExporting(false);
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[260] flex items-center justify-center p-3 sm:p-4 bg-black/90 backdrop-blur-2xl overflow-y-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.92, y: 15 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.92, y: 15 }}
                    className="relative w-full max-w-sm sm:max-w-md bg-gradient-to-b from-slate-900/95 via-slate-950 to-black border-2 border-amber-500/50 rounded-3xl shadow-[0_0_60px_rgba(0,0,0,0.9)] p-4 sm:p-5 text-white my-auto flex flex-col items-center"
                >
                    {/* Botón cerrar */}
                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 p-2 rounded-full bg-slate-800/90 hover:bg-red-500 text-slate-300 hover:text-white transition z-20 shadow-lg"
                        title="Cerrar Cromo"
                    >
                        <X className="h-4 w-4" />
                    </button>

                    {/* Título de la Ficha */}
                    <div className="flex items-center gap-2 mb-2.5 text-center">
                        <Sparkles className="h-4 w-4 text-amber-400" />
                        <h2 className="text-xs sm:text-sm font-black uppercase tracking-widest text-amber-300">
                            Cromo Coleccionista Digital
                        </h2>
                        <Sparkles className="h-4 w-4 text-amber-400" />
                    </div>

                    {/* BARRA DE TRANSFORMACIÓN CON GEMINI */}
                    <div className="w-full mb-3">
                        <button
                            onClick={() => setShowAiDrawer(!showAiDrawer)}
                            className="w-full py-1.5 px-3 rounded-xl bg-gradient-to-r from-purple-600/30 via-cyan-600/30 to-amber-600/30 hover:from-purple-600/40 hover:to-amber-600/40 border border-cyan-400/50 text-cyan-200 text-xs font-black uppercase tracking-wider flex items-center justify-between shadow-lg shadow-cyan-500/10 transition"
                        >
                            <span className="flex items-center gap-1.5 truncate">
                                <Wand2 className="h-3.5 w-3.5 text-yellow-300 animate-pulse shrink-0" />
                                <span className="truncate">{aiResult ? `✨ ${aiResult.style_name}` : '🪄 Ilustrar con Maestros MOTU'}</span>
                            </span>
                            <span className="text-[10px] text-cyan-300/80 font-mono shrink-0 ml-1">
                                {showAiDrawer ? '▲ Ocultar' : '▼ 4 Estilos'}
                            </span>
                        </button>

                        {/* Menú Desplegable de Estilos de Ilustradores MOTU */}
                        {showAiDrawer && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="mt-2 p-2 bg-slate-950/90 border border-cyan-500/30 rounded-xl grid grid-cols-2 gap-1.5 text-[10px]"
                            >
                                <button
                                    onClick={() => handleTransformWithAI('obrero_norem_80s')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Sparkles className="h-3 w-3 text-amber-400 shrink-0" />
                                        <span className="font-black">🎨 Óleo Box-Art 80s</span>
                                    </div>
                                    <span className="text-[8px] text-amber-400/70 font-normal">Rudy Obrero & Earl Norem</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('alcala_texeira_minicomic')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Zap className="h-3 w-3 text-cyan-400 shrink-0" />
                                        <span className="font-black">⚔️ Mini-Cómic 80s</span>
                                    </div>
                                    <span className="text-[8px] text-cyan-400/70 font-normal">Alfredo Alcala & Texeira</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('gimenez_santalucia_modern')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <Award className="h-3 w-3 text-emerald-400 shrink-0" />
                                        <span className="font-black">✨ Cardback Moderno</span>
                                    </div>
                                    <span className="text-[8px] text-emerald-400/70 font-normal">Axel Gimenez & Santalucia</span>
                                </button>

                                <button
                                    onClick={() => handleTransformWithAI('heavy_metal_dark_eternia')}
                                    disabled={isAiLoading}
                                    className="p-2 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 font-bold flex flex-col items-start gap-0.5 transition text-left"
                                >
                                    <div className="flex items-center gap-1">
                                        <BookOpen className="h-3 w-3 text-purple-400 shrink-0" />
                                        <span className="font-black">🌌 Dark Fantasy MOTU</span>
                                    </div>
                                    <span className="text-[8px] text-purple-400/70 font-normal">Kenneth Rocafort & Bisley</span>
                                </button>

                                {aiResult && (
                                    <button
                                        onClick={() => setAiResult(null)}
                                        className="col-span-2 mt-1 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 font-bold flex items-center justify-center gap-1 transition"
                                    >
                                        <RotateCcw className="h-3 w-3" />
                                        <span>Restaurar Foto Original</span>
                                    </button>
                                )}
                            </motion.div>
                        )}

                        {isAiLoading && (
                            <div className="mt-2 py-1.5 px-3 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-200 text-[11px] font-bold flex items-center justify-center gap-2 animate-pulse">
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                <span>Recreando figura fuera del blíster con IA en Eternia...</span>
                            </div>
                        )}

                        {aiError && (
                            <div className="mt-1.5 text-center text-red-400 text-[10px]">
                                {aiError}
                            </div>
                        )}
                    </div>

                    {/* CONTENEDOR 3D DEL CROMO */}
                    <div
                        className="w-full flex justify-center cursor-grab active:cursor-grabbing"
                        style={{ perspective: 1000 }}
                        onMouseMove={handleMouseMove}
                        onMouseLeave={handleMouseLeave}
                    >
                        <motion.div
                            ref={cardRef}
                            style={{
                                transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
                                transformStyle: 'preserve-3d',
                                transition: 'transform 0.1s ease-out'
                            }}
                            className="relative w-full max-w-[340px] rounded-2xl bg-gradient-to-b from-slate-950 via-slate-900 to-black p-3.5 border-2 border-amber-400/80 shadow-[0_0_35px_rgba(245,158,11,0.25)] overflow-hidden"
                        >
                            {/* Marco exterior metálico grabado */}
                            <div className="absolute inset-0.5 rounded-2xl border border-emerald-400/40 pointer-events-none" />
                            <div className="absolute inset-1.5 rounded-xl border border-amber-500/20 pointer-events-none" />

                            {/* Brillo reflectivo holográfico dinámico */}
                            <div
                                className="absolute inset-0 pointer-events-none z-10 transition-opacity duration-200"
                                style={{
                                    opacity: glarePos.opacity,
                                    background: `radial-gradient(circle at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,0.4) 0%, rgba(6,182,212,0.2) 30%, rgba(245,158,11,0.15) 55%, transparent 80%)`
                                }}
                            />

                            {/* Nebulosa cósmica de fondo */}
                            <div className="absolute -top-12 -right-12 w-36 h-36 bg-cyan-500/20 rounded-full blur-2xl pointer-events-none" />
                            <div className="absolute -bottom-12 -left-12 w-36 h-36 bg-amber-500/20 rounded-full blur-2xl pointer-events-none" />

                            {/* 1. Cabecera Heroica del Cromo */}
                            <div className="relative z-10 flex items-center justify-between border-b border-amber-500/30 pb-2 mb-2">
                                <div className="flex items-center gap-1.5">
                                    <div className="p-1 rounded-md bg-gradient-to-br from-amber-400 to-yellow-600 text-black shadow-sm">
                                        <Shield className="h-3.5 w-3.5 fill-black" />
                                    </div>
                                    <div>
                                        <div className="text-[10px] font-black text-amber-300 uppercase tracking-widest leading-none">
                                            {item.sub_category || 'MOTU Origins'}
                                        </div>
                                        <div className="text-[8px] text-slate-400 font-mono tracking-tighter">
                                            {aiResult?.rarity_class || `HERITAGE ARCHIVE • #${(item.sku || String(item.id)).slice(-5)}`}
                                        </div>
                                    </div>
                                </div>

                                {/* Insignia de Grado Oficial */}
                                <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-400/50 shadow-sm">
                                    <Award className="h-3 w-3 text-emerald-400" />
                                    <span className="text-[10px] font-black text-emerald-300 font-mono">
                                        GRADE {grade.toFixed(1)}
                                    </span>
                                </div>
                            </div>

                            {/* 2. Marco Holográfico con Foto HD o Arte Transformado con IA */}
                            <div className="relative z-10 h-52 w-full rounded-xl bg-gradient-to-b from-slate-950 via-slate-900 to-black border border-slate-800 flex items-center justify-center overflow-hidden mb-2.5 group shadow-inner">
                                {/* Patrón de rejilla de fondo */}
                                <div
                                    className="absolute inset-0 opacity-10"
                                    style={{
                                        backgroundImage: 'radial-gradient(#22d3ee 1px, transparent 1px)',
                                        backgroundSize: '12px 12px'
                                    }}
                                />

                                {aiResult?.image_base64 ? (
                                    <img
                                        src={aiResult.image_base64}
                                        alt={name}
                                        className="h-full w-full object-cover z-10 animate-in fade-in zoom-in-95 duration-500"
                                    />
                                ) : (
                                    <div className="relative h-full w-full flex items-center justify-center overflow-hidden">
                                        <MOTUImage
                                            productId={item.id}
                                            src={item.image_url}
                                            alt={name}
                                            className="max-h-full max-w-full object-contain p-2.5 z-10 drop-shadow-[0_10px_15px_rgba(0,0,0,0.8)] transition-all duration-500"
                                        />
                                    </div>
                                )}

                                {/* Badge de Estado (MOC / LOOSE / AI ART) con resplandor */}
                                <div className="absolute top-2 left-2 z-20">
                                    <span
                                        className={`px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-wider border shadow-lg ${
                                            aiResult
                                                ? 'bg-purple-600/90 text-white border-purple-300 shadow-purple-500/40'
                                                : isMoc
                                                ? 'bg-amber-500/90 text-black border-amber-300 shadow-amber-500/40'
                                                : 'bg-cyan-500/90 text-black border-cyan-300 shadow-cyan-500/40'
                                        }`}
                                    >
                                        {aiResult ? `✨ ${aiResult.style_name.split(' ')[0] || 'AI'}` : isMoc ? '🛡️ MOC • CARDED' : '⚔️ LOOSE • MINT'}
                                    </span>
                                </div>

                                {/* Multiplicador Flotante o Golpe Especial */}
                                {purchase > 0 && profit > 0 && (
                                    <div className="absolute bottom-2 right-2 z-20 px-2 py-0.5 rounded-md bg-black/80 border border-emerald-500/60 text-emerald-400 text-[10px] font-mono font-black flex items-center gap-1 shadow-md">
                                        <TrendingUp className="h-3 w-3" />
                                        <span>{multiplier}x GAIN</span>
                                    </div>
                                )}
                            </div>

                            {/* 3. Nombre y Datos Técnicos */}
                            <div className="relative z-10 text-center mb-2">
                                <h3 className="text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-sm">
                                    {name}
                                </h3>
                                <div className="flex items-center justify-center gap-2 text-[10px] text-slate-400 mt-0.5">
                                    {item.release_year && (
                                        <span className="flex items-center gap-1">
                                            <Calendar className="h-2.5 w-2.5 text-amber-400" /> {item.release_year}
                                        </span>
                                    )}
                                    <span>•</span>
                                    <span className="text-emerald-400 font-semibold">100% Auténtico</span>
                                </div>
                            </div>

                            {/* 4. Panel Dinámico: Matriz de Lore & Stats RPG de Gemini O Valoración Financiera */}
                            {aiResult?.stats ? (
                                <div className="relative z-10 bg-slate-950/90 border border-cyan-500/40 rounded-xl p-2 mb-2 text-center shadow-inner">
                                    {/* Mini-Lore Narrativo */}
                                    {aiResult.lore && (
                                        <p className="text-[9px] text-cyan-200 italic mb-1.5 leading-tight line-clamp-2 px-1">
                                            "{aiResult.lore}"
                                        </p>
                                    )}
                                    {/* Estadísticas de Combate RPG */}
                                    <div className="grid grid-cols-4 gap-1 text-[8px] font-mono border-t border-slate-800 pt-1">
                                        <div className="bg-red-500/10 p-1 rounded border border-red-500/20">
                                            <span className="text-red-400 block font-bold">FUERZA</span>
                                            <span className="text-white font-bold text-xs">{aiResult.stats.fuerza}</span>
                                        </div>
                                        <div className="bg-purple-500/10 p-1 rounded border border-purple-500/20">
                                            <span className="text-purple-400 block font-bold">MAGIA</span>
                                            <span className="text-white font-bold text-xs">{aiResult.stats.magia}</span>
                                        </div>
                                        <div className="bg-blue-500/10 p-1 rounded border border-blue-500/20">
                                            <span className="text-blue-400 block font-bold">DEFENSA</span>
                                            <span className="text-white font-bold text-xs">{aiResult.stats.defensa}</span>
                                        </div>
                                        <div className="bg-emerald-500/10 p-1 rounded border border-emerald-500/20">
                                            <span className="text-emerald-400 block font-bold">AGILIDAD</span>
                                            <span className="text-white font-bold text-xs">{aiResult.stats.agilidad}</span>
                                        </div>
                                    </div>
                                    {aiResult.special_move && (
                                        <div className="text-[8px] text-amber-300 font-bold uppercase mt-1 tracking-wider">
                                            ⚡ {aiResult.special_move}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                /* Matriz de Rendimiento Estándar */
                                <div className="relative z-10 grid grid-cols-3 gap-1.5 bg-slate-950/90 border border-amber-500/20 rounded-xl p-2 mb-2 text-center shadow-inner">
                                    <div className="border-r border-slate-800 pr-1">
                                        <span className="text-[8px] text-slate-400 uppercase tracking-tighter block">Inversión</span>
                                        <span className="text-xs font-bold text-white font-mono">{purchase.toFixed(2)}€</span>
                                    </div>
                                    <div className="border-r border-slate-800 px-1">
                                        <span className="text-[8px] text-slate-400 uppercase tracking-tighter block">Mercado</span>
                                        <span className="text-xs font-bold text-amber-300 font-mono">{market.toFixed(2)}€</span>
                                    </div>
                                    <div className="pl-1">
                                        <span className="text-[8px] text-slate-400 uppercase tracking-tighter block">Plusvalía</span>
                                        <span className={`text-xs font-black font-mono ${profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            {profit >= 0 ? '+' : ''}{roiPct}%
                                        </span>
                                    </div>
                                </div>
                            )}

                            {/* 5. Sello de Autenticidad de La Fortaleza */}
                            <div className="relative z-10 flex items-center justify-between border-t border-slate-800/80 pt-1.5 px-1 text-[8px] text-slate-400 uppercase tracking-widest font-mono">
                                <div className="flex items-center gap-1">
                                    <Lock className="h-2.5 w-2.5 text-amber-400" />
                                    <span>FORTALEZA DE GRAYSKULL</span>
                                </div>
                                <span className="text-amber-400/80 font-bold">NUEVA ETERNIA</span>
                            </div>
                        </motion.div>
                    </div>

                    {/* BOTONES DE EXPORTACIÓN Y COMPARTIR */}
                    <div className="w-full grid grid-cols-3 gap-2 mt-4">
                        {/* 1. Compartir Nativo a WhatsApp / Móvil */}
                        <button
                            onClick={handleNativeShare}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-[10px] font-bold shadow-lg shadow-emerald-600/30 transition active:scale-95 disabled:opacity-50"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : shared ? (
                                <Check className="h-4 w-4 text-white" />
                            ) : (
                                <Share2 className="h-4 w-4" />
                            )}
                            <span>{shared ? '¡Listo!' : 'WhatsApp / Redes'}</span>
                        </button>

                        {/* 2. Copiar Imagen al Portapapeles */}
                        <button
                            onClick={handleCopyImage}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : copied ? (
                                <Check className="h-4 w-4 text-emerald-400" />
                            ) : (
                                <Copy className="h-4 w-4" />
                            )}
                            <span>{copied ? '¡Copiado!' : 'Copiar Imagen'}</span>
                        </button>

                        {/* 3. Descargar Imagen HD */}
                        <button
                            onClick={handleDownload}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50"
                        >
                            {exporting ? (
                                <Loader2 className="h-4 w-4 animate-spin text-amber-300" />
                            ) : downloaded ? (
                                <Check className="h-4 w-4 text-emerald-400" />
                            ) : (
                                <Download className="h-4 w-4" />
                            )}
                            <span>{downloaded ? '¡Descargado!' : 'Descargar HD'}</span>
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TradingCardModal;
