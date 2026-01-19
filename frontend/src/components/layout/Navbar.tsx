import { Search, Bell, Menu } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.png';
import guardianRoleImg from '../../assets/role-guardian.png';

interface NavbarProps {
    onMenuClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
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
                <div className="relative w-full max-w-md">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/40" />
                    <input
                        type="text"
                        placeholder="Buscar figuras..."
                        className="w-full rounded-2xl bg-white/5 py-2 pl-9 pr-4 text-sm text-white border border-white/10 focus:border-brand-primary outline-none transition-all placeholder:text-white/20"
                    />
                </div>
            </div>

            <div className="flex items-center gap-2 md:gap-6 shrink-0">
                <button className="relative p-2 text-white/60 hover:text-white transition-colors">
                    <Bell className="h-5 w-5" />
                    <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand-primary"></span>
                </button>

                {/* Selector de Héroes */}
                <div
                    onClick={() => {
                        const currentUser = localStorage.getItem('active_user_id') || '1';
                        const nextUser = currentUser === '1' ? '2' : '1';
                        localStorage.setItem('active_user_id', nextUser);
                        window.location.reload(); // Recarga simple para propagar el cambio de identidad
                    }}
                    className="flex items-center gap-3 border-l border-white/10 pl-3 md:pl-6 cursor-pointer group hover:bg-white/5 py-1 px-2 rounded-xl transition-all"
                >
                    <div className="relative flex h-9 w-9 items-center justify-center rounded-full overflow-hidden border border-white/20 shadow-lg group-hover:scale-110 transition-transform bg-black/40">
                        <img
                            src={localStorage.getItem('active_user_id') === '2' ? guardianRoleImg : masterRoleImg}
                            alt="Hero"
                            className="h-full w-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20 text-[10px] font-black text-white pointer-events-none">
                            {localStorage.getItem('active_user_id') === '2' ? 'DA' : 'AD'}
                        </div>
                    </div>
                    <div className="hidden md:flex flex-col">
                        <span className="text-sm font-medium text-white/80 group-hover:text-white transition-colors leading-none">
                            {localStorage.getItem('active_user_id') === '2' ? 'David' : 'Admin'}
                        </span>
                        <span className="text-[10px] text-white/40 group-hover:text-brand-primary transition-colors">
                            Cambiar Heroe
                        </span>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
