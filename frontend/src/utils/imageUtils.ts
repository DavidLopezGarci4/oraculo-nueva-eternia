/**
 * Utilidades de imágenes para optimización de carga.
 * Si en el futuro se activa el plan de pago en Supabase, se puede reemplazar
 * '/object/public/' por '/render/image/public/' y añadir parámetros de tamaño.
 */
export const getOptimizedImageUrl = (url: string | null | undefined, _width = 300): string => {
    if (!url) {
        // Retorna un placeholder sutil y premium
        return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="%23121214"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="bold" fill="%23333336">MOTU</text></svg>';
    }

    // Por ahora, al estar en capa gratuita de Supabase, retornamos la URL tal cual.
    // Si se activa el redimensionamiento, descomentar la línea de abajo:
    // if (url.includes('supabase.co/storage/v1/object/public/')) {
    //     return url.replace('/object/public/', '/render/image/public/') + `?width=${width}&quality=80`;
    // }

    return url;
};
