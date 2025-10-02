import { StrictMode, lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

// Lazy load the main app component
const AppClaude = lazy(() => import('./AppClaude.jsx'))

// Simple loading component
const LoadingFallback = () => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: '#fff',
    fontFamily: 'system-ui, sans-serif'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '40px',
        height: '40px',
        border: '3px solid #f3f3f3',
        borderTop: '3px solid #3498db',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 16px'
      }} />
      <p style={{ color: '#666' }}>Loading...</p>
    </div>
  </div>
)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Suspense fallback={<LoadingFallback />}>
      <AppClaude />
    </Suspense>
  </StrictMode>,
)
