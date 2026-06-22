<!-- src/components/NavBar.vue -->
<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="nav-logo">
        <i class="ti ti-pig-money" aria-hidden="true"></i>
        Richman
      </router-link>

      <ul class="nav-menu">
        <li>
          <router-link to="/stocks/watchlist" class="nav-item">
            <i class="ti ti-chart-candle" aria-hidden="true"></i>
            주식
          </router-link>
        </li>
        <li>
          <router-link to="/crypto" class="nav-item">
            <i class="ti ti-coin" aria-hidden="true"></i>
            크립토
          </router-link>
        </li>
        <li>
          <router-link to="/crypto/buzz" class="nav-item">
            <i class="ti ti-flame" aria-hidden="true"></i>
            Buzz
          </router-link>
        </li>
        <li>
          <router-link to="/chat" class="nav-item">
            <i class="ti ti-robot" aria-hidden="true"></i>
            챗봇
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
                  👤 마이페이지
                </router-link>
                <div class="dropdown-divider" />
                <button class="dropdown-item dropdown-item--danger" @click="logout">
                  🚪 로그아웃
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
  (authStore.user?.nickname || authStore.user?.username || '?')[0]
)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

function logout() {
  dropdownOpen.value = false
  authStore.logout()
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
  z-index: 100;
  background: var(--color-bg-card);
  border-bottom: 0.5px solid var(--color-border);
  font-family: var(--font-main);
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
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
  flex-shrink: 0;
}
.nav-logo i { font-size: 18px; color: var(--color-primary); }
.nav-menu {
  display: flex;
  align-items: center;
  gap: 4px;
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
  border-radius: var(--radius-md);
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-item i { font-size: 16px; }
.nav-item:hover { background: var(--color-bg-secondary); color: var(--color-text-primary); }
.router-link-active.nav-item {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.nav-auth { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.nav-username { font-size: 0.8rem; color: var(--color-text-secondary); font-weight: 600; }
.nav-btn {
  padding: 7px 14px;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 500;
  font-family: var(--font-main);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
  border: none;
}
.nav-btn--primary { background: var(--color-primary); color: white; }
.nav-btn--primary:hover { background: var(--color-primary-hover); }

/* 프로필 드롭다운 */
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
  background: var(--color-bg-secondary);
  border-color: var(--color-border);
}
.profile-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
  transition: transform 0.15s;
}
.dropdown-arrow.open { transform: rotate(180deg); }

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 180px;
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-md);
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
  color: var(--color-text-secondary);
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  width: 100%;
  transition: background 0.15s;
}
.dropdown-item:hover { background: var(--color-bg-secondary); color: var(--color-primary); }
.dropdown-item--danger:hover { background: #fef2f2; color: #ef4444; }
.dropdown-divider {
  height: 0.5px;
  background: var(--color-border);
  margin: 4px 2px;
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>