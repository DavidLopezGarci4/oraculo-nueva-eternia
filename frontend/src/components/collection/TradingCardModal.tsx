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
    Lock
} from 'lucide-react';
import { toBlob, toPng } from 'html-to-image';
import { MOTUImage } from '../ui/MOTUImage';

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

export const TradingCardModal: React.FC<TradingCardModalProps> = ({ isOpen, onClose, item }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [exporting, setExporting] = useState(false);
    const [copied, setCopied] = useState(false);
    const [shared, setShared] = useState(false);
    const [rotateX, setRotateX] = useState(0);
    const [rotateY, setRotateY] = useState(0);
    const [glarePos, setGlarePos] = useState({ x: 50, y: 50, opacity: 0 });

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

    // 1. Descargar imagen PNG HD
    const handleDownload = async () => {
        if (!cardRef.current) return;
        try {
            setExporting(true);
            const dataUrl = await toPng(cardRef.current, {
                pixelRatio: 3,
                cacheBust: true,
                style: { transform: 'none' }
            });
            const link = document.createElement('a');
            link.download = `Cromo_MOTU_${name.replace(/\s+/g, '_')}.png`;
            link.href = dataUrl;
            link.click();
        } catch (err) {
            console.error('Error generando cromo:', err);
        } finally {
            setExporting(false);
        }
    };

    // 2. Copiar Imagen al Portapapeles (para pegar directo en WhatsApp Web / Telegram)
    const handleCopyImage = async () => {
        if (!cardRef.current) return;
        try {
            setExporting(true);
            const blob = await toBlob(cardRef.current, {
                pixelRatio: 3,
                cacheBust: true,
                style: { transform: 'none' }
            });
            if (blob && navigator.clipboard && (window as any).ClipboardItem) {
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);
                setCopied(true);
                setTimeout(() => setCopied(false), 2500);
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
        if (!cardRef.current) return;
        try {
            setExporting(true);
            const blob = await toBlob(cardRef.current, {
                pixelRatio: 3,
                cacheBust: true,
                style: { transform: 'none' }
            });
            if (blob) {
                const file = new File([blob], `Cromo_MOTU_${name.replace(/\s+/g, '_')}.png`, {
                    type: 'image/png'
                });

                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    await navigator.share({
                        title: `Cromo MOTU: ${name}`,
                        text: `🏰 Cromo Oficial de ${name} custodidado en La Fortaleza de Grayskull.\nValor de Mercado: ${market.toFixed(2)}€ (${profit >= 0 ? '+' : ''}${profit.toFixed(2)}€ | ${roiPct}% ROI)`,
                        files: [file]
                    });
                    setShared(true);
                    setTimeout(() => setShared(false), 2500);
                } else {
                    handleCopyImage();
                }
            }
        } catch (err) {
            console.error('Error compartiendo cromo:', err);
        } finally {
            setExporting(false);
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-xl overflow-y-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.92, y: 15 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.92, y: 15 }}
                    className="relative w-full max-w-sm sm:max-w-md bg-gradient-to-b from-slate-900/95 via-slate-950 to-black border border-amber-500/40 rounded-3xl shadow-2xl p-4 sm:p-5 text-white my-auto flex flex-col items-center"
                >
                    {/* Botón cerrar */}
                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 p-2 rounded-full bg-slate-800/80 hover:bg-red-500 text-slate-300 hover:text-white transition z-20 shadow-lg"
                    >
                        <X className="h-4 w-4" />
                    </button>

                    {/* Título y subtítulo */}
                    <div className="text-center mb-3">
                        <div className="flex items-center justify-center gap-1.5 text-amber-400 text-xs font-black uppercase tracking-widest">
                            <Sparkles className="h-4 w-4 text-amber-300 animate-spin" style={{ animationDuration: '6s' }} />
                            <span>Cromo Holográfico de Grayskull</span>
                        </div>
                        <p className="text-[10px] text-slate-400">Exporta y comparte tu reliquia en alta fidelidad</p>
                    </div>

                    {/* CONTENEDOR DEL CROMO (RENDERIZADO VISUAL ESPECTACULAR) */}
                    <div
                        style={{ perspective: 1000 }}
                        className="w-full flex justify-center py-1 select-none"
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
                                            HERITAGE ARCHIVE • #{(item.sku || String(item.id)).slice(-5)}
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

                            {/* 2. Marco Holográfico con Foto HD */}
                            <div className="relative z-10 h-52 w-full rounded-xl bg-gradient-to-b from-slate-950 via-slate-900 to-black border border-slate-800 flex items-center justify-center overflow-hidden mb-2.5 group shadow-inner">
                                {/* Patrón de rejilla de fondo */}
                                <div
                                    className="absolute inset-0 opacity-10"
                                    style={{
                                        backgroundImage: 'radial-gradient(#22d3ee 1px, transparent 1px)',
                                        backgroundSize: '12px 12px'
                                    }}
                                />

                                <MOTUImage
                                    productId={item.id}
                                    src={item.image_url}
                                    alt={name}
                                    className="max-h-full max-w-full object-contain p-2.5 z-10 drop-shadow-[0_10px_15px_rgba(0,0,0,0.8)]"
                                />

                                {/* Badge de Estado (MOC / LOOSE) con resplandor */}
                                <div className="absolute top-2 left-2 z-20">
                                    <span
                                        className={`px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-wider border shadow-lg ${
                                            isMoc
                                                ? 'bg-amber-500/90 text-black border-amber-300 shadow-amber-500/40'
                                                : 'bg-cyan-500/90 text-black border-cyan-300 shadow-cyan-500/40'
                                        }`}
                                    >
                                        {isMoc ? '🛡️ MOC • CARDED' : '⚔️ LOOSE • MINT'}
                                    </span>
                                </div>

                                {/* Multiplicador Flotante */}
                                {purchase > 0 && profit > 0 && (
                                    <div className="absolute bottom-2 right-2 z-20 px-2 py-0.5 rounded-md bg-black/80 border border-emerald-500/60 text-emerald-400 text-[10px] font-mono font-black flex items-center gap-1 shadow-md">
                                        <TrendingUp className="h-3 w-3" />
                                        <span>{multiplier}x GAIN</span>
                                    </div>
                                )}
                            </div>

                            {/* 3. Nombre y Datos Técnicos */}
                            <div className="relative z-10 text-center mb-2.5">
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

                            {/* 4. Matriz de Valoración y Rendimiento */}
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
                            {shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}
                            <span>{shared ? '¡Compartido!' : 'WhatsApp / Redes'}</span>
                        </button>

                        {/* 2. Copiar Imagen al Portapapeles */}
                        <button
                            onClick={handleCopyImage}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50"
                        >
                            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                            <span>{copied ? '¡Imagen Copiada!' : 'Copiar Imagen'}</span>
                        </button>

                        {/* 3. Descargar Imagen HD */}
                        <button
                            onClick={handleDownload}
                            disabled={exporting}
                            className="flex flex-col items-center justify-center gap-1 p-2.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 rounded-xl text-[10px] font-bold shadow-md transition active:scale-95 disabled:opacity-50"
                        >
                            <Download className="h-4 w-4" />
                            <span>{exporting ? 'Generando...' : 'Descargar HD'}</span>
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TradingCardModal;
