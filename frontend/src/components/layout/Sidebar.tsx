
import React from 'react';
import { LayoutDashboard, Database, Box, ShieldAlert, Settings, LogOut } from 'lucide-react';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
    const menuItems = [
        { id: 'dashboard', label: 'Tablero', icon: LayoutDashboard },
        { id: 'catalog', label: 'Eternia', icon: Database },
        { id: 'collection', label: 'Mi Fortaleza', icon: Box },
        { id: 'purgatory', label: 'Purgatorio', icon: ShieldAlert },
    ];

    return (
        <aside className="relative flex h-screen w-64 flex-col border-r border-glass-border glass">
            {/* Logo */}
            <div className="flex h-16 items-center border-b border-glass-border px-6">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-brand-primary shadow-[0_0_15px_rgba(14,165,233,0.5)]"></div>
                    <h1 className="text-xl font-bold tracking-tight text-white">ORÁCULO</h1>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-2 p-4 pt-8">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
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
            <div className="border-t border-glass-border p-4 space-y-2">
                <button className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white/50 hover:bg-white/5 hover:text-white transition-all">
                    <Settings className="h-5 w-5" />
                    Ajustes
                </button>
                <button className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-400/60 hover:bg-red-500/10 hover:text-red-400 transition-all">
                    <LogOut className="h-5 w-5" />
                    Cerrar Sesión
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
