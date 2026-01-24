
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
    CheckCircle2
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

    if (error || !marketData) {
        return (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md">
                <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-3xl text-center space-y-4 max-w-sm">
                    <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
                    <h3 className="text-white font-black text-xl uppercase italic">Error Arcano</h3>
                    <p className="text-white/60 text-xs">No se han podido invocar los datos de mercado para este producto. Asegúrate de que tenga ofertas registradas.</p>
                    <button onClick={onClose} className="w-full bg-white text-black py-3 rounded-xl font-bold uppercase transition-transform hover:scale-95 text-xs">Cerrar Visión</button>
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
                                <span>Mercio Actual</span>
                            </div>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] font-bold text-white/20 uppercase">Retail (Official)</p>
                                    <h4 className="text-2xl font-black text-brand-primary">{marketData.retail_price_official || '---'} €</h4>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-bold text-white/20 uppercase">Mínimo Activo</p>
                                    <h4 className="text-2xl font-black text-green-500">{marketData.current_market_low || '---'} €</h4>
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
                                    {bid.reason || `Basado en el percentil 25 de ${bid.total_samples} ventas registradas.`}
                                </p>
                            </div>
                            <div className="text-right space-y-4">
                                <div className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] font-black border ${bid.confidence === 'high' ? 'bg-green-500/20 text-green-500 border-green-500/10' : 'bg-yellow-500/20 text-yellow-500 border-yellow-500/10'}`}>
                                    <CheckCircle className="h-3 w-3" />
                                    CONFIDENCIA {bid.confidence.toUpperCase()}
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] font-black text-white/20 uppercase">Media de Venta</p>
                                    <p className="text-lg font-black text-white/60">{bid.avg_sold || '---'} €</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Chart Area */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-[2rem] p-6 md:p-10 space-y-6">
                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <h3 className="text-white font-black text-lg">Evolución del Justiprecio</h3>
                                <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest">Estativa histórica de los últimos 6 meses</p>
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
