import React from 'react';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import type { ProductPriceHistory } from '../../api/products';

interface Props {
    data: ProductPriceHistory[];
}

const PriceHistoryChart: React.FC<Props> = ({ data }) => {
    // Transform data for Recharts (Combine all shops into unified points by date)
    // For simplicity in this version, we will map each shop's history

    // We need a unified set of dates or just show them by shop if overlapping is hard.
    // Better: Combine into a single array of { date, Shop1: price, Shop2: price, ... }
    const allDates = Array.from(new Set(data.flatMap(s => s.history.map(h => h.date)))).sort();

    const chartData = allDates.map(date => {
        const point: any = {
            name: format(new Date(date), 'dd MMM', { locale: es }),
            fullDate: date
        };
        data.forEach(shop => {
            const historyPoint = shop.history.find(h => h.date === date);
            if (historyPoint) {
                point[shop.shop_name] = historyPoint.price;
            }
        });
        return point;
    });

    const colors = ['#0ea5e9', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b'];

    return (
        <div className="h-[300px] w-full mt-4 bg-white/5 rounded-[2rem] p-4 border border-white/10 backdrop-blur-xl">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                        {data.map((_, idx) => (
                            <linearGradient key={`grad-${idx}`} id={`color-${idx}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={colors[idx % colors.length]} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={colors[idx % colors.length]} stopOpacity={0} />
                            </linearGradient>
                        ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                        unit="€"
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '1rem',
                            backdropFilter: 'blur(10px)'
                        }}
                        itemStyle={{ fontSize: '12px', fontWeight: 900 }}
                        labelStyle={{ color: 'rgba(255,255,255,0.4)', marginBottom: '4px', fontSize: '10px' }}
                    />
                    <Legend iconType="circle" />
                    {data.map((_, idx) => (
                        <Area
                            key={data[idx].shop_name}
                            type="monotone"
                            dataKey={data[idx].shop_name}
                            stroke={colors[idx % colors.length]}
                            strokeWidth={3}
                            fillOpacity={1}
                            fill={`url(#color-${idx})`}
                            animationDuration={1500}
                        />
                    ))}
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PriceHistoryChart;
