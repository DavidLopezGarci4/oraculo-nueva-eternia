import { useState, useEffect, useRef } from 'react';
import { Search, Menu, Repeat, Eye, EyeOff, Volume2, VolumeX } from 'lucide-react';
import masterRoleImg from '../../assets/role-master.webp';
import guardianRoleImg from '../../assets/role-guardian.webp';

import { type Hero } from '../../api/admin';

interface NavbarProps {
    onMenuClick: () => void;
    showSearch?: boolean;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
    isSovereign?: boolean; // Added
    user: Hero | null; // Kept
    onIdentityChange?: () => void; // Changed to optional
    isIncognito?: boolean;
    onToggleIncognito?: () => void;
}

const Navbar = ({ onMenuClick, showSearch = true, searchValue = "", onSearchChange, user, isSovereign = false, onIdentityChange, isIncognito = false, onToggleIncognito }: NavbarProps) => {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    useEffect(() => {
        audioRef.current = new Audio('/theme.mp3');
        audioRef.current.loop = true;

        const savedPlayState = localStorage.getItem('theme_music_playing') === 'true';
        if (savedPlayState) {
            audioRef.current.play().then(() => {
                setIsPlaying(true);
            }).catch(() => {
                setIsPlaying(false);
            });
        }

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
        };
    }, []);

    const toggleMusic = () => {
        if (!audioRef.current) return;
        if (isPlaying) {
            audioRef.current.pause();
            setIsPlaying(false);
            localStorage.setItem('theme_music_playing', 'false');
        } else {
            audioRef.current.play().then(() => {
                setIsPlaying(true);
                localStorage.setItem('theme_music_playing', 'true');
            }).catch(err => {
                console.error("Audio playback failed:", err);
            });
        }
    };
    return (
        <nav className="sticky top-0 z-10 flex flex-col md:flex-row items-center justify-between border-b border-glass-border glass px-4 py-3 md:h-16 md:py-0 md:px-6 backdrop-blur-md gap-3 md:gap-4">
            {/* Mobile Top Row: Menu & User Profile */}
            <div className="flex w-full items-center justify-between md:w-auto md:shrink-0">
                <div className="flex items-center">
                    <button
                        onClick={onMenuClick}
                        className="p-2 -ml-2 text-white/60 hover:text-white md:hidden"
                    >
                        <Menu className="h-6 w-6" />
                    </button>
                </div>

                <div className="flex items-center gap-2 md:gap-6 shrink-0 md:ml-auto">
                    {/* Identidad del Héroe */}
                    <div className="flex items-center gap-2 md:gap-3 border-l border-white/10 pl-3 md:pl-6 group py-1 px-2 rounded-xl transition-all">
                        <div className="relative flex h-8 w-8 md:h-9 md:w-9 items-center justify-center rounded-full overflow-hidden border border-white/20 shadow-lg bg-black/40">
                            <img
                                src={user?.role === 'admin' ? masterRoleImg : guardianRoleImg}
                                alt="Hero"
                                className="h-full w-full object-cover"
                            />
                            <div className="absolute inset-0 flex items-center justify-center bg-black/20 text-[10px] font-black text-white pointer-events-none">
                                {user?.username?.slice(0, 2).toUpperCase()}
                            </div>
                        </div>
                        <div className="flex flex-col items-start pr-1 md:pr-2">
                            <span className="text-xs md:text-sm font-black text-white leading-none tracking-tight">
                                {user?.username || 'Cargando...'}
                            </span>
                            <span className="text-[8px] md:text-[9px] font-bold text-white/30 uppercase tracking-widest mt-0.5">
                                {user?.role === 'admin' ? 'Arquitecto' : 'Guardián'}
                            </span>
                        </div>

                        {/* Botón de Cambio Rápido */}
                        {(user?.id === 1 || isSovereign) && (
                            <button
                                onClick={() => {
                                    if (onIdentityChange) onIdentityChange();
                                }}
                                className="ml-1 p-1 md:p-2 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white transition-all border border-brand-primary/20"
                                title="Alternar Identidad (Admin/David)"
                            >
                                <Repeat className="h-4 w-4" />
                            </button>
                        )}

                        {/* Botón de Modo Incógnito */}
                        {onToggleIncognito && (
                            <button
                                onClick={onToggleIncognito}
                                className={`ml-1.5 p-1 md:p-2 rounded-lg transition-all border ${isIncognito ? 'bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500 hover:text-white' : 'bg-white/5 text-white/60 border-white/10 hover:bg-white/10 hover:text-white'}`}
                                title={isIncognito ? "Desactivar Modo Incógnito (Esc dual / Ctrl+I)" : "Activar Modo Incógnito (Esc dual / Ctrl+I)"}
                            >
                                {isIncognito ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                        )}

                        {/* Botón de Música */}
                        <button
                            onClick={toggleMusic}
                            className={`ml-1.5 p-1 md:p-2 rounded-lg transition-all border ${isPlaying ? 'bg-brand-primary/15 text-brand-primary border-brand-primary/30 hover:bg-brand-primary hover:text-white' : 'bg-white/5 text-white/60 border-white/10 hover:bg-white/10 hover:text-white'}`}
                            title={isPlaying ? "Silenciar Música" : "Reproducir Música"}
                        >
                            {isPlaying ? <Volume2 className="h-4 w-4 animate-pulse text-brand-primary group-hover:text-white" /> : <VolumeX className="h-4 w-4" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Middle/Bottom Row: Search Bar */}
            {showSearch && (
                <div className="flex w-full items-center justify-center md:flex-1 md:max-w-xl md:mx-auto">
                    <div className="relative w-full animate-in fade-in slide-in-from-left-4 duration-500">
                        <Search className="absolute left-3 top-3 h-4 w-4 text-white/40" />
                        <input
                            type="text"
                            placeholder="Buscar figuras (nombre, EAN, ID)..."
                            value={searchValue}
                            onChange={(e) => onSearchChange?.(e.target.value)}
                            className="w-full rounded-2xl bg-white/5 py-2.5 pl-9 pr-4 text-sm font-bold text-white border border-white/10 focus:border-brand-primary outline-none transition-all placeholder:text-white/20"
                        />
                    </div>
                </div>
            )}

            {/* Empty space for md screens to maintain balance if search is missing/to balance the left side */}
            <div className="hidden md:block md:w-[200px]"></div>
        </nav>
    );
};

export default Navbar;
