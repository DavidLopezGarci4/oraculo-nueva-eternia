import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Catalog from './pages/Catalog';

function App() {
  const [activeTab, setActiveTab] = useState('catalog');

  return (
    <div className="flex min-h-screen w-screen overflow-hidden bg-transparent">
      {/* Menu Lateral */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex flex-1 flex-col overflow-y-auto">
        {/* Barra Superior */}
        <Navbar />

        {/* Contenido Principal */}
        <main className="flex-1 p-6">
          {activeTab === 'catalog' && <Catalog />}
          {activeTab === 'purgatory' && (
            <div className="flex flex-col items-center justify-center h-full opacity-50">
              <h2 className="text-2xl font-bold">Purgatorio</h2>
              <p>Próximamente en la Fase 4.2</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
