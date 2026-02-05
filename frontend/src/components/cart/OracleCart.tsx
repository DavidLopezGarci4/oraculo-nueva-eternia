import React from 'react';
import { useCart } from '../../context/CartContext';
import { useQuery } from '@tanstack/react-query';
import { calculateCart } from '../../api/cart';
import { ShoppingBasket, Trash2, Plus, Minus, ReceiptText, Package, Truck, Info, Zap } from 'lucide-react';

const OracleCart: React.FC = () => {
    const { items, removeFromCart, updateQuantity, clearCart, totalItems } = useCart();

    const { data: invoice, isLoading } = useQuery({
        queryKey: ['cart-calculation', items],
        queryFn: () => calculateCart(items),
        enabled: items.length > 0,
        placeholderData: (prev) => prev
    });

    if (items.length === 0) {
        return (
            <div className="rounded-[2.5rem] border border-white/5 bg-white/[0.01] p-10 flex flex-col items-center justify-center text-center gap-4">
                <div className="h-16 w-16 rounded-full bg-white/5 flex items-center justify-center text-white/10">
                    <ShoppingBasket className="h-8 w-8" />
                </div>
                <div className="space-y-1">
                    <h3 className="text-white font-black uppercase tracking-widest text-sm">Carrito Ficticio Vacío</h3>
                    <p className="text-[10px] text-white/20 font-bold max-w-xs uppercase">Añade reliquias desde Oportunidades, El Pabellón o Nueva Eternia para simular tu pedido logístico.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Oracle Cart (Simulador)</h4>
                    <div className="flex items-center gap-1.5 rounded-full bg-orange-500/10 px-2 py-0.5 border border-orange-500/20">
                        <span className="text-[8px] font-black text-orange-500 uppercase tracking-tighter">{totalItems} Ítems</span>
                    </div>
                </div>
                <button onClick={clearCart} className="text-[10px] font-black text-red-400/50 hover:text-red-400 uppercase tracking-widest transition-colors">Vaciar Carrito</button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Items List */}
                <div className="lg:col-span-2 space-y-3">
                    {items.map((item) => (
                        <div key={item.id} className="group flex items-center justify-between gap-4 p-4 rounded-[1.5rem] border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all">
                            <div className="flex items-center gap-4 min-w-0">
                                <div className="h-12 w-12 shrink-0 rounded-xl bg-black/40 overflow-hidden border border-white/5">
                                    <img src={item.image_url || undefined} alt="" className="h-full w-full object-cover" />
                                </div>
                                <div className="min-w-0">
                                    <p className="truncate text-sm font-bold text-white">{item.product_name}</p>
                                    <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">{item.shop_name} - {item.price} €</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-3 bg-black/40 rounded-xl p-1 border border-white/5">
                                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="p-1 rounded-lg hover:bg-white/10 text-white/40 hover:text-white transition-all"><Minus className="h-3 w-3" /></button>
                                    <span className="text-xs font-black text-white w-4 text-center">{item.quantity}</span>
                                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="p-1 rounded-lg hover:bg-white/10 text-white/40 hover:text-white transition-all"><Plus className="h-3 w-3" /></button>
                                </div>
                                <button onClick={() => removeFromCart(item.id)} className="p-2 rounded-xl text-red-500/30 hover:text-red-500 hover:bg-red-500/10 transition-all"><Trash2 className="h-4 w-4" /></button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Summary / Invoice */}
                <div className="space-y-4">
                    <div className="rounded-[2rem] border border-brand-primary/20 bg-brand-primary/[0.02] p-6 lg:p-8 space-y-6 relative overflow-hidden backdrop-blur-xl">
                        <div className="absolute top-0 right-0 p-8 opacity-[0.02] select-none pointer-events-none">
                            <ReceiptText className="h-32 w-32" />
                        </div>

                        <div className="space-y-1">
                            <h5 className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Resumen del Oráculo</h5>
                            <p className="text-2xl font-black text-white">{invoice?.grand_total_eur || '---'} €</p>
                            <p className="text-[8px] text-white/20 font-bold uppercase tracking-widest italic">Simulación Total Landed (Puerta a Puerta)</p>
                        </div>

                        {isLoading ? (
                            <div className="py-10 flex flex-col items-center justify-center gap-3 text-brand-primary/40">
                                <Zap className="h-6 w-6 animate-pulse" />
                                <span className="text-[8px] font-black uppercase tracking-widest">Calculando Rutas Logísticas...</span>
                            </div>
                        ) : (
                            <div className="space-y-6">
                                {invoice?.breakdown.map((shop, idx) => (
                                    <div key={idx} className="space-y-3 pt-4 border-t border-white/5 first:border-0 first:pt-0">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[10px] font-black text-white uppercase tracking-widest">{shop.shop}</span>
                                            {shop.status === 'PENDING_RULES' && (
                                                <span className="px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500 text-[6px] font-black border border-yellow-500/20">REGLAS PENDIENTES</span>
                                            )}
                                        </div>

                                        <div className="space-y-1.5">
                                            <div className="flex justify-between text-[10px] items-center">
                                                <div className="flex items-center gap-2 text-white/40 font-bold"><Package className="h-3 w-3 opacity-50" /> Base Artículos</div>
                                                <span className="text-white/80 font-black">{shop.items.reduce((acc, i) => acc + i.subtotal_eur, 0).toFixed(2)} €</span>
                                            </div>
                                            <div className="flex justify-between text-[10px] items-center">
                                                <div className="flex items-center gap-2 text-white/40 font-bold"><Truck className="h-3 w-3 opacity-50" /> Envío Logístico</div>
                                                <span className="text-white/80 font-black">{shop.shipping_eur.toFixed(2)} €</span>
                                            </div>
                                            <div className="flex justify-between text-[10px] items-center">
                                                <div className="flex items-center gap-2 text-white/40 font-bold"><Info className="h-3 w-3 opacity-50" /> IVA / Tasas</div>
                                                <span className="text-white/80 font-black">{(shop.tax_eur + (shop.fees_eur || 0)).toFixed(2)} €</span>
                                            </div>
                                        </div>

                                        <div className="flex justify-between items-center pt-1">
                                            <span className="text-[8px] font-black text-white/20 uppercase">Subtotal Landed</span>
                                            <span className="text-xs font-black text-brand-primary">{shop.total_eur.toFixed(2)} €</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="pt-4 border-t border-white/10">
                            <div className="flex items-start gap-3">
                                <Info className="h-3 w-3 text-white/20 mt-0.5" />
                                <p className="text-[7px] text-white/20 font-bold leading-relaxed uppercase tracking-widest">
                                    Los cálculos se basan en las reglas de {invoice?.user_location === 'ES' ? 'España' : invoice?.user_location}. Si una tienda está "Pending", solo se suma el precio base.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OracleCart;
