import './assets/design-tokens.css'
import 'pretendard/dist/web/static/pretendard.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'   // ← 추가

const app = createApp(App)
const pinia = createPinia()                     // ← 변수로 분리

app.use(pinia)
app.use(router)

// 새로고침 시 토큰이 있으면 프로필 자동 복원
const authStore = useAuthStore()                 // ← pinia 등록 후에 호출
if (authStore.access) {
  authStore.fetchProfile().catch(() => {
    authStore.logout()
  })
}

app.mount('#app')

function loadKakaoMapScript() {
  return new Promise((resolve) => {
    if (window.kakao && window.kakao.maps) return resolve()
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_JS_KEY}&libraries=services&autoload=false`
    script.onload = () => window.kakao.maps.load(resolve)
    document.head.appendChild(script)
  })
}

loadKakaoMapScript()