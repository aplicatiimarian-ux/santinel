import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Generate self-signed certificate for HTTPS (required for microphone access on mobile)
function getHttpsConfig() {
  const certDir = path.join(__dirname, '.certs')
  const keyFile = path.join(certDir, 'key.pem')
  const certFile = path.join(certDir, 'cert.pem')

  if (fs.existsSync(keyFile) && fs.existsSync(certFile)) {
    return {
      key: fs.readFileSync(keyFile),
      cert: fs.readFileSync(certFile),
    }
  }
  return true // Let Vite auto-generate
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: getHttpsConfig(),
    proxy: {
      '/api': 'http://192.168.1.50:8000',
      '/analyze': 'http://192.168.1.50:8000',
      '/health': 'http://192.168.1.50:8000',
    },
  }
})