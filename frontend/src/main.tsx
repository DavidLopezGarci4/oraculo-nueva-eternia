import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { MotionConfig } from 'framer-motion'
import './index.css'
import './api/client' // Registra los interceptores de auth (JWT) sobre axios global antes de cualquier petición
import App from './App.tsx'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos de 'frescura' para navegación instantánea
      gcTime: 1000 * 60 * 10,   // Mantener en memoria 10 minutos
      refetchOnWindowFocus: false, // Evitar recargas al cambiar de pestaña del navegador
    },
  },
})

import { CartProvider } from './context/CartContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* Fase AAA-Ola2 (2d): respeta prefers-reduced-motion del sistema
        operativo para TODOS los componentes motion.* de la app, sin tocar
        cada animación una por una. */}
    <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <CartProvider>
            <App />
          </CartProvider>
        </QueryClientProvider>
      </BrowserRouter>
    </MotionConfig>
  </StrictMode>,
)
