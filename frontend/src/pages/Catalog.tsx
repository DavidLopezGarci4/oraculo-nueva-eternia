import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Package, AlertCircle, Loader2, Info } from 'lucide-react';

interface Product {
    id: number;
    name: string;
    category: string;
    sub_category: string;
    figure_id: string;
    image_url: string | null;
}

const Catalog: React.FC = () => {
    const { data: products, isLoading, isError } = useQuery<Product[]>({
        queryKey: ['products'],
        queryFn: async () => {
            const response = await axios.get('http://localhost:8000/api/products');
            return response.data;
        }
    });

    if (isLoading) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/50">
                <Loader2 className="h-10 w-10 animate-spin text-brand-primary" />
                <p className="text-sm font-medium animate-pulse">Sincronizando con Eternia...</p>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-red-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al conectar con la API Broker</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="space-y-1">
                    <h2 className="text-3xl font-bold tracking-tight text-white">Catálogo Maestro</h2>
                    <p className="text-sm text-white/50">Visualización de los 297 productos purificados en Supabase.</p>
                </div>
                <div className="flex items-center gap-2 rounded-full bg-brand-primary/10 px-4 py-2 border border-brand-primary/20">
                    <Package className="h-4 w-4 text-brand-primary" />
                    <span className="text-xs font-bold text-brand-primary">{products?.length} Items</span>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {products?.map((product) => (
                    <div key={product.id} className="glass-card group flex flex-col gap-4">
                        {/* Image Placeholder / Actual Image */}
                        <div className="aspect-square w-full overflow-hidden rounded-xl bg-white/5 border border-white/10 relative">
                            {product.image_url ? (
                                <img
                                    src={product.image_url}
                                    alt={product.name}
                                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                                />
                            ) : (
                                <div className="flex h-full w-full items-center justify-center italic text-white/20 text-xs">
                                    Sin imagen
                                </div>
                            )}
                            <div className="absolute top-3 right-3 rounded-md bg-black/60 px-2 py-1 text-[10px] font-bold text-white/80 backdrop-blur-md border border-white/10">
                                #{product.figure_id}
                            </div>
                        </div>

                        {/* Info */}
                        <div className="space-y-2">
                            <div className="flex items-start justify-between gap-2">
                                <h3 className="line-clamp-2 text-sm font-bold text-white/90 group-hover:text-brand-primary transition-colors">
                                    {product.name}
                                </h3>
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                                <span className="rounded-md bg-white/5 px-2 py-0.5 text-[10px] text-white/40 border border-white/5">
                                    {product.sub_category}
                                </span>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="mt-auto flex items-center justify-between pt-2">
                            <button className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium text-white/60 hover:bg-white/10 hover:text-white transition-all border border-white/5">
                                <Info className="h-3.5 w-3.5" />
                                Detalles
                            </button>
                            <div className="h-2 w-2 rounded-full bg-green-500/50 shadow-[0_0_8px_rgba(34,197,94,0.4)]"></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Catalog;
