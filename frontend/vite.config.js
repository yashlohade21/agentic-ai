import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    // Enable production optimizations
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug']
      }
    },
    // Optimize chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'markdown': ['react-markdown', 'remark-gfm', 'react-syntax-highlighter'],
          'ui-vendor': ['framer-motion', 'lucide-react', 'react-hot-toast']
        }
      }
    },
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // Enable source maps for production debugging (optional)
    sourcemap: false,
    // Optimize CSS
    cssCodeSplit: true,
    // Target modern browsers for smaller bundle
    target: 'es2015'
  },
  // Optimize dev server
  server: {
    // Enable HMR for faster development
    hmr: true,
    // Optimize dependencies
    warmup: {
      clientFiles: ['./src/AppClaude.jsx', './src/main.jsx']
    }
  },
  // Pre-bundle dependencies for faster cold starts
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'axios',
      'react-markdown',
      'remark-gfm',
      'framer-motion',
      'lucide-react',
      'react-hot-toast'
    ]
  }
})
