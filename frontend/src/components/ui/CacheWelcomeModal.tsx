import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Zap, Cloud, Database, AlertCircle, Sparkles, X } from 'lucide-react';
import { useModalA11y } from '../../hooks/useModalA11y';

interface CacheWelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (mode: 'download_all' | 'on_demand' | 'none') => void;
}

export default function CacheWelcomeModal({ isOpen, onClose, onSelect }: CacheWelcomeModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  useModalA11y(isOpen, onClose, containerRef);

  const handleSelect = (mode: 'download_all' | 'on_demand' | 'none') => {
    onSelect(mode);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[150] flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-md"
          />

          {/* Modal Card */}
          <motion.div
            ref={containerRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="cache-welcome-title"
            tabIndex={-1}
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 180 }}
            className="relative w-full max-w-lg overflow-hidden rounded-[2.5rem] border border-white/10 bg-gradient-to-b from-slate-900/90 to-black/95 p-6 md:p-8 text-white shadow-2xl backdrop-blur-3xl outline-none"
          >
            {/* Ambient glows */}
            <div className="absolute -right-16 -top-16 h-32 w-32 rounded-full bg-brand-primary/10 blur-3xl pointer-events-none" />
            <div className="absolute -left-16 -bottom-16 h-32 w-32 rounded-full bg-brand-secondary/10 blur-3xl pointer-events-none" />

            {/* Header */}
            <div className="flex items-start justify-between relative z-10 mb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-primary/10 border border-brand-primary/30 text-brand-primary shadow-inner">
                  <Database className="h-6 w-6 animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4 text-brand-primary" />
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-brand-primary">OPTIMIZACIÓN TÁCTICA</span>
                  </div>
                  <h3 id="cache-welcome-title" className="text-xl font-bold uppercase tracking-wide text-white">
                    Bóveda de Imágenes Local
                  </h3>
                </div>
              </div>
              <button
                onClick={onClose}
                aria-label="Cerrar"
                className="rounded-lg p-1.5 text-white/40 hover:bg-white/5 hover:text-white transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Content */}
            <div className="space-y-4 relative z-10">
              <p className="text-xs text-white/70 leading-relaxed font-medium">
                ¡Bienvenido al Oráculo de Nueva Eternia! Para asegurar que tu navegación sea 
                <span className="text-brand-primary font-bold"> instantánea</span>, funcione offline y resista caídas de cuota del servidor de base de datos, te ofrecemos almacenar las imágenes de las figuras directamente en tu dispositivo.
              </p>

              {/* Warning box */}
              <div className="flex items-start gap-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 p-3.5 text-amber-500">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <span className="text-[10px] font-black uppercase tracking-wider block">INFORMACIÓN DE ALMACENAMIENTO:</span>
                  <p className="text-[10px] leading-relaxed text-amber-500/80 font-medium">
                    Gracias a la nueva conversión de alto rendimiento <span className="font-bold">WebP</span>, todas las imágenes ocupan solo unos <span className="font-bold text-white">15 MB - 20 MB</span> de espacio en disco (frente a los más de 50 MB en JPEG original).
                  </p>
                </div>
              </div>

              {/* Options */}
              <div className="space-y-2.5 pt-2">
                {/* Mode 1: Download All (Recommended) */}
                <button
                  onClick={() => handleSelect('download_all')}
                  className="w-full flex items-start gap-3 rounded-2xl border border-brand-primary/30 bg-brand-primary/5 hover:bg-brand-primary/10 p-3.5 text-left transition-all hover:scale-[1.01] active:scale-[0.99]"
                >
                  <Download className="h-5 w-5 text-brand-primary shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white uppercase tracking-wider">Activar y Descargar Todo</span>
                      <span className="text-[8px] font-black text-brand-primary uppercase tracking-wider bg-brand-primary/10 border border-brand-primary/20 px-1.5 py-0.5 rounded-md">
                        Recomendado
                      </span>
                    </div>
                    <p className="text-[10px] text-white/50 leading-relaxed mt-0.5">
                      Descarga progresivamente todas las imágenes en segundo plano (con esperas suaves para no consumir CPU o red) y úsalas al instante.
                    </p>
                  </div>
                </button>

                {/* Mode 2: On Demand */}
                <button
                  onClick={() => handleSelect('on_demand')}
                  className="w-full flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] p-3.5 text-left transition-all hover:scale-[1.01] active:scale-[0.99]"
                >
                  <Zap className="h-5 w-5 text-yellow-500 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-xs font-bold text-white uppercase tracking-wider block">Activar Bajo Demanda</span>
                    <p className="text-[10px] text-white/50 leading-relaxed mt-0.5">
                      Almacena en caché únicamente las imágenes de las figuras que visites. Ahorra red inicial, pero la primera carga de cada figura será remota.
                    </p>
                  </div>
                </button>

                {/* Mode 3: Cloud only */}
                <button
                  onClick={() => handleSelect('none')}
                  className="w-full flex items-start gap-3 rounded-2xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.03] p-3.5 text-left transition-all hover:scale-[1.01] active:scale-[0.99] opacity-70 hover:opacity-100"
                >
                  <Cloud className="h-5 w-5 text-sky-400 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-xs font-bold text-white/80 uppercase tracking-wider block">Mantener en la Nube</span>
                    <p className="text-[10px] text-white/40 leading-relaxed mt-0.5">
                      No guarda nada en disco. Carga siempre las imágenes de la nube (CDN). Si el servidor está saturado o sin cuota, algunas imágenes podrían no visualizarse.
                    </p>
                  </div>
                </button>
              </div>

              {/* Extra explanation */}
              <div className="text-[9px] text-white/40 uppercase tracking-widest text-center pt-2">
                Puedes cambiar esta configuración en cualquier momento desde los Ajustes del Arquitecto.
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
