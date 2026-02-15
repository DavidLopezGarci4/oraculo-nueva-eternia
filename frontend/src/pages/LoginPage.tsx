import React, { useState } from 'react';
import { User, Lock, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';

interface LoginPageProps {
    onLoginSuccess: (userData: any, isSovereign: boolean) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('/api/auth/login', { email, password });
            if (response.data.status === 'success') {
                const { user, is_sovereign } = response.data;

                // Persistencia local
                localStorage.setItem('active_user_id', user.id.toString());
                localStorage.setItem('is_sovereign', is_sovereign ? 'true' : 'false');
                localStorage.setItem('user_email', email);
                localStorage.setItem('is_logged_in', 'true');

                onLoginSuccess(user, is_sovereign);
            }
        } catch (err: any) {
            console.error("Login failed", err);
            setError(err.response?.data?.detail || 'Error de conexión con el Oráculo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black p-4">
            {/* Ambient Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] right-[-10%] h-[60%] w-[60%] rounded-full bg-brand-primary/5 blur-[150px]" />
                <div className="absolute bottom-[-20%] left-[-10%] h-[60%] w-[60%] rounded-full bg-blue-500/5 blur-[150px]" />
            </div>

            <div className="relative w-full max-w-md animate-in fade-in slide-in-from-bottom-8 duration-1000">
                <div className="relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-white/[0.02] p-8 md:p-12 backdrop-blur-3xl shadow-2xl">
                    {/* Oracle Logo/Header */}
                    <div className="mb-10 flex flex-col items-center text-center">
                        <div className="mb-6 relative">
                            <div className="absolute inset-0 bg-brand-primary/20 blur-2xl rounded-full" />
                            <div className="relative flex h-20 w-20 items-center justify-center rounded-3xl bg-black border border-white/10 shadow-2xl">
                                <Sparkles className="h-10 w-10 text-brand-primary animate-pulse" />
                            </div>
                        </div>
                        <h1 className="text-3xl font-black uppercase tracking-[0.2em] text-white">
                            Nueva <span className="text-brand-primary">Eternia</span>
                        </h1>
                        <p className="mt-2 text-[10px] font-bold uppercase tracking-[0.4em] text-white/30">
                            Identificación de Héroe
                        </p>
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                Correo Electrónico
                            </label>
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="arquitecto@eternia.com"
                                    className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                    required
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                Contraseña
                            </label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••••••"
                                    className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-center text-[10px] font-bold text-red-400 animate-in shake duration-500">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full overflow-hidden rounded-2xl bg-brand-primary py-4 text-[10px] font-black uppercase tracking-[0.2em] text-black transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                        >
                            <div className="relative z-10 flex items-center justify-center gap-2">
                                {loading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <>
                                        Entrar al Oráculo
                                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                                    </>
                                )}
                            </div>
                            <div className="absolute inset-0 z-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </button>
                    </form>

                    <div className="mt-8 text-center">
                        <button className="text-[9px] font-bold text-white/20 hover:text-white/60 transition-colors uppercase tracking-widest">
                            ¿Olvidaste tu llave? Solicita una nueva
                        </button>
                    </div>
                </div>

                <p className="mt-8 text-center text-[8px] font-black uppercase tracking-[0.3em] text-white/10">
                    Propiedad Privada del Gran Arquitecto 🏛️
                </p>
            </div>
        </div>
    );
};

export default LoginPage;
