/** Fase AAA-4a: helpers puros extraidos de Config.tsx (sin dependencia de estado/props). */

export const getParsedMetrics = (logsText?: string) => {
    if (!logsText) return null;
    const match = logsText.match(/📊 \[Resumen\] Nuevas en Purgatorio: (\d+) \| Precios actualizados: (\d+) \| Sin cambios: (\d+) \| Descartadas: (\d+)/);
    if (match) {
        return {
            newItems: parseInt(match[1]),
            priceUpdates: parseInt(match[2]),
            unchanged: parseInt(match[3]),
            discarded: parseInt(match[4])
        };
    }
    return null;
};

export interface StepperStatus {
    step: number;
    title: string;
    description: string;
    status: 'pending' | 'running' | 'completed' | 'error' | 'warning';
}

export const getStepperStatus = (logsText?: string, statusText?: string): StepperStatus[] => {
    const steps: StepperStatus[] = [
        { step: 1, title: 'Inicialización', description: 'Arranque de sistemas', status: 'pending' },
        { step: 2, title: 'Bypass de WAF', description: 'Validación de CloudFront', status: 'pending' },
        { step: 3, title: 'Extracción', description: 'Raspado de ofertas', status: 'pending' },
        { step: 4, title: 'Ingesta', description: 'Persistencia en BD', status: 'pending' },
    ];

    if (!logsText) return steps;

    const lower = logsText.toLowerCase();

    // --- STEP 1: Inicialización ---
    if (lower.includes('desplegando incursión') || lower.includes('iniciando secuencia') || lower.includes('buscando reliquias')) {
        steps[0].status = 'completed';
        steps[0].description = 'Sistemas listos';
    }

    // --- STEP 2: Bypass de WAF ---
    if (lower.includes('validando estado de conexión') || lower.includes('intentando conexión directa') || lower.includes('ip de origen detectada')) {
        steps[1].status = 'running';
        steps[1].description = 'Verificando firewall';
    }

    if (lower.includes('bloqueada por waf')) {
        if (lower.includes('re-intentando playwright con proxy') || lower.includes('ruteando wallapop api a través de scraperapi')) {
            steps[1].status = 'completed';
            steps[1].description = 'Bypass con Proxy';
        } else {
            steps[1].status = 'error';
            steps[1].description = 'IP bloqueada por WAF';
        }
    } else if (lower.includes('ip de origen detectada') || lower.includes('bypassing probe') || lower.includes('de forma directa')) {
        steps[1].status = 'completed';
        steps[1].description = 'Conexión directa limpia';
    }

    // --- STEP 3: Extracción ---
    if (lower.includes('navegando directamente') || lower.includes('buscando') || lower.includes('iniciando búsqueda') || lower.includes('re-intentando playwright con proxy')) {
        if (steps[1].status !== 'error') {
            steps[2].status = 'running';
            steps[2].description = 'Buscando reliquias';
        }
    }

    if (lower.includes('halladas') || lower.includes('encontrados') || lower.includes('encontradas') || lower.includes('persistiendo')) {
        steps[2].status = 'completed';
        const matchFound = logsText.match(/(?:halladas|encontrados|encontradas) (\d+) reliquias/i) || logsText.match(/encontrados (\d+) objetos/i);
        const count = matchFound ? matchFound[1] : '?';
        steps[2].description = `Encontradas ${count} reliquias`;
    } else if (lower.includes('timeout') || lower.includes('falló la comprobación de red') || lower.includes('error general')) {
        steps[2].status = 'error';
        steps[2].description = 'Error de red / Timeout';
    }

    // --- STEP 4: Ingesta ---
    if (lower.includes('persistiendo')) {
        steps[3].status = 'running';
        steps[3].description = 'Persistiendo ofertas...';
    }

    if (lower.includes('incursión completada con éxito') || lower.includes('incursión completada') || statusText === 'success' || statusText === 'completed') {
        steps[3].status = 'completed';
        steps[3].description = 'BD Purificada con éxito';
        if (steps[2].status === 'running') steps[2].status = 'completed';
    } else if (lower.includes('fallo crítico') || statusText === 'error' || lower.includes('error detectado')) {
        steps[3].status = 'error';
        steps[3].description = 'Fallo de persistencia';
    }

    return steps;
};

export const CHART_COLORS = [
    '#8b5cf6', // Violeta/Esqueleto
    '#06b6d4', // Cian/Tecnológico
    '#f59e0b', // Ámbar/He-Man
    '#10b981', // Esmeralda/Grayskull
    '#ec4899', // Rosa/Eternia
    '#ef4444', // Rojo/Horda
    '#3b82f6', // Azul/Héroe
    '#f97316', // Naranja/Fuego
    '#6366f1', // Índigo/Místico
    '#a855f7'  // Púrpura/Mágico
];
