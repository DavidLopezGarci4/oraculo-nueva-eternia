import React, { useState } from 'react';
import { User, Lock, ArrowRight, RefreshCw } from 'lucide-react';
import entranceBg from '../assets/Entrance_prod.png';
import axios from 'axios';

interface LoginPageProps {
    onLoginSuccess: (userData: any, isSovereign: boolean) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
    // ... rest of state and handleSubmit logic remains same ...
    const [mode, setMode] = useState<'login' | 'register' | 'forgot' | 'reset'>('login');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [token, setToken] = useState<string | null>(null);

    React.useEffect(() => {
        const urlParams = new URLSearchParams(window.location.hash.split('?')[1]);
        const resetToken = urlParams.get('token');
        if (resetToken) {
            setToken(resetToken);
            setMode('reset');
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');

        try {
            if (mode === 'login') {
                const response = await axios.post('/api/auth/login', { email, password });
                if (response.data.status === 'success') {
                    const { user, is_sovereign } = response.data;
                    localStorage.setItem('active_user_id', user.id.toString());
                    localStorage.setItem('is_sovereign', is_sovereign ? 'true' : 'false');
                    localStorage.setItem('user_email', email);
                    localStorage.setItem('is_logged_in', 'true');
                    onLoginSuccess(user, is_sovereign);
                }
            } else if (mode === 'register') {
                const response = await axios.post('/api/auth/register', {
                    email,
                    username: username || email.split('@')[0],
                    password
                });
                if (response.data.status === 'success') {
                    setSuccessMessage('¡Héroe reclutado! Ahora puedes entrar.');
                    setMode('login');
                }
            } else if (mode === 'forgot') {
                const response = await axios.post('/api/auth/forgot-password', { email });
                if (response.data.status === 'success') {
                    setSuccessMessage(response.data.message);
                }
            } else if (mode === 'reset') {
                if (password !== confirmPassword) {
                    setError('Las contraseñas no coinciden.');
                    setLoading(false);
                    return;
                }
                const response = await axios.post('/api/auth/reset-password', {
                    token,
                    new_password: password
                });
                if (response.data.status === 'success') {
                    setSuccessMessage(response.data.message);
                    setMode('login');
                    window.location.hash = '/';
                }
            }
        } catch (err: any) {
            console.error(`${mode} failed`, err);
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            setError(detail || (status ? `Error ${status} del Oráculo.` : 'Error de conexión con el Oráculo.'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-[#050608]">
            {/* Cinematic Background */}
            <div className="absolute inset-0 overflow-hidden">
                <img
                    src={entranceBg}
                    className="w-full h-full object-cover opacity-90 scale-100 animate-in fade-in duration-1000"
                    alt="Entrance Backdrop"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#050608]/80 via-transparent to-[#050608]/20" />
                <div className="absolute top-[-10%] right-[-5%] h-[50%] w-[50%] rounded-full bg-red-500/5 blur-[120px]" />
                <div className="absolute bottom-[0%] left-[-5%] h-[40%] w-[40%] rounded-full bg-purple-500/5 blur-[120px]" />
            </div>

            <div className="relative w-full max-w-md mt-[22vh] animate-in fade-in slide-in-from-bottom-12 duration-1000">
                {/* The Glass Card Container */}
                <div className="relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-white/[0.03] pt-6 pb-8 px-8 md:pt-10 md:pb-12 md:px-12 backdrop-blur-3xl shadow-2xl">
                    {/* Glass highlight overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent pointer-events-none" />

                    {/* Oracle Logo Removed as per user request (Letters are in the background image) */}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* ... fields ... */}
                        {/* [Existing fields logic is already correct, just keeping the structure] */}
                        {mode === 'register' && (
                            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-500">
                                <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                    Nombre de Héroe
                                </label>
                                <div className="relative group">
                                    <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                    <input
                                        type="text"
                                        name="username"
                                        id="username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="David, Héroe de Eternia..."
                                        className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                        required={mode === 'register'}
                                    />
                                </div>
                            </div>
                        )}

                        {mode !== 'reset' && (
                            <div className="space-y-2">
                                <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                    Correo Electrónico
                                </label>
                                <div className="relative group">
                                    <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                    <input
                                        type="email"
                                        name="email"
                                        id="email"
                                        autoComplete="username"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="arquitecto@eternia.com"
                                        className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                        required
                                        autoFocus={mode === 'login' || mode === 'forgot'}
                                    />
                                </div>
                            </div>
                        )}

                        {mode !== 'forgot' && (
                            <div className="space-y-2">
                                <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                    {mode === 'reset' ? 'Nueva Contraseña' : 'Contraseña'}
                                </label>
                                <div className="relative group">
                                    <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                    <input
                                        type="password"
                                        name="password"
                                        id="password"
                                        autoComplete={mode === 'register' || mode === 'reset' ? "new-password" : "current-password"}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••••••"
                                        className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                        required
                                    />
                                </div>
                            </div>
                        )}

                        {mode === 'reset' && (
                            <div className="space-y-2">
                                <label className="text-[9px] font-black uppercase tracking-widest text-white/40 ml-1">
                                    Confirmar Nueva Contraseña
                                </label>
                                <div className="relative group">
                                    <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="••••••••••••"
                                        className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                        required
                                    />
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-center text-[10px] font-bold text-red-400 animate-in shake duration-500">
                                {error}
                            </div>
                        )}

                        {successMessage && (
                            <div className="rounded-xl border border-green-500/20 bg-green-500/10 p-3 text-center text-[10px] font-bold text-green-400 animate-in fade-in duration-500">
                                {successMessage}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full overflow-hidden rounded-2xl bg-brand-primary py-4 text-[10px] font-black uppercase tracking-[0.2em] text-black transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                        >
                            <div className="relative z-10 flex items-center justify-center gap-2">
                                {loading ? (
                                    <RefreshCw className="h-5 w-5 animate-spin mx-auto opacity-70" />
                                ) : (
                                    <>
                                        {mode === 'login' && 'Entrar al Oráculo'}
                                        {mode === 'register' && 'Unirse a la Resistencia'}
                                        {mode === 'forgot' && 'Enviar Enlace de Recuperación'}
                                        {mode === 'reset' && 'Confirmar Nueva Llave'}
                                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                                    </>
                                )}
                            </div>
                            <div className="absolute inset-0 z-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </button>
                    </form>

                    {/* Mode Switching Links */}
                    <div className="mt-8 flex flex-col items-center gap-4 text-[9px] font-black uppercase tracking-widest">
                        {mode === 'login' ? (
                            <>
                                <button
                                    onClick={() => setMode('register')}
                                    className="text-white/40 hover:text-brand-primary transition-colors"
                                >
                                    ¿Nuevo en la resistencia? <span className="text-white">Regístrate</span>
                                </button>
                                <button
                                    onClick={() => setMode('forgot')}
                                    className="text-white/20 hover:text-white transition-colors"
                                >
                                    He olvidado mi llave de acceso
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setMode('login')}
                                className="flex items-center gap-2 text-white/40 hover:text-brand-primary transition-colors"
                            >
                                <ArrowRight className="h-3 w-3 rotate-180" />
                                Volver al Acceso Principal
                            </button>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default LoginPage;
