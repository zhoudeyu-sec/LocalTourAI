import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // 将所有以 /api 开头的请求转发到 FastAPI 后端
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path // FastAPI 已经包含了 /api 前缀，所以无需重写
      }
    }
  }
})