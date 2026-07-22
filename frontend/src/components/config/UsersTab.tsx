import { motion } from 'framer-motion';
import { Users, Swords, Shield, ChevronDown, Target, Repeat, FileSpreadsheet, Database, ShieldAlert, Trash2, CheckCircle2, Activity } from 'lucide-react';
import type { Hero, Device } from '../../api/admin';
import DevicesCard from './DevicesCard';

interface UsersTabProps {
    heroes: Hero[];
    onAddUserClick: () => void;
    onIdentityChange?: (targetId: number) => void;
    handleUpdateRole: (userId: number, newRole: string) => void;
    handleExportExcelAdmin: (userId: number) => void;
    handleExportSqliteAdmin: (userId: number) => void;
    handlePasswordReset: (heroId: number) => void;
    handleDeleteHero: (heroId: number, username: string) => void;
    devices?: Device[];
    loadingDevices?: boolean;
    onAuthorizeDevice?: (deviceId: string) => void;
    onDeleteDevice?: (deviceId: string) => void;
    onRefreshDevices?: () => void;
}

/** Fase AAA-4a: extraido de Config.tsx (pestaña "users"). */
export default function UsersTab({
    heroes,
    onAddUserClick,
    onIdentityChange,
    handleUpdateRole,
    handleExportExcelAdmin,
    handleExportSqliteAdmin,
    handlePasswordReset,
    handleDeleteHero,
    devices = [],
    loadingDevices = false,
    onAuthorizeDevice,
    onDeleteDevice,
    onRefreshDevices,
}: UsersTabProps) {
    return (
        <motion.div
            key="users"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-6"
        >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div className="flex flex-col gap-1">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Users className="h-6 w-6 text-brand-primary" />
                        Gestión de Héroes del Reino
                    </h3>
                    <p className="text-white/65 text-sm">Control de acceso, roles y estados de las fortalezas individuales.</p>
                </div>
                <button
                    onClick={onAddUserClick}
                    className="bg-brand-primary/20 text-brand-primary border border-brand-primary/30 hover:bg-brand-primary hover:text-white px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                >
                    <Users className="h-4 w-4" />
                    RECLUTAR NUEVO HÉROE
                </button>
            </div>

            <div className="glass border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
                <div className="overflow-x-auto scrollbar-none custom-scrollbar">
                    <table className="w-full text-left text-sm min-w-[700px]">
                        <thead className="bg-white/5 text-white/60 uppercase text-[9px] font-bold">
                            <tr>
                                <th className="px-4 py-3">Héroe</th>
                                <th className="px-2 py-3 text-center w-10">ID</th>
                                <th className="px-4 py-3">Rango</th>
                                <th className="px-4 py-3">Fortaleza</th>
                                <th className="px-4 py-3">Ubicación</th>
                                <th className="px-4 py-3 text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-white/70">
                            {heroes.map((hero: Hero) => (
                                <tr key={hero.id} className="hover:bg-white/5 transition-colors group">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                            <div className="h-8 w-8 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary font-bold text-xs border border-brand-primary/30 shadow-inner group-hover:scale-110 transition-transform flex-shrink-0">
                                                {hero.username.charAt(0).toUpperCase()}
                                            </div>
                                            <div className="truncate max-w-[120px]">
                                                <p className="font-bold text-white text-xs group-hover:text-brand-primary transition-colors truncate">{hero.username}</p>
                                                <p className="text-[9px] text-white/60 font-mono truncate">{hero.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-2 py-3 text-center">
                                        <span className="text-[10px] font-mono text-brand-primary/70 bg-brand-primary/10 px-1.5 py-0.5 rounded-md border border-brand-primary/20">{hero.id}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="relative flex items-center w-fit">
                                            {hero.role === 'admin' ? (
                                                <Swords className="absolute left-2 h-3 w-3 text-brand-primary pointer-events-none" />
                                            ) : (
                                                <Shield className="absolute left-2 h-3 w-3 text-brand-primary pointer-events-none" />
                                            )}
                                            <select
                                                value={hero.role}
                                                onChange={(e) => handleUpdateRole(hero.id, e.target.value)}
                                                aria-label={`Rol de ${hero.username}`}
                                                className="bg-brand-primary/10 text-brand-primary text-[9px] uppercase font-black border border-brand-primary/20 rounded pl-6 pr-5 py-1.5 outline-none cursor-pointer hover:bg-brand-primary/30 appearance-none text-left"
                                            >
                                                <option value="viewer" className="bg-black text-white">Guardián</option>
                                                <option value="admin" className="bg-black text-white">Maestro</option>
                                            </select>
                                            <ChevronDown className="absolute right-1.5 h-2.5 w-2.5 text-brand-primary pointer-events-none" />
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1.5">
                                            <Target className="h-3 w-3 text-brand-primary" />
                                            <span className="font-black text-sm text-white">{hero.collection_size}</span>
                                            <span className="text-[9px] text-brand-primary/50 font-black uppercase tracking-tighter">unidades</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-[9px] font-bold text-white/65 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded-md truncate block max-w-[80px]">{hero.location}</span>
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <div className="flex items-center justify-end gap-1 transition-opacity">
                                            <button
                                                onClick={() => onIdentityChange?.(hero.id)}
                                                title={`Asumir Identidad`}
                                                className="h-7 w-7 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white border border-brand-primary/20 flex items-center justify-center transition-all"
                                            >
                                                <Repeat className="h-3.5 w-3.5" />
                                            </button>
                                            <button
                                                onClick={() => handleExportExcelAdmin(hero.id)}
                                                title="Bajar Excel"
                                                className="h-7 w-7 rounded-lg bg-green-500/10 text-green-400 hover:bg-green-500 hover:text-white border border-green-500/20 flex items-center justify-center transition-all"
                                            >
                                                <FileSpreadsheet className="h-3.5 w-3.5" />
                                            </button>
                                            <button
                                                onClick={() => handleExportSqliteAdmin(hero.id)}
                                                title="Bajar SQLite"
                                                className="h-7 w-7 rounded-lg bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500 hover:text-white border border-indigo-500/20 flex items-center justify-center transition-all"
                                            >
                                                <Database className="h-3.5 w-3.5" />
                                            </button>
                                            <button
                                                onClick={() => handlePasswordReset(hero.id)}
                                                title="Reset Password"
                                                className="h-7 w-7 rounded-lg bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 flex items-center justify-center transition-all"
                                            >
                                                <ShieldAlert className="h-3.5 w-3.5" />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteHero(hero.id, hero.username)}
                                                title="Purgar"
                                                className="h-7 w-7 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white border border-red-500/20 flex items-center justify-center transition-all"
                                            >
                                                <Trash2 className="h-3.5 w-3.5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {heroes.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="px-6 py-8 text-center text-white/20 italic">
                                        No hay héroes reclutados en este momento...
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Escudo de Eternia - Gestión de Dispositivos */}
            <DevicesCard
                devices={devices}
                loading={loadingDevices}
                onAuthorize={(deviceId) => onAuthorizeDevice?.(deviceId)}
                onDelete={(deviceId) => onDeleteDevice?.(deviceId)}
                onRefresh={onRefreshDevices}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all">
                    <div className="flex items-center gap-4">
                        <div className="bg-green-500/10 p-3 rounded-lg"><CheckCircle2 className="h-5 w-5 text-green-400" /></div>
                        <div>
                            <h4 className="text-sm font-bold text-white">Registro Abierto</h4>
                            <p className="text-[10px] text-white/65">Permitir que nuevos usuarios se unan.</p>
                        </div>
                    </div>
                    <div className="h-4 w-8 bg-brand-primary/30 rounded-full relative shadow-inner cursor-pointer"><div className="absolute right-1 top-1 h-2 w-2 bg-brand-primary rounded-full shadow-[0_0_8px_rgba(14,165,233,0.5)]"></div></div>
                </div>
                <div className="glass border border-white/10 p-5 rounded-2xl flex items-center justify-between group hover:bg-white/5 transition-all opacity-50">
                    <div className="flex items-center gap-4">
                        <div className="bg-red-500/10 p-3 rounded-lg"><Activity className="h-5 w-5 text-red-400" /></div>
                        <div>
                            <h4 className="text-sm font-bold text-white">Vigilancia de Sesión</h4>
                            <p className="text-[10px] text-white/65">Cierre automático por inactividad.</p>
                        </div>
                    </div>
                    <div className="h-4 w-8 bg-white/10 rounded-full relative cursor-not-allowed"><div className="absolute left-1 top-1 h-2 w-2 bg-white/30 rounded-full"></div></div>
                </div>
            </div>
        </motion.div>
    );
}
