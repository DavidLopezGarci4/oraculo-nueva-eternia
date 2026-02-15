
import { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Catalog from './pages/Catalog';
import Collection from './pages/Collection';
import Purgatory from './pages/Purgatory';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Auctions from './pages/Auctions';
import RadarP2P from './pages/RadarP2P';
import ShieldBypass from './components/ShieldBypass';
import MasterLogin from './components/auth/MasterLogin';
import { type Hero } from './api/admin';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentUser, setCurrentUser] = useState<Hero | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [isSovereign, setIsSovereign] = useState<boolean>(localStorage.getItem('is_sovereign') === 'true');
  const [activeUserId, setActiveUserId] = useState<number>(parseInt(localStorage.getItem('active_user_id') || '2'));

  const fetchUser = async (userId: number) => {
    try {
      setLoading(true);
      setIsUnauthorized(false);
      const { getUserSettings } = await import('./api/admin');
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
    if (isSovereign) {
      fetchUser(activeUserId);
    } else {
      setLoading(false);
    }
  }, [activeUserId, isSovereign]);

  const handleIdentityChange = () => {
    const newId = parseInt(localStorage.getItem('active_user_id') || '2');
    setActiveUserId(newId);
  };

  // Redirección automática si un usuario no-admin está en una pestaña restringida
  useEffect(() => {
    // Si el usuario ya cargó y no es admin
    if (currentUser && currentUser.role !== 'admin') {
      const restrictedTabs = ['purgatory'];
      if (restrictedTabs.includes(activeTab)) {
        console.log("🛡️ Seguridad: Redirigiendo a Tablero (Usuario no administrativo)");
        setActiveTab('dashboard');
      }
    }
  }, [currentUser, activeTab]);

  // Reset search when changing tabs
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setSearchQuery('');
  };

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-black">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-full border-t-2 border-brand-primary animate-spin" />
          <p className="text-white/40 text-[10px] font-black uppercase tracking-[0.4em]">Sincronizando Identidad...</p>
        </div>
      </div>
    );
  }

  if (!isSovereign) {
    return <MasterLogin onSuccess={(isSov) => {
      setIsSovereign(isSov);
      const currentId = parseInt(localStorage.getItem('active_user_id') || '2');
      setActiveUserId(currentId);
    }} />;
  }

  if (isUnauthorized) {
    return <ShieldBypass onRetry={() => fetchUser(activeUserId)} />;
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-transparent">
      {/* Menu Lateral (Responsive Drawer) */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
        user={currentUser}
      />

      <div className="flex flex-1 flex-col overflow-hidden relative w-full">
        {/* Barra Superior */}
        <Navbar
          onMenuClick={() => setIsMobileMenuOpen(prev => !prev)}
          showSearch={activeTab === 'catalog' || activeTab === 'collection'}
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          user={currentUser}
          onIdentityChange={handleIdentityChange}
          isSovereign={isSovereign}
        />

        {/* Contenido Principal con Scroll */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 scroll-smooth">
          <div className="max-w-7xl mx-auto w-full">
            {activeTab === 'dashboard' && <Dashboard user={currentUser} />}
            {activeTab === 'catalog' && <Catalog searchQuery={searchQuery} />}
            {activeTab === 'auctions' && <Auctions />}
            {activeTab === 'radar' && <RadarP2P />}
            {activeTab === 'collection' && <Collection searchQuery={searchQuery} />}
            {activeTab === 'purgatory' && <Purgatory />}
            {activeTab === 'settings' && <Config user={currentUser} onUserUpdate={() => fetchUser(activeUserId)} />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
