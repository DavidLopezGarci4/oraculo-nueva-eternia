import React, { useState, useEffect, useRef } from 'react';
import { Activity, TrendingUp, TrendingDown, DollarSign, Award, Sparkles, Calendar } from 'lucide-react';
import axios from 'axios';

interface HistoricalPoint {
    date: string;
    index_value: number;
    volume?: number;
}

interface WaveBreakdown {
    category: string;
    figures_count: number;
    avg_msrp: number;
    avg_market: number;
    revaluation_pct: number;
}

interface PortfolioMetrics {
    total_items_in_collection: number;
    total_invested_eur: number;
    total_market_value_eur: number;
    net_unrealized_profit_eur: number;
    roi_percentage: number;
    bargains_detected_count: number;
    overpaid_count: number;
    total_bargain_savings_eur: number;
    alpha_percentage: number;
}

interface MarketIndexData {
    current_index_value: number;
    base_msrp_value: number;
    trend_pct: number;
    trend_direction: 'bullish' | 'bearish' | 'stable';
    status_label: string;
    period: string;
    historical_series: HistoricalPoint[];
    waves_breakdown: WaveBreakdown[];
    portfolio_metrics?: PortfolioMetrics | null;
}

export const EterniaMarketIndexWidget: React.FC = () => {
    const [period, setPeriod] = useState<string>('3M');
    const [data, setData] = useState<MarketIndexData | null>(null);
    const [loading, setLoading] = useState(true);
    const [hoverPoint, setHoverPoint] = useState<HistoricalPoint | null>(null);
    const [hoverIndex, setHoverIndex] = useState<number | null>(null);
    const svgRef = useRef<SVGSVGElement | null>(null);

    const fetchIndex = async (p: string) => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const activeUserId = localStorage.getItem('active_user_id') || '2';
            const res = await axios.get(`/api/analytics/market-index?period=${p}&user_id=${activeUserId}`, {
                headers: token ? { Authorization: `Bearer ${token}` } : {}
            });
            setData(res.data);
        } catch (e) {
            console.error('Error fetching market index:', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchIndex(period);
    }, [period]);

    if (loading && !data) {
        return (
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 mb-6 animate-pulse">
                <div className="flex items-center justify-between mb-4">
                    <div className="h-6 bg-slate-800 rounded w-48"></div>
                    <div className="h-8 bg-slate-800 rounded w-36"></div>
                </div>
                <div className="h-44 bg-slate-950/60 rounded-xl mb-4"></div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="h-16 bg-slate-800/40 rounded-xl"></div>
                    <div className="h-16 bg-slate-800/40 rounded-xl"></div>
                    <div className="h-16 bg-slate-800/40 rounded-xl"></div>
                    <div className="h-16 bg-slate-800/40 rounded-xl"></div>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const isBullish = data.trend_direction === 'bullish';
    const isBearish = data.trend_direction === 'bearish';

    const trendColor = isBullish ? 'text-emerald-400' : isBearish ? 'text-rose-400' : 'text-cyan-400';
    const badgeBg = isBullish ? 'bg-emerald-500/15 border-emerald-500/30' : isBearish ? 'bg-rose-500/15 border-rose-500/30' : 'bg-cyan-500/15 border-cyan-500/30';

    // Dimensiones de la gráfica SVG responsiva
    const series = data.historical_series || [];
    const values = series.map((s) => s.index_value);
    const minVal = values.length > 0 ? Math.min(...values) * 0.92 : data.base_msrp_value * 0.8;
    const maxVal = values.length > 0 ? Math.max(...values) * 1.08 : data.base_msrp_value * 1.3;
    const range = Math.max(1, maxVal - minVal);

    const svgWidth = 700;
    const svgHeight = 150;
    const padX = 25;
    const padTop = 15;
    const padBottom = 30;
    const chartW = svgWidth - padX * 2;
    const chartH = svgHeight - padTop - padBottom;

    const points = series.map((s, idx) => {
        const x = padX + (idx / Math.max(1, series.length - 1)) * chartW;
        const y = padTop + chartH - ((s.index_value - minVal) / range) * chartH;
        return { x, y, data: s };
    });

    const pathD = points.length > 0 ? `M ${points.map((p) => `${p.x},${p.y}`).join(' L ')}` : '';
    const areaD = points.length > 0 ? `${pathD} L ${padX + chartW},${padTop + chartH} L ${padX},${padTop + chartH} Z` : '';

    // Manejo de interacción de cursor / toque
    const handleMouseMove = (e: React.MouseEvent<SVGSVGElement> | React.TouchEvent<SVGSVGElement>) => {
        if (!svgRef.current || points.length === 0) return;
        const rect = svgRef.current.getBoundingClientRect();
        const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
        const relX = ((clientX - rect.left) / rect.width) * svgWidth;

        let closestIdx = 0;
        let minDiff = Infinity;
        points.forEach((p, idx) => {
            const diff = Math.abs(p.x - relX);
            if (diff < minDiff) {
                minDiff = diff;
                closestIdx = idx;
            }
        });

        setHoverIndex(closestIdx);
        setHoverPoint(points[closestIdx].data);
    };

    const handleMouseLeave = () => {
        setHoverIndex(null);
        setHoverPoint(null);
    };

    // Fechas clave para el eje X
    const dateLabels: Array<{ label: string; x: number }> = [];
    if (points.length >= 3) {
        const step = Math.floor((points.length - 1) / 3);
        const indices = [0, step, step * 2, points.length - 1];
        indices.forEach((idx) => {
            const pt = points[idx];
            if (pt) {
                const parts = pt.data.date.split('-');
                const formatted = parts.length === 3 ? `${parts[2]}/${parts[1]}` : pt.data.date;
                dateLabels.push({ label: formatted, x: pt.x });
            }
        });
    }

    const port = data.portfolio_metrics;

    return (
        <div className="bg-gradient-to-br from-slate-900/90 via-slate-950 to-black border border-slate-800/80 rounded-2xl md:rounded-3xl p-4 sm:p-6 mb-6 shadow-2xl backdrop-blur-md">
            {/* Header del Widget */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                        <Activity className="h-6 w-6" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="text-base sm:text-lg font-black text-white tracking-wide uppercase">
                                Índice Bursátil MOTU (EMI)
                            </h3>
                            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-mono font-bold flex items-center gap-1 ${badgeBg} ${trendColor}`}>
                                {isBullish ? <TrendingUp className="h-3.5 w-3.5" /> : isBearish ? <TrendingDown className="h-3.5 w-3.5" /> : null}
                                {data.trend_pct >= 0 ? '+' : ''}{data.trend_pct}%
                            </span>
                        </div>
                        <p className="text-xs text-slate-400 font-medium">
                            Cotización del mercado secundario ponderada por recencia (EMA) y volumen
                        </p>
                    </div>
                </div>

                {/* Selector de Período Temporal */}
                <div className="flex items-center gap-1 bg-slate-950/90 p-1.5 rounded-xl border border-slate-800/90 self-start sm:self-auto shadow-inner">
                    {['1M', '3M', '6M', '1A', 'ALL'].map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                                period === p
                                    ? 'bg-cyan-500/25 text-cyan-300 border border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                                    : 'text-slate-400 hover:text-slate-200'
                            }`}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {/* KPIs Financieros Clave (Fila Superior) */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                {/* KPI 1: Cotización Actual EMI */}
                <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                    <div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 block mb-0.5">
                            Cotización Media Actual
                        </span>
                        <div className="flex items-baseline gap-2">
                            <span className="text-xl font-black text-white">{data.current_index_value.toFixed(2)} €</span>
                            <span className="text-[11px] font-bold text-slate-500 line-through">PVP {data.base_msrp_value.toFixed(2)}€</span>
                        </div>
                    </div>
                    <div className={`px-2 py-1 rounded-lg text-xs font-mono font-bold ${trendColor} ${badgeBg}`}>
                        {data.trend_pct >= 0 ? '+' : ''}{data.trend_pct}%
                    </div>
                </div>

                {/* KPI 2: Plusvalía Neta de la Colección */}
                {port && (
                    <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                        <div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400/80 block mb-0.5 flex items-center gap-1">
                                <DollarSign className="h-3 w-3" /> Tu Plusvalía Neta
                            </span>
                            <div className="flex items-baseline gap-2">
                                <span className="text-xl font-black text-emerald-400 blur-incognito">
                                    {port.net_unrealized_profit_eur >= 0 ? '+' : ''}{port.net_unrealized_profit_eur.toLocaleString('es-ES')} €
                                </span>
                                <span className="text-[11px] font-bold text-emerald-500/80 font-mono blur-incognito">
                                    (+{port.roi_percentage}%)
                                </span>
                            </div>
                        </div>
                        <span className="text-[9px] font-bold text-slate-400 text-right">
                            {port.total_items_in_collection} figuras
                        </span>
                    </div>
                )}

                {/* KPI 3: Alpha / Gangas Conseguidas */}
                {port && (
                    <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                        <div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-amber-400/80 block mb-0.5 flex items-center gap-1">
                                <Sparkles className="h-3 w-3" /> Gangas / Ahorro
                            </span>
                            <div className="flex items-baseline gap-2">
                                <span className="text-xl font-black text-amber-400 blur-incognito">
                                    {port.total_bargain_savings_eur.toLocaleString('es-ES')} €
                                </span>
                                <span className="text-[11px] font-bold text-amber-300 font-mono">
                                    ({port.bargains_detected_count} gangas)
                                </span>
                            </div>
                        </div>
                        <div className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-[10px] font-bold text-amber-300 font-mono">
                            Alpha +{port.alpha_percentage}%
                        </div>
                    </div>
                )}
            </div>

            {/* Gráfico Vectorial Responsivo de Alta Precisión */}
            <div className="relative w-full bg-slate-950/90 rounded-2xl border border-slate-800/90 overflow-hidden mb-5 p-3 select-none">
                <svg
                    ref={svgRef}
                    viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                    className="w-full h-36 sm:h-44 overflow-visible cursor-crosshair"
                    onMouseMove={handleMouseMove}
                    onTouchMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    onTouchEnd={handleMouseLeave}
                >
                    <defs>
                        <linearGradient id="emiAreaGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.45" />
                            <stop offset="60%" stopColor="#06b6d4" stopOpacity="0.12" />
                            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
                        </linearGradient>
                        <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="2.5" result="blur" />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>

                    {/* Líneas Guía Horizontales Sutiles */}
                    <line x1={padX} y1={padTop} x2={padX + chartW} y2={padTop} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
                    <line x1={padX} y1={padTop + chartH * 0.5} x2={padX + chartW} y2={padTop + chartH * 0.5} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
                    <line x1={padX} y1={padTop + chartH} x2={padX + chartW} y2={padTop + chartH} stroke="rgba(255,255,255,0.12)" />

                    {/* Área con Gradiente Cyan */}
                    {areaD && <path d={areaD} fill="url(#emiAreaGradient)" />}

                    {/* Línea de Cotización Principal */}
                    {pathD && (
                        <path
                            d={pathD}
                            fill="none"
                            stroke="#00f3ff"
                            strokeWidth="2.8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            filter="url(#glowEffect)"
                        />
                    )}

                    {/* Cursor Vertical Interactivo al Pasar el Ratón o Tocar */}
                    {hoverIndex !== null && points[hoverIndex] && (
                        <>
                            <line
                                x1={points[hoverIndex].x}
                                y1={padTop}
                                x2={points[hoverIndex].x}
                                y2={padTop + chartH}
                                stroke="#22d3ee"
                                strokeWidth="1.2"
                                strokeDasharray="4 3"
                            />
                            <circle
                                cx={points[hoverIndex].x}
                                cy={points[hoverIndex].y}
                                r="5.5"
                                fill="#ffffff"
                                stroke="#00f3ff"
                                strokeWidth="2.5"
                                filter="url(#glowEffect)"
                            />
                        </>
                    )}

                    {/* Eje X: Etiquetas de Fechas Legibles */}
                    {dateLabels.map((dl, idx) => (
                        <text
                            key={idx}
                            x={dl.x}
                            y={svgHeight - 8}
                            textAnchor={idx === 0 ? 'start' : idx === dateLabels.length - 1 ? 'end' : 'middle'}
                            className="text-[10px] font-bold fill-slate-500"
                        >
                            {dl.label}
                        </text>
                    ))}
                </svg>

                {/* Tooltip HUD Flotante Interactivo */}
                {hoverPoint && (
                    <div className="absolute top-3 left-4 bg-slate-900/95 border border-cyan-400/40 rounded-xl p-2.5 shadow-2xl backdrop-blur-md pointer-events-none animate-in fade-in duration-150 z-20">
                        <div className="flex items-center gap-1.5 text-[10px] font-bold text-cyan-300 mb-0.5">
                            <Calendar className="h-3 w-3" />
                            <span>{hoverPoint.date}</span>
                        </div>
                        <div className="text-sm font-black text-white">
                            {hoverPoint.index_value.toFixed(2)} €
                        </div>
                        {hoverPoint.volume !== undefined && (
                            <div className="text-[9px] text-slate-400 font-medium">
                                {hoverPoint.volume} cotizaciones procesadas
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Desglose Cuantitativo por Waves (Carrusel Horizontal Táctil) */}
            <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-widest text-slate-400">
                    <span className="flex items-center gap-1.5">
                        <Award className="h-3.5 w-3.5 text-cyan-400" />
                        Desglose de Cotización por Subcategorías & Waves
                    </span>
                    <span className="text-[9px] text-slate-500">MSRP vs Fair Market Value</span>
                </div>

                <div className="flex items-center gap-2.5 overflow-x-auto pb-2 custom-scrollbar">
                    {data.waves_breakdown.map((w) => {
                        const isPos = w.revaluation_pct >= 0;
                        return (
                            <div
                                key={w.category}
                                className="flex-shrink-0 bg-slate-950/80 border border-slate-800/80 hover:border-cyan-500/30 rounded-xl p-3 min-w-[150px] sm:min-w-[170px] transition-all"
                            >
                                <div className="text-[11px] font-black text-slate-200 truncate mb-1" title={w.category}>
                                    {w.category}
                                </div>
                                <div className="flex items-baseline justify-between gap-1 mb-1">
                                    <span className="font-black text-white text-sm">{w.avg_market.toFixed(2)} €</span>
                                    <span className="text-[10px] font-bold text-slate-500">PVP {w.avg_msrp.toFixed(2)}€</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className={`text-[10px] font-black font-mono ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {isPos ? '+' : ''}{w.revaluation_pct}% vs salida
                                    </span>
                                    <span className="text-[9px] text-slate-500 font-bold">
                                        {w.figures_count} figs
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default EterniaMarketIndexWidget;
