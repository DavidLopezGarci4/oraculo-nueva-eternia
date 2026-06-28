/**
 * Convierte un string de fecha del backend (que suele venir sin sufijo de zona de tiempo en UTC)
 * a un objeto Date interpretado correctamente en UTC.
 */
export const parseUtcDate = (dateStr: string | Date | undefined | null): Date => {
    if (!dateStr) return new Date();
    if (dateStr instanceof Date) return dateStr;
    
    // Si ya termina con Z o contiene un indicador de zona de tiempo (+ o - tras la hora), lo dejamos igual
    const hasTimezone = dateStr.endsWith('Z') || dateStr.includes('+') || (dateStr.includes('T') && dateStr.split('T')[1]?.includes('-'));
    const cleanStr = hasTimezone ? dateStr : `${dateStr}Z`;
    
    const d = new Date(cleanStr);
    
    // En caso de que sea inválida por el formateo de string, retornamos la fecha original parsed
    return isNaN(d.getTime()) ? new Date(dateStr) : d;
};
