import { Zap } from 'lucide-react';
import PowerSwordLoader from '../ui/PowerSwordLoader';
import type { SwordCoords } from './VintageCalibratorModal';

interface ModernCalibratorModalProps {
    isOpen: boolean;
    coords: SwordCoords;
    onChange: (coords: SwordCoords) => void;
    onSave: () => void;
    onReset: () => void;
    onClose: () => void;
}

/** Fase AAA-4a: extraido de Config.tsx ("Skeletor Light Ray Calibrator Modal"). */
export default function ModernCalibratorModal({ isOpen, coords, onChange, onSave, onReset, onClose }: ModernCalibratorModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md p-4 flex justify-center items-start animate-in fade-in duration-300 custom-scrollbar">
            <div className="relative w-full max-w-4xl my-8 md:my-12 rounded-[2.5rem] border border-purple-500/30 bg-[#0A0A0B] p-6 md:p-8 flex flex-col gap-6 shadow-[0_0_50px_rgba(168,85,247,0.2)]">
                <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-purple-500/10">
                        <Zap className="h-6 w-6 text-purple-400 animate-pulse" />
                    </div>
                    <div>
                        <h4 className="text-2xl font-black text-white">Calibrador de Pantalla de Carga <span className="text-purple-400">Skeletor</span></h4>
                        <p className="text-[10px] text-white/50 font-bold uppercase tracking-wider">Alinea los rayos de energía de Grayskull sobre el báculo de Skeletor en la pantalla de carga</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center justify-center">
                    {/* Preview Area */}
                    <div className="flex flex-col items-center justify-center gap-4 bg-black/40 border border-white/5 p-6 rounded-3xl">
                        <span className="text-[10px] font-black uppercase tracking-widest text-purple-400/60">Simulador de Pantalla de Carga</span>

                        <div className="relative w-64 h-64 border border-white/10 rounded-2xl overflow-hidden bg-[#050608] flex items-center justify-center shadow-inner">
                            <PowerSwordLoader
                                isVintage={false}
                                isSkeletor={true}
                                disableRandom={true}
                                size={250}
                                skeletorGuardX={coords.gX}
                                skeletorGuardY={coords.gY}
                                skeletorTipX={coords.tX}
                                skeletorTipY={coords.tY}
                                progress={parseFloat(localStorage.getItem('calib_test_progress_modern') || '75')}
                            />

                            {/* Overlay helper lines to visually debug guard & tip points */}
                            <svg viewBox="0 0 250 250" className="absolute inset-0 w-full h-full pointer-events-none">
                                {/* Guard center indicator */}
                                <circle cx={coords.gX} cy={coords.gY} r="4" fill="#A855F7" stroke="white" strokeWidth="1" />
                                <text x={coords.gX + 6} y={coords.gY + 3} fill="#A855F7" fontSize="8" fontWeight="bold">Empuñadura ({coords.gX.toFixed(1)}, {coords.gY.toFixed(1)})</text>

                                {/* Tip indicator */}
                                <circle cx={coords.tX} cy={coords.tY} r="4" fill="#A855F7" stroke="white" strokeWidth="1" />
                                <text x={coords.tX + 6} y={coords.tY + 3} fill="#A855F7" fontSize="8" fontWeight="bold">Punta ({coords.tX.toFixed(1)}, {coords.tY.toFixed(1)})</text>

                                {/* Axis line */}
                                <line x1={coords.gX} y1={coords.gY} x2={coords.tX} y2={coords.tY} stroke="rgba(168,85,247,0.3)" strokeDasharray="3" strokeWidth="1.5" />
                            </svg>
                        </div>

                        <div className="w-full space-y-1">
                            <div className="flex justify-between text-[10px] text-white/50 font-bold">
                                <span>PROGRESO DE PRUEBA</span>
                                <span className="text-purple-400 font-mono">{localStorage.getItem('calib_test_progress_modern') || '75'}%</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={localStorage.getItem('calib_test_progress_modern') || '75'}
                                onChange={(e) => {
                                    localStorage.setItem('calib_test_progress_modern', e.target.value);
                                    // Trigger state update to re-render preview
                                    onChange({ ...coords });
                                }}
                                className="w-full accent-purple-500"
                            />
                        </div>
                    </div>

                    {/* Controls Area */}
                    <div className="space-y-6">
                        <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                            <div className="flex items-center gap-2 text-purple-400 font-bold text-xs uppercase tracking-widest">
                                <div className="h-2 w-2 rounded-full bg-purple-400" />
                                Punto de Empuñadura (X, Y)
                            </div>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                        <span>Horizontal (X)</span>
                                        <span className="text-white font-mono">{coords.gX}px</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="250"
                                        step="0.5"
                                        value={coords.gX}
                                        onChange={(e) => onChange({ ...coords, gX: parseFloat(e.target.value) })}
                                        className="w-full accent-purple-500"
                                    />
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                        <span>Vertical (Y)</span>
                                        <span className="text-white font-mono">{coords.gY}px</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="250"
                                        step="0.5"
                                        value={coords.gY}
                                        onChange={(e) => onChange({ ...coords, gY: parseFloat(e.target.value) })}
                                        className="w-full accent-purple-500"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4 bg-white/[0.02] border border-white/5 p-4 rounded-2xl">
                            <div className="flex items-center gap-2 text-purple-400 font-bold text-xs uppercase tracking-widest">
                                <div className="h-2 w-2 rounded-full bg-purple-400" />
                                Punto de la Punta (X, Y)
                            </div>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                        <span>Horizontal (X)</span>
                                        <span className="text-white font-mono">{coords.tX}px</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="250"
                                        step="0.5"
                                        value={coords.tX}
                                        onChange={(e) => onChange({ ...coords, tX: parseFloat(e.target.value) })}
                                        className="w-full accent-purple-500"
                                    />
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] text-white/50 font-bold mb-1">
                                        <span>Vertical (Y)</span>
                                        <span className="text-white font-mono">{coords.tY}px</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="250"
                                        step="0.5"
                                        value={coords.tY}
                                        onChange={(e) => onChange({ ...coords, tY: parseFloat(e.target.value) })}
                                        className="w-full accent-purple-500"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 pt-2">
                            <button
                                onClick={onReset}
                                className="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-white/70 hover:text-white hover:bg-white/5 font-black text-[10px] uppercase tracking-widest transition-all"
                            >
                                Restablecer
                            </button>
                            <button
                                onClick={onSave}
                                className="flex-1 px-4 py-2.5 rounded-xl bg-purple-500 hover:bg-purple-600 text-black font-black text-[10px] uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(168,85,247,0.2)]"
                            >
                                Guardar en Eternia
                            </button>
                            <button
                                onClick={onClose}
                                className="px-4 py-2.5 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 text-white font-black text-[10px] uppercase tracking-widest transition-all"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
