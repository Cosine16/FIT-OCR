import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  base: '/admin/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api/admin': 'http://localhost:8001',
      '/uploads': 'http://localhost:8001',
      '/output': 'http://localhost:8001',
    },
  },
  build: {
    outDir: '../server/api/static/admin',
    emptyOutDir: true,
  },
})
