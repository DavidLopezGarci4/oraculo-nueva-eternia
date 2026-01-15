
import React from 'react';
import { LayoutDashboard, Database, Box, ShieldAlert, Settings, LogOut, X } from 'lucide-react';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
    isMobileOpen: boolean;
    onCloseMobile: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isMobileOpen, onCloseMobile }) => {
    const isAdmin = localStorage.getItem('active_user_id') === '1';

    const menuItems = [
        { id: 'dashboard', label: 'Tablero', icon: LayoutDashboard },
        { id: 'catalog', label: 'Eternia', icon: Database },
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
                        <div className="h-8 w-8 rounded-lg bg-brand-primary shadow-[0_0_15px_rgba(14,165,233,0.5)]"></div>
                        <h1 className="text-xl font-bold tracking-tight text-white">ORÁCULO</h1>
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
