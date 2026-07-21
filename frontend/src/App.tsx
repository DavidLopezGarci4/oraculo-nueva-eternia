import { useState, useEffect, lazy, Suspense } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import ShieldBypass from './components/ShieldBypass';
import MasterLogin from './components/auth/MasterLogin';
import { getUserSettings, type Hero } from './api/admin';
import PowerSwordLoader from './components/ui/PowerSwordLoader';
import axios from 'axios';
import CacheWelcomeModal from './components/ui/CacheWelcomeModal';
import { clearSession, setUnauthorizedHandler } from './api/client';

// Lazy-Loaded Page Components for Code Splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Catalog = lazy(() => import('./pages/Catalog'));
const Collection = lazy(() => import('./pages/Collection'));
const Purgatory = lazy(() => import('./pages/Purgatory'));
const Config = lazy(() => import('./pages/Config'));
const Auctions = lazy(() => import('./pages/Auctions'));
const VintageMiscellaneous = lazy(() => import('./pages/VintageMiscellaneous'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const Showcase = lazy(() => import('./pages/Showcase'));

// Fase AAA-3.1: router real en vez de activeTab + "visitedTabs" mantenidos
// vivos para siempre. Cada tab-id sigue existiendo (Sidebar/Navbar no se
// tocan) pero ahora mapea a una ruta real; cada página monta/desmonta al
// navegar, en vez de acumularse oculta en el DOM con sus queries activas.
const TAB_PATHS: Record<string, string> = {
  dashboard: '/',
  catalog: '/catalog',
  eternia: '/eternia',
  auctions: '/auctions',
  collection: '/collection',
  fortaleza_vintage: '/fortaleza_vintage',
  vintage_miscellaneous: '/vintage_miscellaneous',
  purgatory: '/purgatory',
  settings: '/settings',
};

const PATH_TO_TAB: Record<string, string> = Object.fromEntries(
  Object.entries(TAB_PATHS).map(([tab, path]) => [path, tab])
);

// Fase AAA-4.4: al pasar el ratón por un enlace del sidebar, se dispara el
// mismo import() dinámico que usa lazy() para esa página — el navegador ya
// tiene el chunk descargado y parseado para cuando el usuario hace clic.
const TAB_PREFETCH: Record<string, () => Promise<unknown>> = {
  dashboard: () => import('./pages/Dashboard'),
  catalog: () => import('./pages/Catalog'),
  eternia: () => import('./pages/Catalog'),
  auctions: () => import('./pages/Auctions'),
  collection: () => import('./pages/Collection'),
  fortaleza_vintage: () => import('./pages/Collection'),
  vintage_miscellaneous: () => import('./pages/VintageMiscellaneous'),
  purgatory: () => import('./pages/Purgatory'),
  settings: () => import('./pages/Config'),
};
const _prefetched = new Set<string>();

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const activeTab = PATH_TO_TAB[location.pathname] ?? 'dashboard';
  const setActiveTab = (tab: string) => navigate(TAB_PATHS[tab] ?? '/');
  const handlePrefetch = (tab: string) => {
    if (_prefetched.has(tab)) return;
    _prefetched.add(tab);
    TAB_PREFETCH[tab]?.().catch(() => {
      // Si falla (p.ej. sin red), lo intentamos de nuevo en el próximo hover.
      _prefetched.delete(tab);
    });
  };
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentUser, setCurrentUser] = useState<Hero | null>(null);
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(true);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [isSovereign, setIsSovereign] = useState<boolean>(localStorage.getItem('is_sovereign') === 'true');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(localStorage.getItem('is_logged_in') === 'true');
  const [activeUserId, setActiveUserId] = useState<number>(parseInt(localStorage.getItem('active_user_id') || '2'));
  const [isIncognito, setIsIncognito] = useState<boolean>(() => localStorage.getItem('motu_incognito') === 'true');
  const [useLocalImages, setUseLocalImages] = useState<boolean>(() => localStorage.getItem('use_local_images') === 'true');
  const [bgDownloadEnabled, setBgDownloadEnabled] = useState<boolean>(() => localStorage.getItem('motu_background_download_enabled') === 'true');
  const [showCacheWelcome, setShowCacheWelcome] = useState<boolean>(false);

  // Global Incognito Keyboard Shortcuts: Double Esc or Ctrl + I
  useEffect(() => {
    let lastEscTime = 0;

    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      // Do not trigger shortcuts when user is typing in form fields
      if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
        return;
      }

      if (e.ctrlKey && (e.key === 'i' || e.key === 'I')) {
        e.preventDefault();
        setIsIncognito(prev => {
          const val = !prev;
          localStorage.setItem('motu_incognito', val ? 'true' : 'false');
          return val;
        });
      } else if (e.key === 'Escape') {
        const now = Date.now();
        if (now - lastEscTime < 300) {
          e.preventDefault();
          setIsIncognito(prev => {
            const val = !prev;
            localStorage.setItem('motu_incognito', val ? 'true' : 'false');
            return val;
          });
        }
        lastEscTime = now;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const handleNavigate = () => {
      navigate(TAB_PATHS.catalog);
    };
    window.addEventListener('navigate-to-catalog', handleNavigate);
    return () => window.removeEventListener('navigate-to-catalog', handleNavigate);
  }, [navigate]);


  const fetchUser = async (userId: number) => {
    try {
      setLoading(true);
      setIsUnauthorized(false);
      const data = await getUserSettings(userId);
      setCurrentUser(data);
    } catch (err: any) {
      console.error("Failed to fetch current user", err);
      const status = err.response?.status;
      if (status === 403) {
        setIsUnauthorized(true);
      } else if (status === 401) {
        // Sesión inexistente o token caducado → volver al login.
        clearSession();
        setIsLoggedIn(false);
        setIsSovereign(false);
        setCurrentUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  // Cuando cualquier petición devuelve 401 (token inválido), cerramos sesión de forma global.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      setIsLoggedIn(false);
      setIsSovereign(false);
      setCurrentUser(null);
    });
  }, []);

  useEffect(() => {
    if (isSovereign || isLoggedIn) {
      fetchUser(activeUserId);
    } else {
      setLoading(false);
    }
  }, [activeUserId, isSovereign, isLoggedIn]);

  // Background Image Pre-fetching (Best Practice for smooth offline experience)
  useEffect(() => {
    if (!isLoggedIn && !isSovereign) return;
    if (!useLocalImages || !bgDownloadEnabled) return;

    let active = true;
    const cacheImagesInBackground = async () => {
      // Delay initial execution by 4 seconds to allow primary resources to load
      await new Promise(resolve => setTimeout(resolve, 4000));
      if (!active) return;

      try {
        const response = await axios.get('/api/products');
        const products = response.data;
        const productsWithImages = products.filter((p: any) => p.image_url);
        
        const cache = await caches.open('motu-image-cache');

        // Throttle downloads to prevent CPU/network spikes: 1 image every 1500ms
        for (const p of productsWithImages) {
          if (!active) break;
          const cacheKey = `/api/static/images/${p.id}.webp`;
          
          try {
            const hasMatch = await cache.match(cacheKey);
            if (!hasMatch) {
              // Fetch from local static server first (since it is populated and fast)
              let imgResponse = await fetch(cacheKey);
              if (!imgResponse.ok) {
                // Fallback to Supabase remote image URL if local is missing
                imgResponse = await fetch(p.image_url);
              }
              if (imgResponse.ok) {
                await cache.put(cacheKey, imgResponse);
              }
            }
          } catch (err) {
            // Silently handle single image fetch failures in background
          }
          
          // Wait 1.5s between images
          await new Promise(resolve => setTimeout(resolve, 1500));
        }
      } catch (err) {
        console.warn("Background image caching initialization failed:", err);
      }
    };

    cacheImagesInBackground();

    return () => {
      active = false;
    };
  }, [isLoggedIn, isSovereign, useLocalImages, bgDownloadEnabled]);

  // Show Cache Welcome Dialog for first time users
  useEffect(() => {
    if (isLoggedIn || isSovereign) {
      const seen = localStorage.getItem('motu_cache_intro_seen') === 'true';
      if (!seen) {
        // Show after a brief delay
        const timer = setTimeout(() => {
          setShowCacheWelcome(true);
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [isLoggedIn, isSovereign]);

  const handleCacheWelcomeSelect = (mode: 'download_all' | 'on_demand' | 'none') => {
    localStorage.setItem('motu_cache_intro_seen', 'true');
    if (mode === 'download_all') {
      localStorage.setItem('use_local_images', 'true');
      localStorage.setItem('motu_background_download_enabled', 'true');
      setUseLocalImages(true);
      setBgDownloadEnabled(true);
    } else if (mode === 'on_demand') {
      localStorage.setItem('use_local_images', 'true');
      localStorage.setItem('motu_background_download_enabled', 'false');
      setUseLocalImages(true);
      setBgDownloadEnabled(false);
    } else {
      localStorage.setItem('use_local_images', 'false');
      localStorage.setItem('motu_background_download_enabled', 'false');
      setUseLocalImages(false);
      setBgDownloadEnabled(false);
    }
  };

  const handleLoginSuccess = (user: any, sovereign: boolean) => {
    setIsLoggedIn(true);
    setIsSovereign(sovereign);
    setActiveUserId(user.id);
    setCurrentUser(user);
    localStorage.setItem('is_sovereign', sovereign ? 'true' : 'false');
    localStorage.setItem('is_logged_in', 'true');
    localStorage.setItem('active_user_id', user.id.toString());
  };

  const handleLogout = () => {
    clearSession();
    setIsLoggedIn(false);
    setCurrentUser(null);
    setIsSovereign(false);
    setActiveUserId(2);
    navigate(TAB_PATHS.dashboard);
  };

  const handleIdentityChange = async (targetId?: number) => {
    if (!isSovereign && activeUserId !== 1) return;
    const newId = targetId || (activeUserId === 1 ? 2 : 1);
    localStorage.setItem('active_user_id', newId.toString());
    setActiveUserId(newId);
    navigate(TAB_PATHS.dashboard);
    queryClient.resetQueries();
    await fetchUser(newId);
  };

  // Fase AAA-3.1: antes esto forzaba el tab de vuelta a 'dashboard' con un
  // efecto reactivo; ahora es un guard declarativo directamente en la ruta
  // /purgatory (ver <Routes> más abajo), sin necesidad de useEffect.
  const isAdminUser = currentUser?.role === 'admin' || currentUser?.username === 'David';

  const [showMasterLogin, setShowMasterLogin] = useState(false);

  // --- PUBLIC SHOWCASE BYPASS ---
  const match = window.location.pathname.match(/^\/santuario\/([^/]+)/);
  const showcaseUsername = match ? match[1] : null;

  if (showcaseUsername) {
    return (
      <ErrorBoundary>
        <Suspense fallback={<PowerSwordLoader variant="fullScreen" text="Cargando Exhibición..." />}>
          <Showcase username={showcaseUsername} />
        </Suspense>
      </ErrorBoundary>
    );
  }

  if (loading) {
    return <PowerSwordLoader variant="fullScreen" text="Sincronizando Identidad..." />;
  }

  if (isUnauthorized) {
    if (showMasterLogin) {
      return (
        <MasterLogin
          onSuccess={(isSov) => {
            setIsSovereign(isSov);
            setIsLoggedIn(true);
            setShowMasterLogin(false);
            const currentId = parseInt(localStorage.getItem('active_user_id') || '2');
            setActiveUserId(currentId);
          }}
          onCancel={() => setShowMasterLogin(false)}
        />
      );
    }
    return (
      <ShieldBypass
        onRetry={() => fetchUser(activeUserId)}
        onSovereignClick={() => setShowMasterLogin(true)}
      />
    );
  }

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className={`flex h-screen w-screen overflow-hidden bg-transparent text-white font-inter ${isIncognito ? 'mode-incognito' : ''}`}>
      {/* Global Background Layer with Glassmorphism Haloes */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-10%] right-[-5%] h-[60%] w-[60%] rounded-full bg-brand-primary/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-5%] h-[60%] w-[60%] rounded-full bg-brand-secondary/5 blur-[120px]" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/0 via-black/10 to-black/40" />
      </div>

      {/* Main UI Container */}
      <div className="relative z-10 flex h-full w-full overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isMobileOpen={isMobileMenuOpen}
          onCloseMobile={() => setIsMobileMenuOpen(false)}
          user={currentUser}
          onLogout={handleLogout}
          onPrefetch={handlePrefetch}
        />

        <div className="flex flex-1 flex-col overflow-hidden relative">
          <Navbar
            onMenuClick={() => setIsMobileMenuOpen(prev => !prev)}
            showSearch={activeTab === 'catalog' || activeTab === 'collection' || activeTab === 'eternia' || activeTab === 'fortaleza_vintage' || activeTab === 'vintage_miscellaneous'}
            searchValue={searchQuery}
            onSearchChange={setSearchQuery}
            user={currentUser}
            isSovereign={isSovereign}
            onIdentityChange={handleIdentityChange}
            isIncognito={isIncognito}
            onToggleIncognito={() => setIsIncognito(prev => {
              const val = !prev;
              localStorage.setItem('motu_incognito', val ? 'true' : 'false');
              return val;
            })}
          />

          <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 scroll-smooth">
            <div className="max-w-7xl mx-auto w-full">
              <ErrorBoundary>
                <Suspense fallback={<PowerSwordLoader variant="fullScreen" text="Canalizando Poder..." />}>
                  <Routes>
                    <Route path={TAB_PATHS.dashboard} element={<Dashboard user={currentUser} />} />
                    <Route path={TAB_PATHS.catalog} element={<Catalog user={currentUser} searchQuery={searchQuery} isIncognito={isIncognito} />} />
                    <Route path={TAB_PATHS.eternia} element={<Catalog user={currentUser} isVintageOnly={true} searchQuery={searchQuery} isIncognito={isIncognito} />} />
                    <Route path={TAB_PATHS.auctions} element={<Auctions user={currentUser} />} />
                    <Route path={TAB_PATHS.collection} element={<Collection user={currentUser} searchQuery={searchQuery} isIncognito={isIncognito} />} />
                    <Route path={TAB_PATHS.fortaleza_vintage} element={<Collection user={currentUser} isVintageOnly={true} searchQuery={searchQuery} isIncognito={isIncognito} />} />
                    <Route path={TAB_PATHS.vintage_miscellaneous} element={<VintageMiscellaneous user={currentUser} />} />
                    <Route
                      path={TAB_PATHS.purgatory}
                      element={isAdminUser ? <Purgatory /> : <Navigate to={TAB_PATHS.dashboard} replace />}
                    />
                    <Route
                      path={TAB_PATHS.settings}
                      element={(
                        <Config
                          user={currentUser}
                          onUserUpdate={() => fetchUser(activeUserId)}
                          onIdentityChange={handleIdentityChange}
                        />
                      )}
                    />
                    <Route path="*" element={<Navigate to={TAB_PATHS.dashboard} replace />} />
                  </Routes>
                </Suspense>
              </ErrorBoundary>
            </div>
          </main>
        </div>
      </div>
      
      <CacheWelcomeModal
        isOpen={showCacheWelcome}
        onClose={() => setShowCacheWelcome(false)}
        onSelect={handleCacheWelcomeSelect}
      />
    </div>
  );
}

export default App;
