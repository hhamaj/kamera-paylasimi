import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../server/static',
    emptyOutDir: true,
  },
  server: {
    // npm run dev sirasinda WebSocket'i Flask server'a yonlendir
    proxy: {
      '/ws': { target: 'ws://localhost:5000', ws: true },
    },
  },
})
