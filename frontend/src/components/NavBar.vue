// frontend/src/components/NavBar.vue
<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="nav-logo">
        <i class="ti ti-pig-money" aria-hidden="true"></i>
        Richman
      </router-link>

      <ul class="nav-menu">
        <li class="nav-item-dropdown">
          <div class="nav-item">
            <i class="ti ti-building-bank" aria-hidden="true"></i>
            예/적금
            <i class="ti ti-chevron-down arrow" aria-hidden="true"></i>
          </div>
          <ul class="dropdown-menu">
            <li>
              <router-link to="/finlife" class="dropdown-link">예적금 목록</router-link>
            </li>
            <li>
              <router-link to="/bank-map" class="dropdown-link">근처 은행 위치</router-link>
            </li>
            <li>
              <router-link to="/youtube" class="dropdown-link">관심 영상 자료</router-link>
            </li>
          </ul>
        </li>

        <li>
          <router-link to="/stocks/watchlist" class="nav-item">
            <i class="ti ti-chart-candle" aria-hidden="true"></i>
            주식/현물
            <i class="ti ti-chevron-down arrow" aria-hidden="true"></i>
          </router-link>
          <ul class="dropdown-menu">
            <li>
              <router-link to="/stocks/chart/AAPL" class="dropdown-link">주식 시세표</router-link>
            </li>
            <li>
              <router-link to="/commodities" class="dropdown-link">금/은 현물 시세</router-link>
            </li>
          </ul>
        </li>

        <li class="nav-item-dropdown">
          <div class="nav-item">
            <i class="ti ti-coin" aria-hidden="true"></i>
            크립토
            <i class="ti ti-chevron-down arrow" aria-hidden="true"></i>
          </div>
          <ul class="dropdown-menu">
            <li>
              <router-link to="/crypto" class="dropdown-link">시세 대시보드</router-link>
            </li>
            <li>
              <router-link to="/crypto/buzz" class="dropdown-link">크립토 Buzz</router-link>
            </li>
          </ul>
        </li>

        <li>
          <router-link to="/chat" class="nav-item">
            <i class="ti ti-robot" aria-hidden="true"></i>
            AI 챗봇
          </router-link>
        </li>
        <li>
          <router-link to="/board" class="nav-item">
            <i class="ti ti-message-circle" aria-hidden="true"></i>
            게시판
          </router-link>
        </li>
      </ul>
      <div class="nav-auth">
        <template v-if="authStore.isLoggedIn">
          <div class="profile-menu" ref="profileMenuRef">
            <button class="profile-trigger" @click="toggleDropdown">
              <span class="profile-icon">{{ initial }}</span>
              <span class="nav-username">{{ authStore.user?.nickname || authStore.user?.username }}</span>
              <span class="dropdown-arrow" :class="{ open: dropdownOpen }">▾</span>
            </button>

            <transition name="dropdown-fade">
              <div v-if="dropdownOpen" class="profile-dropdown">
                <router-link to="/mypage" class="dropdown-item" @click="dropdownOpen = false">
                  <i class="ti ti-user" aria-hidden="true"></i> 마이페이지
                </router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item dropdown-item--danger" @click="logout">
                  <i class="ti ti-logout" aria-hidden="true"></i> 로그아웃
                </button>
              </div>
            </transition>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-btn nav-btn--primary">로그인</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const dropdownOpen   = ref(false)
const profileMenuRef = ref(null)

const initial = computed(() =>
  (authStore.user?.nickname || authStore.user?.username || '?')[0].toUpperCase()
)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

async function logout() {
  dropdownOpen.value = false
  await authStore.logout()
  router.push('/')
}

function handleOutsideClick(e) {
  if (profileMenuRef.value && !profileMenuRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--color-bg-card, #ffffff);
  border-bottom: 0.5px solid var(--color-border, #e2e8f0);
  font-family: var(--font-main, sans-serif);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 32px;
}
.nav-logo {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary, #1e293b);
  text-decoration: none;
  flex-shrink: 0;
}
.nav-logo i { font-size: 20px; color: var(--color-primary, #42b883); }

/* ── 메인 메뉴 및 드롭다운 ── */
.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: var(--radius-md, 6px);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-item i { font-size: 18px; }
.nav-item .arrow { font-size: 14px; margin-left: 2px; transition: transform 0.2s; }

.nav-item:hover,
.nav-item-dropdown:hover .nav-item {
  background: var(--color-bg-secondary, #f1f5f9);
  color: var(--color-text-primary, #1e293b);
}

.router-link-active.nav-item {
  background: var(--color-primary-light, #ecfdf5);
  color: var(--color-primary, #42b883);
}

/* Hover Dropdown */
.nav-item-dropdown {
  position: relative;
}

.nav-item-dropdown:hover .arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: var(--color-bg-card, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-md, 8px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  min-width: 150px;
  padding: 8px 0;
  list-style: none;
  margin: 0;
  
  /* Hover 애니메이션 */
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.2s ease;
  z-index: 200;
}

.nav-item-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(4px); /* 살짝 아래로 띄움 */
}

.dropdown-link {
  display: block;
  padding: 10px 16px;
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.dropdown-link:hover {
  background: var(--color-bg-secondary, #f1f5f9);
  color: var(--color-primary, #42b883);
}

.router-link-exact-active.dropdown-link {
  color: var(--color-primary, #42b883);
  font-weight: 600;
  background: var(--color-primary-light, #ecfdf5);
}

/* ── 인증 영역 ── */
.nav-auth { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.nav-username { font-size: 0.85rem; color: var(--color-text-secondary, #64748b); font-weight: 600; }
.nav-btn {
  padding: 7px 16px;
  border-radius: var(--radius-md, 6px);
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-main, sans-serif);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
  border: none;
}
.nav-btn--primary { background: var(--color-primary, #42b883); color: white; }
.nav-btn--primary:hover { background: var(--color-primary-hover, #34d399); }

/* 프로필 드롭다운 (기존 유지) */
.profile-menu { position: relative; }
.profile-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px 5px 5px;
  border-radius: 20px;
  border: 0.5px solid transparent;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, border-color 0.15s;
}
.profile-trigger:hover {
  background: var(--color-bg-secondary, #f1f5f9);
  border-color: var(--color-border, #e2e8f0);
}
.profile-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-primary, #42b883);
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.dropdown-arrow { font-size: 0.7rem; color: var(--color-text-tertiary, #94a3b8); transition: transform 0.15s; }
.dropdown-arrow.open { transform: rotate(180deg); }

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 180px;
  background: var(--color-bg-card, #ffffff);
  border: 0.5px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 7px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  width: 100%;
  transition: background 0.15s;
}
.dropdown-item:hover { background: var(--color-bg-secondary, #f1f5f9); color: var(--color-primary, #42b883); }
.dropdown-item--danger:hover { background: #fef2f2; color: #ef4444; }
.dropdown-divider { height: 0.5px; background: var(--color-border, #e2e8f0); margin: 4px 2px; }

.dropdown-fade-enter-active, .dropdown-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.dropdown-fade-enter-from, .dropdown-fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>