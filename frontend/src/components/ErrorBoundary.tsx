import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
    children?: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) return this.props.fallback;

            return (
                <div className="flex h-[60vh] w-full flex-col items-center justify-center gap-6 p-10 text-center animate-in fade-in duration-500">
                    <div className="relative">
                        <div className="absolute inset-0 bg-red-500/20 blur-3xl rounded-full" />
                        <div className="relative flex h-20 w-20 items-center justify-center rounded-3xl bg-black border border-red-500/50 shadow-2xl">
                            <AlertTriangle className="h-10 w-10 text-red-500 animate-pulse" />
                        </div>
                    </div>

                    <div className="space-y-2 max-w-sm">
                        <h2 className="text-2xl font-black uppercase tracking-tighter text-white">Transgresión Dimensional</h2>
                        <p className="text-xs font-bold uppercase tracking-widest text-white/40 leading-relaxed">
                            El Oráculo ha detectado una anomalía crítica en este sector. La soberanía de los datos ha sido protegida.
                        </p>
                        {this.state.error && (
                            <p className="mt-4 text-[8px] font-mono text-white/20 bg-black/40 p-2 rounded-lg border border-white/5 truncate">
                                {this.state.error.message}
                            </p>
                        )}
                    </div>

                    <button
                        onClick={() => this.setState({ hasError: false })}
                        className="flex items-center gap-2 px-8 py-3 rounded-2xl bg-brand-primary text-black text-[10px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-brand-primary/20"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Reiniciar Sector
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
