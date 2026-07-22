const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const valA = payload[0]?.value;
        const valB = payload[1]?.value;

        let deltaStr = '';
        if (typeof valA === 'number' && typeof valB === 'number') {
            const diff = valA - valB;
            const pct = ((valA - valB) / valB) * 100;
            const sign = diff > 0 ? '+' : '';
            deltaStr = `Dif: ${sign}${diff.toFixed(2)}€ (${sign}${pct.toFixed(1)}%)`;
        }

        return (
            <div className="bg-black/90 border border-white/10 rounded-2xl p-4 shadow-2xl backdrop-blur-xl space-y-2">
                <p className="text-[10px] font-black text-white/40 uppercase tracking-widest">{label}</p>
                <div className="space-y-1">
                    {payload.map((item: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-3 text-xs font-bold justify-between">
                            <div className="flex items-center gap-1.5 min-w-0 pr-4">
                                <span className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: item.color }}></span>
                                <span className="text-white/80 truncate max-w-[150px]">{item.name}</span>
                            </div>
                            <span className="text-white font-black whitespace-nowrap">{item.value.toFixed(2)} €</span>
                        </div>
                    ))}
                </div>
                {deltaStr && (
                    <div className="h-px bg-white/5 my-1.5"></div>
                )}
                {deltaStr && (
                    <p className="text-[10px] font-black text-brand-primary uppercase tracking-widest text-center">
                        {deltaStr}
                    </p>
                )}
            </div>
        );
    }
    return null;
};

export default CustomTooltip;
