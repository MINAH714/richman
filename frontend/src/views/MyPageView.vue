<!-- src/views/MyPageView.vue -->
<template>
  <div class="mypage">
    <div class="mypage-inner">
      <aside class="mypage-side">
        <div class="side-profile">
          <div class="side-avatar">
            <img v-if="authStore.user?.profile_image_url" :src="authStore.user.profile_image_url" alt="" />
            <span v-else>{{ initial }}</span>
          </div>
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

      <main class="mypage-content">
        <SpendingTab  v-if="activeTab === 'spending'" />
        <PortfolioTab v-else-if="activeTab === 'portfolio'" />
        <MyProfileTab v-else-if="activeTab === 'profile'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import SpendingTab  from '@/components/mypage/SpendingTab.vue'
import PortfolioTab from '@/components/mypage/PortfolioTab.vue'
import MyProfileTab from '@/components/mypage/MyProfileTab.vue'

const authStore = useAuthStore()
const router    = useRouter()

const MENU = [
  { key: 'profile',   label: '프로필' },
  { key: 'portfolio', label: '포트폴리오' },
  { key: 'spending',  label: '소비' },
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
  background: var(--color-bg-page);
  min-height: calc(100vh - 56px);
  padding: 40px 24px;
  font-family: var(--font-main);
  color: var(--color-text-primary);
}

.mypage-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
  align-items: start;
}

/* ── 좌측 사이드바 ── */
.mypage-side {
  position: sticky;
  top: 72px;
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 프로필 영역 */
.side-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  margin-bottom: 8px;
  border-bottom: 0.5px solid var(--color-border);
}

.side-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.side-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 2px;
}

.side-email {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 130px;
}

/* 메뉴 */
.side-menu {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.side-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
  font-family: var(--font-main);
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: background 0.15s, color 0.15s;
  width: 100%;
}

.side-menu__item i {
  font-size: 17px;
  flex-shrink: 0;
}

.side-menu__item:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.side-menu__item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.side-menu__item.active i {
  color: var(--color-primary);
}

/* 로그아웃 버튼 */
.side-logout {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 8px;
  padding: 10px 12px;
  border: 0.5px solid var(--color-border);
  background: none;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--font-main);
  border-radius: var(--radius-md);
  width: 100%;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.side-logout i { font-size: 16px; }

.side-logout:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

/* ── 우측 콘텐츠 ── */
.mypage-content {
  min-width: 0;
  background: var(--color-bg-card);
  border: 0.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 28px;
}

/* ── 반응형 ── */
@media (max-width: 900px) {
  .mypage-inner {
    grid-template-columns: 1fr;
  }

  .mypage-side {
    position: static;
    flex-direction: row;
    align-items: center;
    padding: 12px 16px;
    gap: 8px;
    overflow-x: auto;
  }

  .side-profile { display: none; }

  .side-menu {
    flex-direction: row;
    flex: 1;
    gap: 4px;
  }

  .side-menu__item {
    white-space: nowrap;
    padding: 8px 12px;
    border-radius: var(--radius-md);
  }

  .side-logout {
    margin-top: 0;
    white-space: nowrap;
    width: auto;
    padding: 8px 12px;
  }

  .mypage-content {
    padding: 20px;
  }
}

@media (max-width: 600px) {
  .mypage { padding: 20px 16px; }
}
</style>