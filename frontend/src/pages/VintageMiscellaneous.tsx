import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bookmark, AlertCircle, Info, X, ExternalLink, RotateCcw, Box, Trash2, ArrowUp, ArrowDown } from 'lucide-react';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import { getMiscellaneousItems, revertMiscellaneousItem, deleteMiscellaneousItem, type VintageMiscellaneousItem } from '../api/purgatory';
import type { Hero } from '../api/admin';

interface VintageMiscellaneousProps {
    user?: Hero | null;
}

const VintageMiscellaneous: React.FC<VintageMiscellaneousProps> = ({ user }) => {
    const queryClient = useQueryClient();
    const [selectedItem, setSelectedItem] = React.useState<VintageMiscellaneousItem | null>(null);
    const [expandedImage, setExpandedImage] = React.useState<string | null>(null);
    const [sortBy, setSortBy] = React.useState<'title' | 'price' | 'date'>('date');
    const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('desc');

    const isAdmin = user?.role === 'admin' || user?.username === 'David';

    // 1. Fetch miscellaneous items
    const { data: items, isLoading, isError } = useQuery<VintageMiscellaneousItem[]>({
        queryKey: ['vintage-miscellaneous'],
        queryFn: getMiscellaneousItems
    });

    // 2. Revert miscellaneous item back to purgatory
    const revertMutation = useMutation({
        mutationFn: (itemId: number) => revertMiscellaneousItem(itemId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vintage-miscellaneous'] });
            queryClient.invalidateQueries({ queryKey: ['purgatory'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedItem(null);
        },
        onError: (err) => {
            console.error('Error al devolver el lote al Purgatorio:', err);
            alert('No se pudo devolver al Purgatorio. Inténtelo de nuevo.');
        }
    });

    // 3. Delete miscellaneous item permanently
    const deleteMutation = useMutation({
        mutationFn: (itemId: number) => deleteMiscellaneousItem(itemId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vintage-miscellaneous'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
            setSelectedItem(null);
        },
        onError: (err) => {
            console.error('Error al eliminar el lote permanentemente:', err);
            alert('No se pudo eliminar el artículo. Inténtelo de nuevo.');
        }
    });

    const handleDelete = (itemId: number, title: string) => {
        const confirm1 = confirm(`¿Está seguro de que desea eliminar permanentemente el lote "${title}" de Miscelánea?`);
        if (confirm1) {
            const confirm2 = confirm(`Esta acción es irreversible y eliminará el registro de la base de datos para siempre. ¿Realmente desea continuar y borrarlo?`);
            if (confirm2) {
                deleteMutation.mutate(itemId);
            }
        }
    };

    const sortedItems = React.useMemo(() => {
        if (!items) return [];
        return [...items].sort((a, b) => {
            let comparison = 0;
            if (sortBy === 'title') {
                comparison = a.title.localeCompare(b.title);
            } else if (sortBy === 'price') {
                comparison = a.price - b.price;
            } else if (sortBy === 'date') {
                const dateA = a.added_at ? new Date(a.added_at).getTime() : 0;
                const dateB = b.added_at ? new Date(b.added_at).getTime() : 0;
                comparison = dateA - dateB;
            }
            return sortOrder === 'asc' ? comparison : -comparison;
        });
    }, [items, sortBy, sortOrder]);

    if (isLoading) {
        return <PowerSwordLoader variant="fullScreen" text="Canalizando Bóvedas de Miscelánea..." />;
    }

    if (isError) {
        return (
            <div className="flex h-64 flex-col items-center justify-center gap-4 text-purple-400">
                <AlertCircle className="h-10 w-10" />
                <p className="text-sm font-medium">Error al acceder al Pabellón de Miscelánea Vintage</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 md:space-y-3 animate-in fade-in duration-1000">
            {/* Header / Banner */}
            <div className="relative overflow-hidden flex flex-col gap-4 md:flex-row md:items-center md:justify-between rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-purple-500/10 blur-[100px] pointer-events-none"></div>
                <div className="relative z-10 flex flex-col gap-1">
                    <div className="flex items-center gap-2 text-purple-400">
                        <Bookmark className="h-4 w-4" />
                        <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                            Miscelánea <span className="text-purple-400">Vintage</span>
                        </h2>
                    </div>
                    <p className="max-w-xl text-[11px] md:text-sm text-white/40 font-medium uppercase tracking-[0.1em]">Lotes, packs y reliquias varias de MOTU sin catalogar individualmente</p>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full md:w-auto">
                    <div className="flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
                        <div className="grid grid-cols-3 gap-1 sm:gap-2 p-1 sm:p-1.5 rounded-xl bg-white/[0.03] border border-white/5 flex-1 sm:flex-initial">
                            <button
                                onClick={() => setSortBy('title')}
                                className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'title' ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                            >
                                Título
                            </button>
                            <button
                                onClick={() => setSortBy('price')}
                                className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'price' ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                            >
                                Precio
                            </button>
                            <button
                                onClick={() => setSortBy('date')}
                                className={`w-full py-1.5 rounded-lg text-[9px] sm:text-[10px] font-black uppercase tracking-[0.05em] sm:tracking-widest transition-all ${sortBy === 'date' ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]' : 'text-white/20 hover:text-white/40'}`}
                            >
                                Fecha
                            </button>
                        </div>
                        
                        <button
                            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                            className="h-[36px] w-[36px] sm:h-[42px] sm:w-[42px] flex items-center justify-center rounded-xl bg-white/[0.03] border border-white/5 text-purple-400 hover:bg-white/10 hover:text-white transition-all shrink-0 shadow-md"
                            title={sortOrder === 'asc' ? 'Orden Ascendente (A-Z, Menor Precio, Más Antiguos)' : 'Orden Descendente (Z-A, Mayor Precio, Más Recientes)'}
                        >
                            {sortOrder === 'asc' ? <ArrowUp className="h-4 w-4 sm:h-5 sm:w-5" /> : <ArrowDown className="h-4 w-4 sm:h-5 sm:w-5" />}
                        </button>
                    </div>
                    <div className="flex items-center justify-between sm:justify-start gap-3 rounded-xl sm:rounded-2xl bg-white/[0.03] px-4 sm:px-6 py-2 sm:py-3 border border-white/5 backdrop-blur-3xl w-full sm:w-auto">
                        <div className="flex items-center gap-2">
                            <Box className="h-4 w-4 sm:h-5 sm:w-5 text-purple-400" />
                            <span className="text-xl sm:text-2xl font-black text-white leading-none">{items?.length}</span>
                        </div>
                        <span className="text-[8px] sm:text-[10px] font-black text-white/20 uppercase tracking-[0.15em] sm:tracking-[0.2em] pt-0.5 leading-tight text-right sm:text-left">
                            Lotes & Varios<br className="sm:hidden" /> Registrados
                        </span>
                    </div>
                </div>
            </div>

            {/* Grid */}
            {sortedItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-20 text-white/20 space-y-4">
                    <Bookmark className="h-16 w-16 opacity-20" />
                    <p className="text-xl font-black uppercase tracking-widest">Sección Vacía...</p>
                    <p className="text-[10px] font-bold uppercase tracking-widest opacity-40">Clasifique lotes o packs vintage en el Purgatorio para verlos aquí.</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 gap-3 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {sortedItems.map((item) => {
                        return (
                            <div
                                key={item.id}
                                className="group relative flex flex-col gap-1.5 sm:gap-4 rounded-2xl sm:rounded-[2.5rem] border border-white/5 bg-black/25 backdrop-blur-md p-2 sm:p-5 hover:bg-white/[0.05] transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl"
                            >
                                <div
                                    className="relative aspect-square w-full overflow-hidden rounded-2xl sm:rounded-[2rem] bg-black/40 border border-white/10 shadow-inner group/img cursor-pointer"
                                    onClick={() => setSelectedItem(item)}
                                >
                                    {item.image_url ? (
                                        <img src={item.image_url} alt={item.title} className="h-full w-full object-cover transition-all duration-700 group-hover/img:scale-110" loading="lazy" />
                                    ) : (
                                        <div className="flex h-full w-full items-center justify-center italic text-white/20 text-[10px] sm:text-xs font-black uppercase tracking-widest">Sin Imagen</div>
                                    )}

                                    {/* Shop Indicator */}
                                    <div className="absolute bottom-2 left-2 sm:bottom-4 sm:left-4 z-40 rounded-lg sm:rounded-xl bg-black/75 px-2 py-1 text-[8px] sm:text-[10px] font-black text-white/50 border border-white/5 backdrop-blur-md uppercase tracking-wider">
                                        {item.shop_name}
                                    </div>
                                </div>

                                <div className="flex flex-1 flex-col gap-1 sm:gap-3 px-1">
                                    <div className="space-y-0.5 sm:space-y-1">
                                        <span className="text-[7px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-purple-400 opacity-80 group-hover:opacity-100 transition-colors line-clamp-1">lote / miscelánea motu</span>
                                        <h3 className="line-clamp-2 md:min-h-[2rem] text-[11px] sm:text-lg font-black leading-tight text-white group-hover:text-purple-400 transition-colors">{item.title}</h3>
                                    </div>

                                    <div className="mt-auto flex flex-col gap-2">
                                        <div className="flex flex-col flex-1 min-w-0 justify-end pt-2">
                                            <div className="flex items-center gap-1 sm:gap-1.5 overflow-hidden w-full mb-0.5 sm:mb-1">
                                                <span className="text-[6px] sm:text-[8px] font-black text-white/30 uppercase tracking-widest leading-none shrink-0">Precio Oferta</span>
                                            </div>
                                            <div className="text-[16px] sm:text-2xl font-black text-purple-400 leading-[0.8] sm:leading-none tracking-tighter truncate">{item.price || 0} <span className="text-[8px] sm:text-xs text-white/40">€</span></div>
                                        </div>

                                        {/* Action Buttons Row */}
                                        <div className="flex items-center justify-center gap-2 rounded-2xl bg-white/[0.03] p-1.5 border border-white/10 group-hover:border-purple-500/20 transition-all backdrop-blur-sm w-full">
                                            {/* Action Button: Detail View */}
                                            <button
                                                onClick={() => setSelectedItem(item)}
                                                className="flex-1 flex h-8 items-center justify-center gap-1 rounded-xl bg-white/5 text-white/40 border border-white/10 transition-all hover:bg-purple-500/20 hover:text-purple-400 hover:border-purple-500/45 hover:scale-105 active:scale-95 duration-300 shadow-md text-[9px] font-black uppercase tracking-wider"
                                                title="Ver Detalles"
                                            >
                                                <Info className="h-4 w-4" />
                                                <span>Detalle</span>
                                            </button>

                                            {/* Action: Revert back to Purgatory */}
                                            {isAdmin && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        if (confirm(`¿Devolver este lote al Purgatorio?`)) {
                                                            revertMutation.mutate(item.id);
                                                        }
                                                    }}
                                                    disabled={revertMutation.isPending}
                                                    className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-amber-500/60 border border-white/10 transition-all hover:bg-amber-500/20 hover:text-amber-400 hover:border-amber-500/50 hover:scale-110 active:scale-95 duration-300 shadow-md shrink-0"
                                                    title="Devolver al Purgatorio (Reversión)"
                                                >
                                                    <RotateCcw className="h-4 w-4" />
                                                </button>
                                            )}

                                            {/* Action: Delete permanently */}
                                            {isAdmin && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDelete(item.id, item.title);
                                                    }}
                                                    disabled={deleteMutation.isPending}
                                                    className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 text-red-500/60 border border-white/10 transition-all hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/50 hover:scale-110 active:scale-95 duration-300 shadow-md shrink-0"
                                                    title="Eliminar Permanentemente"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {selectedItem && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl" onClick={() => setSelectedItem(null)}>
                    <div className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-[2rem] sm:rounded-[3rem] border border-white/10 bg-[#0A0A0B] shadow-[0_50px_100px_-20px_rgba(0,0,0,1)] flex flex-col" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6 sm:p-8 pb-4 flex items-start justify-between">
                            <div className="flex gap-4 sm:gap-6 items-center">
                                <div
                                    className="h-16 w-16 sm:h-20 sm:w-20 shrink-0 overflow-hidden rounded-2xl sm:rounded-3xl border border-white/10 bg-black/40 cursor-zoom-in hover:scale-105 transition-transform"
                                    onClick={() => setExpandedImage(selectedItem.image_url ?? null)}
                                    title="Expandir Imagen"
                                >
                                    <img src={selectedItem.image_url || ''} className="h-full w-full object-cover" />
                                </div>
                                <div className="space-y-0.5 sm:space-y-1">
                                    <h4 className="text-xl sm:text-2xl font-black tracking-tighter text-white">Lote <span className="text-purple-400">Miscelánea</span></h4>
                                    <p className="text-[9px] sm:text-xs font-bold text-white/30 uppercase tracking-widest">{selectedItem.title}</p>
                                </div>
                            </div>
                            <button onClick={() => setSelectedItem(null)} className="h-9 w-9 sm:h-10 sm:w-10 flex items-center justify-center rounded-xl bg-white/5 text-white/40 hover:bg-red-500/20 hover:text-red-400 text-lg sm:text-xl">&times;</button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 sm:p-8 pt-4 custom-scrollbar">
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-2">
                                    <div className="glass p-4 rounded-2xl border border-white/5 flex flex-col items-center justify-center">
                                        <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">Precio</p>
                                        <span className="text-xl sm:text-2xl font-black text-purple-400">{selectedItem.price} €</span>
                                    </div>
                                    <div className="glass p-4 rounded-2xl border border-white/5 flex flex-col items-center justify-center">
                                        <p className="text-[10px] font-black text-white/20 uppercase tracking-widest">Procedencia</p>
                                        <span className="text-base sm:text-lg font-black text-white">{selectedItem.shop_name}</span>
                                    </div>
                                </div>

                                {selectedItem.notes && (
                                    <div className="space-y-2">
                                        <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 px-2">Notas de Clasificación</h5>
                                        <div className="rounded-2xl sm:rounded-3xl p-4 sm:p-5 bg-white/[0.03] border border-white/5 text-xs text-white/70">
                                            {selectedItem.notes}
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-3">
                                    <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 px-2">Origen y Enlace</h5>
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-3xl p-4 sm:p-5 bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all">
                                        <div className="space-y-1">
                                            <div className="text-xs font-black uppercase tracking-widest text-white/80">{selectedItem.shop_name}</div>
                                            <div className="text-[9px] font-bold text-white/20 uppercase">Lote Vintage de MOTU</div>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-2 sm:gap-3 w-full sm:w-auto">
                                            <a
                                                href={selectedItem.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex-1 sm:flex-initial flex h-10 sm:h-12 px-4 sm:px-5 items-center justify-center gap-2 rounded-2xl bg-purple-600 text-white hover:brightness-110 transition-all text-xs font-black uppercase tracking-widest shadow-lg shadow-purple-500/20"
                                                title="Ver Anuncio Original"
                                            >
                                                <ExternalLink className="h-4.5 w-4.5 sm:h-5 sm:w-5" />
                                                <span>Ver Anuncio</span>
                                            </a>
                                            {isAdmin && (
                                                <button
                                                    onClick={() => {
                                                        if (confirm(`¿Desclasificar y devolver al Purgatorio?`)) {
                                                            revertMutation.mutate(selectedItem.id);
                                                        }
                                                    }}
                                                    className="flex-1 sm:flex-initial flex h-10 sm:h-12 px-4 sm:px-5 items-center justify-center gap-2 rounded-2xl bg-amber-500/10 text-amber-500 border border-amber-500/20 hover:bg-amber-500 hover:text-white transition-all text-xs font-black uppercase tracking-widest"
                                                >
                                                    <RotateCcw className="h-4 w-4" /> <span>Revertir</span>
                                                </button>
                                            )}
                                            {isAdmin && (
                                                <button
                                                    onClick={() => handleDelete(selectedItem.id, selectedItem.title)}
                                                    className="flex-1 sm:flex-initial flex h-10 sm:h-12 px-4 sm:px-5 items-center justify-center gap-2 rounded-2xl bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all text-xs font-black uppercase tracking-widest"
                                                >
                                                    <Trash2 className="h-4 w-4" /> <span>Eliminar</span>
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* FULLSCREEN IMAGE EXPANSION */}
            {expandedImage && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-20 bg-black/95 backdrop-blur-3xl animate-in zoom-in duration-300 shadow-2xl"
                    onClick={() => setExpandedImage(null)}
                >
                    <div className="relative max-w-full max-h-full group">
                        <img
                            src={expandedImage}
                            alt="Expanded Vintage Lot"
                            className="max-w-full max-h-[90vh] rounded-[2rem] sm:rounded-[3rem] border border-white/10 shadow-[0_0_100px_rgba(0,0,0,0.8)] object-contain"
                            onClick={(e) => e.stopPropagation()}
                        />
                        <button
                            onClick={() => setExpandedImage(null)}
                            className="absolute -top-4 -right-4 sm:-top-8 sm:-right-8 h-10 w-10 sm:h-14 sm:w-14 flex items-center justify-center rounded-2xl bg-white/10 text-white hover:bg-red-500 hover:scale-110 transition-all border border-white/10 backdrop-blur-md shadow-2xl z-50"
                        >
                            <X className="h-6 w-6 sm:h-8 sm:w-8" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VintageMiscellaneous;
