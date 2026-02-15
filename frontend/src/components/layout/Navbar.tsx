import { Search, Bell, Menu } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.png';
import guardianRoleImg from '../../assets/role-guardian.png';

import { type Hero } from '../../api/admin';

interface NavbarProps {
    onMenuClick: () => void;
    showSearch?: boolean;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
    user: Hero | null;
    onIdentityChange: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuClick, showSearch = true, searchValue = "", onSearchChange, user, onIdentityChange }) => {
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
                <button className="relative p-2 text-white/60 hover:text-white transition-colors">
                    <Bell className="h-5 w-5" />
                    <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand-primary"></span>
                </button>

                {/* Selector de Héroes (Solo para Admin ID 1) */}
                {user?.id === 1 && (
                    <button
                        onClick={() => {
                            const currentUser = localStorage.getItem('active_user_id') || '1';
                            const nextUser = currentUser === '1' ? '2' : '1';
                            localStorage.setItem('active_user_id', nextUser);
                            onIdentityChange(); // Trigger re-fetch in App.tsx
                        }}
                        className="flex items-center gap-3 border-l border-white/10 pl-3 md:pl-6 cursor-pointer group hover:bg-white/5 py-1 px-2 rounded-xl transition-all outline-none focus:ring-1 focus:ring-brand-primary/50"
                        title="Cambiar de Héroe"
                    >
                        <div className="relative flex h-9 w-9 items-center justify-center rounded-full overflow-hidden border border-white/20 shadow-lg group-hover:scale-110 transition-transform bg-black/40">
                            <img
                                src={user?.role === 'admin' ? masterRoleImg : guardianRoleImg}
                                alt="Hero"
                                className="h-full w-full object-cover"
                            />
                            <div className="absolute inset-0 flex items-center justify-center bg-black/20 text-[10px] font-black text-white pointer-events-none">
                                {user?.username?.slice(0, 2).toUpperCase()}
                            </div>
                        </div>
                        <div className="hidden md:flex flex-col items-start">
                            <span className="text-sm font-medium text-white/80 group-hover:text-white transition-colors leading-none">
                                {user?.username}
                            </span>
                            <span className="text-[10px] text-white/40 group-hover:text-brand-primary transition-colors">
                                Cambiar Heroe
                            </span>
                        </div>
                    </button>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
