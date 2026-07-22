import React from 'react';
import { X } from 'lucide-react';
import { MOTUImage } from '../ui/MOTUImage';

interface FullscreenImageModalProps {
    expandedImage: string | null;
    setExpandedImage: (url: string | null) => void;
    productId: number | undefined;
}

const FullscreenImageModal: React.FC<FullscreenImageModalProps> = ({ expandedImage, setExpandedImage, productId }) => {
    if (!expandedImage) return null;

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-20 bg-black/95 backdrop-blur-3xl animate-in zoom-in duration-300 shadow-2xl"
            onClick={() => setExpandedImage(null)}
        >
            <div className="relative max-w-full max-h-full group">
                <MOTUImage
                    productId={productId}
                    src={expandedImage}
                    alt="Expanded Relic"
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
    );
};

export default FullscreenImageModal;
