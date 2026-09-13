export interface FaqItem {
    id: string;
    question: string;
    category: 'fortaleza' | 'catalogo' | 'telegram' | 'vinted' | 'purgatorio' | 'seguridad';
    points: { label: string; text: string }[];
    tags: string[];
}

export interface FaqCategory {
    id: 'all' | 'fortaleza' | 'catalogo' | 'telegram' | 'vinted' | 'purgatorio' | 'seguridad';
    label: string;
    iconName: string;
}

export const FAQ_CATEGORIES: FaqCategory[] = [
    { id: 'all', label: 'Todas las Dudas', iconName: 'HelpCircle' },
    { id: 'fortaleza', label: 'Mi Fortaleza', iconName: 'Box' },
    { id: 'catalogo', label: 'Catálogo & ID', iconName: 'Database' },
    { id: 'telegram', label: 'Alertas Telegram', iconName: 'Bell' },
    { id: 'vinted', label: 'Vinted & Caza', iconName: 'Flame' },
    { id: 'purgatorio', label: 'Purgatorio', iconName: 'ShieldAlert' },
    { id: 'seguridad', label: 'Seguridad & SSL', iconName: 'ShieldCheck' },
];

export const FAQ_ITEMS: FaqItem[] = [
    // 1. Fortaleza
    {
        id: 'fortaleza-claim',
        category: 'fortaleza',
        question: '¿Cómo aseguro una figura en mi colección o lista de deseos?',
        points: [
            { label: 'Asegurar en la Fortaleza', text: 'Pulsa el botón "En Sanctum" (o "En Fortaleza" en vintage) o el lateral de la tarjeta para confirmar posesión física.' },
            { label: 'Lista de Deseos', text: 'Pulsa el icono de la estrella "Deseo" para seguir la figura en tu radar de compras pendientes.' },
            { label: 'Liberar / Desvincular', text: 'Al pasar el cursor sobre una figura en posesión el botón cambiará a "Liberar", retirándola instantáneamente de tu búnker.' }
        ],
        tags: ['sanctum', 'fortaleza', 'deseos', 'wishlist', 'liberar']
    },
    {
        id: 'fortaleza-incognito',
        category: 'fortaleza',
        question: '¿Qué es el Modo Incógnito y cómo se activa?',
        points: [
            { label: 'Propósito', text: 'Oculta y difumina instantáneamente todos los precios de compra, valoraciones financieras y totales coleccionados.' },
            { label: 'Activación', text: 'Pulsa el icono del ojo en la barra superior (Navbar) de la app en cualquier momento.' },
            { label: 'Protección', text: 'Ideal para capturas de pantalla, streams o para mostrar tu colección sin revelar tu inversión económica.' }
        ],
        tags: ['incógnito', 'privacidad', 'difuminar', 'precios', 'ojo']
    },
    {
        id: 'fortaleza-export',
        category: 'fortaleza',
        question: '¿Cómo puedo exportar mi inventario a Excel o SQLite?',
        points: [
            { label: 'Exportación a Excel', text: 'Pulsa el botón verde "Excel" en la cabecera de Mi Fortaleza para descargar una hoja de cálculo completa con nombres, estados, valoraciones y costes.' },
            { label: 'Bóveda Portátil SQLite', text: 'Pulsa el botón "SQLite" para generar un archivo .db portable estándar de tu inventario.' }
        ],
        tags: ['excel', 'sqlite', 'exportar', 'backup', 'descargar']
    },

    // 2. Catálogo & ID
    {
        id: 'catalogo-search-id',
        category: 'catalogo',
        question: '¿Cómo busco figuras por su identificador numérico (ID)?',
        points: [
            { label: 'Búsqueda por ID', text: 'Escribe el número en el buscador superior (por ejemplo "12033" o "#12033"). El catálogo filtrará al instante a 0ms la figura correspondiente.' },
            { label: 'Búsqueda Combinada', text: 'Puedes buscar también por nombre de personaje ("He-Man", "Skeletor") o por línea ("Origins", "Turtles of Grayskull").' }
        ],
        tags: ['id', 'buscar', 'filtro', 'número', 'identificador']
    },
    {
        id: 'catalogo-sort-controls',
        category: 'catalogo',
        question: '¿Cómo funciona la ordenación simétrica de la barra de controles?',
        points: [
            { label: 'Botón NOM', text: 'Ordena el catálogo alfabéticamente por el nombre canónico de la figura.' },
            { label: 'Botón ID', text: 'Ordena las piezas cronológica y numéricamente por su identificador único de base de datos.' },
            { label: 'Botón OFERTAS', text: 'Prioriza las figuras que cuentan con oportunidades activas o coincidencias en el Purgatorio.' },
            { label: 'Botón SET', text: 'Ordena según el porcentaje de completitud de la sub-categoría a la que pertenece la pieza.' },
            { label: 'Alternar Sentido', text: 'Pulsa la flecha para conmutar entre orden ascendente (↑) y descendente (↓).' }
        ],
        tags: ['orden', 'nom', 'id', 'ofertas', 'set', 'simétrico', 'clasificar']
    },
    {
        id: 'catalogo-cronos',
        category: 'catalogo',
        question: '¿Cómo utilizo el Comparador Cronos de precios?',
        points: [
            { label: 'Acceso', text: 'En la vista del Catálogo Maestro, selecciona la pestaña "Cronos" en la barra de sub-navegación.' },
            { label: 'Comparación Dual', text: 'Selecciona dos figuras para comparar en un gráfico interactivo sus curvas históricas y diferenciales de mercado.' },
            { label: 'Filtro de Tiendas', text: 'Activa o silencia tiendas específicas (Wallapop, Vinted, Smyths, eBay) para aislar datos.' }
        ],
        tags: ['cronos', 'gráficos', 'histórico', 'comparar', 'tiendas']
    },

    // 3. Telegram & Alertas
    {
        id: 'telegram-only-missing',
        category: 'telegram',
        question: '¿Cómo configuro para recibir SOLO alertas de figuras que NO poseo?',
        points: [
            { label: 'Desde la App Web', text: 'Ve a Configuración (Ajustes), localiza la tarjeta "Alertas Push de Telegram" y activa el interruptor "Solo Figuras NO Poseídas".' },
            { label: 'Desde Telegram', text: 'Envía el comando /alertas a tu bot de Telegram y pulsa el botón interactivo para alternar el modo.' },
            { label: 'Resultado', text: 'El sistema silencia de inmediato alertas de compras obligatorias y chollos de piezas que ya consten aseguradas en tu Fortaleza.' }
        ],
        tags: ['telegram', 'push', 'alertas', 'filtro', 'poseídas', 'adquiridas']
    },
    {
        id: 'telegram-alert-types',
        category: 'telegram',
        question: '¿Qué tipos de alertas automáticas envía el bot de Telegram?',
        points: [
            { label: 'Compras Obligatorias', text: 'Oportunidades con Opportunity Score de 90+ puntos y alto descuento respecto a la media de mercado.' },
            { label: 'Lista de Deseos', text: 'Aviso instantáneo cuando se detecta a la venta una figura que tienes marcada en tus deseos.' },
            { label: 'Precio Objetivo', text: 'Alerta personalizada si el precio cae por debajo del umbral que fijaste en El Centinela.' },
            { label: 'Gangas de Vinted', text: 'Avisos en batidas del cazador autónomo con Landed Price inferior al precio de referencia.' }
        ],
        tags: ['score', 'chollos', 'compras', 'obligatorias', 'radar', 'bot']
    },

    // 4. Vinted & Caza
    {
        id: 'vinted-sentinel-mode',
        category: 'vinted',
        question: '¿Qué es el Centinela de Vinted y cómo opera?',
        points: [
            { label: 'Incursiones 24/7', text: 'Ejecuta batidas automáticas a intervalos aleatorios de 100 a 120 minutos para eludir bloqueos WAF.' },
            { label: 'IP Rotatoria', text: 'Opera a través de proxies y entornos protegidos para consultar el mercado de segunda mano en tiempo real.' },
            { label: 'Landed Price Real', text: 'Calcula el coste final sumando precio de producto + gastos de envío (5,00€) + tasa de seguro de comprador (2%).' }
        ],
        tags: ['vinted', 'centinela', 'landed', 'seguro', 'envío', 'rotatorio']
    },
    {
        id: 'vinted-manual-hunt',
        category: 'vinted',
        question: '¿Cómo lanzo una incursión de caza manual desde Telegram?',
        points: [
            { label: 'Caza Canónica', text: 'Envía /caza por Telegram para rastrear las 4 familias principales de MOTU.' },
            { label: 'Caza Específica', text: 'Envía /caza [nombre] (ej. /caza trap jaw origins) para buscar una figura puntual.' },
            { label: 'Pausar o Reanudar', text: 'Usa /centinela on o /centinela off para encender o pausar el piloto automático.' }
        ],
        tags: ['caza', 'hunt', 'manual', 'comando', 'telegram', 'vinted']
    },

    // 5. Purgatorio
    {
        id: 'purgatorio-purpose',
        category: 'purgatorio',
        question: '¿Qué es el Purgatorio y por qué van ofertas allí?',
        points: [
            { label: 'Cámara de Validación', text: 'Las ofertas extraídas por scrapers que no alcanzan un 90% de coincidencia automática se depositan allí para revisión humana.' },
            { label: 'Protección Vintage Estricta', text: 'Ninguna figura o lote de los años 80 se vincula automáticamente; todas pasan obligatoriamente por el Purgatorio para evitar errores históricos.' },
            { label: 'Vincular o Descartar', text: 'Puedes pulsar "Vincular" para emparejar la oferta al catálogo o "Bloquear" para enviarla a la lista negra permanente.' }
        ],
        tags: ['purgatorio', 'vintage', 'validación', 'vincular', 'bloquear']
    },

    // 6. Seguridad & SSL
    {
        id: 'seguridad-devices',
        category: 'seguridad',
        question: '¿Cómo autorizo un nuevo dispositivo o navegador?',
        points: [
            { label: 'Alerta Soberana', text: 'Al iniciar sesión desde un nuevo navegador, el sistema enviará un mensaje con botones [Permitir] y [Bloquear] a tu Telegram.' },
            { label: 'Gestión de Dispositivos', text: 'Puedes auditar y revocar huellas dactilares autorizadas en la pestaña Dispositivos de Configuración o con /devices en Telegram.' }
        ],
        tags: ['dispositivos', 'fingerprint', 'aprobar', 'bloquear', 'telegram']
    },
    {
        id: 'seguridad-ssl',
        category: 'seguridad',
        question: '¿Cómo se gestionan los certificados SSL (HTTPS)?',
        points: [
            { label: 'Guardián Automatizado', text: 'El servidor comprueba diariamente la caducidad del certificado Let\'s Encrypt para oraculo-eternia.duckdns.org.' },
            { label: 'Renovación Anticipada', text: 'Si faltan 14 días o menos para expirar, GitHub Actions o el backend ejecutan la renovación remota por SSH.' },
            { label: 'Diagnóstico Remoto', text: 'Escribe /ssl en Telegram para conocer los días restantes de validez o /renew_ssl para forzar la renovación inmediata.' }
        ],
        tags: ['ssl', 'https', 'certbot', 'renovar', 'servidor', 'duckdns']
    }
];
