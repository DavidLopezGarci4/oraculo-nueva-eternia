
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    X,
    Target,
    Info,
    Calendar,
    Loader2,
    AlertCircle,
    Zap,
    CheckCircle2,
    Users,
    TrendingUp,
    Hash,
    ShoppingBag
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import axios from 'axios';

interface MarketIntelligenceModalProps {
    productId: number;
    onClose: () => void;
}

const MarketIntelligenceModal: React.FC<MarketIntelligenceModalProps> = ({ productId, onClose }) => {
    const { data: marketData, isLoading, error } = useQuery({
        queryKey: ['market-intelligence', productId],
        queryFn: async () => {
            const response = await axios.get(`/api/intelligence/market/${productId}`);
            return response.data;
        }
    });

    if (isLoading) {
        return (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md">
                <div className="text-center space-y-4">
                    <Loader2 className="h-10 w-10 animate-spin text-brand-primary mx-auto" />
                    <p className="text-xs font-black uppercase tracking-widest text-white/40">Infiltrando base de datos del mercado...</p>
                </div>
            </div>
        );
    }

    // Distinguir entre error real y datos vacíos
    const isError = error || (!marketData && !isLoading);
    const hasData = marketData && (marketData.current_retail_low || marketData.current_p2p_low || marketData.bid_strategy?.ideal_bid > 0);

    if (isError || !hasData) {
        return (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md">
                <div className="bg-white/[0.03] border border-white/10 p-10 rounded-[2.5rem] text-center space-y-6 max-w-sm backdrop-blur-2xl shadow-2xl">
                    <div className="relative mx-auto h-16 w-16">
                        <AlertCircle className="h-16 w-16 text-brand-primary/40" />
                        <div className="absolute inset-0 animate-ping rounded-full bg-brand-primary/20"></div>
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-white font-black text-2xl uppercase italic tracking-tighter">Sabiduría en Acumulación</h3>
                        <p className="text-white/40 text-[10px] font-bold uppercase leading-relaxed tracking-widest">
                            El Oráculo aún no ha recolectado suficientes reliquias de este tipo para generar un informe industrial fidedigno.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-full bg-brand-primary text-white py-4 rounded-2xl font-black uppercase transition-all hover:brightness-125 text-[10px] tracking-[0.2em] shadow-lg shadow-brand-primary/20"
                    >
                        Cerrar Visión
                    </button>
                </div>
            </div>
        );
    }

    // Prepare chart data
    const chartData: any[] = [];
    const evolution = marketData.evolution || {};
    const months = Array.from(new Set([
        ...(evolution.Retail || []).map((d: any) => d.date),
        ...(evolution['Peer-to-Peer'] || []).map((d: any) => d.date)
    ])).sort();

    months.forEach(date => {
        const retail = evolution.Retail?.find((d: any) => d.date === date)?.avg_price;
        const p2p = evolution['Peer-to-Peer']?.find((d: any) => d.date === date)?.avg_price;
        chartData.push({ date, Retail: retail, P2P: p2p });
    });

    const bid = marketData.bid_strategy;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-xl p-4 md:p-10 animate-in fade-in zoom-in duration-300">
            <div className="relative w-full max-w-5xl rounded-[2.5rem] border border-white/10 bg-gradient-to-br from-white/[0.05] to-transparent overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="flex items-center justify-between p-6 md:p-8 border-b border-white/5 bg-white/[0.02]">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Target className="h-4 w-4" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em]">Estudio de Mercado Industrial</span>
                        </div>
                        <h2 className="text-xl md:text-3xl font-black text-white">{marketData.product_name}</h2>
                    </div>
                    <button onClick={onClose} className="h-12 w-12 flex items-center justify-center rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                        <X className="h-6 w-6 text-white" />
                    </button>
                </div>

                {/* Content Scroll Area */}
                <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 custom-scrollbar">

                    {/* Insights Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                        {/* Summary Card 1: Retail vs P2P */}
                        <div className="bg-white/[0.03] border border-white/5 p-6 rounded-3xl space-y-4">
                            <div className="flex items-center gap-2 text-white/40 uppercase text-[10px] font-black tracking-widest">
                                <Calendar className="h-3 w-3" />
                                <span>Mercado Actual</span>
                            </div>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] font-bold text-white/20 uppercase">Mínimo Retail</p>
                                    <h4 className="text-2xl font-black text-brand-primary">{marketData.current_retail_low || '---'} €</h4>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-bold text-white/20 uppercase">Mínimo P2P</p>
                                    <h4 className="text-2xl font-black text-purple-500">{marketData.current_p2p_low || '---'} €</h4>
                                </div>
                            </div>
                        </div>

                        {/* Summary Card 2: Ideal Bid Prediction */}
                        <div className="md:col-span-2 bg-gradient-to-r from-orange-500/10 to-transparent border border-orange-500/20 p-6 rounded-3xl flex items-center justify-between gap-6">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-orange-500 uppercase text-[10px] font-black tracking-widest">
                                    <Zap className="h-3 w-3 fill-orange-500" />
                                    <span>Estrategia de Puja (Ideal Bid)</span>
                                </div>
                                <h4 className="text-4xl font-black text-white">{bid.ideal_bid} €</h4>
                                <p className="text-[10px] font-medium text-white/40 leading-tight max-w-[240px]">
                                    {bid.reason}
                                </p>
                            </div>
                            <div className="text-right space-y-4">
                                <div className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] font-black border ${bid.confidence === 'high' ? 'bg-green-500/20 text-green-500 border-green-500/10' :
                                    bid.confidence === 'medium' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/10' :
                                        'bg-red-500/20 text-red-500 border-red-500/10'
                                    }`}>
                                    <CheckCircle className="h-3 w-3" />
                                    CONFIDENCIA {bid.confidence.toUpperCase()}
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] font-black text-white/20 uppercase">Muestra Industrial</p>
                                    <p className="text-lg font-black text-white/60">{bid.total_samples || 0} items</p>
                                </div>
                            </div>
                        </div>

                        {/* NEW: Sentiment & Identifiers Card */}
                        <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white/[0.03] border border-white/5 p-5 rounded-3xl space-y-2">
                                <div className="flex items-center gap-2 text-white/40 uppercase text-[8px] font-black tracking-[0.2em]">
                                    <Users className="h-3 w-3" />
                                    <span>Popularidad</span>
                                </div>
                                <p className="text-xl font-black text-white">{marketData.popularity_score || 0}</p>
                                <p className="text-[8px] font-bold text-white/20 uppercase">Coleccionistas</p>
                            </div>

                            <div className="bg-white/[0.03] border border-white/5 p-5 rounded-3xl space-y-2">
                                <div className="flex items-center gap-2 text-white/40 uppercase text-[8px] font-black tracking-[0.2em]">
                                    <TrendingUp className="h-3 w-3" />
                                    <span>Momento</span>
                                </div>
                                <div className="flex items-baseline gap-2">
                                    <p className={`text-xl font-black ${(marketData.market_momentum || 1.0) > 1.2 ? 'text-green-400' : (marketData.market_momentum || 1.0) < 0.9 ? 'text-brand-primary' : 'text-white'}`}>
                                        {(marketData.market_momentum || 1.0).toFixed(2)}x
                                    </p>
                                    <span className="text-[8px] font-bold text-white/20 uppercase">Trend</span>
                                </div>
                            </div>

                            <div className="bg-white/[0.03] border border-white/5 p-5 rounded-3xl space-y-2">
                                <div className="flex items-center gap-2 text-white/40 uppercase text-[8px] font-black tracking-[0.2em]">
                                    <Hash className="h-3 w-3" />
                                    <span>UPC</span>
                                </div>
                                <p className="text-[10px] font-black text-white/60 truncate">{marketData.upc || 'N/A'}</p>
                                <p className="text-[8px] font-bold text-white/20 uppercase">Universal ID</p>
                            </div>

                            <div className="bg-white/[0.03] border border-white/5 p-5 rounded-3xl space-y-2">
                                <div className="flex items-center gap-2 text-white/40 uppercase text-[8px] font-black tracking-[0.2em]">
                                    <ShoppingBag className="h-3 w-3" />
                                    <span>ASIN</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <p className="text-[10px] font-black text-white/60">{marketData.asin || 'N/A'}</p>
                                    {marketData.asin && (
                                        <a href={`https://www.amazon.es/dp/${marketData.asin}`} target="_blank" rel="noopener noreferrer" className="text-brand-primary hover:text-white transition-colors">
                                            <Zap className="h-3 w-3 fill-current" />
                                        </a>
                                    )}
                                </div>
                                <p className="text-[8px] font-bold text-white/20 uppercase">Amazon Reference</p>
                            </div>
                        </div>
                    </div>

                    {/* Chart Area */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-[2rem] p-6 md:p-10 space-y-6">
                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <h3 className="text-white font-black text-lg">Evolución del Justiprecio</h3>
                                <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest">
                                    {chartData.length > 1 ? 'Estativa histórica de los últimos 6 meses' : 'Dato puntual actual (Sin historial registrado)'}
                                </p>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-2 rounded-full bg-brand-primary"></div>
                                    <span className="text-[10px] font-black text-white/40 uppercase">Retail</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-2 rounded-full bg-purple-500"></div>
                                    <span className="text-[10px] font-black text-white/40 uppercase">P2P (Wallapop/eBay)</span>
                                </div>
                            </div>
                        </div>

                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        stroke="rgba(255,255,255,0.2)"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                        dy={10}
                                    />
                                    <YAxis
                                        stroke="rgba(255,255,255,0.2)"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                        unit="€"
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem', fontSize: '10px' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="Retail"
                                        stroke="#00A3FF"
                                        strokeWidth={4}
                                        dot={{ fill: '#00A3FF', strokeWidth: 2, r: 4 }}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                        connectNulls
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="P2P"
                                        stroke="#A855F7"
                                        strokeWidth={4}
                                        dot={{ fill: '#A855F7', strokeWidth: 2, r: 4 }}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                        connectNulls
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="flex items-start gap-4 p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                        <Info className="h-5 w-5 text-brand-primary shrink-0 mt-1" />
                        <div className="space-y-1">
                            <h5 className="text-[10px] font-black text-white uppercase tracking-widest">Protocolo de Inteligencia 3OX</h5>
                            <p className="text-[10px] text-white/40 leading-relaxed font-medium">
                                Estos datos son generados por el Oráculo asimilando miles de puntos de datos de tiendas retail y mercados entre particulares. La estrategia de "Ideal Bid" es una sugerencia algorítmica y no garantiza la compra. Invierte con sabiduría.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketIntelligenceModal;

// Mock icons if missing in lucide-react version (CheckCircle2 used instead)
const CheckCircle = ({ className }: { className?: string }) => <CheckCircle2 className={className} />;
