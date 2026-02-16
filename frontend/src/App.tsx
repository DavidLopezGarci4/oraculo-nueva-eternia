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
import RadarP2P from './pages/RadarP2P';
import ShieldBypass from './components/ShieldBypass';
import MasterLogin from './components/auth/MasterLogin';
import LoginPage from './pages/LoginPage';
import { getUserSettings, type Hero } from './api/admin';
import { Sparkles } from 'lucide-react';
import PowerSwordLoader from './components/ui/PowerSwordLoader';

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
  };

  const handleIdentityChange = async (targetId?: number) => {
    if (!isSovereign && activeUserId !== 1) return;
    const newId = targetId || (activeUserId === 1 ? 2 : 1);
    localStorage.setItem('active_user_id', newId.toString());
    setActiveUserId(newId);
    queryClient.resetQueries();
    await fetchUser(newId);
  };

  useEffect(() => {
    if (currentUser && currentUser.role !== 'admin') {
      const restrictedTabs = ['purgatory'];
      if (restrictedTabs.includes(activeTab)) {
        setActiveTab('dashboard');
      }
    }
  }, [currentUser, activeTab]);

  const [showMasterLogin, setShowMasterLogin] = useState(false);

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
    <div className="flex h-screen w-screen overflow-hidden bg-transparent text-white font-inter">
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
            showSearch={activeTab === 'catalog' || activeTab === 'collection'}
            searchValue={searchQuery}
            onSearchChange={setSearchQuery}
            user={currentUser}
            isSovereign={isSovereign}
            onIdentityChange={handleIdentityChange}
          />

          <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 scroll-smooth">
            <div className="max-w-7xl mx-auto w-full">
              <ErrorBoundary>
                {activeTab === 'dashboard' && <Dashboard user={currentUser} />}
                {activeTab === 'catalog' && <Catalog searchQuery={searchQuery} />}
                {activeTab === 'auctions' && <Auctions />}
                {activeTab === 'radar' && <RadarP2P />}
                {activeTab === 'collection' && <Collection searchQuery={searchQuery} />}
                {activeTab === 'purgatory' && <Purgatory />}
                {activeTab === 'settings' && (
                  <Config
                    user={currentUser}
                    onUserUpdate={() => fetchUser(activeUserId)}
                    onIdentityChange={handleIdentityChange}
                  />
                )}
              </ErrorBoundary>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
