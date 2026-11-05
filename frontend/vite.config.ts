import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 开发环境下把 /api 请求代理到后端，避免跨域问题
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
