import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: false,
    proxy: {
      '/api': 'http://192.168.1.50:8000',
      '/health': 'http://192.168.1.50:8000',
    },
  }
})
