import React from 'react';
import { motion } from 'framer-motion';
import { Flame, Zap, Shield, Sparkles } from 'lucide-react';

export type HeatFilterType = 'ALL' | 'HOT' | 'WARM' | 'COOL';

interface OpportunityHeatMatrixProps {
    deals: any[];
    activeFilter: HeatFilterType;
    onSelectFilter: (filter: HeatFilterType) => void;
}

export const getDealDiscount = (d: any): number => {
    if (d.discount_pct !== undefined && d.discount_pct !== null && d.discount_pct > 0) {
        return d.discount_pct;
    }
    if (d.savings_pct !== undefined && d.savings_pct !== null && d.savings_pct > 0) {
        return d.savings_pct;
    }
    const retail = d.retail_price || 19.99;
    const price = Math.min(d.landing_price || d.price, d.price || d.landing_price);
    if (retail > 0 && price < retail) {
        return Math.round(((retail - price) / retail) * 100);
    }
    return 0;
};

export const OpportunityHeatMatrix: React.FC<OpportunityHeatMatrixProps> = ({
    deals,
    activeFilter,
    onSelectFilter
}) => {
    // Clasificar ofertas por nivel de temperatura de ahorro
    const hotDeals = deals.filter((d) => getDealDiscount(d) >= 40);
    const warmDeals = deals.filter(
        (d) => getDealDiscount(d) >= 20 && getDealDiscount(d) < 40
    );
    const coolDeals = deals.filter((d) => getDealDiscount(d) < 20);

    const tiers = [
        {
            id: 'HOT' as HeatFilterType,
            label: 'Nivel Fuego',
            subtitle: '>40% de Ahorro',
            count: hotDeals.length,
            icon: Flame,
            color: 'from-rose-600/30 to-red-600/10 border-red-500/40 text-red-400',
            activeColor: 'border-red-400 shadow-red-500/20 bg-red-500/20',
            badgeBg: 'bg-red-500/20 text-red-300'
        },
        {
            id: 'WARM' as HeatFilterType,
            label: 'Nivel Rayo',
            subtitle: '20% - 40% Ahorro',
            count: warmDeals.length,
            icon: Zap,
            color: 'from-amber-500/30 to-yellow-500/10 border-amber-500/40 text-amber-400',
            activeColor: 'border-amber-400 shadow-amber-500/20 bg-amber-500/20',
            badgeBg: 'bg-amber-500/20 text-amber-300'
        },
        {
            id: 'COOL' as HeatFilterType,
            label: 'Nivel Escudo',
            subtitle: '<20% Precios Suelo',
            count: coolDeals.length,
            icon: Shield,
            color: 'from-cyan-500/30 to-blue-500/10 border-cyan-500/40 text-cyan-400',
            activeColor: 'border-cyan-400 shadow-cyan-500/20 bg-cyan-500/20',
            badgeBg: 'bg-cyan-500/20 text-cyan-300'
        }
    ];

    return (
        <div className="mb-6">
            {/* Cabecera del Termómetro */}
            <div className="flex items-center justify-between mb-3 px-1">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-400" />
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Termómetro de Oportunidades
                    </span>
                </div>
                {activeFilter !== 'ALL' && (
                    <button
                        onClick={() => onSelectFilter('ALL')}
                        className="text-[11px] text-cyan-400 hover:text-cyan-300 transition underline underline-offset-2"
                    >
                        Ver todas ({deals.length})
                    </button>
                )}
            </div>

            {/* Selector de Niveles Térmicos (Swipeable en Móvil / 3 Columnas en PC) */}
            <div className="grid grid-cols-3 gap-2 sm:gap-3">
                {tiers.map((t) => {
                    const Icon = t.icon;
                    const isSelected = activeFilter === t.id;

                    return (
                        <motion.button
                            key={t.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => onSelectFilter(isSelected ? 'ALL' : t.id)}
                            className={`flex flex-col items-center sm:items-start justify-between p-3 rounded-xl border bg-gradient-to-br transition-all duration-200 text-left relative overflow-hidden ${
                                t.color
                            } ${isSelected ? `${t.activeColor} shadow-lg ring-1 ring-white/20` : 'hover:border-slate-600'}`}
                        >
                            <div className="flex items-center justify-between w-full mb-1">
                                <Icon className="h-4 w-4 shrink-0" />
                                <span className={`text-xs font-bold px-1.5 py-0.5 rounded-full ${t.badgeBg}`}>
                                    {t.count}
                                </span>
                            </div>
                            <div>
                                <div className="text-xs font-bold text-white tracking-wide truncate w-full">
                                    {t.label}
                                </div>
                                <div className="text-[10px] text-slate-400 hidden sm:block">
                                    {t.subtitle}
                                </div>
                            </div>
                        </motion.button>
                    );
                })}
            </div>
        </div>
    );
};

export default OpportunityHeatMatrix;
