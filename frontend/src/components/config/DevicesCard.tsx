import { useState } from 'react';
import { ShieldCheck, CheckCircle2, Trash2, Smartphone, AlertTriangle, RefreshCw } from 'lucide-react';
import type { Device } from '../../api/admin';

interface DevicesCardProps {
    devices: Device[];
    loading?: boolean;
    onAuthorize: (deviceId: string) => void;
    onDelete: (deviceId: string) => void;
    onRefresh?: () => void;
}

export default function DevicesCard({
    devices,
    loading = false,
    onAuthorize,
    onDelete,
    onRefresh
}: DevicesCardProps) {
    const [actionId, setActionId] = useState<string | null>(null);

    const handleAuthorizeClick = async (deviceId: string) => {
        setActionId(deviceId);
        try {
            await onAuthorize(deviceId);
        } finally {
            setActionId(null);
        }
    };

    const handleDeleteClick = async (deviceId: string) => {
        setActionId(deviceId);
        try {
            await onDelete(deviceId);
        } finally {
            setActionId(null);
        }
    };

    const pendingCount = devices.filter(d => !d.is_authorized).length;

    return (
        <div className="glass border border-white/10 rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-brand-primary/10 rounded-2xl border border-brand-primary/20">
                        <ShieldCheck className="h-6 w-6 text-brand-primary" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h4 className="text-lg font-bold text-white">Dispositivos & Escudo de Eternia</h4>
                            {pendingCount > 0 && (
                                <span className="bg-amber-500/20 text-amber-300 text-[10px] font-black uppercase px-2 py-0.5 rounded-full border border-amber-500/30 flex items-center gap-1 animate-pulse">
                                    <AlertTriangle className="h-3 w-3" />
                                    {pendingCount} Pendiente{pendingCount > 1 ? 's' : ''}
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-white/65">Autorización de huellas digitales de navegador y alertas de acceso Telegram.</p>
                    </div>
                </div>

                {onRefresh && (
                    <button
                        onClick={onRefresh}
                        disabled={loading}
                        className="bg-white/5 hover:bg-white/10 text-white/80 border border-white/10 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 self-end sm:self-auto"
                    >
                        <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                        Actualizar
                    </button>
                )}
            </div>

            <div className="overflow-x-auto scrollbar-none custom-scrollbar">
                <table className="w-full text-left text-sm min-w-[650px]">
                    <thead className="bg-white/5 text-white/60 uppercase text-[9px] font-bold">
                        <tr>
                            <th className="px-4 py-3">Dispositivo / Nombre</th>
                            <th className="px-4 py-3">ID Huella Digital</th>
                            <th className="px-4 py-3">Estado</th>
                            <th className="px-4 py-3">Último Acceso</th>
                            <th className="px-4 py-3 text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-white/70">
                        {devices.map((device) => {
                            const isPending = !device.is_authorized;
                            const isProcessing = actionId === device.device_id;

                            return (
                                <tr key={device.id} className="hover:bg-white/5 transition-colors group">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-3">
                                            <div className={`h-8 w-8 rounded-xl flex items-center justify-center border flex-shrink-0 ${
                                                isPending
                                                    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                                                    : 'bg-green-500/10 border-green-500/30 text-green-400'
                                            }`}>
                                                <Smartphone className="h-4 w-4" />
                                            </div>
                                            <div>
                                                <p className="font-bold text-white text-xs group-hover:text-brand-primary transition-colors">
                                                    {device.device_name || 'Dispositivo Desconocido'}
                                                </p>
                                                <p className="text-[9px] text-white/40">
                                                    Registrado: {new Date(device.created_at).toLocaleDateString('es-ES')}
                                                </p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-[10px] font-mono text-white/70 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                                            {device.device_id}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        {isPending ? (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/30">
                                                <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-ping" />
                                                Bloqueado
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-green-500/10 text-green-400 border border-green-500/30">
                                                <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                                                Autorizado
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-4 py-3 text-xs text-white/60 font-mono">
                                        {device.last_access_at
                                            ? new Date(device.last_access_at).toLocaleString('es-ES', {
                                                year: 'numeric', month: '2-digit', day: '2-digit',
                                                hour: '2-digit', minute: '2-digit'
                                            })
                                            : 'Nunca'}
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            {isPending && (
                                                <button
                                                    onClick={() => handleAuthorizeClick(device.device_id)}
                                                    disabled={isProcessing}
                                                    title="Autorizar Dispositivo"
                                                    className="bg-green-500/20 hover:bg-green-500 text-green-300 hover:text-white border border-green-500/30 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 shadow-lg shadow-green-500/10 disabled:opacity-50"
                                                >
                                                    <CheckCircle2 className="h-3.5 w-3.5" />
                                                    APROBAR
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleDeleteClick(device.device_id)}
                                                disabled={isProcessing}
                                                title="Revocar / Eliminar Dispositivo"
                                                className="h-8 w-8 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white border border-red-500/20 flex items-center justify-center transition-all disabled:opacity-50"
                                            >
                                                <Trash2 className="h-3.5 w-3.5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}

                        {devices.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-6 py-8 text-center text-white/30 italic">
                                    No hay dispositivos registrados en las bitácoras del Escudo.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
