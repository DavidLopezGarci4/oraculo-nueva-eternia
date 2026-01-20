
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

  return (
    <div className="flex h-screen w-full overflow-hidden bg-transparent">
      {/* Menu Lateral (Responsive Drawer) */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      <div className="flex flex-1 flex-col overflow-hidden relative w-full">
        {/* Barra Superior */}
        <Navbar onMenuClick={() => setIsMobileMenuOpen(prev => !prev)} />

        {/* Contenido Principal con Scroll */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 scroll-smooth">
          <div className="max-w-7xl mx-auto w-full">
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'catalog' && <Catalog />}
            {activeTab === 'auctions' && <Auctions />}
            {activeTab === 'radar' && <RadarP2P />}
            {activeTab === 'collection' && <Collection />}
            {activeTab === 'purgatory' && <Purgatory />}
            {activeTab === 'settings' && <Config />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
