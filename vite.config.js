import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: './web',
  build: {
    outDir: '../dist'
  },
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: false
  }
})