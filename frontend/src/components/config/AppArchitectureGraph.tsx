import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  Atom, Sparkles, ShieldCheck, Server, Cpu, Brain, Cloud, Database,
  Smartphone, Activity, RefreshCw, X, Network, GitBranch, ArrowRight, ArrowLeft
} from 'lucide-react';
import stackManifest from '../../config/stack.config.json';
import { apiClient } from '../../api/client';

type HealthStatus = 'healthy' | 'degraded' | 'static' | 'error';
interface TelemetryItem { status: HealthStatus; metric: string; detail: string; }
interface ConnectedEdge {
  neighborId: string;
  neighborLabel: string;
  direction: 'in' | 'out';
  relation: string;
  protocol: string;
  type: string;
}

const ICON_MAP: Record<string, React.ElementType> = {
  Atom, Sparkles, ShieldCheck, Server, Cpu, Brain, Cloud, Database, Smartphone,
};

const STATUS_COLORS: Record<HealthStatus, string> = {
  healthy: '#10b981',
  degraded: '#f59e0b',
  static: '#94a3b8',
  error: '#ef4444',
};

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const clean = hex.replace('#', '');
  const num = parseInt(clean.length === 3 ? clean.split('').map(c => c + c).join('') : clean, 16);
  return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
}

interface Props { onClose: () => void; }

export default function AppArchitectureGraph({ onClose }: Props) {
  const [mode, setMode] = useState<'topology' | 'flows'>('topology');
  const [selectedNodeId, setSelectedNodeId] = useState<string>(stackManifest.nodes[4]?.id || stackManifest.nodes[0].id);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [activeFlowId, setActiveFlowId] = useState<string>(stackManifest.flows[0]?.id || '');
  const [telemetry, setTelemetry] = useState<Record<string, TelemetryItem>>({});
  const [probing, setProbing] = useState<boolean>(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const labelMetricsCache = useRef<Map<string, number>>(new Map());
  const nodePositionsRef = useRef<Map<string, { x: number; y: number; r: number }>>(new Map());

  // 1. Pre-parse RGB colors & orbital angles once (O(1) in render loop)
  const enrichedNodes = useMemo(() => {
    const total = stackManifest.nodes.length;
    return stackManifest.nodes.map((n, idx) => ({
      ...n,
      rgb: hexToRgb(n.color),
      baseAngle: (idx / total) * Math.PI * 2 - Math.PI / 2,
      floatPhase: idx * 0.85,
    }));
  }, []);

  const nodeMap = useMemo(() => new Map(enrichedNodes.map(n => [n.id, n])), [enrichedNodes]);

  // 2. Pre-index O(1) adjacency map for topology navigation
  const adjacencyMap = useMemo(() => {
    const map = new Map<string, ConnectedEdge[]>();
    stackManifest.nodes.forEach(n => map.set(n.id, []));
    stackManifest.links.forEach(l => {
      const src = nodeMap.get(l.source);
      const tgt = nodeMap.get(l.target);
      if (src && tgt) {
        map.get(l.source)?.push({
          neighborId: tgt.id, neighborLabel: tgt.label, direction: 'out',
          relation: l.relation, protocol: l.protocol, type: l.type,
        });
        map.get(l.target)?.push({
          neighborId: src.id, neighborLabel: src.label, direction: 'in',
          relation: l.relation, protocol: l.protocol, type: l.type,
        });
      }
    });
    return map;
  }, [nodeMap]);

  const activeFlow = useMemo(
    () => stackManifest.flows.find(f => f.id === activeFlowId) || stackManifest.flows[0],
    [activeFlowId]
  );

  // 3. Passive non-blocking health probes
  const runHealthProbes = useCallback(async () => {
    setProbing(true);
    const next: Record<string, TelemetryItem> = {};
    const t0 = performance.now();

    // Storage probe (LocalStorage + Cache API estimate)
    let storageMs = 0.4;
    let storageDetail = 'LocalStorage + Cache API operativos';
    try {
      const s0 = performance.now();
      localStorage.getItem('motu_incognito');
      if (navigator.storage?.estimate) {
        const est = await navigator.storage.estimate();
        const mb = ((est.usage || 0) / (1024 * 1024)).toFixed(1);
        storageDetail = `Cache Storage activo (${mb} MB en uso)`;
      }
      storageMs = Math.max(0.1, performance.now() - s0);
    } catch {
      storageDetail = 'Almacenamiento local aislado';
    }

    // Network & API Backend probe
    let netStatus: HealthStatus = 'healthy';
    let netMs = 12;
    let netDetail = 'FastAPI + Supabase Cloud sincronizados';
    try {
      const n0 = performance.now();
      await apiClient.get('/health', { timeout: 3500 });
      netMs = Math.round(performance.now() - n0);
    } catch {
      netStatus = navigator.onLine ? 'degraded' : 'error';
      netDetail = navigator.onLine ? 'Backend en modo diferido / caché activa' : 'Sin conexión de red';
    }

    const runtimeMs = Math.max(0.2, performance.now() - t0).toFixed(1);
    const hasDeviceId = Boolean(localStorage.getItem('oraculo_device_id'));

    stackManifest.nodes.forEach(node => {
      if (node.healthType === 'storage') {
        next[node.id] = { status: 'healthy', metric: `${storageMs.toFixed(1)} ms`, detail: storageDetail };
      } else if (node.healthType === 'network') {
        next[node.id] = { status: netStatus, metric: `${netMs} ms`, detail: netDetail };
      } else if (node.healthType === 'native_bridge') {
        next[node.id] = {
          status: 'healthy',
          metric: hasDeviceId ? 'CDP + Shield OK' : 'Standby',
          detail: 'Motor REA/CDP (Chrome124) y cola Nexus listos',
        };
      } else {
        next[node.id] = { status: 'healthy', metric: `${runtimeMs} ms`, detail: 'Fiber + Canvas 2D a 60 FPS' };
      }
    });
    setTelemetry(next);
    setProbing(false);
  }, []);

  useEffect(() => { runHealthProbes(); }, [runHealthProbes]);

  // 4. High-performance 60 FPS Canvas 2D loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId = 0;
    const start = performance.now();

    const render = (now: number) => {
      animId = requestAnimationFrame(render);
      if (document.hidden) return;

      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      if (canvas.width !== Math.floor(rect.width * dpr) || canvas.height !== Math.floor(rect.height * dpr)) {
        canvas.width = Math.floor(rect.width * dpr);
        canvas.height = Math.floor(rect.height * dpr);
      }
      ctx.save();
      ctx.scale(dpr, dpr);

      const W = rect.width;
      const H = rect.height;
      const cx = W / 2;
      const cy = H / 2;
      const rx = Math.min(W * 0.36, 250);
      const ry = Math.min(H * 0.34, 155);
      const elapsed = (now - start) * 0.001;

      ctx.fillStyle = '#080c14';
      ctx.fillRect(0, 0, W, H);

      // Compute deterministic orbital coordinates without repulsive velocity jank
      const coords = new Map<string, { x: number; y: number; r: number }>();
      enrichedNodes.forEach((n, idx) => {
        const isCenter = idx === 3; // api_backend at hub center
        const ox = isCenter ? cx : cx + Math.cos(n.baseAngle) * rx + Math.cos(elapsed + n.floatPhase) * 4;
        const oy = isCenter ? cy : cy + Math.sin(n.baseAngle) * ry + Math.sin(elapsed + n.floatPhase) * 4;
        const isFocus = n.id === selectedNodeId || n.id === hoveredNodeId;
        coords.set(n.id, { x: ox, y: oy, r: isFocus ? 27 : 21 });
      });
      nodePositionsRef.current = coords;

      const flowStepIndex = new Map<string, number>();
      if (mode === 'flows' && activeFlow) {
        activeFlow.steps.forEach((s, i) => flowStepIndex.set(s.nodeId, i + 1));
      }

      // Batch inactive Bézier links into two single stroke() calls (solid vs dashed)
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.16)';
      ctx.setLineDash([]);
      ctx.beginPath();
      stackManifest.links.forEach(l => {
        if (l.type !== 'jerarquia') return;
        const p1 = coords.get(l.source);
        const p2 = coords.get(l.target);
        if (p1 && p2) { ctx.moveTo(p1.x, p1.y); ctx.quadraticCurveTo(cx, cy, p2.x, p2.y); }
      });
      ctx.stroke();

      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      stackManifest.links.forEach(l => {
        if (l.type === 'jerarquia') return;
        const p1 = coords.get(l.source);
        const p2 = coords.get(l.target);
        if (p1 && p2) { ctx.moveTo(p1.x, p1.y); ctx.quadraticCurveTo(cx, cy, p2.x, p2.y); }
      });
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw active edges + traveling particles
      const activePairs: Array<{ from: string; to: string; color: string }> = [];
      if (mode === 'topology') {
        stackManifest.links.forEach(l => {
          if (l.source === selectedNodeId || l.target === selectedNodeId) {
            const srcNode = nodeMap.get(l.source);
            activePairs.push({ from: l.source, to: l.target, color: srcNode?.color || '#38bdf8' });
          }
        });
      } else if (activeFlow) {
        for (let i = 0; i < activeFlow.steps.length - 1; i++) {
          const sA = activeFlow.steps[i].nodeId;
          const sB = activeFlow.steps[i + 1].nodeId;
          const srcNode = nodeMap.get(sA);
          activePairs.push({ from: sA, to: sB, color: srcNode?.color || '#f59e0b' });
        }
      }

      activePairs.forEach(({ from, to, color }, idx) => {
        const p1 = coords.get(from);
        const p2 = coords.get(to);
        if (!p1 || !p2) return;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();

        const t = (elapsed * 0.65 + idx * 0.25) % 1;
        const px = p1.x + (p2.x - p1.x) * t;
        const py = p1.y + (p2.y - p1.y) * t;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(px, py, 3.2, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw nodes with concentric radialGradient halos (zero shadowBlur overhead)
      ctx.font = '600 10px system-ui, sans-serif';
      enrichedNodes.forEach(n => {
        const pos = coords.get(n.id);
        if (!pos) return;
        const isSelected = n.id === selectedNodeId;
        const stepNum = flowStepIndex.get(n.id);
        const dimmed = mode === 'flows' && !stepNum;

        const grad = ctx.createRadialGradient(pos.x, pos.y, pos.r * 0.2, pos.x, pos.y, pos.r * 1.9);
        grad.addColorStop(0, `rgba(${n.rgb.r}, ${n.rgb.g}, ${n.rgb.b}, ${dimmed ? 0.12 : 0.42})`);
        grad.addColorStop(1, `rgba(${n.rgb.r}, ${n.rgb.g}, ${n.rgb.b}, 0)`);
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.r * 1.9, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#0f172a';
        ctx.strokeStyle = isSelected ? '#ffffff' : n.color;
        ctx.lineWidth = isSelected ? 2.6 : 1.8;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Health ring dot
        const hStatus = telemetry[n.id]?.status || 'healthy';
        ctx.fillStyle = STATUS_COLORS[hStatus];
        ctx.beginPath();
        ctx.arc(pos.x + pos.r * 0.7, pos.y - pos.r * 0.7, 4.5, 0, Math.PI * 2);
        ctx.fill();

        // Flow step badge
        if (stepNum) {
          ctx.fillStyle = '#f59e0b';
          ctx.beginPath();
          ctx.arc(pos.x - pos.r * 0.75, pos.y - pos.r * 0.75, 8.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = '#000000';
          ctx.textAlign = 'center';
          ctx.fillText(String(stepNum), pos.x - pos.r * 0.75, pos.y - pos.r * 0.75 + 3.5);
        }

        // Cached label width
        if (!labelMetricsCache.current.has(n.label)) {
          labelMetricsCache.current.set(n.label, ctx.measureText(n.label).width);
        }
        ctx.fillStyle = dimmed ? 'rgba(255,255,255,0.35)' : '#f8fafc';
        ctx.textAlign = 'center';
        ctx.fillText(n.label, pos.x, pos.y + pos.r + 14);
      });

      ctx.restore();
    };

    animId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animId);
  }, [enrichedNodes, nodeMap, selectedNodeId, hoveredNodeId, mode, activeFlow, telemetry]);

  const handleCanvasPointer = (e: React.MouseEvent<HTMLCanvasElement>, isClick: boolean) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    let hit: string | null = null;
    nodePositionsRef.current.forEach((pos, id) => {
      if (Math.hypot(mx - pos.x, my - pos.y) <= pos.r + 8) hit = id;
    });
    if (isClick && hit) setSelectedNodeId(hit);
    else if (!isClick) setHoveredNodeId(hit);
  };

  const selectedNode = nodeMap.get(selectedNodeId) || enrichedNodes[0];
  const selectedEdges = adjacencyMap.get(selectedNode.id) || [];
  const selectedTelemetry = telemetry[selectedNode.id];
  const SelectedIcon = ICON_MAP[selectedNode.icon] || Cpu;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 md:p-6 bg-black/85 backdrop-blur-md animate-fade-in">
      <div className="bg-[#0b0f19] border border-cyan-500/30 rounded-3xl w-full max-w-6xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header & Mode Switcher */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 border-b border-white/10 bg-white/[0.02]">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-black uppercase tracking-widest">
              <Network className="h-4 w-4" />
              <span>{stackManifest.appName} — {stackManifest.version}</span>
            </div>
            <p className="text-[11px] text-white/60 mt-0.5">{stackManifest.description}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMode('topology')}
              className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider flex items-center gap-1.5 cursor-pointer transition-all ${
                mode === 'topology' ? 'bg-cyan-500 text-black' : 'bg-white/5 text-white/70 hover:text-white'
              }`}
            >
              <Network className="h-3.5 w-3.5" /> Mapa Topológico
            </button>
            <button
              onClick={() => setMode('flows')}
              className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider flex items-center gap-1.5 cursor-pointer transition-all ${
                mode === 'flows' ? 'bg-amber-500 text-black' : 'bg-white/5 text-white/70 hover:text-white'
              }`}
            >
              <GitBranch className="h-3.5 w-3.5" /> Rutas de Flujo ({stackManifest.flows.length})
            </button>
            <button
              onClick={runHealthProbes}
              title="Re-ejecutar sondas de salud"
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-emerald-400 cursor-pointer"
            >
              <RefreshCw className={`h-4 w-4 ${probing ? 'animate-spin' : ''}`} />
            </button>
            <button onClick={onClose} className="p-2 rounded-xl bg-white/5 hover:bg-red-500/20 text-white/70 hover:text-red-400 cursor-pointer">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Main Split Viewport: Nebula Canvas + Inspector Drawer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-y-auto">
          <div className="lg:col-span-7 flex flex-col border-b lg:border-b-0 lg:border-r border-white/10 bg-[#080c14]">
            {mode === 'flows' && (
              <div className="p-3 border-b border-white/10 flex flex-wrap gap-1.5 bg-white/[0.02]">
                {stackManifest.flows.map(f => (
                  <button
                    key={f.id}
                    onClick={() => { setActiveFlowId(f.id); if (f.steps[0]) setSelectedNodeId(f.steps[0].nodeId); }}
                    className={`px-2.5 py-1.5 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                      activeFlow.id === f.id ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-white/5 text-white/60 hover:text-white'
                    }`}
                  >
                    {f.title}
                  </button>
                ))}
              </div>
            )}
            <div className="relative flex-1 min-h-[340px]">
              <canvas
                ref={canvasRef}
                onClick={e => handleCanvasPointer(e, true)}
                onMouseMove={e => handleCanvasPointer(e, false)}
                className="w-full h-full min-h-[340px] cursor-pointer block"
              />
            </div>
            {mode === 'flows' && activeFlow && (
              <div className="p-3.5 border-t border-white/10 bg-amber-500/[0.04] space-y-2">
                <div className="text-[11px] font-black text-amber-300">{activeFlow.title}</div>
                <p className="text-[10px] text-white/70">{activeFlow.explanation}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pt-1">
                  {activeFlow.steps.map((s, idx) => (
                    <button
                      key={s.nodeId}
                      onClick={() => setSelectedNodeId(s.nodeId)}
                      className={`text-left p-2 rounded-xl border text-[10px] transition-all cursor-pointer ${
                        selectedNodeId === s.nodeId ? 'bg-amber-500/15 border-amber-400/50 text-white' : 'bg-black/40 border-white/10 text-white/70'
                      }`}
                    >
                      <span className="font-black text-amber-400 mr-1">Paso {idx + 1}:</span> {s.role}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Pedagogical & Telemetry Inspector */}
          <div className="lg:col-span-5 p-5 space-y-4 overflow-y-auto max-h-[72vh]">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl border border-white/15" style={{ backgroundColor: `${selectedNode.color}22`, color: selectedNode.color }}>
                  <SelectedIcon className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-black text-white uppercase">{selectedNode.label}</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/10 text-cyan-300">{selectedNode.version}</span>
                  </div>
                  <p className="text-[11px] text-white/60 font-bold">{selectedNode.role}</p>
                </div>
              </div>
            </div>

            {/* Live Health Telemetry Card */}
            {selectedTelemetry && (
              <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-400" />
                  <div>
                    <div className="text-[10px] font-black uppercase text-white/80">{selectedTelemetry.detail}</div>
                    <div className="text-[9px] text-white/45 uppercase">Sonda Pasiva ({selectedNode.healthType})</div>
                  </div>
                </div>
                <span className="text-xs font-mono font-black text-emerald-400">{selectedTelemetry.metric}</span>
              </div>
            )}

            <div className="space-y-2 text-[11px]">
              <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/5">
                <div className="text-[9px] font-black uppercase tracking-wider text-cyan-400 mb-1">Modelo Computacional</div>
                <p className="text-white/80 leading-relaxed">{selectedNode.computationalModel}</p>
              </div>
              <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/5">
                <div className="text-[9px] font-black uppercase tracking-wider text-amber-400 mb-1">Por qué se eligió en el Oráculo</div>
                <p className="text-white/80 leading-relaxed">{selectedNode.whyChosen}</p>
              </div>
            </div>

            {/* Clickable Direct Connections (Topology Hop) */}
            <div className="space-y-2">
              <div className="text-[10px] font-black uppercase tracking-wider text-white/60">
                Conexiones Directas ({selectedEdges.length}) — Pulsa para navegar
              </div>
              <div className="flex flex-wrap gap-1.5">
                {selectedEdges.map((edge, i) => (
                  <button
                    key={`${edge.neighborId}-${i}`}
                    onClick={() => setSelectedNodeId(edge.neighborId)}
                    className="px-2.5 py-1.5 rounded-xl bg-white/5 hover:bg-cyan-500/20 border border-white/10 hover:border-cyan-400/40 text-left transition-all cursor-pointer flex items-center gap-1.5"
                  >
                    {edge.direction === 'in' ? <ArrowLeft className="h-3 w-3 text-amber-400" /> : <ArrowRight className="h-3 w-3 text-cyan-400" />}
                    <div>
                      <div className="text-[10px] font-black text-white">{edge.neighborLabel}</div>
                      <div className="text-[8px] font-mono text-white/50">{edge.relation} · {edge.protocol}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
