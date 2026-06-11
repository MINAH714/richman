// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import GoogleCallbackView from '@/views/oauth/GoogleCallbackView.vue'
import KakaoCallbackView from '@/views/oauth/KakaoCallbackView.vue'

const routes = [
  // ── 인증 ───────────────────────────────────────────
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/oauth/google/callback',
    name: 'google-callback',
    component: GoogleCallbackView,
  },
  {
    path: '/oauth/naver/callback',
    name: 'naver-callback',
    component: () => import('@/views/oauth/NaverCallbackView.vue'),
  },
  {
    path: '/oauth/kakao/callback',
    name: 'KakaoCallback',
    component: () => import('@/views/oauth/KakaoCallbackView.vue'),
  },

  // ── 메인 ───────────────────────────────────────────
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },

  // ── 코인 대시보드 ────────────────────────────────────
  {
    path: '/crypto',
    name: 'crypto-dashboard',
    component: () => import('@/views/CryptoDashboardView.vue'),
  },
  {
    path: '/crypto/buzz',
    name: 'crypto-buzz',
    component: () => import('@/views/CryptoBuzzView.vue'),
  },

  // ── 감성 분석 (독립 페이지) ──────────────────────────
  // ※ /crypto/:market 보다 반드시 위에 위치해야 함 (라우트 충돌 방지)
  {
    path: '/crypto/sentiment/:market',
    name: 'crypto-sentiment',
    component: () => import('@/views/CryptoSentimentView.vue'),
    meta: { requiresAuth: true },
  },

  // ── 코인 상세 ────────────────────────────────────────
  // ※ 동적 세그먼트(:market)는 정적 경로보다 아래에 위치
  {
    path: '/crypto/:market',
    name: 'crypto-detail',
    component: () => import('@/views/CryptoDetailView.vue'),
  },

  // ── 404 ────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access')
  if (to.meta.requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router