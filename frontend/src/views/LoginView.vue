<template>
  <div class="login-page">
    <div class="bg-blob bg-blob-1" aria-hidden="true"></div>
    <div class="bg-blob bg-blob-2" aria-hidden="true"></div>

    <div class="login-card">

      <!-- 로고 -->
      <div class="logo-wrap">
        <div class="logo-icon">◈</div>
        <h1 class="logo-text">RICHMAN</h1>
        <p class="logo-sub">금융 통합 플랫폼</p>
      </div>

      <!-- 에러 메시지 -->
      <transition name="slide-down">
        <div v-if="errorMsg" class="error-banner" role="alert">
          <svg class="err-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/>
            <path d="M10 6v4M10 13.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          {{ errorMsg }}
        </div>
      </transition>

      <!-- 로그인 폼 -->
      <form @submit.prevent="login" class="login-form" novalidate>
        <div class="field-wrap">
          <label class="field-label" for="username">아이디</label>
          <div class="input-wrap">
            <svg class="input-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <circle cx="10" cy="7" r="3.5" stroke="currentColor" stroke-width="1.4"/>
              <path d="M3 17c0-3.314 3.134-6 7-6s7 2.686 7 6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            <input
              id="username"
              v-model="username"
              type="text"
              class="field-input"
              placeholder="아이디를 입력하세요"
              autocomplete="username"
              :disabled="isLoading"
            />
          </div>
        </div>

        <div class="field-wrap">
          <label class="field-label" for="password">비밀번호</label>
          <div class="input-wrap">
            <svg class="input-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <rect x="3.5" y="8.5" width="13" height="9" rx="2" stroke="currentColor" stroke-width="1.4"/>
              <path d="M7 8.5V6a3 3 0 016 0v2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            <input
              id="password"
              v-model="password"
              :type="showPw ? 'text' : 'password'"
              class="field-input has-toggle"
              placeholder="비밀번호를 입력하세요"
              autocomplete="current-password"
              :disabled="isLoading"
            />
            <button
              type="button"
              class="pw-toggle"
              @click="showPw = !showPw"
              tabindex="-1"
              :aria-label="showPw ? '비밀번호 숨기기' : '비밀번호 표시'"
            >
              <!-- 눈 열림 -->
              <svg v-if="!showPw" viewBox="0 0 20 20" fill="none">
                <path d="M1 10s3-6 9-6 9 6 9 6-3 6-9 6-9-6-9-6z" stroke="currentColor" stroke-width="1.4"/>
                <circle cx="10" cy="10" r="2.5" stroke="currentColor" stroke-width="1.4"/>
              </svg>
              <!-- 눈 닫힘 -->
              <svg v-else viewBox="0 0 20 20" fill="none">
                <path d="M2 2l16 16M8.5 8.7A2.5 2.5 0 0012.7 13M6.2 5.4C4.1 6.7 2.6 8.7 2.6 10c0 0 3 6 7.4 6 1.3 0 2.5-.4 3.5-1M10 4C14.4 4 17.4 10 17.4 10c-.4.9-1 1.8-1.7 2.6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="btn-primary"
          :disabled="isLoading || !username || !password"
        >
          <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
          <svg v-else class="btn-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M3 10h14M11 4l6 6-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <!-- 구분선 -->
      <div class="divider">
        <span>소셜 계정으로 계속하기</span>
      </div>

      <!-- 소셜 로그인 -->
      <div class="social-wrap">
        <button class="btn-social btn-google" @click="googleLogin" :disabled="isLoading" type="button">
          <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Google
        </button>

        <button class="btn-social btn-kakao" @click="kakaoLogin" :disabled="isLoading" type="button">
          <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 3C6.477 3 2 6.477 2 10.8c0 2.7 1.636 5.08 4.1 6.52l-1.046 3.9 4.556-2.997A11.8 11.8 0 0012 18.6c5.523 0 10-3.477 10-7.8S17.523 3 12 3z" fill="#3C1E1E"/>
          </svg>
          Kakao
        </button>

        <button class="btn-social btn-naver" @click="naverLogin" :disabled="isLoading" type="button">
          <span class="naver-n" aria-hidden="true">N</span>
          Naver
        </button>
      </div>

      <!-- 회원가입 링크 -->
      <p class="signup-link">
        아직 계정이 없으신가요?
        <RouterLink to="/signup">회원가입</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const username  = ref('')
const password  = ref('')
const showPw    = ref(false)
const isLoading = ref(false)
const errorMsg  = ref('')

// ── 일반 로그인 ──────────────────────────────────────────
const login = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    await authStore.login(username.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    errorMsg.value = e.response?.status === 401
      ? '아이디 또는 비밀번호가 올바르지 않습니다.'
      : '로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    isLoading.value = false
  }
}

// ── Google OAuth ─────────────────────────────────────────
const googleLogin = () => {
  const params = new URLSearchParams({
    client_id:     import.meta.env.VITE_GOOGLE_CLIENT_ID,
    redirect_uri:  'http://localhost:5173/oauth/google/callback',
    response_type: 'code',
    scope:         'email profile',
  })
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`
}

// ── Kakao OAuth ──────────────────────────────────────────
const kakaoLogin = () => {
  const clientId = import.meta.env.VITE_KAKAO_CLIENT_ID
  const redirectUri = import.meta.env.VITE_KAKAO_REDIRECT_URI
  
  const kakaoAuthUrl =
    `https://kauth.kakao.com/oauth/authorize` +
    `?client_id=${clientId}` +
    `&redirect_uri=${redirectUri}` +
    `&response_type=code` +
    `&prompt=login` 
  
  window.location.href = kakaoAuthUrl
}

// ── Naver OAuth ──────────────────────────────────────────
const naverLogin = () => {
  const state = crypto.randomUUID()
  sessionStorage.setItem('naver_oauth_state', state)
  const params = new URLSearchParams({
    client_id:     import.meta.env.VITE_NAVER_CLIENT_ID,
    redirect_uri:  import.meta.env.VITE_NAVER_REDIRECT_URI,
    response_type: 'code',
    state,
  })
  window.location.href = `https://nid.naver.com/oauth2.0/authorize?${params}`
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&display=swap');

/* ── 색상 변수 ────────────────────────────────────────── */
.login-page {
  --blue-50:  #eff6ff;
  --blue-100: #dbeafe;
  --blue-200: #bfdbfe;
  --blue-300: #93c5fd;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --blue-700: #1d4ed8;

  --gray-50:  #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-400: #94a3b8;
  --gray-500: #64748b;
  --gray-700: #334155;
  --gray-900: #0f172a;

  --red-50:  #fef2f2;
  --red-200: #fecaca;
  --red-600: #dc2626;

  font-family: 'Noto Sans KR', sans-serif;
}

/* ── 페이지 ──────────────────────────────────────────── */
.login-page {
  min-height: 100vh;
  background: linear-gradient(150deg, #eff6ff 0%, #f0f9ff 55%, #eef2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

/* 배경 블롭 */
.bg-blob {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}
.bg-blob-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(59,130,246,0.10) 0%, transparent 70%);
  top: -150px;
  right: -100px;
}
.bg-blob-2 {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(99,102,241,0.09) 0%, transparent 70%);
  bottom: -100px;
  left: -80px;
}

/* ── 카드 ────────────────────────────────────────────── */
.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid var(--blue-100);
  box-shadow:
    0 2px 4px rgba(0,0,0,0.04),
    0 12px 40px rgba(37,99,235,0.09);
  padding: 44px 40px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── 로고 ────────────────────────────────────────────── */
.logo-wrap { text-align: center; }

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  background: var(--blue-50);
  border: 1.5px solid var(--blue-200);
  border-radius: 14px;
  font-size: 22px;
  color: var(--blue-600);
  margin-bottom: 14px;
}

.logo-text {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 600;
  color: var(--gray-900);
  letter-spacing: 0.10em;
}
.logo-sub {
  margin: 0;
  font-size: 12px;
  color: var(--gray-400);
  letter-spacing: 0.03em;
}

/* ── 에러 배너 ───────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: var(--red-50);
  border: 1px solid var(--red-200);
  color: var(--red-600);
  font-size: 13px;
  padding: 11px 14px;
  border-radius: 10px;
  line-height: 1.5;
}
.err-icon { width: 16px; height: 16px; flex-shrink: 0; margin-top: 1px; }

.slide-down-enter-active { transition: all 0.2s ease; }
.slide-down-leave-active { transition: all 0.15s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-6px); }
.slide-down-leave-to     { opacity: 0; }

/* ── 폼 ──────────────────────────────────────────────── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-700);
}
.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 12px;
  width: 17px;
  height: 17px;
  stroke: var(--gray-300);
  pointer-events: none;
}
.field-input {
  width: 100%;
  box-sizing: border-box;
  background: var(--gray-50);
  border: 1.5px solid var(--gray-200);
  color: var(--gray-900);
  font-family: inherit;
  font-size: 14px;
  padding: 11px 12px 11px 40px;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.18s, background 0.18s, box-shadow 0.18s;
}
.field-input.has-toggle { padding-right: 42px; }
.field-input::placeholder { color: var(--gray-300); }
.field-input:hover:not(:disabled) {
  border-color: var(--blue-300);
  background: #fff;
}
.field-input:focus {
  border-color: var(--blue-500);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
}
.field-input:disabled { opacity: 0.5; cursor: not-allowed; }

.pw-toggle {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--gray-300);
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: color 0.15s;
}
.pw-toggle svg { width: 17px; height: 17px; stroke: currentColor; }
.pw-toggle:hover { color: var(--blue-500); }

/* ── 로그인 버튼 ──────────────────────────────────────── */
.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: var(--blue-600);
  border: none;
  color: #fff;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 10px;
  margin-top: 2px;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
  box-shadow: 0 2px 10px rgba(37,99,235,0.25);
  letter-spacing: 0.02em;
}
.btn-primary:hover:not(:disabled) {
  background: var(--blue-700);
  box-shadow: 0 4px 16px rgba(37,99,235,0.32);
}
.btn-primary:active:not(:disabled) { transform: scale(0.99); }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }

.btn-icon { width: 16px; height: 16px; stroke: #fff; }

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 구분선 ──────────────────────────────────────────── */
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--gray-100);
}
.divider span {
  font-size: 11px;
  color: var(--gray-400);
  white-space: nowrap;
  letter-spacing: 0.04em;
}

/* ── 소셜 버튼 ───────────────────────────────────────── */
.social-wrap {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.btn-social {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 13px 8px 11px;
  border-radius: 10px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1.5px solid var(--gray-200);
  background: #fff;
  color: var(--gray-700);
  transition: border-color 0.15s, background 0.15s, transform 0.12s, box-shadow 0.15s;
}
.btn-social:hover:not(:disabled) {
  background: var(--gray-50);
  border-color: var(--gray-300);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.07);
}
.btn-social:active:not(:disabled) { transform: scale(0.97); }
.btn-social:disabled { opacity: 0.4; cursor: not-allowed; }

.social-icon { width: 22px; height: 22px; }

.btn-kakao {
  border-color: #f5d700;
  background: #fee500;
  color: #3c1e1e;
}
.btn-kakao:hover:not(:disabled) {
  background: #fdd800;
  border-color: #e5c900;
}
.btn-naver {
  border-color: #03c75a;
  background: #03c75a;
  color: #fff;
}
.btn-naver:hover:not(:disabled) {
  background: #02b350;
  border-color: #02b350;
}
.naver-n {
  font-size: 18px;
  font-weight: 700;
  font-family: Arial, sans-serif;
  line-height: 1;
}

/* ── 회원가입 링크 ────────────────────────────────────── */
.signup-link {
  text-align: center;
  font-size: 13px;
  color: var(--gray-400);
  margin: 0;
}
.signup-link a {
  color: var(--blue-600);
  font-weight: 500;
  text-decoration: none;
  margin-left: 4px;
}
.signup-link a:hover { text-decoration: underline; }
</style>