import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Where the FastAPI server runs during development. With this proxy in place
// the browser talks to the Vite origin, so no CORS setup or .env is needed.
const API_TARGET = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    port: 3000,
    proxy: {
      // Trailing slashes matter: a bare '/ai' would also capture the SPA route
      // '/ai-planner' and proxy it to the API, which 502s in the browser.
      '/auth/': { target: API_TARGET, changeOrigin: true },
      '/ai/': { target: API_TARGET, changeOrigin: true },
      '/api/': { target: API_TARGET, changeOrigin: true },
    },
  },
})
