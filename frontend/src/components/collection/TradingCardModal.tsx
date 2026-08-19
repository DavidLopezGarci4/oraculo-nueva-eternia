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
    Lock,
    Loader2,
    Wand2,
    RotateCcw,
    Zap,
    BookOpen,
    Image as ImageIcon,
    Plus,
    Minus,
    Move,
    Skull,
    Flame,
    Infinity as InfinityIcon,
    Swords
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

// Interfaz para la configuración estética de cada facción
interface FactionThemeConfig {
    name: string;
    faction: string;
    typeLine: string;
    borderClass: string;
    innerBorderClass: string;
    headerBg: string;
    textAccent: string;
    badgeBg: string;
    boxBg: string;
    boxBorder: string;
    gemColors: string[];
    emblemIcon: 'shield' | 'skull' | 'bat' | 'snake' | 'sparkles' | 'infinity';
}

const FACTION_THEMES: Record<string, FactionThemeConfig> = {
    castle_grayskull: {
        name: 'Guerreros Heroicos',
        faction: 'Guerreros Heroicos',
        typeLine: 'Criatura Legendaria — Guerrero Heroico',
        borderClass: 'border-emerald-500/80 shadow-[0_0_35px_rgba(16,185,129,0.35)]',
        innerBorderClass: 'border-amber-400/50',
        headerBg: 'from-emerald-950/90 via-slate-900 to-black',
        textAccent: 'text-emerald-300',
        badgeBg: 'from-emerald-500/20 to-teal-500/20 border-emerald-400/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-emerald-500/30',
        gemColors: ['#10b981', '#10b981', '#f59e0b', '#38bdf8'],
        emblemIcon: 'shield'
    },
    snake_mountain: {
        name: 'Guerreros Diabólicos',
        faction: 'Guerreros Diabólicos',
        typeLine: 'Criatura Legendaria — Guerrero Diabólico',
        borderClass: 'border-purple-600/90 shadow-[0_0_35px_rgba(168,85,247,0.35)]',
        innerBorderClass: 'border-amber-500/40',
        headerBg: 'from-purple-950/90 via-slate-900 to-black',
        textAccent: 'text-purple-300',
        badgeBg: 'from-purple-500/20 to-red-500/20 border-purple-400/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-purple-500/30',
        gemColors: ['#a855f7', '#ef4444', '#f59e0b', '#8b5cf6'],
        emblemIcon: 'skull'
    },
    evil_horde: {
        name: 'La Horda del Terror',
        faction: 'La Horda del Terror',
        typeLine: 'Tirano Legendario — Soldado de la Horda',
        borderClass: 'border-red-600/90 shadow-[0_0_35px_rgba(239,68,68,0.35)]',
        innerBorderClass: 'border-slate-500/50',
        headerBg: 'from-red-950/90 via-slate-900 to-black',
        textAccent: 'text-red-300',
        badgeBg: 'from-red-600/20 to-rose-600/20 border-red-500/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-red-500/30',
        gemColors: ['#ef4444', '#dc2626', '#111827', '#f87171'],
        emblemIcon: 'bat'
    },
    snake_men: {
        name: 'Los Hombres Serpiente',
        faction: 'Los Hombres Serpiente',
        typeLine: 'Monarca Ofídico — Hombre Serpiente',
        borderClass: 'border-lime-500/90 shadow-[0_0_35px_rgba(132,204,22,0.35)]',
        innerBorderClass: 'border-amber-500/40',
        headerBg: 'from-emerald-950/90 via-lime-950/40 to-black',
        textAccent: 'text-lime-300',
        badgeBg: 'from-lime-500/20 to-emerald-500/20 border-lime-400/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-lime-500/30',
        gemColors: ['#84cc16', '#22c55e', '#eab308', '#10b981'],
        emblemIcon: 'snake'
    },
    great_rebellion: {
        name: 'La Gran Rebelión',
        faction: 'La Gran Rebelión',
        typeLine: 'Princesa del Poder — Gran Rebelión',
        borderClass: 'border-pink-400/90 shadow-[0_0_35px_rgba(244,114,182,0.35)]',
        innerBorderClass: 'border-amber-300/40',
        headerBg: 'from-pink-950/80 via-slate-900 to-black',
        textAccent: 'text-pink-300',
        badgeBg: 'from-pink-500/20 to-cyan-500/20 border-pink-400/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-pink-500/30',
        gemColors: ['#f472b6', '#38bdf8', '#fbbf24', '#c084fc'],
        emblemIcon: 'sparkles'
    },
    cosmic_enforcers: {
        name: 'Guardianes Cósmicos',
        faction: 'Guardianes Cósmicos',
        typeLine: 'Ejecutor Cósmico — Juez del Equilibrio',
        borderClass: 'border-cyan-400/90 shadow-[0_0_35px_rgba(6,182,212,0.35)]',
        innerBorderClass: 'border-slate-400/40',
        headerBg: 'from-cyan-950/80 via-slate-900 to-black',
        textAccent: 'text-cyan-300',
        badgeBg: 'from-cyan-500/20 to-blue-500/20 border-cyan-400/50',
        boxBg: 'bg-slate-950/90',
        boxBorder: 'border-cyan-500/30',
        gemColors: ['#06b6d4', '#3b82f6', '#e0e7ff', '#a855f7'],
        emblemIcon: 'infinity'
    }
};

// Resolver canónico determinista para la interfaz local
const getLocalMotuProfile = (productName: string, _subCategory?: string) => {
    const clean = (productName || '').toLowerCase().trim();

    if (clean.includes('skeletor') || clean.includes('beast') || clean.includes('trap') || clean.includes('tri-klops') || clean.includes('mer-man') || clean.includes('evil-lyn') || clean.includes('faker') || clean.includes('scare') || clean.includes('clawful') || clean.includes('whiplash') || clean.includes('webstor') || clean.includes('spikor') || clean.includes('stinkor') || clean.includes('two-bad') || clean.includes('ninjor') || clean.includes('jitsu') || clean.includes('blade') || clean.includes('saurod')) {
        return {
            themeKey: 'snake_mountain',
            faction: 'Guerreros Diabólicos',
            typeLine: 'Criatura Legendaria — Guerrero Diabólico',
            specialMove: clean.includes('beast') ? 'Zarpazo Titánico de la Jungla' : clean.includes('trap') ? 'Mordisco de Mandíbula de Acero' : clean.includes('tri-klops') ? 'Láser Óptico de Rastreo Letal' : clean.includes('mer-man') ? 'Tsunami de las Profundidades de Rakash' : clean.includes('evil-lyn') ? 'Tormenta Ilusoria de Subternia' : clean.includes('clawful') ? 'Presa Hidráulica Trituradora' : clean.includes('whiplash') ? 'Azote Ofídico Venenoso' : clean.includes('faker') ? 'Tajo Cósmico de Luz Ancestral' : 'Descarga de Sombras Arcanas',
            lore: clean.includes('beast') ? 'Señor salvaje de las bestias de Eternia y leal esbirro de Skeletor. Con su látigo ardiente y telepatía animal doblega a las criaturas más temibles.' : clean.includes('skeletor') ? 'Señor de la destrucción y tirano nigromántico de Snake Mountain cuya sed de conquista amenaza la existencia.' : 'Combatiente despiadado de las legiones oscuras de Snake Mountain al servicio de Skeletor.',
            stats: { fuerza: 92, magia: clean.includes('skeletor') || clean.includes('lyn') ? 98 : 68, defensa: 89, agilidad: 86 }
        };
    }
    if (clean.includes('hordak') || clean.includes('horde') || clean.includes('weaver') || clean.includes('catra') || clean.includes('grizzlor') || clean.includes('mantenna') || clean.includes('leech') || clean.includes('scorpia') || clean.includes('mosquitor') || clean.includes('modulok')) {
        return {
            themeKey: 'evil_horde',
            faction: 'La Horda del Terror',
            typeLine: 'Tirano Legendario — Soldado de la Horda',
            specialMove: 'Flecha de Plasma Carmesí de la Horda',
            lore: 'Tirano supremo de la Zona del Terror y maestro de la tecno-magia oscura, capaz de transmutar su propio cuerpo en armamento mecánico mortal.',
            stats: { fuerza: 95, magia: 96, defensa: 95, agilidad: 87 }
        };
    }
    if (clean.includes('snake') || clean.includes('hiss') || clean.includes('khan') || clean.includes('rattlor') || clean.includes('tung') || clean.includes('lashr') || clean.includes('sssqueeze') || clean.includes('serpiente')) {
        return {
            themeKey: 'snake_men',
            faction: 'Los Hombres Serpiente',
            typeLine: 'Monarca Ofídico — Hombre Serpiente',
            specialMove: clean.includes('khan') ? 'Chorro Ácido Corrosivo' : 'Mordisco Asfixiante del Rey Hiss',
            lore: 'Antiquísimo monarca ofídico cuyo disfraz humano oculta una masa de serpientes devoradoras. Regresa del pasado para dominar Eternia.',
            stats: { fuerza: 93, magia: 95, defensa: 91, agilidad: 93 }
        };
    }
    if (clean.includes('she-ra') || clean.includes('shera') || clean.includes('bow') || clean.includes('glimmer') || clean.includes('frosta') || clean.includes('angella') || clean.includes('mermista') || clean.includes('rebellion')) {
        return {
            themeKey: 'great_rebellion',
            faction: 'La Gran Rebelión',
            typeLine: 'Princesa del Poder — Gran Rebelión',
            specialMove: 'Tajo Cósmico de Luz Ancestral',
            lore: 'Princesa del Poder y líder invicta de la Gran Rebelión en Etheria. Con la Espada de Protección canaliza la luz pura del honor.',
            stats: { fuerza: 98, magia: 94, defensa: 95, agilidad: 96 }
        };
    }
    if (clean.includes('zodac') || clean.includes('zodak') || clean.includes('he-ro') || clean.includes('eldor') || clean.includes('cosmic')) {
        return {
            themeKey: 'cosmic_enforcers',
            faction: 'Guardianes Cósmicos',
            typeLine: 'Ejecutor Cósmico — Juez del Equilibrio',
            specialMove: 'Descarga Cósmica de Zodac',
            lore: 'Enforcer Cósmico neutral que vela por el equilibrio universal entre la luz y las sombras con su conocimiento infinito.',
            stats: { fuerza: 90, magia: 95, defensa: 92, agilidad: 91 }
        };
    }
    // Default: Guerreros Heroicos (Grayskull)
    return {
        themeKey: 'castle_grayskull',
        faction: 'Guerreros Heroicos',
        typeLine: 'Criatura Legendaria — Guerrero Heroico',
        specialMove: clean.includes('ram') ? 'Impacto de Ariete Inamovible' : clean.includes('man-at-arms') ? 'Ráfaga Fotónica Man-At-Arms' : clean.includes('stratos') ? 'Picado Aéreo de Avion' : clean.includes('teela') ? 'Estocada Táctica de la Cobra' : clean.includes('cat') ? 'Desgarro Feroz de la Selva Carmesí' : clean.includes('sorceress') ? 'Escudo del Halcón Místico' : clean.includes('fisto') ? 'Golpe Demoledor de Murallas' : 'Furia del Relámpago de Grayskull',
        lore: clean.includes('he-man') ? 'Defensor supremo de los secretos de Castle Grayskull y campeón de Eternia. Guiado por la Espada del Poder, protege el cosmos de la oscuridad.' : 'Noble defensor de la corte real de Eternia y custodio de la paz sagrada de Grayskull.',
        stats: { fuerza: clean.includes('he-man') ? 99 : 88, magia: clean.includes('sorceress') ? 99 : 78, defensa: 92, agilidad: 89 }
    };
};

// Convertidor de DataURL base64 a Blob nativo
const dataUrlToBlob = async (dataUrl: string): Promise<Blob> => {
    const res = await fetch(dataUrl);
    return await res.blob();
};

// Obtiene la imagen individual pura con el encuadre y zoom personalizados como DataURL HD
const getSingleIllustrationDataUrl = async (
    item: any,
    aiImageBase64?: string | null,
    zoom: number = 1,
    pan: { x: number; y: number } = { x: 0, y: 0 }
): Promise<string> => {
    if (zoom === 1 && pan.x === 0 && pan.y === 0 && aiImageBase64) {
        return aiImageBase64;
    }
    const targetSrc = aiImageBase64 || item.image_url;
    if (!targetSrc) return '';

    return new Promise((resolve) => {
        const img = new window.Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = 900;
            canvas.height = 1200;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = '#090d16';
                ctx.fillRect(0, 0, 900, 1200);

                ctx.save();
                ctx.translate(450 + pan.x * (900 / 320), 600 + pan.y * (1200 / 224));
                ctx.scale(zoom, zoom);

                const imgAspect = img.width / img.height;
                const canvasAspect = 900 / 1200;
                let drawW = 900;
                let drawH = 1200;
                if (imgAspect > canvasAspect) {
                    drawW = 1200 * imgAspect;
                } else {
                    drawH = 900 / imgAspect;
                }
                ctx.drawImage(img, -drawW / 2, -drawH / 2, drawW, drawH);
                ctx.restore();

                try {
                    resolve(canvas.toDataURL('image/png'));
                } catch {
                    resolve(targetSrc);
                }
            } else {
                resolve(targetSrc);
            }
        };
        img.onerror = () => resolve(targetSrc);
        img.src = targetSrc;
    });
};

// Generador de Cromo PNG con html-to-image y fallback infalible mediante Canvas 2D (Sin Panel Financiero)
const generateTradingCardDataUrl = async (
    node: HTMLElement,
    item: any,
    activeImageSrc?: string,
    aiLore?: string | null,
    profileData?: any
): Promise<string> => {
    try {
        // Intento 1: Renderizado vectorial nítido con html-to-image (excluyendo controles interactivos)
        return await toPng(node, {
            pixelRatio: 2.5,
            skipFonts: true,
            cacheBust: false,
            filter: (domNode) => {
                if (domNode instanceof HTMLElement && domNode.classList.contains('export-exclude')) {
                    return false;
                }
                return true;
            },
            style: { transform: 'none' }
        });
    } catch (e1) {
        console.warn('html-to-image falló, ejecutando motor de composición directa por Canvas:', e1);

        // Intento 2: Motor de Dibujo Canvas 2D Nativo MTG Showcase
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return reject('No se pudo inicializar contexto Canvas 2D');

            const width = 750;
            const height = 1050;
            canvas.width = width;
            canvas.height = height;

            const faction = profileData?.faction || 'Guerreros Heroicos';
            const specialMove = profileData?.specialMove || 'Furia del Relámpago de Grayskull';
            const loreText = aiLore || profileData?.lore || 'Defensor legendario de Eternia custodiado en La Fortaleza de Grayskull.';
            const stats = profileData?.stats || { fuerza: 90, magia: 85, defensa: 90, agilidad: 88 };

            // 1. Fondo Oscuro y Textura de Facción
            const grad = ctx.createLinearGradient(0, 0, 0, height);
            if (faction === 'Guerreros Diabólicos') {
                grad.addColorStop(0, '#1e102d');
                grad.addColorStop(0.5, '#0f0a17');
                grad.addColorStop(1, '#050308');
            } else if (faction === 'La Horda del Terror') {
                grad.addColorStop(0, '#2b0c0c');
                grad.addColorStop(0.5, '#150606');
                grad.addColorStop(1, '#050202');
            } else {
                grad.addColorStop(0, '#0a2318');
                grad.addColorStop(0.5, '#07150e');
                grad.addColorStop(1, '#030805');
            }
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);

            // 2. Marco Dorado y Bisel Metálico
            ctx.strokeStyle = '#d97706';
            ctx.lineWidth = 12;
            ctx.strokeRect(18, 18, width - 36, height - 36);

            ctx.strokeStyle = faction === 'Guerreros Diabólicos' ? '#a855f7' : faction === 'La Horda del Terror' ? '#ef4444' : '#10b981';
            ctx.lineWidth = 3;
            ctx.strokeRect(32, 32, width - 64, height - 64);

            // 3. Cabecera (Header con Nombre y Orbes)
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 30px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(item.product_name || item.name || 'FIGURA MOTU', 55, 80);

            // Orbes de poder en la cabecera derecha
            const orbColors = faction === 'Guerreros Diabólicos' ? ['#a855f7', '#ef4444', '#f59e0b'] : ['#10b981', '#10b981', '#f59e0b'];
            orbColors.forEach((col, idx) => {
                ctx.beginPath();
                ctx.arc(width - 65 - idx * 26, 70, 9, 0, Math.PI * 2);
                ctx.fillStyle = col;
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            });

            // 4. Área de Ilustración
            ctx.fillStyle = '#05070c';
            ctx.fillRect(50, 110, width - 100, 480);
            ctx.strokeStyle = '#d97706';
            ctx.lineWidth = 3;
            ctx.strokeRect(50, 110, width - 100, 480);

            const finishDraw = () => {
                // 5. Barra de Tipo y Facción (Type-Line)
                ctx.fillStyle = '#0f172a';
                ctx.fillRect(50, 610, width - 100, 45);
                ctx.strokeStyle = '#f59e0b';
                ctx.lineWidth = 2;
                ctx.strokeRect(50, 610, width - 100, 45);

                ctx.fillStyle = '#fde68a';
                ctx.font = 'bold 20px sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(`⚡ CRIATURA LEGENDARIA — ${faction.toUpperCase()}`, 65, 640);

                ctx.textAlign = 'right';
                ctx.fillStyle = '#94a3b8';
                ctx.font = 'bold 16px monospace';
                ctx.fillText(item.sub_category || 'ORIGINS', width - 65, 640);

                // 6. Text Box (Habilidad + Lore Canónico)
                ctx.fillStyle = '#090d16';
                ctx.fillRect(50, 675, width - 100, 240);
                ctx.strokeStyle = '#334155';
                ctx.lineWidth = 2;
                ctx.strokeRect(50, 675, width - 100, 240);

                // Título de Habilidad
                ctx.textAlign = 'left';
                ctx.fillStyle = '#f59e0b';
                ctx.font = 'bold 22px sans-serif';
                ctx.fillText(`⚡ ${specialMove}`, 70, 715);

                // Línea divisoria
                ctx.strokeStyle = '#334155';
                ctx.beginPath();
                ctx.moveTo(70, 735);
                ctx.lineTo(width - 70, 735);
                ctx.stroke();

                // Flavor Text (Lore en cursiva)
                ctx.fillStyle = '#cbd5e1';
                ctx.font = 'italic 18px sans-serif';
                const words = `"${loreText}"`.split(' ');
                let line = '';
                let yPos = 770;
                for (let n = 0; n < words.length; n++) {
                    const testLine = line + words[n] + ' ';
                    const metrics = ctx.measureText(testLine);
                    if (metrics.width > width - 140 && n > 0) {
                        ctx.fillText(line, 70, yPos);
                        line = words[n] + ' ';
                        yPos += 26;
                    } else {
                        line = testLine;
                    }
                }
                ctx.fillText(line, 70, yPos);

                // 7. Placas de Estadísticas RPG (FUE, MAG, DEF, AGI) y Sello Holográfico
                ctx.fillStyle = '#0f172a';
                ctx.fillRect(50, 935, width - 100, 55);
                ctx.strokeStyle = '#d97706';
                ctx.lineWidth = 2;
                ctx.strokeRect(50, 935, width - 100, 55);

                ctx.textAlign = 'left';
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 18px monospace';
                ctx.fillText(`FUE ${stats.fuerza}  |  MAG ${stats.magia}`, 70, 970);

                ctx.textAlign = 'right';
                ctx.fillText(`DEF ${stats.defensa}  |  AGI ${stats.agilidad}`, width - 70, 970);

                // Sello Holográfico Oval Central
                ctx.save();
                ctx.beginPath();
                ctx.ellipse(width / 2, 962, 38, 18, 0, 0, Math.PI * 2);
                const holoGrad = ctx.createLinearGradient(width / 2 - 38, 0, width / 2 + 38, 0);
                holoGrad.addColorStop(0, '#06b6d4');
                holoGrad.addColorStop(0.3, '#3b82f6');
                holoGrad.addColorStop(0.6, '#ec4899');
                holoGrad.addColorStop(1, '#f59e0b');
                ctx.fillStyle = holoGrad;
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1.5;
                ctx.stroke();
                ctx.restore();

                // 8. Sello de Autenticidad en Footer
                ctx.textAlign = 'center';
                ctx.fillStyle = '#94a3b8';
                ctx.font = 'bold 14px monospace';
                ctx.fillText(`🏰 FORTALEZA DE GRAYSKULL • NUEVA ETERNIA • #${(item.sku || String(item.id)).slice(-5)}`, width / 2, 1020);

                resolve(canvas.toDataURL('image/png'));
            };

            const targetImgUrl = activeImageSrc || item.image_url;
            if (targetImgUrl) {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = () => {
                    try {
                        const aspect = img.width / img.height;
                        let drawW = width - 120;
                        let drawH = drawW / aspect;
                        if (drawH > 460) {
                            drawH = 460;
                            drawW = drawH * aspect;
                        }
                        const drawX = (width - drawW) / 2;
                        const drawY = 120 + (460 - drawH) / 2;
                        ctx.drawImage(img, drawX, drawY, drawW, drawH);
                    } catch {}
                    finishDraw();
                };
                img.onerror = () => finishDraw();
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

    // Estado para selector dual de exportación (Carta Completa vs Solo Ilustración)
    const [exportTarget, setExportTarget] = useState<'card' | 'image'>('card');

    // Estado para Encuadre y Zoom interactivo de la imagen
    const [imgZoom, setImgZoom] = useState<number>(1);
    const [imgPan, setImgPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
    const [isDraggingImg, setIsDraggingImg] = useState(false);
    const dragStartRef = useRef<{ x: number; y: number; startPanX: number; startPanY: number }>({
        x: 0,
        y: 0,
        startPanX: 0,
        startPanY: 0
    });
    const touchStartRef = useRef<{ dist: number; startZoom: number; x: number; y: number; startPanX: number; startPanY: number }>({
        dist: 0,
        startZoom: 1,
        x: 0,
        y: 0,
        startPanX: 0,
        startPanY: 0
    });

    const resetFraming = () => {
        setImgZoom(1);
        setImgPan({ x: 0, y: 0 });
    };

    if (!isOpen || !item) return null;

    const name = item.product_name || item.name || 'Figura MOTU';
    const condition = (item.condition || 'MOC').toUpperCase();
    const grade = item.grading || 10.0;

    // Perfil canónico local y tema de facción
    const localProfile = getLocalMotuProfile(name, item.sub_category);
    const themeKey = aiResult?.frame_theme || localProfile.themeKey;
    const theme = FACTION_THEMES[themeKey] || FACTION_THEMES.castle_grayskull;
    const factionName = aiResult?.faction || localProfile.faction;
    const typeLineText = aiResult?.type_line || localProfile.typeLine;
    const specialMoveText = aiResult?.special_move || localProfile.specialMove;
    const loreText = aiResult?.lore || localProfile.lore;
    const statsData = aiResult?.stats || localProfile.stats;

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
            resetFraming();
        } catch (err: any) {
            console.error('Error transformando con Gemini:', err);
            setAiError('No se pudo conectar con Gemini. Inténtalo de nuevo.');
        } finally {
            setIsAiLoading(false);
        }
    };

    // Control de Arrastre con Ratón
    const handleImgMouseDown = (e: React.MouseEvent) => {
        if (e.button !== 0) return;
        e.preventDefault();
        e.stopPropagation();
        setIsDraggingImg(true);
        dragStartRef.current = {
            x: e.clientX,
            y: e.clientY,
            startPanX: imgPan.x,
            startPanY: imgPan.y
        };
    };

    const handleImgMouseMove = (e: React.MouseEvent) => {
        if (!isDraggingImg) return;
        e.preventDefault();
        e.stopPropagation();
        const dx = e.clientX - dragStartRef.current.x;
        const dy = e.clientY - dragStartRef.current.y;
        setImgPan({
            x: dragStartRef.current.startPanX + dx,
            y: dragStartRef.current.startPanY + dy
        });
    };

    const handleImgMouseUp = (e: React.MouseEvent) => {
        if (isDraggingImg) {
            e.stopPropagation();
            setIsDraggingImg(false);
        }
    };

    // Control de Zoom con Rueda del Ratón
    const handleImgWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        e.stopPropagation();
        const delta = e.deltaY < 0 ? 0.08 : -0.08;
        setImgZoom((prev) => Math.min(3.5, Math.max(0.4, +(prev + delta).toFixed(2))));
    };

    // Control Táctil (Móvil)
    const handleImgTouchStart = (e: React.TouchEvent) => {
        e.stopPropagation();
        if (e.touches.length === 1) {
            setIsDraggingImg(true);
            touchStartRef.current = {
                ...touchStartRef.current,
                x: e.touches[0].clientX,
                y: e.touches[0].clientY,
                startPanX: imgPan.x,
                startPanY: imgPan.y
            };
        } else if (e.touches.length === 2) {
            setIsDraggingImg(true);
            const dist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            touchStartRef.current = {
                dist,
                startZoom: imgZoom,
                x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
                y: (e.touches[0].clientY + e.touches[1].clientY) / 2,
                startPanX: imgPan.x,
                startPanY: imgPan.y
            };
        }
    };

    const handleImgTouchMove = (e: React.TouchEvent) => {
        if (!isDraggingImg) return;
        e.stopPropagation();
        if (e.touches.length === 1) {
            const dx = e.touches[0].clientX - touchStartRef.current.x;
            const dy = e.touches[0].clientY - touchStartRef.current.y;
            setImgPan({
                x: touchStartRef.current.startPanX + dx,
                y: touchStartRef.current.startPanY + dy
            });
        } else if (e.touches.length === 2 && touchStartRef.current.dist > 0) {
            const currentDist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            const scale = currentDist / touchStartRef.current.dist;
            setImgZoom(Math.min(3.5, Math.max(0.4, +(touchStartRef.current.startZoom * scale).toFixed(2))));
        }
    };

    const handleImgTouchEnd = (e: React.TouchEvent) => {
        e.stopPropagation();
        if (e.touches.length === 0) {
            setIsDraggingImg(false);
            touchStartRef.current.dist = 0;
        }
    };

    // 1. Descargar PNG HD
    const handleDownload = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            // Breve espera para que React aplique el ocultamiento de controles
            await new Promise((r) => setTimeout(r, 60));

            let dataUrl = '';
            let filename = '';

            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    faction: factionName,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData
                });
                filename = `Carta_TCG_${name.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${name.replace(/\s+/g, '_')}${aiResult ? `_${aiResult.style}` : ''}.png`;
            }

            if (!dataUrl) return;

            const link = document.createElement('a');
            link.download = filename;
            link.href = dataUrl;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setDownloaded(true);
            setTimeout(() => setDownloaded(false), 3000);
        } catch (err) {
            console.error('Error descargando:', err);
        } finally {
            setExporting(false);
        }
    };

    // 2. Copiar Imagen al Portapapeles
    const handleCopyImage = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            await new Promise((r) => setTimeout(r, 60));

            let dataUrl = '';
            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    faction: factionName,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData
                });
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
            }

            if (!dataUrl) return;
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

    // 3. Compartir nativo
    const handleNativeShare = async () => {
        if (!cardRef.current || !item) return;
        try {
            setExporting(true);
            await new Promise((r) => setTimeout(r, 60));

            let dataUrl = '';
            let filename = '';

            if (exportTarget === 'card') {
                const activeImage = aiResult?.image_base64 || undefined;
                dataUrl = await generateTradingCardDataUrl(cardRef.current, item, activeImage, aiResult?.lore, {
                    faction: factionName,
                    specialMove: specialMoveText,
                    lore: loreText,
                    stats: statsData
                });
                filename = `Carta_TCG_${name.replace(/\s+/g, '_')}.png`;
            } else {
                dataUrl = await getSingleIllustrationDataUrl(item, aiResult?.image_base64, imgZoom, imgPan);
                filename = `Ilustracion_${name.replace(/\s+/g, '_')}.png`;
            }

            if (!dataUrl) return;
            const blob = await dataUrlToBlob(dataUrl);
            const file = new File([blob], filename, { type: 'image/png' });

            let shareText = `🏰 Cromo Coleccionista: ${name}\n⚔️ Facción: ${factionName}\n⚡ Técnica: ${specialMoveText}`;
            if (loreText) shareText += `\n\n📜 "${loreText}"`;

            if (navigator.canShare && navigator.canShare({ files: [file] })) {
                await navigator.share({
                    title: `Cromo TCG: ${name}`,
                    text: shareText,
                    files: [file]
                });
                setShared(true);
                setTimeout(() => setShared(false), 3000);
            } else {
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
            console.error('Error compartiendo:', err);
        } finally {
            setExporting(false);
        }
    };

    const renderEmblemIcon = () => {
        if (theme.emblemIcon === 'skull') return <Skull className="h-3.5 w-3.5 text-purple-400" />;
        if (theme.emblemIcon === 'bat') return <Flame className="h-3.5 w-3.5 text-red-400" />;
        if (theme.emblemIcon === 'snake') return <Zap className="h-3.5 w-3.5 text-lime-400" />;
        if (theme.emblemIcon === 'sparkles') return <Sparkles className="h-3.5 w-3.5 text-pink-400" />;
        if (theme.emblemIcon === 'infinity') return <InfinityIcon className="h-3.5 w-3.5 text-cyan-400" />;
        return <Shield className="h-3.5 w-3.5 text-emerald-400" />;
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

                    {/* CONTENEDOR 3D DEL CROMO MTG SHOWCASE */}
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
                            className={`relative w-full max-w-[340px] rounded-2xl bg-gradient-to-b ${theme.headerBg} p-3.5 border-2 ${theme.borderClass} overflow-hidden select-none`}
                        >
                            {/* Bisel metálico grabado */}
                            <div className={`absolute inset-0.5 rounded-2xl border ${theme.innerBorderClass} pointer-events-none`} />
                            <div className="absolute inset-1.5 rounded-xl border border-amber-500/20 pointer-events-none" />

                            {/* Brillo reflectivo holográfico dinámico */}
                            <div
                                className="absolute inset-0 pointer-events-none z-10 transition-opacity duration-200"
                                style={{
                                    opacity: glarePos.opacity,
                                    background: `radial-gradient(circle at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,0.4) 0%, rgba(6,182,212,0.2) 30%, rgba(245,158,11,0.15) 55%, transparent 80%)`
                                }}
                            />

                            {/* 1. Cabecera MTG: Nombre con Relieve y Orbes de Poder */}
                            <div className="relative z-10 flex items-center justify-between border-b border-amber-500/30 pb-2 mb-2">
                                <div className="flex items-center gap-1.5 min-w-0 pr-1">
                                    <div className="p-1 rounded-md bg-gradient-to-br from-amber-400 to-yellow-600 text-black shadow-sm shrink-0">
                                        {renderEmblemIcon()}
                                    </div>
                                    <h3 className="text-xs sm:text-sm font-black text-white uppercase tracking-wider truncate drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
                                        {name}
                                    </h3>
                                </div>

                                {/* Orbes de Maná / Poder */}
                                <div className="flex items-center gap-1 shrink-0 bg-black/60 px-2 py-0.5 rounded-full border border-amber-400/40 shadow-inner">
                                    {theme.gemColors.map((color, idx) => (
                                        <div
                                            key={idx}
                                            className="w-2.5 h-2.5 rounded-full shadow-sm"
                                            style={{
                                                backgroundColor: color,
                                                boxShadow: `0 0 6px ${color}`
                                            }}
                                        />
                                    ))}
                                </div>
                            </div>

                            {/* 2. Ventana de Arte Coleccionista (Foto HD o Arte IA con Zoom/Encuadre) */}
                            <div
                                onMouseDown={handleImgMouseDown}
                                onMouseMove={handleImgMouseMove}
                                onMouseUp={handleImgMouseUp}
                                onMouseLeave={handleImgMouseUp}
                                onWheel={handleImgWheel}
                                onTouchStart={handleImgTouchStart}
                                onTouchMove={handleImgTouchMove}
                                onTouchEnd={handleImgTouchEnd}
                                onContextMenu={(e) => {
                                    e.preventDefault();
                                    resetFraming();
                                }}
                                onDoubleClick={(e) => {
                                    e.preventDefault();
                                    resetFraming();
                                }}
                                className={`relative z-10 h-52 w-full rounded-xl bg-gradient-to-b from-slate-950 via-slate-900 to-black border-2 border-amber-500/40 flex items-center justify-center overflow-hidden mb-2 group shadow-inner select-none ${
                                    isDraggingImg ? 'cursor-grabbing' : 'cursor-grab'
                                }`}
                                title="Arrastra con el ratón o usa la rueda para ampliar y encuadrar"
                            >
                                {/* Patrón de rejilla de fondo */}
                                <div
                                    className="absolute inset-0 opacity-10 pointer-events-none"
                                    style={{
                                        backgroundImage: 'radial-gradient(#22d3ee 1px, transparent 1px)',
                                        backgroundSize: '12px 12px'
                                    }}
                                />

                                {/* Capa de la Imagen con Zoom y Desplazamiento */}
                                <div
                                    className="absolute flex items-center justify-center pointer-events-none select-none"
                                    style={{
                                        transform: `translate(${imgPan.x}px, ${imgPan.y}px) scale(${imgZoom})`,
                                        transformOrigin: 'center center',
                                        transition: isDraggingImg ? 'none' : 'transform 0.1s ease-out'
                                    }}
                                >
                                    {aiResult?.image_base64 ? (
                                        <img
                                            src={aiResult.image_base64}
                                            alt={name}
                                            draggable={false}
                                            className="max-w-none max-h-none select-none pointer-events-none animate-in fade-in duration-300"
                                            style={{
                                                width: '320px',
                                                height: 'auto',
                                                minHeight: '208px',
                                                display: 'block'
                                            }}
                                        />
                                    ) : (
                                        <div className="flex items-center justify-center pointer-events-none select-none" style={{ width: '320px', height: '208px' }}>
                                            <MOTUImage
                                                productId={item.id}
                                                src={item.image_url}
                                                alt={name}
                                                className="max-h-full max-w-full object-contain p-2.5 z-10 drop-shadow-[0_10px_15px_rgba(0,0,0,0.8)] pointer-events-none select-none"
                                            />
                                        </div>
                                    )}
                                </div>

                                {/* Mini Barra de Herramientas de Zoom Flotante (OCULTA EN EXPORTACIÓN) */}
                                {!exporting && (
                                    <div className="export-exclude absolute top-2 right-2 z-30 flex items-center gap-1 bg-black/80 backdrop-blur-md px-1.5 py-1 rounded-lg border border-slate-700/80 shadow-md opacity-80 group-hover:opacity-100 transition-opacity">
                                        <button
                                            type="button"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setImgZoom((prev) => Math.min(3.5, +(prev + 0.15).toFixed(2)));
                                            }}
                                            title="Ampliar Imagen (+)"
                                            className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                        >
                                            <Plus className="h-3 w-3" />
                                        </button>
                                        <button
                                            type="button"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setImgZoom((prev) => Math.max(0.4, +(prev - 0.15).toFixed(2)));
                                            }}
                                            title="Reducir Imagen (-)"
                                            className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition active:scale-90"
                                        >
                                            <Minus className="h-3 w-3" />
                                        </button>
                                        {(imgZoom !== 1 || imgPan.x !== 0 || imgPan.y !== 0) && (
                                            <button
                                                type="button"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    resetFraming();
                                                }}
                                                title="Restablecer Encuadre Original"
                                                className="p-1 hover:bg-rose-500/20 text-amber-400 hover:text-rose-300 rounded transition active:scale-90"
                                            >
                                                <RotateCcw className="h-3 w-3" />
                                            </button>
                                        )}
                                    </div>
                                )}

                                {/* Pista de Interacción (OCULTA EN EXPORTACIÓN) */}
                                {!exporting && (
                                    <div className="export-exclude absolute bottom-2 left-2 z-20 pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity">
                                        <span className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-black/75 border border-slate-800 text-[8px] font-mono text-slate-300">
                                            <Move className="h-2.5 w-2.5 text-amber-400" />
                                            {imgZoom !== 1 ? `${Math.round(imgZoom * 100)}%` : 'Arrastra / Zoom'}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* 3. Barra de Tipo y Facción (Type-Line MTG) */}
                            <div className="relative z-10 flex items-center justify-between px-2.5 py-1 rounded-lg bg-slate-950/95 border border-amber-500/30 mb-2 shadow-inner">
                                <div className="flex items-center gap-1.5 min-w-0">
                                    <Swords className="h-3 w-3 text-amber-400 shrink-0" />
                                    <span className="text-[9px] font-black text-amber-200 uppercase tracking-wide truncate">
                                        {typeLineText}
                                    </span>
                                </div>
                                <span className="text-[8px] font-mono font-bold text-slate-400 shrink-0 ml-1">
                                    {item.sub_category || 'ORIGINS'}
                                </span>
                            </div>

                            {/* 4. Text Box: Habilidad Definitiva + Lore Canónico */}
                            <div className="relative z-10 bg-slate-950/95 border border-amber-500/25 rounded-xl p-2 mb-2 shadow-inner">
                                {/* Habilidad / Ataque */}
                                <div className="flex items-center gap-1 text-[10px] font-black text-amber-300 uppercase tracking-wider mb-1">
                                    <Zap className="h-3 w-3 text-yellow-400 shrink-0" />
                                    <span className="truncate">{specialMoveText}</span>
                                </div>

                                {/* Línea Divisoria Ornamental */}
                                <div className="w-full h-px bg-gradient-to-r from-transparent via-amber-500/40 to-transparent my-1" />

                                {/* Lore Canónico en Cursiva (Flavor Text) */}
                                <p className="text-[8.5px] text-slate-300 italic leading-snug line-clamp-2 px-0.5">
                                    "{loreText}"
                                </p>
                            </div>

                            {/* 5. Placas de Estadísticas RPG y Sello Holográfico de Grayskull */}
                            <div className="relative z-10 flex items-center justify-between bg-slate-950/95 border border-amber-500/30 rounded-xl px-2 py-1.5 mb-1.5 shadow-inner">
                                {/* Lado Izquierdo: FUERZA / MAGIA */}
                                <div className="flex items-center gap-2 font-mono text-[9px]">
                                    <span className="text-red-400 font-bold">FUE <strong className="text-white text-xs">{statsData.fuerza}</strong></span>
                                    <span className="text-slate-600">•</span>
                                    <span className="text-purple-400 font-bold">MAG <strong className="text-white text-xs">{statsData.magia}</strong></span>
                                </div>

                                {/* Sello Holográfico Oval 3D Central */}
                                <div
                                    className="w-12 h-6 rounded-full border border-amber-300/60 flex items-center justify-center shadow-md overflow-hidden relative"
                                    style={{
                                        background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 30%, #ec4899 70%, #f59e0b 100%)'
                                    }}
                                    title="Sello de Autenticidad Grayskull"
                                >
                                    <div className="absolute inset-0 bg-white/20 backdrop-blur-[0.5px]" />
                                    <Shield className="h-3 w-3 text-black/80 drop-shadow-sm z-10" />
                                </div>

                                {/* Lado Derecho: DEFENSA / AGILIDAD */}
                                <div className="flex items-center gap-2 font-mono text-[9px]">
                                    <span className="text-blue-400 font-bold">DEF <strong className="text-white text-xs">{statsData.defensa}</strong></span>
                                    <span className="text-slate-600">•</span>
                                    <span className="text-emerald-400 font-bold">AGI <strong className="text-white text-xs">{statsData.agilidad}</strong></span>
                                </div>
                            </div>

                            {/* 6. Sello de Autenticidad en Footer */}
                            <div className="relative z-10 flex items-center justify-between border-t border-slate-800/80 pt-1 px-1 text-[7.5px] text-slate-400 uppercase tracking-widest font-mono">
                                <div className="flex items-center gap-1">
                                    <Lock className="h-2 w-2 text-amber-400" />
                                    <span>FORTALEZA DE GRAYSKULL</span>
                                </div>
                                <span className="text-amber-400/80 font-bold">#{ (item.sku || String(item.id)).slice(-5) } • NUEVA ETERNIA</span>
                            </div>
                        </motion.div>
                    </div>

                    {/* SELECTOR DE MODO: CARTA COMPLETA VS SOLO ILUSTRACIÓN */}
                    <div className="w-full flex items-center justify-center p-1 rounded-xl bg-slate-950/90 border border-amber-500/30 gap-1 mt-3 mb-1 shadow-inner">
                        <button
                            onClick={() => setExportTarget('card')}
                            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[11px] font-black uppercase tracking-wider transition-all ${
                                exportTarget === 'card'
                                    ? 'bg-gradient-to-r from-amber-500 to-yellow-600 text-black shadow-md shadow-amber-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                            }`}
                        >
                            <Shield className="h-3.5 w-3.5" />
                            <span>🃏 Carta Completa</span>
                        </button>
                        <button
                            onClick={() => setExportTarget('image')}
                            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-[11px] font-black uppercase tracking-wider transition-all ${
                                exportTarget === 'image'
                                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                            }`}
                        >
                            <ImageIcon className="h-3.5 w-3.5" />
                            <span>🖼️ Solo Ilustración</span>
                        </button>
                    </div>

                    {/* BOTONES DE EXPORTACIÓN Y COMPARTIR */}
                    <div className="w-full grid grid-cols-3 gap-2 mt-2">
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
                            <span>{shared ? '¡Compartido!' : 'WhatsApp / Redes'}</span>
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
                            <span>
                                {copied
                                    ? '¡Copiado!'
                                    : exportTarget === 'card'
                                    ? 'Copiar Carta'
                                    : 'Copiar Ilustración'}
                            </span>
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
                            <span>
                                {downloaded
                                    ? '¡Descargado!'
                                    : exportTarget === 'card'
                                    ? 'Descargar Carta'
                                    : 'Descargar HD'}
                            </span>
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TradingCardModal;

