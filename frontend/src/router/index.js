// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import GoogleCallbackView from '@/views/oauth/GoogleCallbackView.vue'
import KakaoCallbackView from '@/views/oauth/KakaoCallbackView.vue'

const routes = [
  // ── 메인 (로그인 불필요) ──────────────────────────────
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },

  // ── 인증 ─────────────────────────────────────────────
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
    component: KakaoCallbackView,
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('@/views/SignupView.vue'),
  },

  // ── 도메인 A: 온보딩 및 추천 ───────────────────────────
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('@/views/OnboardingView.vue'),
    meta: { requiresAuth: true }, // 로그인은 필수
  },
  {
    path: '/recommend',
    name: 'recommend',
    component: () => import('@/views/RecommendView.vue'),
    meta: { requiresAuth: true },
  },

  // ── 예적금 (Finlife) ───────────────────────────────────
  {
    path: '/finlife',
    name: 'finlife-list',
    component: () => import('@/views/FinlifeView.vue'),
  },
  {
    path: '/finlife/:id',
    name: 'finlife-detail',
    component: () => import('@/views/FinlifeDetailView.vue'),
  },

  // ── 코인 대시보드 ──────────────────────────────────────
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

  // ── 감성 분석 (/crypto/:market 보다 위에 위치) ─────────
  {
    path: '/crypto/sentiment/:market',
    name: 'crypto-sentiment',
    component: () => import('@/views/CryptoSentimentView.vue'),
    meta: { requiresAuth: true },
  },

  // ── 코인 상세 ──────────────────────────────────────────
  {
    path: '/crypto/:market',
    name: 'crypto-detail',
    component: () => import('@/views/CryptoDetailView.vue'),
  },

  // ── 주식 관심 종목 (로그인 필요) ────────────────────────────
  {
    path: '/stocks/watchlist',
    name: 'stock-watchlist',
    component: () => import('@/views/StockWatchlistView.vue'),
    meta: { requiresAuth: true },
  },

  // ── 주식 차트 (기능 2에서 내용 채울 예정, 일단 라우트만 등록) ───
  {
    path: '/stocks/chart/:symbol',
    name: 'stock-chart',
    component: () => import('@/views/StockChartView.vue'),
    meta: { requiresAuth: true },
  },
  // 기존 stock-chart 라우트 위에 추가
  {
    path: '/stocks/chart',
    name: 'stock-chart-default',
    // 파라미터 없이 접근 시 삼성전자 차트로 리다이렉트
    redirect: { name: 'stock-chart', params: { symbol: '005930.KS' } },
  },
  {
    path: '/stocks/prediction',
    name: 'stock-prediction',
    component: () => import('@/views/StockPredictionView.vue'),
    meta: { requiresAuth: true},
  },

  // ── 챗봇 ───────────────────────────────────────────────
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatPageView.vue'),
  },

  // ── 마이페이지 ─────────────────────────────────────────
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true },
  },

  {
    path: '/youtube',
    name: 'youtube-search',
    component: () => import('@/views/YoutubeSearchView.vue'),
  },

  {
    path: '/youtube/:videoId',
    name: 'youtube-detail',
    component: () => import('@/views/YoutubeDetailView.vue'),
    props: true,
  },
  // ── 기타 부가 기능 ─────────────────────────────────────
  {
    path: '/bank-map',
    name: 'bank-map',
    component: () => import('@/views/BankMapView.vue'),
  },

  {
  path: '/board',
  name: 'board-list',
  component: () => import('@/views/BoardListView.vue'),
},
{
  path: '/board/write',
  name: 'board-write',
  component: () => import('@/views/BoardWriteView.vue'),
  meta: { requiresAuth: true },
},
{
  path: '/board/:id/edit',
  name: 'board-edit',
  component: () => import('@/views/BoardWriteView.vue'),
  meta: { requiresAuth: true },
},
{
  path: '/board/:id',
  name: 'board-detail',
  component: () => import('@/views/BoardDetailView.vue'),
},

  {
      path: '/commodities',
      name: 'commodities',
      component: () => import('@/views/CommoditiesView.vue'),
    },
  
  // ── 404 (항상 가장 마지막에 위치해야 함) ────────────────
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

// ── 전역 라우터 가드 (온보딩 및 인증 제어) ─────────────────
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access')
  const isOnboarded = localStorage.getItem('is_onboarded') === 'true'

  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  const isAuthRoute = to.path.startsWith('/oauth') || to.name === 'login' || to.name === 'signup'
  
  if (token && !isOnboarded && to.name !== 'onboarding' && !isAuthRoute) {
    alert('Richman에 오신 것을 환영합니다! 🎉\n\n고객님께 딱 맞는 금융 여정을 설계하기 위해, 먼저 1분만 투자해서 몇 가지 질문에 답해주세요.')
    
    return next({ name: 'onboarding', replace: true })
  }

  if (token && isOnboarded && to.name === 'onboarding') {
    return next({ name: 'home', replace: true })
  }

  next()
})

export default router