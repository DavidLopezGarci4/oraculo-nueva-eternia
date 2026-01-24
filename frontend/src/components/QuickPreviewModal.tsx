
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    X,
    ExternalLink,
    MapPin,
    User,
    Star,
    Calendar,
    Loader2,
    AlertCircle,
    ChevronLeft,
    ChevronRight,
    Camera
} from 'lucide-react';
import axios from 'axios';

interface QuickPreviewModalProps {
    url: number | string; // Accept object id or just url
    onClose: () => void;
}

const QuickPreviewModal: React.FC<QuickPreviewModalProps> = ({ url, onClose }) => {
    const [currentImageIndex, setCurrentImageIndex] = React.useState(0);

    const { data: item, isLoading, error } = useQuery({
        queryKey: ['wallapop-preview', url],
        queryFn: async () => {
            const response = await axios.get(`/api/wallapop/preview?url=${encodeURIComponent(String(url))}`);
            return response.data;
        }
    });

    if (isLoading) {
        return (
            <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 backdrop-blur-md">
                <div className="text-center space-y-4">
                    <Loader2 className="h-10 w-10 animate-spin text-brand-primary mx-auto" />
                    <p className="text-xs font-black uppercase tracking-widest text-white/40">Invocando el espíritu de Wallapop...</p>
                </div>
            </div>
        );
    }

    if (error || !item) {
        return (
            <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 backdrop-blur-md">
                <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-3xl text-center space-y-4 max-w-sm">
                    <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
                    <h3 className="text-white font-black text-xl uppercase italic">Fallo de Visión</h3>
                    <p className="text-white/60 text-xs">No se ha podido conectar con la fuente original. Es posible que el anuncio ya no exista o Wallapop haya reforzado sus muros.</p>
                    <button onClick={onClose} className="w-full bg-white text-black py-3 rounded-xl font-bold uppercase transition-transform hover:scale-95 text-xs">Cerrar</button>
                </div>
            </div>
        );
    }

    const nextImage = () => {
        if (item.images && item.images.length > 0) {
            setCurrentImageIndex((prev) => (prev + 1) % item.images.length);
        }
    };

    const prevImage = () => {
        if (item.images && item.images.length > 0) {
            setCurrentImageIndex((prev) => (prev - 1 + item.images.length) % item.images.length);
        }
    };

    return (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/95 backdrop-blur-2xl p-4 md:p-10 animate-in fade-in zoom-in duration-300">
            <div className="relative w-full max-w-6xl h-full max-h-[85vh] rounded-[2.5rem] border border-white/10 bg-black/40 overflow-hidden shadow-2xl flex flex-col md:flex-row">

                {/* Close Button Mobile */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 z-50 h-10 w-10 md:hidden flex items-center justify-center rounded-full bg-black/50 backdrop-blur-md border border-white/10"
                >
                    <X className="h-5 w-5 text-white" />
                </button>

                {/* Left Side: Images Viewport */}
                <div className="relative w-full md:w-3/5 h-[40vh] md:h-full bg-black/20 flex items-center justify-center group">
                    {item.images && item.images.length > 0 ? (
                        <>
                            <img
                                src={item.images[currentImageIndex]}
                                alt={item.title}
                                className="w-full h-full object-contain transition-opacity duration-500"
                            />

                            {/* Navigation Buttons */}
                            {item.images.length > 1 && (
                                <>
                                    <button
                                        onClick={prevImage}
                                        className="absolute left-4 h-12 w-12 flex items-center justify-center rounded-2xl bg-black/20 backdrop-blur-xl border border-white/5 opacity-0 group-hover:opacity-100 transition-all hover:bg-black/40"
                                    >
                                        <ChevronLeft className="h-6 w-6 text-white" />
                                    </button>
                                    <button
                                        onClick={nextImage}
                                        className="absolute right-4 h-12 w-12 flex items-center justify-center rounded-2xl bg-black/20 backdrop-blur-xl border border-white/5 opacity-0 group-hover:opacity-100 transition-all hover:bg-black/40"
                                    >
                                        <ChevronRight className="h-6 w-6 text-white" />
                                    </button>

                                    {/* Indicator Dots */}
                                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-1.5 p-2 rounded-full bg-black/20 backdrop-blur-md border border-white/5">
                                        {item.images.map((_: any, idx: number) => (
                                            <div
                                                key={idx}
                                                className={`h-1.5 rounded-full transition-all duration-300 ${idx === currentImageIndex ? 'w-6 bg-brand-primary' : 'w-1.5 bg-white/20'}`}
                                            />
                                        ))}
                                    </div>
                                </>
                            )}
                        </>
                    ) : (
                        <div className="flex flex-col items-center gap-4 text-white/20">
                            <Camera className="h-16 w-16" />
                            <p className="text-xs font-black uppercase">Sin imágenes disponibles</p>
                        </div>
                    )}
                </div>

                {/* Right Side: Details Area */}
                <div className="flex-1 flex flex-col bg-white/[0.02] border-l border-white/5">
                    {/* Header */}
                    <div className="p-8 space-y-4 border-b border-white/5">
                        <div className="flex items-center justify-between">
                            <div className="px-3 py-1 rounded-full bg-brand-primary/10 border border-brand-primary/20 text-brand-primary text-[10px] font-black uppercase tracking-widest">
                                Wallapop Oracle View
                            </div>
                            <button
                                onClick={onClose}
                                className="hidden md:flex h-10 w-10 items-center justify-center rounded-2xl hover:bg-white/5 transition-colors"
                            >
                                <X className="h-5 w-5 text-white/40 hover:text-white" />
                            </button>
                        </div>
                        <h2 className="text-2xl md:text-3xl font-black text-white leading-tight">{item.title}</h2>
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl font-black text-brand-primary">{item.price}</span>
                            <span className="text-xl font-bold text-brand-primary/40 uppercase">{item.currency}</span>
                        </div>
                    </div>

                    {/* Scrollable Info Area */}
                    <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">

                        {/* Tags / Badges */}
                        <div className="flex flex-wrap gap-4">
                            <div className="flex items-center gap-2 text-white/60 bg-white/5 px-4 py-2 rounded-xl text-xs font-bold">
                                <MapPin className="h-3.5 w-3.5 text-brand-primary" />
                                {item.location || 'Localización desconocida'}
                            </div>
                            <div className="flex items-center gap-2 text-white/60 bg-white/5 px-4 py-2 rounded-xl text-xs font-bold">
                                <Calendar className="h-3.5 w-3.5 text-brand-primary" />
                                {item.published_at ? new Date(item.published_at).toLocaleDateString() : 'Subido recientemente'}
                            </div>
                        </div>

                        {/* Description */}
                        <div className="space-y-3">
                            <h4 className="text-[10px] font-black text-white/20 uppercase tracking-[0.2em]">Descripción Cruda</h4>
                            <p className="text-white/60 text-sm leading-relaxed whitespace-pre-line font-medium">
                                {item.description}
                            </p>
                        </div>

                        {/* Seller Card */}
                        <div className="bg-white/[0.03] border border-white/5 p-6 rounded-[2rem] space-y-4">
                            <div className="flex items-center gap-4">
                                {item.seller.avatar ? (
                                    <img src={item.seller.avatar} alt={item.seller.name} className="h-14 w-14 rounded-2xl object-cover ring-2 ring-white/5" />
                                ) : (
                                    <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center text-white/20">
                                        <User className="h-6 w-6" />
                                    </div>
                                )}
                                <div className="space-y-1">
                                    <h5 className="font-black text-white">{item.seller.name || 'Vendedor Anónimo'}</h5>
                                    <div className="flex items-center gap-3">
                                        <div className="flex items-center gap-1 text-yellow-500">
                                            <Star className="h-3 w-3 fill-current" />
                                            <span className="text-xs font-black">{item.seller.stats.average_stars?.toFixed(1) || '0.0'}</span>
                                        </div>
                                        <span className="text-white/20 text-xs font-bold">({item.seller.stats.completed_sales || 0} ventas)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="p-6 bg-white/[0.02] border-t border-white/5 flex gap-4">
                        <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 bg-white hover:bg-brand-primary hover:text-white text-black py-4 rounded-2xl font-black text-xs uppercase transition-all flex items-center justify-center gap-3 shadow-xl hover:shadow-brand-primary/20"
                        >
                            <ExternalLink className="h-4 w-4" />
                            Abrir en Wallapop (Web)
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QuickPreviewModal;
