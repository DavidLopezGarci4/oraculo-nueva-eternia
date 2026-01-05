
import { Search, Bell } from 'lucide-react';

const Navbar: React.FC = () => {
    return (
        <nav className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-glass-border glass px-6 backdrop-blur-md">
            <div className="flex items-center gap-4 flex-1">
                <div className="relative w-full max-w-md">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <input
                        type="text"
                        placeholder="Buscar figuras por nombre o ID..."
                        className="w-full rounded-full bg-white/5 py-2 pl-10 pr-4 text-sm text-white border border-white/10 focus:border-brand-primary outline-none transition-all"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative p-2 text-white/60 hover:text-white transition-colors">
                    <Bell className="h-5 w-5" />
                    <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand-primary"></span>
                </button>
                <div className="flex items-center gap-3 border-l border-white/10 pl-6 cursor-pointer group">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-brand-primary to-brand-secondary text-xs font-bold text-white shadow-lg">
                        AD
                    </div>
                    <span className="text-sm font-medium text-white/80 group-hover:text-white transition-colors">Admin</span>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
