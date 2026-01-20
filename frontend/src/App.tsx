
import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Catalog from './pages/Catalog';
import Collection from './pages/Collection';
import Purgatory from './pages/Purgatory';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Auctions from './pages/Auctions';
import RadarP2P from './pages/RadarP2P';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Reset search when changing tabs
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setSearchQuery('');
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-transparent">
      {/* Menu Lateral (Responsive Drawer) */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      <div className="flex flex-1 flex-col overflow-hidden relative w-full">
        {/* Barra Superior */}
        <Navbar
          onMenuClick={() => setIsMobileMenuOpen(prev => !prev)}
          showSearch={activeTab === 'catalog' || activeTab === 'collection'}
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
        />

        {/* Contenido Principal con Scroll */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 scroll-smooth">
          <div className="max-w-7xl mx-auto w-full">
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'catalog' && <Catalog searchQuery={searchQuery} />}
            {activeTab === 'auctions' && <Auctions />}
            {activeTab === 'radar' && <RadarP2P />}
            {activeTab === 'collection' && <Collection searchQuery={searchQuery} />}
            {activeTab === 'purgatory' && <Purgatory />}
            {activeTab === 'settings' && <Config />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
