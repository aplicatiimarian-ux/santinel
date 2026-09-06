import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: {
      key: fs.readFileSync('F:/Proiecte AI/santinel/100.68.140.75+1-key.pem'),
      cert: fs.readFileSync('F:/Proiecte AI/santinel/100.68.140.75+1.pem'),
    },
    proxy: {
      '/api': 'http://localhost:8000',
      '/analyze': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  }
})