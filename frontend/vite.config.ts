/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In compose the backend is reached via the service name; on the host it's
// localhost. Override with VITE_API_PROXY when needed.
const apiProxy = process.env.VITE_API_PROXY ?? 'http://127.0.0.1:8000'

// Served at sean-michael.dev/tides, so assets and the dev server live under /tides/.
export default defineConfig({
  base: '/tides/',
  plugins: [react()],
  server: {
    host: true,
    port: process.env.PORT ? Number(process.env.PORT) : 5173,
    proxy: {
      '/api': apiProxy,
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
