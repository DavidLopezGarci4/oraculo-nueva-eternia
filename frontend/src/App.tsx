import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Catalog from './pages/Catalog';
import Collection from './pages/Collection';
import Purgatory from './pages/Purgatory';
import Dashboard from './pages/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex min-h-screen w-screen overflow-hidden bg-transparent">
      {/* Menu Lateral */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex flex-1 flex-col overflow-y-auto">
        {/* Barra Superior */}
        <Navbar />

        {/* Contenido Principal */}
        <main className="flex-1 p-6">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'catalog' && <Catalog />}
          {activeTab === 'collection' && <Collection />}
          {activeTab === 'purgatory' && <Purgatory />}
        </main>
      </div>
    </div>
  );
}

export default App;
