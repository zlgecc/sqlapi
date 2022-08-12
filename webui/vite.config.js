import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    hmr: {
      overlay: true,
    },
    proxy: {
      "/a": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/a/, '')
      },
    }
   
  },
  plugins: [vue()]
})
