import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import Catalog from './pages/Catalog';
import Collection from './pages/Collection';
import Purgatory from './pages/Purgatory';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Auctions from './pages/Auctions';
import VintageMiscellaneous from './pages/VintageMiscellaneous';
import ShieldBypass from './components/ShieldBypass';
import MasterLogin from './components/auth/MasterLogin';
import LoginPage from './pages/LoginPage';
import { getUserSettings, type Hero } from './api/admin';
import PowerSwordLoader from './components/ui/PowerSwordLoader';
import Showcase from './pages/Showcase';
import axios from 'axios';
import CacheWelcomeModal from './components/ui/CacheWelcomeModal';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentUser, setCurrentUser] = useState<Hero | null>(null);
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(true);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [isSovereign, setIsSovereign] = useState<boolean>(localStorage.getItem('is_sovereign') === 'true');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(localStorage.getItem('is_logged_in') === 'true');
  const [activeUserId, setActiveUserId] = useState<number>(parseInt(localStorage.getItem('active_user_id') || '2'));
  const [visitedTabs, setVisitedTabs] = useState<Record<string, boolean>>({ dashboard: true });
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
    if (isLoggedIn || isSovereign) {
      setVisitedTabs(prev => ({ ...prev, [activeTab]: true }));
    }
  }, [activeTab, isLoggedIn, isSovereign]);


  const fetchUser = async (userId: number) => {
    try {
      setLoading(true);
      setIsUnauthorized(false);
      const data = await getUserSettings(userId);
      setCurrentUser(data);
    } catch (err: any) {
      console.error("Failed to fetch current user", err);
      if (err.response?.status === 403) {
        setIsUnauthorized(true);
      }
    } finally {
      setLoading(false);
    }
  };

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
    localStorage.removeItem('active_user_id');
    localStorage.removeItem('is_sovereign');
    localStorage.removeItem('is_logged_in');
    localStorage.removeItem('user_email');
    setIsLoggedIn(false);
    setCurrentUser(null);
    setIsSovereign(false);
    setActiveUserId(2);
    setVisitedTabs({ dashboard: true });
    setActiveTab('dashboard');
  };

  const handleIdentityChange = async (targetId?: number) => {
    if (!isSovereign && activeUserId !== 1) return;
    const newId = targetId || (activeUserId === 1 ? 2 : 1);
    localStorage.setItem('active_user_id', newId.toString());
    setActiveUserId(newId);
    setVisitedTabs({ dashboard: true });
    setActiveTab('dashboard');
    queryClient.resetQueries();
    await fetchUser(newId);
  };

  useEffect(() => {
    if (currentUser) {
      const isAdmin = currentUser.role === 'admin' || currentUser.username === 'David';
      if (!isAdmin) {
        const restrictedTabs = ['purgatory'];
        if (restrictedTabs.includes(activeTab)) {
          setActiveTab('dashboard');
        }
      }
    }
  }, [currentUser, activeTab]);

  const [showMasterLogin, setShowMasterLogin] = useState(false);

  // --- PUBLIC SHOWCASE BYPASS ---
  const match = window.location.pathname.match(/^\/santuario\/([^/]+)/);
  const showcaseUsername = match ? match[1] : null;

  if (showcaseUsername) {
    return (
      <ErrorBoundary>
        <Showcase username={showcaseUsername} />
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
                {visitedTabs['dashboard'] && (
                  <div className={activeTab === 'dashboard' ? '' : 'hidden'}>
                    <Dashboard 
                      user={currentUser} 
                    />
                  </div>
                )}
                {visitedTabs['catalog'] && (
                  <div className={activeTab === 'catalog' ? '' : 'hidden'}>
                    <Catalog user={currentUser} searchQuery={searchQuery} isIncognito={isIncognito} />
                  </div>
                )}
                {visitedTabs['eternia'] && (
                  <div className={activeTab === 'eternia' ? '' : 'hidden'}>
                    <Catalog user={currentUser} isVintageOnly={true} searchQuery={searchQuery} isIncognito={isIncognito} />
                  </div>
                )}
                {visitedTabs['auctions'] && (
                  <div className={activeTab === 'auctions' ? '' : 'hidden'}>
                    <Auctions user={currentUser} />
                  </div>
                )}
                {visitedTabs['collection'] && (
                  <div className={activeTab === 'collection' ? '' : 'hidden'}>
                    <Collection user={currentUser} searchQuery={searchQuery} isIncognito={isIncognito} />
                  </div>
                )}
                {visitedTabs['fortaleza_vintage'] && (
                  <div className={activeTab === 'fortaleza_vintage' ? '' : 'hidden'}>
                    <Collection user={currentUser} isVintageOnly={true} searchQuery={searchQuery} isIncognito={isIncognito} />
                  </div>
                )}
                {visitedTabs['vintage_miscellaneous'] && (
                  <div className={activeTab === 'vintage_miscellaneous' ? '' : 'hidden'}>
                    <VintageMiscellaneous user={currentUser} />
                  </div>
                )}
                {visitedTabs['purgatory'] && (
                  <div className={activeTab === 'purgatory' ? '' : 'hidden'}>
                    <Purgatory />
                  </div>
                )}
                {visitedTabs['settings'] && (
                  <div className={activeTab === 'settings' ? '' : 'hidden'}>
                    <Config
                      user={currentUser}
                      onUserUpdate={() => fetchUser(activeUserId)}
                      onIdentityChange={handleIdentityChange}
                    />
                  </div>
                )}
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
