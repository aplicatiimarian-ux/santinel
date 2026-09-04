import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '192.168.1.50',
    port: 5173,
    https: {
      key: fs.readFileSync('F:/Proiecte AI/santinel/100.68.140.75+1-key.pem'),
      cert: fs.readFileSync('F:/Proiecte AI/santinel/100.68.140.75+1.pem'),
    },
  }
})