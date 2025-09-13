import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AppClaude from './AppClaude.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppClaude />
  </StrictMode>,
)
