import { useState } from 'react';
import { Shield, Lock, ArrowRight, Zap, RefreshCw, User } from 'lucide-react';
import axios from 'axios';
import { setToken } from '../../api/client';

interface MasterLoginProps {
    onSuccess: (isSovereign: boolean) => void;
    onCancel?: () => void;
}

const MasterLogin: React.FC<MasterLoginProps> = ({ onSuccess, onCancel }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Acceso soberano por credenciales reales (email + contraseña de admin).
            // La antigua "llave maestra" (API key) fue retirada por seguridad.
            const response = await axios.post('/api/auth/login', { email, password });
            const { user, access_token } = response.data;
            if (response.data.status === 'success' && user?.role === 'admin') {
                if (access_token) setToken(access_token);
                localStorage.setItem('active_user_id', user.id.toString());
                localStorage.setItem('is_sovereign', 'true');
                localStorage.setItem('is_logged_in', 'true');
                localStorage.setItem('user_email', email);
                onSuccess(true);
            } else {
                setError('Estas credenciales no tienen rango de Arquitecto.');
            }
        } catch (err: any) {
            console.error("Login failed", err);
            const detail = err.response?.data?.detail;
            setError(detail || 'Credenciales incorrectas. Acceso Denegado.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black p-4">
            {/* Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
                <div className="absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
            </div>

            <main className="relative w-full max-w-md animate-in fade-in zoom-in-95 duration-700">
                <div className="relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-white/[0.02] p-8 md:p-12 backdrop-blur-3xl">
                    {/* Header */}
                    <div className="mb-10 flex flex-col items-center text-center">
                        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-primary/10 border border-brand-primary/20 shadow-[0_0_30px_rgba(var(--brand-primary-rgb),0.2)]">
                            <Shield className="h-8 w-8 text-brand-primary" />
                        </div>
                        <h1 className="text-2xl font-black uppercase tracking-[0.3em] text-white">
                            Puerta del <span className="text-brand-primary">Soberano</span>
                        </h1>
                        <p className="mt-2 text-[10px] font-black uppercase tracking-widest text-white/30">
                            Identifíquese, Gran Arquitecto
                        </p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label htmlFor="master-login-email" className="text-[10px] font-black uppercase tracking-widest text-white/40 ml-1">
                                Correo del Arquitecto
                            </label>
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                <input
                                    id="master-login-email"
                                    type="email"
                                    autoComplete="username"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="arquitecto@eternia.com"
                                    className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                    required
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="master-login-password" className="text-[10px] font-black uppercase tracking-widest text-white/40 ml-1">
                                Contraseña Soberana
                            </label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                <input
                                    id="master-login-password"
                                    type="password"
                                    autoComplete="current-password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••••••••••"
                                    className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-center text-xs font-bold text-red-500 animate-in shake duration-500">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full overflow-hidden rounded-2xl bg-brand-primary py-4 text-xs font-black uppercase tracking-widest text-black transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100"
                        >
                            <div className="relative z-10 flex items-center justify-center gap-2">
                                {loading ? (
                                    <RefreshCw className="h-5 w-5 animate-spin mx-auto opacity-70" />
                                ) : (
                                    <>
                                        Abrir Oráculo
                                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                                    </>
                                )}
                            </div>
                            <div className="absolute inset-0 z-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </button>

                        {onCancel && (
                            <button
                                type="button"
                                onClick={onCancel}
                                className="w-full py-2 text-[9px] font-black uppercase tracking-widest text-white/20 hover:text-white/60 transition-colors"
                            >
                                Volver a Sala de Espera
                            </button>
                        )}
                    </form>

                    {/* Footer decoration */}
                    <div className="mt-12 flex items-center justify-center gap-3 opacity-20">
                        <div className="h-px w-8 bg-gradient-to-r from-transparent to-white" />
                        <Zap className="h-3 w-3 text-white" />
                        <div className="h-px w-8 bg-gradient-to-l from-transparent to-white" />
                    </div>
                </div>

                <p className="mt-8 text-center text-[9px] font-black uppercase tracking-[0.2em] text-white/20">
                    Soberanía Digital 3OX &copy; {new Date().getFullYear()}
                </p>
            </main>
        </div>
    );
};

export default MasterLogin;
