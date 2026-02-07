import React from 'react';
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
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import type { ProductPriceHistory } from '../../api/products';

interface Props {
    data: ProductPriceHistory[];
}

const PriceHistoryChart: React.FC<Props> = ({ data }) => {
    // Transform data for Recharts (Combine all shops into unified points by date)
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

    // Mapeo fijo de colores para tiendas comunes para asegurar consistencia
    const getShopColor = (name: string, idx: number) => {
        const lowerName = name.toLowerCase();
        if (lowerName.includes('ebay')) return '#0064D2'; // eBay Blue
        if (lowerName.includes('vinted')) return '#00C0CE'; // Vinted Teal
        if (lowerName.includes('wallapop')) return '#13C1AC'; // Wallapop Green
        if (lowerName.includes('amazon')) return '#FF9900'; // Amazon Orange

        const colors = ['#0ea5e9', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b'];
        return colors[idx % colors.length];
    };

    return (
        <div className="h-[280px] w-full mt-4 bg-white/5 rounded-[2rem] p-4 border border-white/10 backdrop-blur-xl">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
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
                        contentStyle={{
                            backgroundColor: '#000',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '1.5rem',
                            backdropFilter: 'blur(20px)',
                            padding: '12px'
                        }}
                        itemStyle={{ fontSize: '12px', fontWeight: 900 }}
                        labelStyle={{ color: 'rgba(255,255,255,0.4)', marginBottom: '6px', fontSize: '10px', fontWeight: 900, textTransform: 'uppercase' }}
                    />
                    <Legend
                        iconType="circle"
                        wrapperStyle={{ paddingTop: '10px', fontSize: '10px', fontWeight: 900, textTransform: 'uppercase' }}
                    />
                    {data.map((shop, idx) => {
                        const color = getShopColor(shop.shop_name, idx);
                        return (
                            <Line
                                key={shop.shop_name}
                                type="monotone"
                                dataKey={shop.shop_name}
                                stroke={color}
                                strokeWidth={4}
                                dot={{ fill: color, stroke: '#fff', strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 7, strokeWidth: 0 }}
                                animationDuration={1000}
                                connectNulls
                            />
                        );
                    })}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PriceHistoryChart;
