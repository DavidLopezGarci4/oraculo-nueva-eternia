
import { LayoutDashboard, Database, Box, ShieldAlert, Settings, LogOut, X, Gavel, Radar } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.png';
import guardianRoleImg from '../../assets/role-guardian.png';

import { type Hero } from '../../api/admin';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
    isMobileOpen: boolean;
    onCloseMobile: () => void;
    user: Hero | null;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isMobileOpen, onCloseMobile, user }) => {
    const isAdmin = user?.role === 'admin';

    const menuItems = [
        { id: 'dashboard', label: 'Tablero', icon: LayoutDashboard },
        { id: 'catalog', label: 'Nueva Eternia', icon: Database },
        { id: 'auctions', label: 'El Pabellón', icon: Gavel },
        { id: 'radar', label: 'Radar P2P', icon: Radar },
        { id: 'collection', label: 'Mi Fortaleza', icon: Box },
        ...(isAdmin ? [{ id: 'purgatory', label: 'Purgatorio', icon: ShieldAlert }] : []),
    ];

    // Clases base para el sidebar
    const sidebarClasses = `
        fixed inset-y-0 left-0 z-50 flex h-full w-72 flex-col border-r border-glass-border glass
        transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:w-64
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
    `;

    return (
        <>
            {/* Mobile Overlay Backdrop */}
            {isMobileOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden animate-in fade-in duration-300"
                    onClick={onCloseMobile}
                />
            )}

            <aside className={sidebarClasses}>
                {/* Logo & Close Button */}
                <div className="flex h-16 items-center justify-between border-b border-glass-border px-6">
                    <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-xl overflow-hidden border border-white/20 shadow-[0_0_15px_rgba(14,165,233,0.3)] bg-black/40">
                            <img
                                src={user?.role === 'admin' ? masterRoleImg : guardianRoleImg}
                                alt="Role Logo"
                                className="h-full w-full object-cover"
                            />
                        </div>
                        <div className="flex flex-col">
                            <h1 className="text-sm font-black tracking-tighter text-white leading-none">ORÁCULO</h1>
                            <span className="text-[8px] font-black text-brand-primary uppercase tracking-[0.2em] mt-1">NUEVA ETERNIA</span>
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
                <nav className="flex-1 space-y-2 p-4 pt-8 overflow-y-auto">
                    {menuItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => {
                                setActiveTab(item.id);
                                onCloseMobile(); // Cerrar drawer al navegar en móvil
                            }}
                            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${activeTab === item.id
                                ? 'bg-brand-primary/20 text-brand-primary border border-brand-primary/30 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                                : 'text-white/50 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <item.icon className={`h-5 w-5 ${activeTab === item.id ? 'animate-pulse' : ''}`} />
                            {item.label}
                        </button>
                    ))}
                </nav>

                {/* Footer */}
                <div className="border-t border-glass-border p-4 space-y-2 mt-auto">
                    {isAdmin && (
                        <button
                            onClick={() => {
                                setActiveTab('settings');
                                onCloseMobile();
                            }}
                            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${activeTab === 'settings'
                                ? 'bg-brand-primary/20 text-brand-primary border border-brand-primary/30 shadow-[0_0_15px_rgba(14,165,233,0.1)]'
                                : 'text-white/50 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <Settings className={`h-5 w-5 ${activeTab === 'settings' ? 'animate-spin-slow' : ''}`} />
                            Configuración
                        </button>
                    )}
                    <button className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-400/60 hover:bg-red-500/10 hover:text-red-400 transition-all">
                        <LogOut className="h-5 w-5" />
                        Cerrar Sesión
                    </button>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
