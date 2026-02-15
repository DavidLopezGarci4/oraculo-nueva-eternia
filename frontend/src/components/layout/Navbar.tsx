import { Search, Bell, Menu, Repeat } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.png';
import guardianRoleImg from '../../assets/role-guardian.png';

import { type Hero } from '../../api/admin';

interface NavbarProps {
    onMenuClick: () => void;
    showSearch?: boolean;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
    notifications?: number; // Added
    isSovereign?: boolean; // Added
    user: Hero | null; // Kept
    onIdentityChange?: () => void; // Changed to optional
}

const Navbar = ({ onMenuClick, showSearch = true, searchValue = "", onSearchChange, user, notifications = 3, isSovereign = false, onIdentityChange }: NavbarProps) => {
    return (
        <nav className="sticky top-0 z-10 flex h-16 items-center border-b border-glass-border glass px-4 md:px-6 backdrop-blur-md gap-4">
            {/* Mobile Menu Button */}
            <button
                onClick={onMenuClick}
                className="p-2 -ml-2 text-white/60 hover:text-white md:hidden"
            >
                <Menu className="h-6 w-6" />
            </button>

            <div className="flex items-center gap-4 flex-1">
                {showSearch && (
                    <div className="relative w-full max-w-md animate-in fade-in slide-in-from-left-4 duration-500">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                        <input
                            type="text"
                            placeholder="Buscar figuras..."
                            value={searchValue}
                            onChange={(e) => onSearchChange?.(e.target.value)}
                            className="w-full rounded-2xl bg-white/5 py-2 pl-9 pr-4 text-sm text-white border border-white/10 focus:border-brand-primary outline-none transition-all placeholder:text-white/20"
                        />
                    </div>
                )}
            </div>

            <div className="flex items-center gap-2 md:gap-6 shrink-0">
                <button className="relative p-2 text-white/60 hover:text-white group">
                    <Bell className="h-5 w-5" />
                    {notifications > 0 && (
                        <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-brand-primary border border-black shadow-[0_0_8px_rgba(14,165,233,0.5)]" title={`${notifications} notificaciones`} />
                    )}
                </button>

                {/* Identidad del Héroe */}
                <div className="flex items-center gap-2 md:gap-3 border-l border-white/10 pl-3 md:pl-6 group py-1 px-2 rounded-xl transition-all">
                    <div className="relative flex h-9 w-9 items-center justify-center rounded-full overflow-hidden border border-white/20 shadow-lg bg-black/40">
                        <img
                            src={user?.role === 'admin' ? masterRoleImg : guardianRoleImg}
                            alt="Hero"
                            className="h-full w-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20 text-[10px] font-black text-white pointer-events-none">
                            {user?.username?.slice(0, 2).toUpperCase()}
                        </div>
                    </div>
                    <div className="flex flex-col items-start pr-2">
                        <span className="text-sm font-black text-white leading-none tracking-tight">
                            {user?.username || 'Cargando...'}
                        </span>
                        <span className="text-[9px] font-bold text-white/30 uppercase tracking-widest mt-0.5">
                            {user?.role === 'admin' ? 'Arquitecto' : 'Guardián'}
                        </span>
                    </div>

                    {/* Botón de Cambio Rápido (Solo para Admin ID 1 o Sesión Soberana) */}
                    {(user?.id === 1 || isSovereign) && (
                        <button
                            onClick={() => {
                                if (onIdentityChange) onIdentityChange();
                            }}
                            className="ml-2 p-2 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white transition-all border border-brand-primary/20"
                            title="Alternar Identidad (Admin/David)"
                        >
                            <Repeat className="h-4 w-4" />
                        </button>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
