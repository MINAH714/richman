<!-- frontend/src/components/NavBar.vue -->
<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="nav-logo">
        <i class="ti ti-pig-money" aria-hidden="true"></i>
        Richman
      </router-link>

      <ul class="nav-menu">
        <li>
          <span class="nav-item nav-disabled" title="준비 중">
            <i class="ti ti-receipt-2" aria-hidden="true"></i>
            소비
            <span class="nav-badge">준비중</span>
          </span>
        </li>
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
          <span class="nav-username">{{ authStore.user?.username }}</span>
          <button class="nav-btn nav-btn--outline" @click="logout">로그아웃</button>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-btn nav-btn--primary">로그인</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
const authStore = useAuthStore()
const router = useRouter()
function logout() {
  authStore.logout()
  router.push('/')
}
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
.nav-disabled { color: var(--color-text-tertiary); cursor: not-allowed; }
.nav-disabled:hover { background: none; color: var(--color-text-tertiary); }
.nav-badge {
  font-size: 9px;
  padding: 1px 6px;
  background: var(--color-bg-secondary);
  color: var(--color-text-tertiary);
  border-radius: 4px;
  font-weight: 600;
}
.nav-auth { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.nav-username { font-size: 0.8rem; color: var(--color-text-secondary); }
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
.nav-btn--outline {
  background: white;
  color: var(--color-text-secondary);
  border: 0.5px solid var(--color-border-strong);
}
.nav-btn--outline:hover { background: var(--color-bg-secondary); }
</style>