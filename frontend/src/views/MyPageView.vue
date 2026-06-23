<!-- src/views/MyPageView.vue -->
<template>
  <div class="mypage">
    <div class="mypage-inner">

      <!-- 좌측 사이드바 -->
      <aside class="mypage-side">
        <div class="side-profile">
          <div class="side-avatar">{{ initial }}</div>
          <p class="side-name">{{ authStore.user?.nickname || authStore.user?.username || '...' }}</p>
        </div>

        <nav class="side-menu">
          <button
            v-for="item in MENU"
            :key="item.key"
            class="side-menu__item"
            :class="{ active: activeTab === item.key }"
            @click="activeTab = item.key"
          >
            <span class="side-menu__label">{{ item.label }}</span>
          </button>
        </nav>

        <button class="side-logout" @click="logout">로그아웃</button>
      </aside>

      <!-- 우측 콘텐츠 -->
      <main class="mypage-content">

        <SpendingTab v-if="activeTab === 'spending'" />
        <PortfolioTab v-else-if="activeTab === 'portfolio'" />
        <EditProfileTab v-else-if="activeTab === 'profile'" />

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import SpendingTab    from '@/components/mypage/SpendingTab.vue'
import PortfolioTab   from '@/components/mypage/PortfolioTab.vue'
import EditProfileTab from '@/components/mypage/EditProfileTab.vue'

const authStore = useAuthStore()
const router    = useRouter()

const MENU = [
  { key: 'spending',  label: '소비 분석' },
  { key: 'portfolio', label: '포트폴리오' },
  { key: 'profile',   label: '프로필 수정' },
]
const activeTab = ref('spending')

onMounted(() => {
  if (!authStore.user) authStore.fetchProfile()
})

const initial = computed(() =>
  (authStore.user?.nickname || authStore.user?.username || '?')[0]
)

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.mypage {
  background: #f8f9fa;
  min-height: calc(100vh - 56px);
  padding: 48px 24px;
  font-family: 'Inter', sans-serif;
  color: #191c1d;
}
.mypage-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
}

/* ── 좌측 사이드바 ── */
.mypage-side {
  position: sticky;
  top: 80px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.side-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 4px 20px;
  border-bottom: 1px solid #e1e3e4;
  margin-bottom: 12px;
}
.side-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #191c1d;
  color: #ffffff;
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.side-name {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: .92rem;
  font-weight: 700;
  color: #191c1d;
}

.side-menu {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.side-menu__item {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  background: none;
  border: none;
  border-radius: 0;
  cursor: pointer;
  text-align: left;
  font-family: 'Inter', sans-serif;
  font-size: .88rem;
  font-weight: 500;
  color: #4c4546;
  transition: background .12s, color .12s, border-color .12s;
  border-right: 2px solid transparent;
}
.side-menu__item:hover { background: #f3f4f5; color: #191c1d; }
.side-menu__item.active {
  background: #f3f4f5;
  color: #191c1d;
  font-weight: 700;
  border-right: 2px solid #191c1d;
}

.side-logout {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #cfc4c5;
  background: #ffffff;
  color: #4c4546;
  font-size: .8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  border-radius: 0;
  transition: border-color .12s, color .12s;
}
.side-logout:hover { border-color: #ba1a1a; color: #ba1a1a; }

.mypage-content { min-width: 0; }

@media (max-width: 900px) {
  .mypage-inner { grid-template-columns: 1fr; }
  .mypage-side {
    position: static;
    flex-direction: row;
    align-items: center;
    overflow-x: auto;
  }
  .side-profile { display: none; }
  .side-menu { flex-direction: row; }
  .side-menu__item { border-right: none; border-bottom: 2px solid transparent; white-space: nowrap; }
  .side-menu__item.active { border-right: none; border-bottom: 2px solid #191c1d; }
  .side-logout { display: none; }
}
</style>