import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Radar, ExternalLink, Package, ArrowDownRight, Info, AlertTriangle, Box } from 'lucide-react';
import type { P2POpportunity } from '../api/dashboard';
import { getPeerToPeerOpportunities } from '../api/dashboard';

const RadarP2P: React.FC = () => {
    const { data: opportunities, isLoading } = useQuery<P2POpportunity[]>({
        queryKey: ['p2p-opportunities'],
        queryFn: getPeerToPeerOpportunities,
        refetchInterval: 60000, // Cada minuto
    });

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] animate-pulse">
                <div className="relative w-32 h-32 mb-8">
                    <div className="absolute inset-0 border-2 border-brand-primary/30 rounded-full animate-ping" />
                    <div className="absolute inset-4 border-2 border-brand-primary/50 rounded-full animate-pulse" />
                    <Radar className="absolute inset-0 m-auto h-12 w-12 text-brand-primary animate-spin-slow" />
                </div>
                <h2 className="text-xl font-black text-white tracking-widest uppercase">Escaneando el Reino...</h2>
                <p className="text-white/40 text-xs mt-2 font-medium tracking-[0.3em]">BUSCANDO GANGAS ENTRE PARTICULARES</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 pb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header / Hero Section */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-primary/20 via-black/40 to-transparent border border-glass-border p-8 md:p-12">
                <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-brand-primary/10 rounded-full blur-[100px]" />

                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-primary/10 border border-brand-primary/30 text-brand-primary text-[10px] font-black uppercase tracking-widest mb-4">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary"></span>
                            </span>
                            Radar de Inteligencia Activo
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-4">
                            Radar de <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-primary to-cyan-400">Oportunidades</span>
                        </h1>
                        <p className="text-white/60 text-lg leading-relaxed">
                            Buscando entre particulares (Wallapop/eBay) ítems que cotizan por debajo del <span className="text-white font-bold">Percentil 25</span> del mercado real.
                            Precios analizados bajo la <span className="text-brand-primary font-bold">Teoría de Cuarentena</span>.
                        </p>
                    </div>

                    <div className="flex gap-4">
                        <div className="glass p-6 rounded-2xl border-white/5 flex flex-col items-center justify-center min-w-[140px]">
                            <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-1">Detectados</span>
                            <span className="text-3xl font-black text-white">{opportunities?.length || 0}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Teoría Warning */}
            <div className="flex items-start gap-4 p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                <div className="mt-1 p-2 rounded-lg bg-amber-500/10">
                    <Info className="h-5 w-5 text-amber-500" />
                </div>
                <div>
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1">Precios en Cuarentena</h3>
                    <p className="text-xs text-white/50 leading-relaxed">
                        Los precios de esta sección son volátiles y provienen de fuentes secundarias. No se promedian con el valor de tu colección para evitar deflactar tu patrimonio. Úsalos solo como benchmark de oportunidad de compra.
                    </p>
                </div>
            </div>

            {/* Grid de Oportunidades */}
            {opportunities && opportunities.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {opportunities.map((opp) => (
                        <div key={opp.id} className="group relative overflow-hidden rounded-2xl border border-glass-border glass hover:shadow-[0_0_30px_rgba(14,165,233,0.15)] transition-all duration-300">
                            {/* Badge de Porcentaje */}
                            <div className="absolute top-4 right-4 z-20 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-black backdrop-blur-md">
                                -{opp.saving_pct}%
                            </div>

                            {/* Imagen */}
                            <div className="aspect-[16/9] w-full overflow-hidden relative">
                                {opp.image_url ? (
                                    <img src={opp.image_url} alt={opp.product_name} className="h-full w-full object-cover group-hover:scale-110 transition-transform duration-500" />
                                ) : (
                                    <div className="h-full w-full flex items-center justify-center bg-white/5">
                                        <Box className="h-12 w-12 text-white/10" />
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent opacity-60" />
                            </div>

                            {/* Contenido */}
                            <div className="p-5 space-y-4">
                                <div>
                                    <h3 className="text-white font-bold truncate group-hover:text-brand-primary transition-colors">{opp.product_name}</h3>
                                    <p className="text-white/30 text-[10px] font-bold uppercase tracking-widest mt-1">{opp.shop_name}</p>
                                </div>

                                {/* Comparativa de Precios */}
                                <div className="grid grid-cols-2 gap-4 pb-4 border-b border-white/5">
                                    <div>
                                        <p className="text-[10px] text-white/40 font-bold uppercase tracking-wider mb-1">Precio Particular</p>
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-2xl font-black text-white">{opp.price}€</span>
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-white/40 font-bold uppercase tracking-wider mb-1">Market Floor (P25)</p>
                                        <div className="flex items-center gap-1 text-brand-primary">
                                            <span className="text-lg font-bold">{opp.p25_price}€</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Ahorro Ganancia */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2 text-emerald-400">
                                        <ArrowDownRight className="h-4 w-4" />
                                        <span className="text-xs font-bold uppercase tracking-widest">Ahorras {opp.saving}€</span>
                                    </div>
                                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
                                        <Package className="h-3.5 w-3.5" />
                                        <span className="text-[10px] font-black uppercase tracking-tighter">Landed: {opp.landing_price}€</span>
                                    </div>
                                </div>

                                {/* Accion */}
                                <a
                                    href={opp.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-bold text-white hover:bg-brand-primary hover:border-brand-primary transition-all group/btn"
                                >
                                    Ver Oferta Original
                                    <ExternalLink className="h-4 w-4 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-20 glass rounded-3xl border-dashed border-white/10">
                    <AlertTriangle className="h-12 w-12 text-white/20 mb-4" />
                    <h3 className="text-xl font-bold text-white/40 uppercase tracking-widest">Sin Anomalías Detectadas</h3>
                    <p className="text-white/20 text-sm mt-2">No hay ofertas de particulares por debajo del suelo de mercado actual.</p>
                </div>
            )}
        </div>
    );
};

export default RadarP2P;
