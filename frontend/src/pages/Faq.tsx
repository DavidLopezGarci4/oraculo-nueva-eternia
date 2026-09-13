import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    HelpCircle,
    ChevronDown,
    Box,
    Database,
    Bell,
    Flame,
    ShieldAlert,
    ShieldCheck,
    X,
} from 'lucide-react';
import { FAQ_ITEMS, FAQ_CATEGORIES } from '../data/faqData';

const CATEGORY_ICONS: Record<string, React.ElementType> = {
    HelpCircle,
    Box,
    Database,
    Bell,
    Flame,
    ShieldAlert,
    ShieldCheck,
};

const Faq: React.FC = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [expandedId, setExpandedId] = useState<string | null>(null);

    const toggleAccordion = (id: string) => {
        setExpandedId(prev => (prev === id ? null : id));
    };

    const filteredItems = useMemo(() => {
        const query = searchQuery.toLowerCase().trim();
        return FAQ_ITEMS.filter(item => {
            const matchesCat = selectedCategory === 'all' || item.category === selectedCategory;
            if (!matchesCat) return false;

            if (!query) return true;

            const inQuestion = item.question.toLowerCase().includes(query);
            const inTags = item.tags.some(t => t.toLowerCase().includes(query));
            const inPoints = item.points.some(
                p => p.label.toLowerCase().includes(query) || p.text.toLowerCase().includes(query)
            );

            return inQuestion || inTags || inPoints;
        });
    }, [searchQuery, selectedCategory]);

    return (
        <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl mx-auto pb-12">
            {/* Header Hero */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/10 bg-black/30 p-6 md:p-8 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
                <div className="absolute -left-20 -bottom-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-3xl pointer-events-none" />

                <div className="relative z-10 space-y-3">
                    <div className="flex items-center gap-2 text-cyan-400">
                        <HelpCircle className="h-5 w-5 md:h-6 md:w-6" />
                        <span className="text-xs md:text-sm font-black uppercase tracking-[0.25em]">
                            Centro de Conocimiento
                        </span>
                    </div>

                    <h1 className="text-xl md:text-3xl font-black uppercase tracking-wider text-white">
                        Guía de Uso & <span className="text-brand-primary">Preguntas Frecuentes</span>
                    </h1>

                    <p className="max-w-2xl text-xs md:text-sm text-white/60 leading-relaxed">
                        Encuentra respuestas rápidas y concisas sobre todas las herramientas, motores de búsqueda,
                        notificaciones de Telegram y configuraciones del Oráculo de Nueva Eternia.
                    </p>

                    {/* Buscador Rápido */}
                    <div className="pt-2">
                        <div className="relative flex items-center max-w-xl">
                            <Search className="absolute left-4 h-4 w-4 text-white/40 pointer-events-none" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Buscar duda (ej. Telegram, ID, Vinted, Landed, Incógnito)..."
                                className="w-full h-11 pl-11 pr-10 rounded-xl bg-white/[0.04] border border-white/10 text-xs md:text-sm text-white placeholder-white/40 focus:outline-none focus:border-cyan-400/50 focus:bg-white/[0.07] transition-all"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setSearchQuery('')}
                                    className="absolute right-3 p-1 text-white/40 hover:text-white transition-colors"
                                    title="Limpiar búsqueda"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Chips de Categorías */}
            <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-white/[0.02] border border-white/5 backdrop-blur-md">
                {FAQ_CATEGORIES.map(cat => {
                    const IconComponent = CATEGORY_ICONS[cat.iconName] || HelpCircle;
                    const isActive = selectedCategory === cat.id;
                    return (
                        <button
                            key={cat.id}
                            onClick={() => setSelectedCategory(cat.id)}
                            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-[10px] md:text-xs font-black uppercase tracking-wider transition-all cursor-pointer ${
                                isActive
                                    ? 'bg-brand-primary text-white border border-cyan-300/40 shadow-[0_0_12px_rgba(14,165,233,0.3)]'
                                    : 'text-white/50 bg-white/[0.02] hover:bg-white/[0.06] hover:text-white border border-transparent'
                            }`}
                        >
                            <IconComponent className="h-3.5 w-3.5 shrink-0" />
                            <span>{cat.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Contador de Resultados */}
            <div className="flex items-center justify-between px-2 text-xs font-bold text-white/40 uppercase tracking-widest">
                <span>
                    {filteredItems.length} {filteredItems.length === 1 ? 'pregunta encontrada' : 'preguntas encontradas'}
                </span>
                {searchQuery && (
                    <span className="text-cyan-400 lowercase">
                        filtrando por &ldquo;{searchQuery}&rdquo;
                    </span>
                )}
            </div>

            {/* Listado de Acordeones */}
            <div className="space-y-3">
                {filteredItems.length === 0 ? (
                    <div className="p-12 text-center rounded-2xl border border-white/5 bg-black/20 backdrop-blur-md space-y-3">
                        <HelpCircle className="h-8 w-8 text-white/20 mx-auto" />
                        <p className="text-sm font-bold text-white/50 uppercase tracking-wider">
                            No se encontraron respuestas para tu búsqueda
                        </p>
                        <p className="text-xs text-white/30 max-w-md mx-auto">
                            Prueba con otros términos como &ldquo;Telegram&rdquo;, &ldquo;ID&rdquo;, &ldquo;Excel&rdquo; o selecciona otra categoría.
                        </p>
                        <button
                            onClick={() => {
                                setSearchQuery('');
                                setSelectedCategory('all');
                            }}
                            className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold uppercase tracking-wider transition-all"
                        >
                            Ver todas las preguntas
                        </button>
                    </div>
                ) : (
                    filteredItems.map(item => {
                        const isExpanded = expandedId === item.id;
                        return (
                            <div
                                key={item.id}
                                className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
                                    isExpanded
                                        ? 'border-cyan-400/40 bg-black/40 shadow-[0_0_20px_rgba(14,165,233,0.15)]'
                                        : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/10'
                                }`}
                            >
                                <button
                                    onClick={() => toggleAccordion(item.id)}
                                    className="w-full p-4 md:p-5 flex items-center justify-between text-left gap-4 cursor-pointer"
                                >
                                    <div className="flex items-center gap-3">
                                        <div
                                            className={`h-2 w-2 rounded-full shrink-0 transition-colors ${
                                                isExpanded ? 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]' : 'bg-white/20'
                                            }`}
                                        />
                                        <h3 className="text-xs md:text-sm font-black text-white tracking-wide">
                                            {item.question}
                                        </h3>
                                    </div>
                                    <ChevronDown
                                        className={`h-4 w-4 text-white/50 shrink-0 transition-transform duration-300 ${
                                            isExpanded ? 'rotate-180 text-cyan-400' : ''
                                        }`}
                                    />
                                </button>

                                <AnimatePresence>
                                    {isExpanded && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{ duration: 0.25, ease: 'easeInOut' }}
                                            className="overflow-hidden"
                                        >
                                            <div className="px-5 pb-5 pt-1 border-t border-white/5 space-y-2.5">
                                                {item.points.map((pt, idx) => (
                                                    <div key={idx} className="flex items-start gap-2.5 text-xs text-white/80">
                                                        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400/60 mt-1.5 shrink-0" />
                                                        <p className="leading-relaxed">
                                                            <strong className="text-cyan-300 font-bold tracking-wide mr-1.5">
                                                                {pt.label}:
                                                            </strong>
                                                            <span>{pt.text}</span>
                                                        </p>
                                                    </div>
                                                ))}

                                                {/* Tags */}
                                                <div className="flex flex-wrap items-center gap-1.5 pt-3">
                                                    {item.tags.map(tag => (
                                                        <span
                                                            key={tag}
                                                            className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-md bg-white/[0.04] text-white/40 border border-white/5"
                                                        >
                                                            #{tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Footer Help Note */}
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
                <div className="flex items-center gap-2 text-white/50 text-xs font-bold">
                    <HelpCircle className="h-4 w-4 text-cyan-400 shrink-0" />
                    <span>¿Necesitas ayuda adicional o soporte de comandos remotos?</span>
                </div>
                <div className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-3 py-1 rounded-xl border border-cyan-500/20">
                    Escribe <b>/help</b> en Telegram
                </div>
            </div>
        </div>
    );
};

export default Faq;
