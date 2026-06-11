<!-- frontend/src/components/NavBar.vue -->
<template>
  <nav class="navbar">
    <div class="nav-inner">

      <!-- 로고 -->
      <router-link to="/" class="nav-logo">
        💰 Richman
      </router-link>

      <!-- 메뉴 -->
      <ul class="nav-menu">
        <li>
          <router-link to="/crypto" class="nav-item">
            🪙 크립토
          </router-link>
        </li>
        <li>
          <router-link to="/crypto/buzz" class="nav-item">
            🔥 Buzz
          </router-link>
        </li>
        <li>
          <span class="nav-item nav-disabled" title="준비 중">
            📈 주식
            <span class="nav-badge">준비중</span>
          </span>
        </li>
        <li>
          <span class="nav-item nav-disabled" title="준비 중">
            💳 소비
            <span class="nav-badge">준비중</span>
          </span>
        </li>
        <li>
          <span class="nav-item nav-disabled" title="준비 중">
            🤖 챗봇
            <span class="nav-badge">준비중</span>
          </span>
        </li>
      </ul>

      <!-- 로그인/유저 -->
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
  background: white;
  border-bottom: 1px solid #e2ecf9;
  font-family: 'IBM Plex Mono', monospace;
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

/* 로고 */
.nav-logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  text-decoration: none;
  flex-shrink: 0;
}
.nav-logo:hover { color: #3b6fd4; }

/* 메뉴 */
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
  gap: 5px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-item:hover { background: #f0f6ff; color: #3b6fd4; }
.router-link-active.nav-item {
  background: #f0f6ff;
  color: #3b6fd4;
  font-weight: 700;
}

/* 비활성 메뉴 */
.nav-disabled {
  color: #94a3b8;
  cursor: not-allowed;
}
.nav-disabled:hover { background: none; color: #94a3b8; }
.nav-badge {
  font-size: 9px;
  padding: 1px 5px;
  background: #f1f5f9;
  color: #94a3b8;
  border-radius: 4px;
  font-weight: 600;
  letter-spacing: 0.03em;
}

/* 인증 */
.nav-auth {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.nav-username {
  font-size: 0.8rem;
  color: #64748b;
}
.nav-btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  font-family: 'IBM Plex Mono', monospace;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
  border: none;
}
.nav-btn--primary {
  background: #3b6fd4;
  color: white;
}
.nav-btn--primary:hover { background: #2d5ab8; }
.nav-btn--outline {
  background: white;
  color: #64748b;
  border: 1px solid #d0e2f5;
}
.nav-btn--outline:hover { background: #f1f5f9; }
</style>