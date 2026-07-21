import React from 'react';
import { RefreshCw, History, X } from 'lucide-react';
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts';
import type { Product } from '../../api/collection';
import CustomTooltip from './CustomTooltip';

interface CronosViewProps {
    selectedCronosA: Product | null;
    setSelectedCronosA: (product: Product | null) => void;
    cronosSearchA: string;
    setCronosSearchA: (term: string) => void;
    selectedCronosB: Product | null;
    setSelectedCronosB: (product: Product | null) => void;
    cronosSearchB: string;
    setCronosSearchB: (term: string) => void;
    products: Product[] | undefined;
    availableShops: string[] | undefined;
    activeCronosShops: string[];
    setActiveCronosShops: (shops: string[]) => void;
    cronosStats: {
        a?: { min: number; max: number; name: string };
        b?: { min: number; max: number; name: string };
    };
    loadingCronosA: boolean;
    loadingCronosB: boolean;
    chartData: any[];
    chartLines: { key: string; color: string }[];
}

const CronosView: React.FC<CronosViewProps> = ({
    selectedCronosA,
    setSelectedCronosA,
    cronosSearchA,
    setCronosSearchA,
    selectedCronosB,
    setSelectedCronosB,
    cronosSearchB,
    setCronosSearchB,
    products,
    availableShops,
    activeCronosShops,
    setActiveCronosShops,
    cronosStats,
    loadingCronosA,
    loadingCronosB,
    chartData,
    chartLines
}) => {
    return (
        <div className="relative overflow-hidden rounded-[2rem] border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Autocomplete Reliquia A */}
                <div className="relative space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Reliquia Principal (A)</label>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Buscar Reliquia A..."
                            value={selectedCronosA ? selectedCronosA.name : cronosSearchA}
                            onChange={(e) => {
                                setCronosSearchA(e.target.value);
                                if (selectedCronosA) setSelectedCronosA(null);
                            }}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white text-xs md:text-sm font-bold focus:outline-none focus:border-brand-primary transition-all"
                        />
                        {selectedCronosA && (
                            <button
                                onClick={() => { setSelectedCronosA(null); setCronosSearchA(''); }}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white font-bold"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                    {/* Dropdown Suggestions */}
                    {!selectedCronosA && cronosSearchA.trim().length > 1 && (
                        <div className="absolute z-50 w-full mt-1 bg-black/90 border border-white/10 rounded-2xl max-h-60 overflow-y-auto shadow-2xl custom-scrollbar">
                            {products?.filter(p => p.name.toLowerCase().includes(cronosSearchA.toLowerCase()))
                                .map(p => (
                                    <div
                                        key={p.id}
                                        onClick={() => {
                                            setSelectedCronosA(p);
                                            setCronosSearchA(p.name);
                                        }}
                                        className="px-4 py-3 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                    >
                                        {p.name} <span className="opacity-40 ml-2">#{p.figure_id}</span>
                                    </div>
                                ))
                            }
                        </div>
                    )}
                </div>

                {/* Autocomplete Reliquia B */}
                <div className="relative space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Reliquia a Comparar (B)</label>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Buscar Reliquia B..."
                            value={selectedCronosB ? selectedCronosB.name : cronosSearchB}
                            onChange={(e) => {
                                setCronosSearchB(e.target.value);
                                if (selectedCronosB) setSelectedCronosB(null);
                            }}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-white text-xs md:text-sm font-bold focus:outline-none focus:border-brand-primary transition-all"
                        />
                        {selectedCronosB && (
                            <button
                                onClick={() => { setSelectedCronosB(null); setCronosSearchB(''); }}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white font-bold"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                    {/* Dropdown Suggestions */}
                    {!selectedCronosB && cronosSearchB.trim().length > 1 && (
                        <div className="absolute z-50 w-full mt-1 bg-black/90 border border-white/10 rounded-2xl max-h-60 overflow-y-auto shadow-2xl custom-scrollbar">
                            {products?.filter(p => p.name.toLowerCase().includes(cronosSearchB.toLowerCase()))
                                .map(p => (
                                    <div
                                        key={p.id}
                                        onClick={() => {
                                            setSelectedCronosB(p);
                                            setCronosSearchB(p.name);
                                        }}
                                        className="px-4 py-3 hover:bg-white/5 text-xs text-white/70 hover:text-white cursor-pointer font-bold transition-colors border-b border-white/5 last:border-0"
                                    >
                                        {p.name} <span className="opacity-40 ml-2">#{p.figure_id}</span>
                                    </div>
                                ))
                            }
                        </div>
                    )}
                </div>
            </div>

            {/* Shop Selection Checkboxes */}
            <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-white/60 ml-1">Filtrar por Tienda</label>
                <div className="flex flex-wrap gap-3 bg-white/[0.02] border border-white/5 p-4 rounded-3xl">
                    {availableShops?.map(shop => {
                        const isChecked = activeCronosShops.includes(shop);
                        return (
                            <label key={shop} className="flex items-center gap-2 cursor-pointer bg-white/5 px-3 py-1.5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                                <input
                                    type="checkbox"
                                    checked={isChecked}
                                    onChange={() => {
                                        if (isChecked) {
                                            setActiveCronosShops(activeCronosShops.filter(s => s !== shop));
                                        } else {
                                            setActiveCronosShops([...activeCronosShops, shop]);
                                        }
                                    }}
                                    className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary/50"
                                />
                                <span className="text-[10px] font-black uppercase tracking-wider text-white/80">{shop}</span>
                            </label>
                        );
                    })}
                    {(!availableShops || availableShops.length === 0) && (
                        <div className="text-[10px] font-bold text-white/60 uppercase tracking-widest py-1">Cargando tiendas...</div>
                    )}
                </div>
            </div>

            {/* Cronos Stats Cards */}
            {cronosStats && (cronosStats.a || cronosStats.b) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                    {cronosStats.a && (
                        <div className="rounded-2xl border border-sky-500/20 bg-sky-500/5 p-4 flex items-center justify-between backdrop-blur-md">
                            <div>
                                <span className="block text-[8px] font-black uppercase tracking-wider text-sky-400">Rango de Precios - Reliquia A</span>
                                <span className="text-xs font-bold text-white truncate max-w-[200px] block">{cronosStats.a.name}</span>
                            </div>
                            <div className="flex gap-4">
                                <div className="text-right">
                                    <span className="block text-[8px] font-black uppercase text-white/40">Mínimo</span>
                                    <span className="text-base font-black text-green-400">{cronosStats.a.min.toFixed(2)} €</span>
                                </div>
                                <div className="text-right">
                                    <span className="block text-[8px] font-black uppercase text-white/40">Máximo</span>
                                    <span className="text-base font-black text-red-400">{cronosStats.a.max.toFixed(2)} €</span>
                                </div>
                            </div>
                        </div>
                    )}
                    {cronosStats.b && (
                        <div className="rounded-2xl border border-pink-500/20 bg-pink-500/5 p-4 flex items-center justify-between backdrop-blur-md">
                            <div>
                                <span className="block text-[8px] font-black uppercase tracking-wider text-pink-400">Rango de Precios - Reliquia B</span>
                                <span className="text-xs font-bold text-white truncate max-w-[200px] block">{cronosStats.b.name}</span>
                            </div>
                            <div className="flex gap-4">
                                <div className="text-right">
                                    <span className="block text-[8px] font-black uppercase text-white/40">Mínimo</span>
                                    <span className="text-base font-black text-green-400">{cronosStats.b.min.toFixed(2)} €</span>
                                </div>
                                <div className="text-right">
                                    <span className="block text-[8px] font-black uppercase text-white/40">Máximo</span>
                                    <span className="text-base font-black text-red-400">{cronosStats.b.max.toFixed(2)} €</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Chart Container */}
            <div className="min-h-[400px] w-full bg-black/40 rounded-3xl p-6 border border-white/10 relative flex flex-col justify-center items-center">
                {(loadingCronosA || loadingCronosB) ? (
                    <div className="flex flex-col items-center justify-center gap-4">
                        <RefreshCw className="h-10 w-10 text-brand-primary animate-spin" />
                        <span className="text-xs font-black uppercase tracking-widest text-white/65">Invocando datos del pasado...</span>
                    </div>
                ) : chartData.length > 0 ? (
                    <div className="h-[380px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                                    dy={5}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                                    unit="€"
                                />
                                <Tooltip
                                    cursor={{ stroke: 'rgba(255, 255, 255, 0.15)', strokeWidth: 1.5, strokeDasharray: '4 4' }}
                                    content={<CustomTooltip />}
                                />
                                <Legend
                                    iconType="circle"
                                    wrapperStyle={{ paddingTop: '10px', fontSize: '10px', fontWeight: 900, textTransform: 'uppercase' }}
                                />
                                {chartLines.map((line) => (
                                    <Line
                                        key={line.key}
                                        type="monotone"
                                        dataKey={line.key}
                                        stroke={line.color}
                                        strokeWidth={3}
                                        dot={{ fill: line.color, stroke: line.color, strokeWidth: 1, r: 4 }}
                                        activeDot={{ r: 8, stroke: '#fff', strokeWidth: 2 }}
                                        animationDuration={1000}
                                        connectNulls
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <div className="text-center text-white/60 space-y-2 uppercase">
                        <History className="h-12 w-12 mx-auto text-white/10 animate-pulse" />
                        <h4 className="text-xs font-black tracking-widest text-white/70">Cronos está inactivo</h4>
                        <p className="text-[9px] font-bold text-white/65 tracking-wider">Selecciona Reliquias para visualizar su evolución de precios</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CronosView;
