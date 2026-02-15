/**
 * ShieldIdentity: Generador de huella digital para el Ojo de Sauron.
 */
export const ShieldIdentity = {
    /**
     * Genera un UUID v4 simple.
     */
    generateUUID: (): string => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    /**
     * Obtiene o genera el ID único del dispositivo.
     */
    getDeviceId: (): string => {
        let deviceId = localStorage.getItem('shield_device_id');
        if (!deviceId) {
            deviceId = `MOTU-${ShieldIdentity.generateUUID().substring(0, 13)}`;
            localStorage.setItem('shield_device_id', deviceId);
        }
        return deviceId;
    },

    /**
     * Intenta detectar un nombre legible para el dispositivo.
     */
    getDeviceName: (): string => {
        const ua = navigator.userAgent;
        if (/iPhone/i.test(ua)) return "iPhone";
        if (/iPad/i.test(ua)) return "iPad";
        if (/Android/i.test(ua)) {
            const match = ua.match(/Android\s+([^\s;]+)/);
            return `Android ${match ? match[1] : ""}`;
        }
        if (/Windows/i.test(ua)) return "Windows PC";
        if (/Macintosh/i.test(ua)) return "Mac";
        return "Navegador Web";
    }
};
