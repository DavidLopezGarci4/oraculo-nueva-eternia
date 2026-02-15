import React, { useState } from 'react';
import { Shield, Lock, ArrowRight, Loader2, Zap } from 'lucide-react';
import axios from 'axios';

interface MasterLoginProps {
    onSuccess: (isSovereign: boolean) => void;
}

const MasterLogin: React.FC<MasterLoginProps> = ({ onSuccess }) => {
    const [apiKey, setApiKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('/api/auth/login', { api_key: apiKey });
            if (response.data.is_sovereign) {
                // Guardar en localStorage para persistencia
                localStorage.setItem('master_key', apiKey);
                localStorage.setItem('is_sovereign', 'true');
                onSuccess(true);
            }
        } catch (err: any) {
            console.error("Login failed", err);
            setError('Llave Maestra incorrecta. Acceso Denegado.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black p-4">
            {/* Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-brand-primary/10 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
            </div>

            <div className="relative w-full max-w-md animate-in fade-in zoom-in-95 duration-700">
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
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/40 ml-1">
                                Llave Maestra (API KEY)
                            </label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/20 group-focus-within:text-brand-primary transition-colors" />
                                <input
                                    type="password"
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="••••••••••••••••"
                                    className="w-full rounded-2xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-white placeholder:text-white/10 outline-none transition-all focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/20"
                                    required
                                    autoFocus
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
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <>
                                        Abrir Oráculo
                                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                                    </>
                                )}
                            </div>
                            <div className="absolute inset-0 z-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </button>
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
            </div>
        </div>
    );
};

export default MasterLogin;
