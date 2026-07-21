import axios, { type InternalAxiosRequestConfig } from 'axios';
import { ShieldIdentity } from './shield-identity';

/**
 * Cliente HTTP central del Oráculo (Fase AAA-1).
 *
 * - La autenticación real es por JWT (Authorization: Bearer <token>).
 * - La API key de administración YA NO viaja al navegador (se eliminó del bundle).
 * - Ante un 401 en cualquier petición no-auth, limpiamos la sesión y avisamos a la app.
 */

const TOKEN_KEY = 'access_token';
const SESSION_KEYS = [
  'access_token',
  'active_user_id',
  'is_sovereign',
  'is_logged_in',
  'user_email',
  'master_key',
];

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string): void => localStorage.setItem(TOKEN_KEY, t);
export const clearSession = (): void =>
  SESSION_KEYS.forEach((k) => localStorage.removeItem(k));

let onUnauthorizedHandler: (() => void) | null = null;
/** La app registra aquí qué hacer cuando el token deja de ser válido (ej. volver al login). */
export const setUnauthorizedHandler = (fn: () => void): void => {
  onUnauthorizedHandler = fn;
};

const attachAuth = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const token = getToken();
  if (token) config.headers.set('Authorization', `Bearer ${token}`);
  // La huella de dispositivo sigue enviándose (telemetría del Escudo), pero ya no autoriza por sí sola.
  config.headers.set('X-Device-ID', ShieldIdentity.getDeviceId());
  config.headers.set('X-Device-Name', ShieldIdentity.getDeviceName());
  return config;
};

const handleAuthError = (error: unknown) => {
  const err = error as { response?: { status?: number }; config?: { url?: string } };
  const status = err?.response?.status;
  const url = err?.config?.url ?? '';
  // No secuestramos los endpoints de auth: que el formulario muestre su propio error.
  if (status === 401 && !url.includes('/auth/')) {
    clearSession();
    onUnauthorizedHandler?.();
  }
  return Promise.reject(error);
};

// Interceptores sobre el axios GLOBAL (lo usan collection.ts, products.ts, dashboard.ts, cart.ts, LoginPage…).
axios.interceptors.request.use(attachAuth);
axios.interceptors.response.use((r) => r, handleAuthError);

// Instancia compartida para los módulos que antes creaban su propia instancia con API key (admin, purgatory).
export const apiClient = axios.create({ baseURL: '/api' });
apiClient.interceptors.request.use(attachAuth);
apiClient.interceptors.response.use((r) => r, handleAuthError);
