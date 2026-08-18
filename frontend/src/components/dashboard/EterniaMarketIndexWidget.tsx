import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import axios from 'axios';

interface MarketIndexData {
    current_index_value: number;
    base_msrp_value: number;
    trend_pct: number;
    trend_direction: 'bullish' | 'bearish' | 'stable';
    status_label: string;
    period: string;
    historical_series: Array<{ date: string; index_value: number }>;
    waves_breakdown: Array<{
        category: string;
        figures_count: number;
        avg_msrp: number;
        avg_market: number;
        revaluation_pct: number;
    }>;
}

export const EterniaMarketIndexWidget: React.FC = () => {
    const [period, setPeriod] = useState<string>('3M');
    const [data, setData] = useState<MarketIndexData | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchIndex = async (p: string) => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const res = await axios.get(`/api/analytics/market-index?period=${p}`, {
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
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 mb-6 animate-pulse">
                <div className="h-5 bg-slate-800 rounded w-48 mb-3"></div>
                <div className="h-32 bg-slate-950/60 rounded-lg"></div>
            </div>
        );
    }

    if (!data) return null;

    const isBullish = data.trend_direction === 'bullish';
    const isBearish = data.trend_direction === 'bearish';

    const trendColor = isBullish ? 'text-emerald-400' : isBearish ? 'text-rose-400' : 'text-cyan-400';
    const badgeBg = isBullish ? 'bg-emerald-500/15 border-emerald-500/30' : isBearish ? 'bg-rose-500/15 border-rose-500/30' : 'bg-cyan-500/15 border-cyan-500/30';

    // Generar path SVG responsivo para la serie histórica
    const series = data.historical_series || [];
    const minVal = Math.min(...series.map((s) => s.index_value), data.base_msrp_value * 0.8);
    const maxVal = Math.max(...series.map((s) => s.index_value), data.base_msrp_value * 1.3);
    const range = Math.max(1, maxVal - minVal);

    const width = 300;
    const height = 80;

    const points = series.map((s, idx) => {
        const x = (idx / Math.max(1, series.length - 1)) * width;
        const y = height - ((s.index_value - minVal) / range) * (height - 15) - 5;
        return `${x},${y}`;
    });

    const pathD = points.length > 0 ? `M ${points.join(' L ')}` : '';
    const areaD = points.length > 0 ? `${pathD} L ${width},${height} L 0,${height} Z` : '';

    return (
        <div className="bg-gradient-to-br from-slate-900/90 via-slate-950 to-black border border-slate-800/80 rounded-2xl p-4 sm:p-5 mb-6 shadow-xl backdrop-blur-md">
            {/* Header del Widget */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2.5">
                    <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
                        <Activity className="h-5 w-5" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-sm sm:text-base font-bold text-slate-100 tracking-wide">
                                Índice Bursátil MOTU (EMI)
                            </h3>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full border font-mono font-bold ${badgeBg} ${trendColor}`}>
                                {data.trend_pct >= 0 ? '+' : ''}{data.trend_pct}%
                            </span>
                        </div>
                        <p className="text-xs text-slate-400">
                            Cotización media del mercado secundario ponderada por Waves
                        </p>
                    </div>
                </div>

                {/* Selector de Período Temporal */}
                <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-slate-800 self-start sm:self-auto">
                    {['1M', '3M', '6M', '1A', 'ALL'].map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition ${
                                period === p
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                                    : 'text-slate-400 hover:text-slate-200'
                            }`}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {/* Gráfico Vectorial Responsivo */}
            <div className="relative w-full h-24 bg-slate-950/60 rounded-xl border border-slate-800/80 overflow-hidden mb-4 p-2 flex items-center">
                <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full preserve-3d overflow-visible">
                    <defs>
                        <linearGradient id="emiGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4" />
                            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
                        </linearGradient>
                    </defs>
                    {areaD && <path d={areaD} fill="url(#emiGradient)" />}
                    {pathD && (
                        <path
                            d={pathD}
                            fill="none"
                            stroke="#22d3ee"
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    )}
                </svg>

                {/* Valor Flotante */}
                <div className="absolute right-4 top-3 text-right">
                    <span className="text-xs text-slate-400 block">Cotización Media:</span>
                    <span className="text-lg font-black text-white">{data.current_index_value.toFixed(2)} €</span>
                </div>
            </div>

            {/* Desglose por Waves (Carrusel Horizontal Táctil) */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar">
                {data.waves_breakdown.map((w) => (
                    <div
                        key={w.category}
                        className="flex-shrink-0 bg-slate-950/80 border border-slate-800/80 rounded-lg p-2.5 min-w-[130px]"
                    >
                        <div className="text-[10px] text-slate-400 truncate mb-0.5">{w.category}</div>
                        <div className="font-bold text-white text-xs">{w.avg_market.toFixed(2)} €</div>
                        <div className={`text-[10px] font-semibold mt-0.5 ${w.revaluation_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {w.revaluation_pct >= 0 ? '+' : ''}{w.revaluation_pct}% vs salida
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EterniaMarketIndexWidget;
