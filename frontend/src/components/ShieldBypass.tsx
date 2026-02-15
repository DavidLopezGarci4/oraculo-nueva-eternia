import React from 'react';
import { ShieldIdentity } from '../api/shield-identity';
import { ShieldAlert, RefreshCw, MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';

interface ShieldBypassProps {
    onRetry: () => void;
    onSovereignClick?: () => void;
}

const ShieldBypass: React.FC<ShieldBypassProps> = ({ onRetry, onSovereignClick }) => {
    const deviceId = ShieldIdentity.getDeviceId();
    const deviceName = ShieldIdentity.getDeviceName();

    return (
        <div className="flex h-screen w-full items-center justify-center bg-black p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-md w-full bg-zinc-900/50 border border-white/5 rounded-3xl p-8 backdrop-blur-xl text-center"
            >
                <div className="flex justify-center mb-6">
                    <div className="h-16 w-16 rounded-2xl bg-brand-primary/10 flex items-center justify-center border border-brand-primary/20">
                        <ShieldAlert className="h-8 w-8 text-brand-primary" />
                    </div>
                </div>

                <h1 className="text-2xl font-black text-white mb-2 uppercase tracking-tight">Acceso Bloqueado</h1>
                <p className="text-white/60 text-sm mb-8">
                    El Escudo de Nueva Eternia ha detectado un dispositivo nuevo. Por seguridad, el Gran Arquitecto debe autorizar la conexión.
                </p>

                <div className="bg-white/5 rounded-2xl p-4 mb-8 text-left border border-white/5">
                    <div className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Tu Identidad</div>
                    <div className="text-white font-mono text-xs">{deviceId}</div>
                    <div className="text-white/40 text-[10px] mt-1">{deviceName}</div>
                </div>

                <div className="flex flex-col gap-3">
                    <div className="flex items-center gap-3 bg-brand-primary/5 border border-brand-primary/10 p-4 rounded-2xl text-left">
                        <MessageSquare className="h-5 w-5 text-brand-primary shrink-0" />
                        <p className="text-xs text-brand-primary/80 leading-relaxed">
                            He enviado una alerta a tu **Telegram**. Por favor, autoriza este ID para continuar.
                        </p>
                    </div>

                    <button
                        onClick={onRetry}
                        className="flex items-center justify-center gap-2 w-full h-14 bg-white text-black font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-brand-primary transition-all active:scale-95 mt-4"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Comprobar Autorización
                    </button>

                    {onSovereignClick && (
                        <button
                            onClick={onSovereignClick}
                            className="mt-4 text-[9px] font-black uppercase tracking-[0.2em] text-white/10 hover:text-brand-primary transition-colors py-2"
                        >
                            ¿Eres el Soberano? Entrar con Llave
                        </button>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default ShieldBypass;
