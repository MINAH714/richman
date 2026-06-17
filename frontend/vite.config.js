// vite.config.js (프로젝트 루트 폴더에 있습니다)
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // 🚨 [여기가 핵심입니다!] server 설정을 확인하고 없으면 통째로 추가해 주세요.
  server: {
    proxy: {
      // 프론트엔드에서 '/api'로 시작하는 요청을 보내면 아래 주소로 배달합니다.
      '/api': {
        target: 'http://127.0.0.1:8000', // Django 백엔드 서버 주소
        changeOrigin: true,
        secure: false,
      }
    }
  }
})