
import { Globe, Store, Sparkles, Database, Box, ShieldAlert, Settings, LogOut, X } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.webp';
import guardianRoleImg from '../../assets/role-guardian.webp';

import { type Hero } from '../../api/admin';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
    isMobileOpen: boolean;
    onCloseMobile: () => void;
    user: Hero | null;
    onLogout: () => void;
    /** Fase AAA-4.4: precarga el chunk de una pagina al pasar el raton por
     * encima de su enlace, para que la navegacion se sienta instantanea. */
    onPrefetch?: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isMobileOpen, onCloseMobile, user, onLogout, onPrefetch }) => {
    const isAdmin = user?.role === 'admin' || user?.username === 'David';

    const globalItems = [
        { id: 'dashboard', label: 'Orbe de Grayskull', icon: Globe },
    ];

    const originsItems = [
        { id: 'collection', label: 'Mi Fortaleza', icon: Box },
        { id: 'catalog', label: 'Nueva Eternia', icon: Database },
        { id: 'auctions', label: 'Mercader de Eternos', icon: Store },
        ...(isAdmin ? [{ id: 'purgatory', label: 'Purgatorio', icon: ShieldAlert }] : []),
    ];

    const vintageItems = [
        { id: 'fortaleza_vintage', label: 'Mi Fortaleza Vintage', icon: Box },
        { id: 'eternia', label: 'Eternia', icon: Database },
        { id: 'vintage_miscellaneous', label: 'Bazar del Oráculo', icon: Sparkles },
    ];

    // Clases base para el sidebar
    const sidebarClasses = `
        fixed inset-y-0 left-0 z-[100] flex h-full w-72 flex-col border-r border-glass-border
        bg-[#0d0d12]/80 backdrop-blur-xl md:glass
        transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:w-64
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
    `;

    return (
        <>
            {/* Mobile Overlay Backdrop */}
            {isMobileOpen && (
                <div
                    className="fixed inset-0 z-[90] bg-black/60 backdrop-blur-sm md:hidden animate-in fade-in duration-300"
                    onClick={onCloseMobile}
                />
            )}

            <aside className={sidebarClasses}>
                {/* Logo & Close Button */}
                <div className="flex h-16 items-center justify-between border-b border-glass-border px-6">
                    <div className="flex items-center gap-3">
                        <div className={`h-9 w-9 rounded-xl overflow-hidden border bg-black/40 transition-all ${['eternia', 'fortaleza_vintage'].includes(activeTab) ? 'border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.3)]' : 'border-white/20 shadow-[0_0_15px_rgba(14,165,233,0.3)]'}`}>
                            <img
                                src={(user?.role === 'admin' || user?.username === 'David') ? masterRoleImg : guardianRoleImg}
                                alt="Role Logo"
                                className="h-full w-full object-cover"
                            />
                        </div>
                        <div className="flex flex-col">
                            <h1 className="text-sm font-black tracking-tighter text-white leading-none">ORÁCULO</h1>
                            {['eternia', 'fortaleza_vintage'].includes(activeTab) ? (
                                <span className="text-[8px] font-black text-amber-500 uppercase tracking-[0.2em] mt-1 drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]">ETERNIA VINTAGE</span>
                            ) : (
                                <span className="text-[8px] font-black text-brand-primary uppercase tracking-[0.2em] mt-1">NUEVA ETERNIA</span>
                            )}
                        </div>
                    </div>
                    {/* Botón de cierre solo en móvil */}
                    <button
                        onClick={onCloseMobile}
                        className="rounded-lg p-1 text-white/50 hover:bg-white/10 hover:text-white md:hidden"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-5 p-4 pt-6 overflow-y-auto custom-scrollbar">
                    {/* Sección Global */}
                    <div className="space-y-1">
                        {globalItems.map((item) => {
                            const isActive = activeTab === item.id;
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        setActiveTab(item.id);
                                        onCloseMobile();
                                    }}
                                    onMouseEnter={() => onPrefetch?.(item.id)}
                                    className={`flex w-full items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${isActive
                                        ? 'bg-white/10 text-white border border-white/20 shadow-[0_0_15px_rgba(255,255,255,0.05)]'
                                        : 'text-white/50 hover:bg-white/5 hover:text-white'
                                        }`}
                                >
                                    <item.icon className={`h-4.5 w-4.5 ${isActive ? 'animate-pulse' : ''}`} />
                                    {item.label}
                                </button>
                            );
                        })}
                    </div>

                    {/* Sección Nueva Eternia (Origins - Halo Azul) */}
                    <div className="space-y-2">
                        <div className="text-[9px] font-black uppercase tracking-[0.2em] text-brand-primary/50 px-2 flex items-center gap-1.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-pulse"></div>
                            NUEVA ETERNIA
                        </div>
                        <div className="rounded-2xl border border-brand-primary/10 bg-brand-primary/[0.02] p-1.5 space-y-1 shadow-[0_0_15px_rgba(14,165,233,0.01)]">
                            {originsItems.map((item) => {
                                const isActive = activeTab === item.id;
                                return (
                                    <button
                                        key={item.id}
                                        onClick={() => {
                                            setActiveTab(item.id);
                                            onCloseMobile();
                                        }}
                                        onMouseEnter={() => onPrefetch?.(item.id)}
                                        className={`flex w-full items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${isActive
                                            ? 'bg-brand-primary/20 text-brand-primary border border-brand-primary/35 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                                            : 'text-white/50 hover:bg-white/5 hover:text-white'
                                            }`}
                                    >
                                        <item.icon className={`h-4.5 w-4.5 ${isActive ? 'animate-pulse' : ''}`} />
                                        {item.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Sección Eternia Vintage (Vintage - Halo de Oro) */}
                    <div className="space-y-2">
                        <div className="text-[9px] font-black uppercase tracking-[0.2em] text-amber-500/50 px-2 flex items-center gap-1.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse"></div>
                            ETERNIA VINTAGE
                        </div>
                        <div className="rounded-2xl border border-amber-500/10 bg-amber-500/[0.02] p-1.5 space-y-1 shadow-[0_0_15px_rgba(245,158,11,0.01)]">
                            {vintageItems.map((item) => {
                                const isActive = activeTab === item.id;
                                return (
                                    <button
                                        key={item.id}
                                        onClick={() => {
                                            setActiveTab(item.id);
                                            onCloseMobile();
                                        }}
                                        onMouseEnter={() => onPrefetch?.(item.id)}
                                        className={`flex w-full items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${isActive
                                            ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.15)]'
                                            : 'text-white/50 hover:bg-white/5 hover:text-white'
                                            }`}
                                    >
                                        <item.icon className={`h-4.5 w-4.5 ${isActive ? 'animate-pulse' : ''}`} />
                                        {item.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </nav>

                {/* Footer */}
                <div className="border-t border-glass-border p-4 space-y-2 mt-auto">
                    {user && (
                        <button
                            onClick={() => {
                                setActiveTab('settings');
                                onCloseMobile();
                            }}
                            onMouseEnter={() => onPrefetch?.('settings')}
                            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${activeTab === 'settings'
                                ? 'bg-brand-primary/20 text-brand-primary border border-brand-primary/30 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                                : 'text-white/50 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <Settings className={`h-5 w-5 ${activeTab === 'settings' ? 'animate-spin-slow' : ''}`} />
                            Configuración
                        </button>
                    )}
                    <button
                        onClick={onLogout}
                        className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-400/60 hover:bg-red-500/10 hover:text-red-400 transition-all"
                    >
                        <LogOut className="h-5 w-5" />
                        Cerrar Sesión
                    </button>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
